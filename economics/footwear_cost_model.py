"""
Footwear-Specific Cost Model

Models size-specific overstock and understock costs.
Key insight: Overstock in size 6 is worse than overstock in size 9.
Stockout in size 8 loses more revenue than stockout in size 6.
"""

import numpy as np
from typing import Dict, Optional


class FootwearCostModel:
    """
    Footwear-specific cost model that accounts for:
    - Size-specific overstock penalties (orphan sizes)
    - Size-specific understock penalties (popular sizes)
    - Markdown costs (must discount entire style)
    """
    
    def __init__(
        self,
        base_unit_cost: float,
        base_selling_price: float,
        holding_cost_rate: float = 0.02,  # 2% per month
        markdown_rate: float = 0.5,  # 50% markdown for unsold sizes
        churn_penalty: float = 0.0
    ):
        """
        Initialize footwear cost model.
        
        Args:
            base_unit_cost: Base cost per unit
            base_selling_price: Base selling price
            holding_cost_rate: Monthly holding cost rate
            markdown_rate: Markdown rate for unsold inventory
            churn_penalty: Penalty per stockout event
        """
        self.base_unit_cost = base_unit_cost
        self.base_selling_price = base_selling_price
        self.holding_cost_rate = holding_cost_rate
        self.markdown_rate = markdown_rate
        self.churn_penalty = churn_penalty
        
        # Size-specific multipliers
        # Less popular sizes (6, 7, 11) have higher overstock penalty
        self.overstock_multipliers = {
            '6': 1.3,   # 30% higher cost
            '7': 1.2,   # 20% higher cost
            '8': 1.0,   # Baseline
            '9': 1.0,   # Baseline
            '10': 1.1,  # 10% higher cost
            '11': 1.3,  # 30% higher cost
        }
        
        # Popular sizes (8, 9) have higher understock penalty
        self.understock_multipliers = {
            '6': 0.8,   # 20% lower cost
            '7': 0.9,   # 10% lower cost
            '8': 1.5,   # 50% higher cost (critical size)
            '9': 1.5,   # 50% higher cost (critical size)
            '10': 1.2,  # 20% higher cost
            '11': 0.9,  # 10% lower cost
        }
    
    def _get_size_multiplier(self, size: str, cost_type: str) -> float:
        """Get size-specific multiplier."""
        if cost_type == 'overstock':
            return self.overstock_multipliers.get(size, 1.0)
        elif cost_type == 'understock':
            return self.understock_multipliers.get(size, 1.0)
        return 1.0
    
    def compute_size_overstock_cost(
        self,
        size: str,
        excess_units: float,
        unit_cost: Optional[float] = None,
        holding_period_months: float = 1.0
    ) -> float:
        """
        Compute overstock cost for a specific size.
        
        Footwear-specific: Overstock in less popular sizes is worse
        because you can't discount just one size - must discount entire style.
        
        Args:
            size: Size (e.g., "6", "7", "8")
            excess_units: Number of excess units
            unit_cost: Cost per unit (defaults to base_unit_cost)
            holding_period_months: Expected holding period
            
        Returns:
            Total overstock cost in ₹
        """
        if excess_units <= 0:
            return 0.0
        
        unit_cost = unit_cost or self.base_unit_cost
        
        # Base cash locked
        cash_locked = excess_units * unit_cost
        
        # Holding cost
        holding_cost = cash_locked * self.holding_cost_rate * holding_period_months
        
        # Markdown cost (must discount entire style if one size doesn't sell)
        # This is the key footwear-specific cost
        markdown_cost = excess_units * unit_cost * self.markdown_rate
        
        # Size-specific multiplier
        size_multiplier = self._get_size_multiplier(size, 'overstock')
        
        total_cost = (cash_locked + holding_cost + markdown_cost) * size_multiplier
        
        return total_cost
    
    def compute_size_understock_cost(
        self,
        size: str,
        unmet_demand: float,
        selling_price: Optional[float] = None,
        unit_cost: Optional[float] = None,
        stockout_occurred: bool = False
    ) -> float:
        """
        Compute understock cost for a specific size.
        
        Footwear-specific: Stockout in popular sizes (8, 9) loses more revenue
        because these are the highest-demand sizes.
        
        Args:
            size: Size (e.g., "6", "7", "8")
            unmet_demand: Number of units of unmet demand
            selling_price: Selling price (defaults to base_selling_price)
            unit_cost: Cost per unit (defaults to base_unit_cost)
            stockout_occurred: Whether a stockout event occurred
            
        Returns:
            Total understock cost in ₹
        """
        if unmet_demand <= 0:
            return 0.0
        
        selling_price = selling_price or self.base_selling_price
        unit_cost = unit_cost or self.base_unit_cost
        
        # Lost margin (opportunity cost)
        margin_per_unit = selling_price - unit_cost
        lost_margin = unmet_demand * margin_per_unit
        
        # Churn penalty (one-time per stockout event)
        churn_cost = self.churn_penalty if stockout_occurred else 0.0
        
        # Size-specific multiplier
        size_multiplier = self._get_size_multiplier(size, 'understock')
        
        total_cost = (lost_margin + churn_cost) * size_multiplier
        
        return total_cost
    
    def compute_style_level_costs(
        self,
        size_results: Dict[str, Dict]
    ) -> Dict[str, float]:
        """
        Aggregate size-level costs to style level.
        
        Args:
            size_results: Dictionary of size -> {overstock_cost, understock_cost, ...}
            
        Returns:
            Style-level aggregated costs
        """
        total_overstock_cost = sum(
            result.get('expected_overstock_cost', 0)
            for result in size_results.values()
        )
        
        total_understock_cost = sum(
            result.get('expected_understock_cost', 0)
            for result in size_results.values()
        )
        
        total_cash_locked = sum(
            result.get('cash_locked', 0)
            for result in size_results.values()
        )
        
        # Cash at high risk (sizes with HIGH risk level)
        cash_at_risk = sum(
            result.get('cash_locked', 0)
            for result in size_results.values()
            if result.get('risk_level') == 'HIGH'
        )
        
        return {
            'total_overstock_cost': total_overstock_cost,
            'total_understock_cost': total_understock_cost,
            'total_expected_loss': total_overstock_cost + total_understock_cost,
            'total_cash_locked': total_cash_locked,
            'cash_at_risk': cash_at_risk
        }









