"""
Reorder Optimization Engine

Evaluates feasible order quantities and selects the one that minimizes expected economic loss.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from economics.cost_model import CostModel
from inventory.risk_estimator import RiskEstimator


class ReorderOptimizer:
    """
    Optimizes reorder quantity by minimizing expected economic loss
    while respecting constraints (cash, MOQ, order multiples, risk tolerance).
    """
    
    def __init__(
        self,
        cost_model: CostModel,
        risk_estimator: RiskEstimator,
        max_stockout_probability: float = 0.20  # 20% max acceptable risk
    ):
        """
        Initialize reorder optimizer.
        
        Args:
            cost_model: CostModel instance
            risk_estimator: RiskEstimator instance
            max_stockout_probability: Maximum acceptable stockout probability
        """
        self.cost_model = cost_model
        self.risk_estimator = risk_estimator
        self.max_stockout_probability = max_stockout_probability
    
    def find_feasible_order_quantities(
        self,
        min_order_quantity: float = 0,
        max_order_quantity: float = 10000,
        order_multiple: float = 1.0,
        available_cash: Optional[float] = None,
        step_size: float = 10.0
    ) -> np.ndarray:
        """
        Generate list of feasible order quantities.
        
        Args:
            min_order_quantity: Minimum order quantity (MOQ)
            max_order_quantity: Maximum order quantity to consider
            order_multiple: Order must be multiple of this (e.g., 10, 50)
            available_cash: Available cash constraint
            step_size: Step size for grid search
            
        Returns:
            Array of feasible order quantities
        """
        # Start from MOQ
        quantities = []
        q = min_order_quantity
        
        # Apply cash constraint
        if available_cash is not None:
            max_q_by_cash = available_cash / self.cost_model.unit_cost
            max_order_quantity = min(max_order_quantity, max_q_by_cash)
        
        while q <= max_order_quantity:
            # Round to nearest multiple
            q_rounded = round(q / order_multiple) * order_multiple
            if q_rounded >= min_order_quantity and q_rounded <= max_order_quantity:
                quantities.append(q_rounded)
            q += step_size
        
        # Remove duplicates and sort
        quantities = sorted(list(set(quantities)))
        
        return np.array(quantities)
    
    def optimize_reorder(
        self,
        forecast_df,
        current_inventory: float,
        lead_time_days: int,
        min_order_quantity: float = 0,
        max_order_quantity: float = 10000,
        order_multiple: float = 1.0,
        available_cash: Optional[float] = None,
        holding_period_months: float = 1.0,
        distribution_type: str = 'normal',
        step_size: float = 10.0
    ) -> Dict:
        """
        Find optimal reorder quantity that minimizes expected economic loss.
        
        Args:
            forecast_df: Forecast DataFrame
            current_inventory: Current inventory level
            lead_time_days: Lead time in days
            min_order_quantity: MOQ
            max_order_quantity: Maximum order quantity
            order_multiple: Order multiple constraint
            available_cash: Available cash constraint
            holding_period_months: Expected holding period
            distribution_type: 'normal' or 'quantile'
            step_size: Step size for grid search
            
        Returns:
            Dictionary with:
            - optimal_quantity: Recommended order quantity
            - optimal_loss: Expected loss at optimal quantity
            - risk_metrics: Risk metrics at optimal quantity
            - all_evaluations: All evaluated quantities with their losses
        """
        # Generate feasible quantities
        feasible_quantities = self.find_feasible_order_quantities(
            min_order_quantity=min_order_quantity,
            max_order_quantity=max_order_quantity,
            order_multiple=order_multiple,
            available_cash=available_cash,
            step_size=step_size
        )
        
        if len(feasible_quantities) == 0:
            return {
                'optimal_quantity': 0,
                'optimal_loss': np.inf,
                'risk_metrics': None,
                'all_evaluations': [],
                'message': 'No feasible order quantities found'
            }
        
        # Evaluate each quantity
        evaluations = []
        
        for qty in feasible_quantities:
            # Compute expected loss
            loss_result = self.cost_model.compute_expected_economic_loss(
                forecast_df=forecast_df,
                current_inventory=current_inventory,
                reorder_quantity=qty,
                lead_time_days=lead_time_days,
                holding_period_months=holding_period_months,
                distribution_type=distribution_type
            )
            
            # Check risk constraint
            risk_result = self.risk_estimator.estimate_risk_with_reorder(
                forecast_df=forecast_df,
                current_inventory=current_inventory,
                reorder_quantity=qty,
                lead_time_days=lead_time_days,
                distribution_type=distribution_type
            )
            
            stockout_prob = risk_result['stockout_probability']
            
            # Penalize if risk exceeds tolerance
            penalty = 0.0
            if stockout_prob > self.max_stockout_probability:
                # Add large penalty for violating risk constraint
                penalty = loss_result['total_expected_loss'] * 10.0
            
            total_loss = loss_result['total_expected_loss'] + penalty
            
            evaluations.append({
                'quantity': qty,
                'total_loss': total_loss,
                'overstock_cost': loss_result['expected_overstock_cost'],
                'understock_cost': loss_result['expected_understock_cost'],
                'stockout_probability': stockout_prob,
                'risk_category': risk_result['risk_category'],
                'expected_ending_inventory': loss_result['expected_ending_inventory'],
                'cash_locked': qty * self.cost_model.unit_cost
            })
        
        # Find optimal (minimum loss)
        evaluations = sorted(evaluations, key=lambda x: x['total_loss'])
        optimal = evaluations[0]
        
        return {
            'optimal_quantity': optimal['quantity'],
            'optimal_loss': optimal['total_loss'],
            'risk_metrics': {
                'stockout_probability': optimal['stockout_probability'],
                'risk_category': optimal['risk_category'],
                'expected_ending_inventory': optimal['expected_ending_inventory']
            },
            'all_evaluations': evaluations,
            'cash_locked': optimal['cash_locked']
        }
    
    def compare_with_naive(
        self,
        forecast_df,
        current_inventory: float,
        lead_time_days: int,
        naive_quantity: float,
        optimal_result: Dict,
        holding_period_months: float = 1.0,
        distribution_type: str = 'normal'
    ) -> Dict:
        """
        Compare optimal decision with naive (gut-based) ordering.
        
        Args:
            forecast_df: Forecast DataFrame
            current_inventory: Current inventory level
            lead_time_days: Lead time in days
            naive_quantity: Naive order quantity to compare
            optimal_result: Result from optimize_reorder()
            holding_period_months: Expected holding period
            distribution_type: 'normal' or 'quantile'
            
        Returns:
            Dictionary with comparison metrics
        """
        # Evaluate naive quantity
        naive_loss_result = self.cost_model.compute_expected_economic_loss(
            forecast_df=forecast_df,
            current_inventory=current_inventory,
            reorder_quantity=naive_quantity,
            lead_time_days=lead_time_days,
            holding_period_months=holding_period_months,
            distribution_type=distribution_type
        )
        
        naive_risk = self.risk_estimator.estimate_risk_with_reorder(
            forecast_df=forecast_df,
            current_inventory=current_inventory,
            reorder_quantity=naive_quantity,
            lead_time_days=lead_time_days,
            distribution_type=distribution_type
        )
        
        optimal_loss = optimal_result['optimal_loss']
        naive_loss = naive_loss_result['total_expected_loss']
        loss_reduction = naive_loss - optimal_loss
        loss_reduction_pct = (loss_reduction / naive_loss * 100) if naive_loss > 0 else 0
        
        # Cash impact
        cash_saved = (naive_quantity - optimal_result['optimal_quantity']) * self.cost_model.unit_cost
        
        return {
            'naive_quantity': naive_quantity,
            'naive_loss': naive_loss,
            'optimal_quantity': optimal_result['optimal_quantity'],
            'optimal_loss': optimal_loss,
            'loss_reduction': loss_reduction,
            'loss_reduction_pct': loss_reduction_pct,
            'cash_saved': cash_saved,
            'naive_stockout_prob': naive_risk['stockout_probability'],
            'optimal_stockout_prob': optimal_result['risk_metrics']['stockout_probability']
        }

