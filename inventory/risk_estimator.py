"""
Inventory Risk Estimator

Pure logic module (no ML) for computing stockout risk and inventory health metrics.
"""

import numpy as np
from typing import Dict, Literal
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulation.demand_simulation import DemandSimulator


class RiskEstimator:
    """
    Computes inventory risk metrics:
    - Probability of stockout before replenishment
    - Expected days of cover
    - Risk category (LOW, MEDIUM, HIGH)
    """
    
    def __init__(self, simulator: DemandSimulator):
        """
        Initialize risk estimator.
        
        Args:
            simulator: DemandSimulator instance for running simulations
        """
        self.simulator = simulator
    
    def estimate_stockout_risk(
        self,
        forecast_df,
        current_inventory: float,
        lead_time_days: int,
        distribution_type: str = 'normal'
    ) -> Dict:
        """
        Estimate probability of stockout during lead time.
        
        Args:
            forecast_df: Forecast DataFrame from demand_forecast
            current_inventory: Current inventory level
            lead_time_days: Lead time in days
            distribution_type: 'normal' or 'quantile'
            
        Returns:
            Dictionary with risk metrics
        """
        # Run simulation
        sim_results = self.simulator.simulate_inventory_depletion(
            forecast_df=forecast_df,
            current_inventory=current_inventory,
            lead_time_days=lead_time_days,
            distribution_type=distribution_type
        )
        
        stockout_prob = sim_results['stockout_probability']
        
        # Get demand statistics
        demand_stats = self.simulator.get_demand_statistics(sim_results)
        
        # Calculate expected days of cover
        # Average daily demand from forecast
        avg_daily_demand = forecast_df['mean'].head(lead_time_days).mean()
        expected_days_of_cover = current_inventory / avg_daily_demand if avg_daily_demand > 0 else np.inf
        
        # Categorize risk
        risk_category = self._categorize_risk(stockout_prob)
        
        return {
            'stockout_probability': stockout_prob,
            'risk_category': risk_category,
            'expected_days_of_cover': expected_days_of_cover,
            'demand_p50': demand_stats['p50'],
            'demand_p90': demand_stats['p90'],
            'demand_p95': demand_stats['p95'],
            'current_inventory': current_inventory,
            'lead_time_days': lead_time_days
        }
    
    def _categorize_risk(
        self,
        stockout_probability: float
    ) -> Literal['LOW', 'MEDIUM', 'HIGH']:
        """
        Categorize stockout risk based on probability.
        
        Args:
            stockout_probability: Probability of stockout (0-1)
            
        Returns:
            Risk category: LOW (<5%), MEDIUM (5-20%), HIGH (>20%)
        """
        if stockout_probability < 0.05:
            return 'LOW'
        elif stockout_probability < 0.20:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def estimate_risk_with_reorder(
        self,
        forecast_df,
        current_inventory: float,
        reorder_quantity: float,
        lead_time_days: int,
        distribution_type: str = 'normal'
    ) -> Dict:
        """
        Estimate risk after placing a reorder.
        
        Args:
            forecast_df: Forecast DataFrame
            current_inventory: Current inventory level
            reorder_quantity: Quantity to reorder
            lead_time_days: Lead time in days
            distribution_type: 'normal' or 'quantile'
            
        Returns:
            Dictionary with risk metrics after reorder
        """
        # Inventory after reorder arrives
        future_inventory = current_inventory + reorder_quantity
        
        # Estimate risk assuming reorder arrives at end of lead time
        # We need to account for demand during lead time
        sim_results = self.simulator.simulate_inventory_depletion(
            forecast_df=forecast_df,
            current_inventory=current_inventory,
            lead_time_days=lead_time_days,
            distribution_type=distribution_type
        )
        
        # Ending inventory distribution
        ending_inventory = sim_results['ending_inventory']
        ending_inventory_after_reorder = ending_inventory + reorder_quantity
        
        # Stockout probability after reorder
        # Stockout occurs if ending inventory is still negative
        stockout_prob_after = np.sum(ending_inventory_after_reorder < 0) / len(ending_inventory_after_reorder)
        
        # Expected days of cover after reorder
        avg_daily_demand = forecast_df['mean'].head(lead_time_days).mean()
        expected_ending_inventory = np.mean(ending_inventory_after_reorder)
        expected_days_of_cover_after = expected_ending_inventory / avg_daily_demand if avg_daily_demand > 0 else np.inf
        
        risk_category = self._categorize_risk(stockout_prob_after)
        
        return {
            'stockout_probability': stockout_prob_after,
            'risk_category': risk_category,
            'expected_ending_inventory': expected_ending_inventory,
            'expected_days_of_cover': expected_days_of_cover_after,
            'reorder_quantity': reorder_quantity
        }

