"""
Footwear-Specific Size Curve Optimizer

Optimizes style-level reorder decisions considering size coupling via factory curves.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from economics.footwear_cost_model import FootwearCostModel
from simulation.size_demand_simulation import SizeDemandSimulator


class SizeCurveOptimizer:
    """
    Optimizes footwear reorder decisions at style-level.
    
    Key differences from generic optimizer:
    - Decision unit = style-level reorder plan (not SKU-level)
    - Evaluates factory-valid size curves
    - Computes risk at size-level, aggregates to style-level
    - Ranks by expected ₹ saved per ₹ committed
    """
    
    def __init__(
        self,
        cost_model: FootwearCostModel,
        simulator: SizeDemandSimulator,
        max_stockout_probability: float = 0.20
    ):
        """
        Initialize size curve optimizer.
        
        Args:
            cost_model: FootwearCostModel instance
            simulator: SizeDemandSimulator instance
            max_stockout_probability: Maximum acceptable stockout probability
        """
        self.cost_model = cost_model
        self.simulator = simulator
        self.max_stockout_probability = max_stockout_probability
    
    def generate_valid_size_curves(
        self,
        size_distribution: Dict[str, float],  # Historical or template distribution
        min_order_total: int,
        order_multiple: int,
        max_order_total: Optional[int] = None
    ) -> List[Dict[str, int]]:
        """
        Generate factory-valid size curves.
        
        Args:
            size_distribution: Size distribution (e.g., {"6": 0.05, "7": 0.10, ...})
            min_order_total: Minimum total units
            order_multiple: Must order in multiples of this
            max_order_total: Maximum total units (cash constraint)
            
        Returns:
            List of valid size curves, each as {"6": 50, "7": 100, ...}
        """
        sizes = list(size_distribution.keys())
        valid_curves = []
        
        # Generate curves for different total quantities
        total_range = range(
            min_order_total,
            (max_order_total or min_order_total * 10) + 1,
            order_multiple
        )
        
        for total_units in total_range:
            if max_order_total and total_units > max_order_total:
                break
            
            # Allocate total units according to distribution
            curve = {}
            allocated = 0
            
            for size in sizes:
                size_qty = int(round(total_units * size_distribution[size]))
                # Round to nearest multiple if needed
                if order_multiple > 1:
                    size_qty = (size_qty // order_multiple) * order_multiple
                curve[size] = max(0, size_qty)
                allocated += curve[size]
            
            # Adjust to match total (handle rounding)
            diff = total_units - allocated
            if diff != 0:
                # Add/subtract from largest size
                largest_size = max(sizes, key=lambda s: size_distribution[s])
                curve[largest_size] = max(0, curve[largest_size] + diff)
            
            valid_curves.append(curve)
        
        return valid_curves
    
    def evaluate_size_curve(
        self,
        curve: Dict[str, int],  # {"6": 50, "7": 100, ...}
        forecast: Dict,  # From SizeShareForecaster
        current_inventory_by_size: Dict[str, float],
        unit_cost: float,
        selling_price: float,
        lead_time_days: int
    ) -> Dict:
        """
        Evaluate a size curve and compute size-level risks.
        
        Returns:
            Dictionary with:
            - size_breakdown: The curve
            - size_results: Risk and cost per size
            - total_cash: Total capital required
            - cash_at_risk_by_size: Cash locked in high-risk sizes
            - expected_loss: Total expected economic loss
            - expected_upside: Revenue protected
        """
        sizes = list(curve.keys())
        size_results = {}
        total_cash = 0
        total_expected_loss = 0
        total_expected_upside = 0
        cash_at_risk = {}
        
        # Simulate demand for each size
        for size in sizes:
            order_qty = curve[size]
            cash_locked = order_qty * unit_cost
            total_cash += cash_locked
            
            # Get forecasted demand for this size
            size_demand_p50 = np.mean(forecast['size_demands'][size]['p50'])
            size_demand_p90 = np.mean(forecast['size_demands'][size]['p90'])
            
            # Current inventory for this size
            current_inv = current_inventory_by_size.get(size, 0)
            
            # Simulate outcomes
            ending_inventory = current_inv + order_qty - size_demand_p50
            
            # Compute costs
            if ending_inventory > 0:
                # Overstock scenario
                overstock_cost = self.cost_model.compute_size_overstock_cost(
                    size=size,
                    excess_units=ending_inventory,
                    unit_cost=unit_cost
                )
                understock_cost = 0
                risk_level = 'LOW' if overstock_cost < cash_locked * 0.1 else 'MEDIUM'
            else:
                # Understock scenario
                unmet_demand = abs(ending_inventory)
                understock_cost = self.cost_model.compute_size_understock_cost(
                    size=size,
                    unmet_demand=unmet_demand,
                    selling_price=selling_price,
                    unit_cost=unit_cost
                )
                overstock_cost = 0
                risk_level = 'HIGH'
            
            size_loss = overstock_cost + understock_cost
            total_expected_loss += size_loss
            
            # Compute upside (revenue protected)
            if ending_inventory >= 0:
                # We have enough stock
                revenue_protected = min(size_demand_p50, current_inv + order_qty) * selling_price
                total_expected_upside += revenue_protected
            
            size_results[size] = {
                'order_quantity': order_qty,
                'cash_locked': cash_locked,
                'expected_overstock_cost': overstock_cost,
                'expected_understock_cost': understock_cost,
                'expected_loss': size_loss,
                'risk_level': risk_level,
                'ending_inventory': ending_inventory
            }
            
            # Track cash at risk (high-risk sizes)
            if risk_level == 'HIGH':
                cash_at_risk[size] = cash_locked
        
        return {
            'size_breakdown': curve,
            'size_results': size_results,
            'total_cash': total_cash,
            'cash_at_risk_by_size': cash_at_risk,
            'total_cash_at_risk': sum(cash_at_risk.values()),
            'expected_loss': total_expected_loss,
            'expected_upside': total_expected_upside,
            'expected_return_per_rupee': (
                (total_expected_upside - total_expected_loss) / max(total_cash, 1)
            )
        }
    
    def optimize_style_reorder(
        self,
        forecast: Dict,
        current_inventory_by_size: Dict[str, float],
        size_curve_templates: List[Dict],  # Valid factory curves
        unit_cost: float,
        selling_price: float,
        lead_time_days: int,
        available_cash: Optional[float] = None
    ) -> Dict:
        """
        Find optimal size curve for a style.
        
        Ranks by: Expected ₹ saved per ₹ committed
        
        Args:
            forecast: From SizeShareForecaster
            current_inventory_by_size: Current stock per size
            size_curve_templates: List of valid factory curves
            unit_cost: Cost per unit
            selling_price: Selling price
            lead_time_days: Lead time
            available_cash: Cash constraint
            
        Returns:
            Optimal curve evaluation result
        """
        candidates = []
        
        for curve_template in size_curve_templates:
            # Evaluate this curve
            result = self.evaluate_size_curve(
                curve=curve_template['size_distribution'],
                forecast=forecast,
                current_inventory_by_size=current_inventory_by_size,
                unit_cost=unit_cost,
                selling_price=selling_price,
                lead_time_days=lead_time_days
            )
            
            # Check cash constraint
            if available_cash and result['total_cash'] > available_cash:
                continue
            
            # Check risk constraint
            # Compute overall stockout probability (simplified)
            # In production, would use full simulation
            
            candidates.append(result)
        
        if not candidates:
            return None
        
        # Rank by expected return per rupee (highest first)
        candidates.sort(
            key=lambda x: x['expected_return_per_rupee'],
            reverse=True
        )
        
        return candidates[0]





