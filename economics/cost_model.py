"""
Economic Cost Model

Explicitly models overstocking vs understocking costs to quantify economic trade-offs.
"""

import numpy as np
from typing import Dict, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulation.demand_simulation import DemandSimulator


class CostModel:
    """
    Models economic costs of inventory decisions:
    - Overstocking costs (cash locked, holding, markdown)
    - Understocking costs (lost sales, lost margin, churn)
    """
    
    def __init__(
        self,
        unit_cost: float,
        selling_price: float,
        holding_cost_rate: float = 0.02,  # 2% per month
        markdown_rate: float = 0.0,  # % of units that expire/go obsolete
        churn_penalty: float = 0.0,  # Penalty per stockout event
        simulator: Optional[DemandSimulator] = None
    ):
        """
        Initialize cost model.
        
        Args:
            unit_cost: Cost per unit purchased
            selling_price: Selling price per unit
            holding_cost_rate: Monthly holding cost as fraction of unit cost
            markdown_rate: Fraction of excess inventory that becomes obsolete
            churn_penalty: Penalty per stockout event (customer churn impact)
            simulator: DemandSimulator instance for demand simulation
        """
        self.unit_cost = unit_cost
        self.selling_price = selling_price
        self.holding_cost_rate = holding_cost_rate
        self.markdown_rate = markdown_rate
        self.churn_penalty = churn_penalty
        self.simulator = simulator
        
        # Calculate margin
        self.margin_per_unit = selling_price - unit_cost
        self.margin_rate = self.margin_per_unit / selling_price if selling_price > 0 else 0
    
    def compute_overstock_cost(
        self,
        excess_units: float,
        holding_period_months: float = 1.0
    ) -> float:
        """
        Compute cost of overstocking.
        
        Args:
            excess_units: Number of excess units (above demand)
            holding_period_months: Expected holding period in months
            
        Returns:
            Total overstock cost
        """
        if excess_units <= 0:
            return 0.0
        
        # Cash locked in excess inventory
        cash_locked = excess_units * self.unit_cost
        
        # Holding cost
        holding_cost = cash_locked * self.holding_cost_rate * holding_period_months
        
        # Markdown/obsolescence cost
        obsolete_units = excess_units * self.markdown_rate
        markdown_cost = obsolete_units * self.unit_cost  # Full cost write-off
        
        total_overstock_cost = cash_locked + holding_cost + markdown_cost
        
        return total_overstock_cost
    
    def compute_understock_cost(
        self,
        unmet_demand: float,
        stockout_occurred: bool = False
    ) -> float:
        """
        Compute cost of understocking.
        
        Args:
            unmet_demand: Number of units of unmet demand
            stockout_occurred: Whether a stockout event occurred
            
        Returns:
            Total understock cost
        """
        if unmet_demand <= 0:
            return 0.0
        
        # Lost sales revenue
        lost_revenue = unmet_demand * self.selling_price
        
        # Lost margin (opportunity cost)
        lost_margin = unmet_demand * self.margin_per_unit
        
        # Churn penalty (one-time per stockout event)
        churn_cost = self.churn_penalty if stockout_occurred else 0.0
        
        # Total understock cost
        # Note: Lost revenue includes lost margin, so we use lost margin + churn
        # Alternatively, we could use lost revenue, but margin is the true economic loss
        total_understock_cost = lost_margin + churn_cost
        
        return total_understock_cost
    
    def compute_expected_economic_loss(
        self,
        forecast_df,
        current_inventory: float,
        reorder_quantity: float,
        lead_time_days: int,
        holding_period_months: float = 1.0,
        distribution_type: str = 'normal'
    ) -> Dict[str, float]:
        """
        Compute expected economic loss for a given reorder quantity.
        
        Args:
            forecast_df: Forecast DataFrame
            current_inventory: Current inventory level
            reorder_quantity: Quantity to reorder
            lead_time_days: Lead time in days
            holding_period_months: Expected holding period for excess inventory
            distribution_type: 'normal' or 'quantile'
            
        Returns:
            Dictionary with:
            - expected_overstock_cost
            - expected_understock_cost
            - total_expected_loss
            - expected_ending_inventory
            - expected_unmet_demand
        """
        if self.simulator is None:
            raise ValueError("Simulator must be provided to compute expected costs")
        
        # Simulate inventory depletion
        sim_results = self.simulator.simulate_inventory_depletion(
            forecast_df=forecast_df,
            current_inventory=current_inventory,
            lead_time_days=lead_time_days,
            distribution_type=distribution_type
        )
        
        ending_inventory = sim_results['ending_inventory']
        ending_inventory_after_reorder = ending_inventory + reorder_quantity
        
        # Compute costs for each simulation
        overstock_costs = []
        understock_costs = []
        unmet_demands = []
        stockout_flags = []
        
        for ending_inv in ending_inventory_after_reorder:
            if ending_inv > 0:
                # Overstock scenario
                excess_units = ending_inv
                overstock_cost = self.compute_overstock_cost(excess_units, holding_period_months)
                overstock_costs.append(overstock_cost)
                understock_costs.append(0.0)
                unmet_demands.append(0.0)
                stockout_flags.append(False)
            else:
                # Understock scenario
                unmet_demand = abs(ending_inv)
                unmet_demands.append(unmet_demand)
                stockout_occurred = ending_inv < 0
                understock_cost = self.compute_understock_cost(unmet_demand, stockout_occurred)
                understock_costs.append(understock_cost)
                overstock_costs.append(0.0)
                stockout_flags.append(stockout_occurred)
        
        # Expected values
        expected_overstock_cost = np.mean(overstock_costs)
        expected_understock_cost = np.mean(understock_costs)
        total_expected_loss = expected_overstock_cost + expected_understock_cost
        expected_ending_inventory = np.mean(ending_inventory_after_reorder)
        expected_unmet_demand = np.mean(unmet_demands)
        
        return {
            'expected_overstock_cost': expected_overstock_cost,
            'expected_understock_cost': expected_understock_cost,
            'total_expected_loss': total_expected_loss,
            'expected_ending_inventory': expected_ending_inventory,
            'expected_unmet_demand': expected_unmet_demand,
            'stockout_probability': np.mean(stockout_flags)
        }
    
    def compute_cash_impact(
        self,
        reorder_quantity: float
    ) -> Dict[str, float]:
        """
        Compute cash impact of reorder decision.
        
        Args:
            reorder_quantity: Quantity to reorder
            
        Returns:
            Dictionary with cash locked, cash freed (if reducing order)
        """
        cash_locked = reorder_quantity * self.unit_cost
        
        return {
            'cash_locked': cash_locked,
            'cash_freed': 0.0  # Will be computed in comparison scenarios
        }

