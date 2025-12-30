"""
AI service that integrates the inventory decision pipeline.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from pipeline import InventoryDecisionPipeline
from app.models.inventory import Product, Inventory, SalesHistory, ReorderDecision, RiskCategory, DecisionStatus


class AIService:
    """Service for running AI-driven inventory decisions."""
    
    def __init__(self):
        """Initialize AI service."""
        self.pipelines: Dict[int, InventoryDecisionPipeline] = {}  # product_id -> pipeline
    
    def get_or_create_pipeline(self, product: Product) -> InventoryDecisionPipeline:
        """Get or create pipeline for a product."""
        if product.id not in self.pipelines:
            pipeline = InventoryDecisionPipeline(
                unit_cost=product.unit_cost,
                selling_price=product.selling_price,
                holding_cost_rate=product.holding_cost_rate,
                markdown_rate=product.markdown_rate,
                churn_penalty=product.churn_penalty,
                n_simulations=5000,
                max_stockout_probability=0.20
            )
            self.pipelines[product.id] = pipeline
        return self.pipelines[product.id]
    
    def prepare_historical_data(
        self,
        sales_history: list[SalesHistory]
    ) -> pd.DataFrame:
        """Convert sales history to DataFrame for forecasting."""
        if not sales_history:
            raise ValueError("No sales history available")
        
        df = pd.DataFrame([
            {
                'date': sh.date,
                'demand': sh.demand
            }
            for sh in sales_history
        ])
        
        df = df.sort_values('date').reset_index(drop=True)
        return df
    
    def generate_recommendation(
        self,
        product: Product,
        current_inventory: Inventory,
        sales_history: list[SalesHistory],
        available_cash: Optional[float] = None
    ) -> Dict:
        """
        Generate reorder recommendation for a product.
        
        Returns:
            Dictionary with recommendation details
        """
        # Get or create pipeline
        pipeline = self.get_or_create_pipeline(product)
        
        # Prepare historical data
        historical_df = self.prepare_historical_data(sales_history)
        
        # Train forecaster if not already trained
        sku_id = f"product_{product.id}"
        if sku_id not in pipeline.forecasters:
            pipeline.train_forecaster(historical_df, sku_id=sku_id)
        
        # Run pipeline
        result = pipeline.run_pipeline(
            sku_id=sku_id,
            current_inventory=current_inventory.current_quantity,
            lead_time_days=product.lead_time_days,
            forecast_horizon_days=30,
            min_order_quantity=product.min_order_quantity,
            max_order_quantity=10000,  # Configurable
            order_multiple=product.order_multiple,
            available_cash=available_cash,
            holding_period_months=1.0,
            distribution_type='normal'
        )
        
        # Extract results
        opt_result = result['optimization_result']
        current_risk = result['current_risk']
        cost_breakdown = result['cost_breakdown']
        
        # Map risk categories
        def map_risk_category(prob: float) -> RiskCategory:
            if prob < 0.05:
                return RiskCategory.LOW
            elif prob < 0.20:
                return RiskCategory.MEDIUM
            else:
                return RiskCategory.HIGH
        
        recommendation = {
            'product_id': product.id,
            'recommended_quantity': opt_result['optimal_quantity'],
            'current_inventory': current_inventory.current_quantity,
            'stockout_probability_before': current_risk['stockout_probability'],
            'stockout_probability_after': opt_result['risk_metrics']['stockout_probability'],
            'risk_category_before': map_risk_category(current_risk['stockout_probability']),
            'risk_category_after': map_risk_category(opt_result['risk_metrics']['stockout_probability']),
            'expected_overstock_cost': cost_breakdown['expected_overstock_cost'],
            'expected_understock_cost': cost_breakdown['expected_understock_cost'],
            'total_expected_loss': cost_breakdown['total_expected_loss'],
            'cash_locked': opt_result['cash_locked'],
            'cash_freed': 0.0,  # Will be computed in comparison
            'explanation': result['explanation'],
            'forecast_data': result['forecast'].to_dict('records') if 'forecast' in result else []
        }
        
        # Add comparison if available
        if result.get('comparison_result'):
            comp = result['comparison_result']
            recommendation['cash_freed'] = comp.get('cash_saved', 0.0)
        
        return recommendation
    
    def generate_recommendations_for_brand(
        self,
        products: list[Product],
        inventories: Dict[int, Inventory],
        sales_histories: Dict[int, list[SalesHistory]],
        total_available_cash: Optional[float] = None
    ) -> list[Dict]:
        """
        Generate recommendations for multiple products with capital allocation.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        for product in products:
            if product.id not in inventories:
                continue
            
            inventory = inventories[product.id]
            sales_history = sales_histories.get(product.id, [])
            
            if not sales_history:
                continue
            
            try:
                rec = self.generate_recommendation(
                    product=product,
                    current_inventory=inventory,
                    sales_history=sales_history,
                    available_cash=None  # Will allocate later
                )
                recommendations.append(rec)
            except Exception as e:
                # Log error but continue with other products
                print(f"Error generating recommendation for product {product.id}: {e}")
                continue
        
        # If cash constraint, allocate capital
        if total_available_cash is not None and recommendations:
            # Simple allocation: prioritize by loss avoided per rupee
            # In production, use the CapitalAllocator
            recommendations = sorted(
                recommendations,
                key=lambda x: x['total_expected_loss'] / max(x['cash_locked'], 1),
                reverse=True
            )
            
            allocated_cash = 0.0
            for rec in recommendations:
                if allocated_cash + rec['cash_locked'] <= total_available_cash:
                    allocated_cash += rec['cash_locked']
                else:
                    # Adjust quantity to fit remaining cash
                    remaining_cash = total_available_cash - allocated_cash
                    if remaining_cash > 0:
                        rec['recommended_quantity'] = min(
                            rec['recommended_quantity'],
                            remaining_cash / rec.get('unit_cost', 1)
                        )
                        rec['cash_locked'] = remaining_cash
                    else:
                        rec['recommended_quantity'] = 0
                        rec['cash_locked'] = 0
        
        return recommendations

