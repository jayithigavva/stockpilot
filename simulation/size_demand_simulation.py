"""
Footwear-Specific Demand Simulation

Simulates size-level demand depletion considering size coupling.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional


class SizeDemandSimulator:
    """
    Simulates demand depletion at size-level for footwear styles.
    
    Key difference: Simulates joint size demand, not independent SKU demand.
    """
    
    def __init__(self, n_simulations: int = 5000):
        """
        Initialize simulator.
        
        Args:
            n_simulations: Number of Monte Carlo simulations
        """
        self.n_simulations = n_simulations
    
    def simulate_size_demand_depletion(
        self,
        forecast: Dict,  # From SizeShareForecaster
        current_inventory_by_size: Dict[str, float],
        reorder_curve: Dict[str, int],  # Size curve being evaluated
        lead_time_days: int
    ) -> Dict:
        """
        Simulate inventory depletion for each size.
        
        Args:
            forecast: Forecast with size_demands
            current_inventory_by_size: Current stock per size
            reorder_curve: Size curve being evaluated {"6": 50, "7": 100, ...}
            lead_time_days: Lead time until reorder arrives
            
        Returns:
            Dictionary with simulation results per size
        """
        sizes = list(reorder_curve.keys())
        horizon_days = len(forecast['size_demands'][sizes[0]]['p50'])
        
        # Simulate demand for each size
        size_results = {}
        
        for size in sizes:
            # Get forecasted demand (use P50 for simulation)
            size_demand = np.array(forecast['size_demands'][size]['p50'])
            
            # Current inventory
            current_inv = current_inventory_by_size.get(size, 0)
            
            # Reorder quantity
            reorder_qty = reorder_curve[size]
            
            # Simulate multiple demand paths
            ending_inventories = []
            stockout_flags = []
            unmet_demands = []
            
            for _ in range(self.n_simulations):
                # Sample demand (add noise to P50)
                # In production, would use full quantile distribution
                demand_sample = np.random.normal(
                    size_demand,
                    size_demand * 0.2  # 20% coefficient of variation
                ).clip(0)
                
                # Simulate day-by-day depletion
                inventory = current_inv
                
                for day in range(min(lead_time_days, horizon_days)):
                    daily_demand = demand_sample[day] if day < len(demand_sample) else 0
                    inventory -= daily_demand
                
                # Reorder arrives
                inventory += reorder_qty
                
                # Continue depletion after reorder
                for day in range(lead_time_days, horizon_days):
                    daily_demand = demand_sample[day] if day < len(demand_sample) else 0
                    inventory -= daily_demand
                
                ending_inventories.append(inventory)
                stockout_flags.append(inventory < 0)
                unmet_demands.append(max(0, -inventory))
            
            # Aggregate results
            size_results[size] = {
                'ending_inventory': np.array(ending_inventories),
                'stockout_probability': np.mean(stockout_flags),
                'expected_ending_inventory': np.mean(ending_inventories),
                'expected_unmet_demand': np.mean(unmet_demands),
                'p10_ending_inventory': np.percentile(ending_inventories, 10),
                'p90_ending_inventory': np.percentile(ending_inventories, 90)
            }
        
        return size_results
    
    def compute_style_level_risk(
        self,
        size_results: Dict[str, Dict]
    ) -> Dict:
        """
        Aggregate size-level risks to style level.
        
        Args:
            size_results: Results from simulate_size_demand_depletion
            
        Returns:
            Style-level risk metrics
        """
        # Overall stockout probability (any size stockouts)
        any_stockout_probs = []
        for size_result in size_results.values():
            any_stockout_probs.append(size_result['stockout_probability'])
        
        # Probability that at least one size stockouts
        style_stockout_prob = 1 - np.prod([1 - p for p in any_stockout_probs])
        
        # Average stockout probability across sizes
        avg_stockout_prob = np.mean(any_stockout_probs)
        
        # Count high-risk sizes (stockout prob > 20%)
        high_risk_sizes = sum(
            1 for result in size_results.values()
            if result['stockout_probability'] > 0.20
        )
        
        return {
            'style_stockout_probability': style_stockout_prob,
            'avg_size_stockout_probability': avg_stockout_prob,
            'high_risk_size_count': high_risk_sizes,
            'size_risks': {
                size: result['stockout_probability']
                for size, result in size_results.items()
            }
        }






