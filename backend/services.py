"""
Business logic services that integrate the AI pipeline with database operations.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import sys
import os

from backend.models import (
    Product, Inventory, SalesHistory, ReorderDecision, DecisionLog,
    Brand, User
)
import sys
import os
# Add parent directory to path for pipeline import
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from pipeline import InventoryDecisionPipeline


class InventoryService:
    """Service for inventory management and AI decision generation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_sales_dataframe(self, product_id: str, min_days: int = 30) -> pd.DataFrame:
        """
        Get historical sales data as DataFrame for forecasting.
        
        Args:
            product_id: Product ID
            min_days: Minimum days of data required
            
        Returns:
            DataFrame with 'date' and 'demand' columns
        """
        sales = self.db.query(SalesHistory).filter(
            SalesHistory.product_id == product_id
        ).order_by(SalesHistory.date).all()
        
        if len(sales) < min_days:
            raise ValueError(
                f"Insufficient sales data. Need at least {min_days} days, got {len(sales)}"
            )
        
        df = pd.DataFrame([{
            'date': s.date,
            'demand': s.demand
        } for s in sales])
        
        return df
    
    def create_pipeline_for_product(self, product: Product) -> InventoryDecisionPipeline:
        """
        Create pipeline instance configured for a product.
        
        Args:
            product: Product model instance
            
        Returns:
            Configured InventoryDecisionPipeline
        """
        pipeline = InventoryDecisionPipeline(
            unit_cost=product.unit_cost,
            selling_price=product.selling_price,
            holding_cost_rate=product.holding_cost_rate,
            markdown_rate=product.markdown_rate,
            churn_penalty=product.churn_penalty,
            n_simulations=5000,
            max_stockout_probability=0.20
        )
        
        return pipeline
    
    def generate_reorder_decision(
        self,
        product: Product,
        available_cash: Optional[float] = None,
        baseline_quantity: Optional[float] = None
    ) -> ReorderDecision:
        """
        Generate AI reorder decision for a product.
        
        Args:
            product: Product model instance
            available_cash: Available cash constraint
            baseline_quantity: Baseline quantity for comparison
            
        Returns:
            ReorderDecision model instance
        """
        # Get current inventory
        inventory = self.db.query(Inventory).filter(
            Inventory.product_id == product.id
        ).first()
        
        if not inventory:
            raise ValueError(f"No inventory record found for product {product.id}")
        
        current_inventory = inventory.current_quantity
        
        # Get sales data
        try:
            sales_df = self.get_sales_dataframe(product.id, min_days=30)
        except ValueError as e:
            raise ValueError(f"Cannot generate decision: {str(e)}")
        
        # Create and configure pipeline
        pipeline = self.create_pipeline_for_product(product)
        
        # Train forecaster
        sku_id = product.id
        pipeline.train_forecaster(sales_df, sku_id=sku_id)
        
        # Run optimization
        result = pipeline.run_pipeline(
            sku_id=sku_id,
            current_inventory=current_inventory,
            lead_time_days=product.lead_time_days,
            forecast_horizon_days=30,
            min_order_quantity=product.min_order_quantity,
            max_order_quantity=10000,  # Configurable
            order_multiple=product.order_multiple,
            available_cash=available_cash,
            holding_period_months=1.0,
            distribution_type='normal',
            naive_quantity=baseline_quantity
        )
        
        opt_result = result['optimization_result']
        cost_breakdown = result['cost_breakdown']
        current_risk = result['current_risk']
        comparison = result.get('comparison_result')
        
        # Create decision record
        decision = ReorderDecision(
            brand_id=product.brand_id,
            product_id=product.id,
            recommended_quantity=opt_result['optimal_quantity'],
            current_inventory=current_inventory,
            stockout_probability_before=current_risk['stockout_probability'],
            stockout_probability_after=opt_result['risk_metrics']['stockout_probability'],
            risk_category_before=current_risk['risk_category'],
            risk_category_after=opt_result['risk_metrics']['risk_category'],
            expected_overstock_cost=cost_breakdown['expected_overstock_cost'],
            expected_understock_cost=cost_breakdown['expected_understock_cost'],
            total_expected_loss=cost_breakdown['total_expected_loss'],
            cash_locked=opt_result['cash_locked'],
            cash_freed=comparison['cash_saved'] if comparison and comparison['cash_saved'] > 0 else 0.0,
            baseline_quantity=baseline_quantity,
            loss_reduction=comparison['loss_reduction'] if comparison else None,
            loss_reduction_pct=comparison['loss_reduction_pct'] if comparison else None,
            status="pending",
            lead_time_days=product.lead_time_days,
            forecast_horizon_days=30,
            n_simulations=5000,
            forecast_data=result['forecast'].to_dict('records') if 'forecast' in result else None
        )
        
        self.db.add(decision)
        self.db.commit()
        self.db.refresh(decision)
        
        # Log decision creation
        self.log_decision_action(
            decision_id=decision.id,
            user_id=None,  # System-generated
            action="created",
            notes="AI-generated recommendation"
        )
        
        return decision
    
    def accept_decision(
        self,
        decision_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> ReorderDecision:
        """
        Accept a reorder decision and update inventory.
        
        Args:
            decision_id: Decision ID
            user_id: User accepting the decision
            notes: Optional notes
            
        Returns:
            Updated ReorderDecision
        """
        decision = self.db.query(ReorderDecision).filter(
            ReorderDecision.id == decision_id
        ).first()
        
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        
        if decision.status != "pending":
            raise ValueError(f"Decision {decision_id} is already {decision.status}")
        
        # Get inventory
        inventory = self.db.query(Inventory).filter(
            Inventory.product_id == decision.product_id
        ).first()
        
        if not inventory:
            raise ValueError(f"Inventory not found for product {decision.product_id}")
        
        # Store previous state for logging
        previous_inventory = inventory.current_quantity
        
        # Update inventory (add reorder quantity)
        inventory.current_quantity += decision.recommended_quantity
        inventory.last_updated = datetime.utcnow()
        
        # Update decision status
        decision.status = "accepted"
        decision.accepted_at = datetime.utcnow()
        decision.accepted_by = user_id
        
        self.db.commit()
        self.db.refresh(decision)
        
        # Log acceptance
        self.log_decision_action(
            decision_id=decision.id,
            user_id=user_id,
            action="accepted",
            previous_state={"inventory": previous_inventory},
            new_state={"inventory": inventory.current_quantity},
            inventory_before=previous_inventory,
            inventory_after=inventory.current_quantity,
            cash_impact=decision.cash_locked,
            notes=notes
        )
        
        return decision
    
    def reject_decision(
        self,
        decision_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> ReorderDecision:
        """
        Reject a reorder decision.
        
        Args:
            decision_id: Decision ID
            user_id: User rejecting the decision
            reason: Optional rejection reason
            
        Returns:
            Updated ReorderDecision
        """
        decision = self.db.query(ReorderDecision).filter(
            ReorderDecision.id == decision_id
        ).first()
        
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        
        if decision.status != "pending":
            raise ValueError(f"Decision {decision_id} is already {decision.status}")
        
        decision.status = "rejected"
        
        self.db.commit()
        self.db.refresh(decision)
        
        # Log rejection
        self.log_decision_action(
            decision_id=decision.id,
            user_id=user_id,
            action="rejected",
            notes=reason or "User rejected decision"
        )
        
        return decision
    
    def log_decision_action(
        self,
        decision_id: str,
        user_id: Optional[str],
        action: str,
        previous_state: Optional[Dict] = None,
        new_state: Optional[Dict] = None,
        inventory_before: Optional[float] = None,
        inventory_after: Optional[float] = None,
        cash_impact: Optional[float] = None,
        notes: Optional[str] = None
    ):
        """Log a decision action for audit trail."""
        decision = self.db.query(ReorderDecision).filter(
            ReorderDecision.id == decision_id
        ).first()
        
        log = DecisionLog(
            brand_id=decision.brand_id,
            decision_id=decision_id,
            user_id=user_id or "system",
            action=action,
            previous_state=previous_state,
            new_state=new_state,
            inventory_before=inventory_before,
            inventory_after=inventory_after,
            cash_impact=cash_impact,
            notes=notes
        )
        
        self.db.add(log)
        self.db.commit()
    
    def generate_decisions_for_brand(
        self,
        brand_id: str,
        product_ids: Optional[List[str]] = None,
        available_cash: Optional[float] = None,
        baseline_quantities: Optional[Dict[str, float]] = None
    ) -> List[ReorderDecision]:
        """
        Generate reorder decisions for multiple products.
        
        Args:
            brand_id: Brand ID
            product_ids: List of product IDs (None = all active products)
            available_cash: Total available cash
            baseline_quantities: Dict mapping product_id to baseline quantity
            
        Returns:
            List of created ReorderDecision instances
        """
        # Get products
        query = self.db.query(Product).filter(
            Product.brand_id == brand_id,
            Product.is_active == True
        )
        
        if product_ids:
            query = query.filter(Product.id.in_(product_ids))
        
        products = query.all()
        
        if not products:
            raise ValueError("No active products found")
        
        decisions = []
        
        for product in products:
            try:
                baseline_qty = baseline_quantities.get(product.id) if baseline_quantities else None
                decision = self.generate_reorder_decision(
                    product=product,
                    available_cash=available_cash,
                    baseline_quantity=baseline_qty
                )
                decisions.append(decision)
            except Exception as e:
                # Log error but continue with other products
                print(f"Error generating decision for product {product.id}: {str(e)}")
                continue
        
        return decisions

