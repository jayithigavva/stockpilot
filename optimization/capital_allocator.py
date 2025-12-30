"""
Capital-Aware Allocation Module

When total cash is insufficient, optimally allocates capital across multiple SKUs
based on economic loss avoided per rupee spent.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from optimization.reorder_optimizer import ReorderOptimizer


class CapitalAllocator:
    """
    Allocates limited capital across multiple SKUs to maximize economic value.
    
    Ranks SKUs by: Economic loss avoided per ₹ spent
    """
    
    def __init__(self, optimizers: Dict[str, ReorderOptimizer]):
        """
        Initialize capital allocator.
        
        Args:
            optimizers: Dictionary mapping SKU IDs to ReorderOptimizer instances
        """
        self.optimizers = optimizers
    
    def compute_loss_avoided_per_rupee(
        self,
        sku_id: str,
        forecast_df,
        current_inventory: float,
        lead_time_days: int,
        min_order_quantity: float,
        max_order_quantity: float,
        order_multiple: float = 1.0,
        holding_period_months: float = 1.0,
        distribution_type: str = 'normal',
        baseline_quantity: float = 0.0
    ) -> Dict:
        """
        Compute economic loss avoided per rupee spent for a SKU.
        
        Args:
            sku_id: SKU identifier
            forecast_df: Forecast DataFrame
            current_inventory: Current inventory level
            lead_time_days: Lead time in days
            min_order_quantity: MOQ
            max_order_quantity: Maximum order quantity
            order_multiple: Order multiple
            holding_period_months: Expected holding period
            distribution_type: 'normal' or 'quantile'
            baseline_quantity: Baseline order quantity (e.g., 0 or current practice)
            
        Returns:
            Dictionary with loss avoided per rupee metrics
        """
        optimizer = self.optimizers[sku_id]
        cost_model = optimizer.cost_model
        
        # Find optimal quantity without cash constraint
        optimal_result = optimizer.optimize_reorder(
            forecast_df=forecast_df,
            current_inventory=current_inventory,
            lead_time_days=lead_time_days,
            min_order_quantity=min_order_quantity,
            max_order_quantity=max_order_quantity,
            order_multiple=order_multiple,
            available_cash=None,  # No constraint
            holding_period_months=holding_period_months,
            distribution_type=distribution_type
        )
        
        # Compute baseline loss
        baseline_loss_result = cost_model.compute_expected_economic_loss(
            forecast_df=forecast_df,
            current_inventory=current_inventory,
            reorder_quantity=baseline_quantity,
            lead_time_days=lead_time_days,
            holding_period_months=holding_period_months,
            distribution_type=distribution_type
        )
        
        baseline_loss = baseline_loss_result['total_expected_loss']
        optimal_loss = optimal_result['optimal_loss']
        loss_avoided = baseline_loss - optimal_loss
        
        # Cash required
        optimal_cash = optimal_result['optimal_quantity'] * cost_model.unit_cost
        baseline_cash = baseline_quantity * cost_model.unit_cost
        incremental_cash = optimal_cash - baseline_cash
        
        # Loss avoided per rupee
        if incremental_cash > 0:
            loss_avoided_per_rupee = loss_avoided / incremental_cash
        else:
            loss_avoided_per_rupee = 0.0
        
        return {
            'sku_id': sku_id,
            'baseline_quantity': baseline_quantity,
            'optimal_quantity': optimal_result['optimal_quantity'],
            'baseline_loss': baseline_loss,
            'optimal_loss': optimal_loss,
            'loss_avoided': loss_avoided,
            'baseline_cash': baseline_cash,
            'optimal_cash': optimal_cash,
            'incremental_cash': incremental_cash,
            'loss_avoided_per_rupee': loss_avoided_per_rupee,
            'stockout_prob': optimal_result['risk_metrics']['stockout_probability']
        }
    
    def rank_skus_by_efficiency(
        self,
        sku_data: List[Dict],
        baseline_quantities: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Rank SKUs by economic loss avoided per rupee spent.
        
        Args:
            sku_data: List of dictionaries, each containing:
                - sku_id
                - forecast_df
                - current_inventory
                - lead_time_days
                - min_order_quantity
                - max_order_quantity
                - order_multiple (optional)
                - holding_period_months (optional)
                - distribution_type (optional)
            baseline_quantities: Dictionary mapping SKU IDs to baseline quantities
            
        Returns:
            DataFrame with SKUs ranked by efficiency
        """
        if baseline_quantities is None:
            baseline_quantities = {}
        
        rankings = []
        
        for sku_info in sku_data:
            sku_id = sku_info['sku_id']
            baseline_qty = baseline_quantities.get(sku_id, 0.0)
            
            metrics = self.compute_loss_avoided_per_rupee(
                sku_id=sku_id,
                forecast_df=sku_info['forecast_df'],
                current_inventory=sku_info['current_inventory'],
                lead_time_days=sku_info['lead_time_days'],
                min_order_quantity=sku_info['min_order_quantity'],
                max_order_quantity=sku_info['max_order_quantity'],
                order_multiple=sku_info.get('order_multiple', 1.0),
                holding_period_months=sku_info.get('holding_period_months', 1.0),
                distribution_type=sku_info.get('distribution_type', 'normal'),
                baseline_quantity=baseline_qty
            )
            
            rankings.append(metrics)
        
        # Create DataFrame and sort by efficiency
        df = pd.DataFrame(rankings)
        df = df.sort_values('loss_avoided_per_rupee', ascending=False).reset_index(drop=True)
        
        return df
    
    def allocate_capital(
        self,
        sku_data: List[Dict],
        total_available_cash: float,
        baseline_quantities: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Allocate limited capital across SKUs optimally.
        
        Uses greedy allocation: allocate to highest efficiency SKUs first.
        
        Args:
            sku_data: List of SKU data dictionaries
            total_available_cash: Total cash available
            baseline_quantities: Dictionary mapping SKU IDs to baseline quantities
            
        Returns:
            Dictionary with:
            - allocations: Dictionary mapping SKU IDs to allocated quantities
            - total_cash_used: Total cash allocated
            - remaining_cash: Remaining cash
            - allocation_order: Order in which SKUs were allocated
        """
        # Rank SKUs by efficiency
        rankings_df = self.rank_skus_by_efficiency(sku_data, baseline_quantities)
        
        allocations = {}
        total_cash_used = 0.0
        allocation_order = []
        
        # Greedy allocation
        for _, row in rankings_df.iterrows():
            sku_id = row['sku_id']
            optimal_cash = row['optimal_cash']
            baseline_cash = row['baseline_cash']
            incremental_cash = row['incremental_cash']
            
            # Check if we can afford this SKU's optimal order
            if total_cash_used + incremental_cash <= total_available_cash:
                # Allocate optimal quantity
                allocations[sku_id] = {
                    'quantity': row['optimal_quantity'],
                    'cash': optimal_cash,
                    'loss_avoided': row['loss_avoided']
                }
                total_cash_used += incremental_cash
                allocation_order.append(sku_id)
            elif total_cash_used + baseline_cash <= total_available_cash:
                # Can afford baseline but not optimal
                # Allocate partial (baseline)
                allocations[sku_id] = {
                    'quantity': row['baseline_quantity'],
                    'cash': baseline_cash,
                    'loss_avoided': 0.0
                }
                total_cash_used += baseline_cash
                allocation_order.append(sku_id)
            else:
                # Cannot afford even baseline
                allocations[sku_id] = {
                    'quantity': 0.0,
                    'cash': 0.0,
                    'loss_avoided': 0.0
                }
        
        return {
            'allocations': allocations,
            'total_cash_used': total_cash_used,
            'remaining_cash': total_available_cash - total_cash_used,
            'allocation_order': allocation_order,
            'rankings': rankings_df
        }

