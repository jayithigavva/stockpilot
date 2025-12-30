"""
Demand Simulation Engine

Monte Carlo simulation for inventory depletion during lead time.
Samples demand paths from forecast distribution and simulates stock depletion.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from scipy import stats


class DemandSimulator:
    """
    Monte Carlo simulator for demand during lead time.
    
    Simulates multiple demand paths to estimate:
    - Distribution of cumulative demand during lead time
    - Distribution of stockout day
    - Probability of stockout
    """
    
    def __init__(self, n_simulations: int = 5000, random_seed: int = 42):
        """
        Initialize the demand simulator.
        
        Args:
            n_simulations: Number of Monte Carlo simulations to run
            random_seed: Random seed for reproducibility
        """
        self.n_simulations = n_simulations
        self.random_seed = random_seed
        np.random.seed(random_seed)
    
    def simulate_demand_path(
        self,
        forecast_df: pd.DataFrame,
        lead_time_days: int,
        distribution_type: str = 'normal'
    ) -> np.ndarray:
        """
        Simulate a single demand path for lead time period.
        
        Args:
            forecast_df: DataFrame with forecast (mean, std, p10, p50, p90) for each day
            lead_time_days: Number of days in lead time
            distribution_type: 'normal' or 'quantile' sampling method
            
        Returns:
            Array of daily demand values for lead time period
        """
        if lead_time_days > len(forecast_df):
            raise ValueError(f"Lead time {lead_time_days} exceeds forecast length {len(forecast_df)}")
        
        daily_demands = []
        
        for day in range(lead_time_days):
            row = forecast_df.iloc[day]
            
            if distribution_type == 'normal':
                # Sample from normal distribution
                mean = row['mean']
                std = row['std']
                # Truncate at 0 to ensure non-negative demand
                demand = max(0, np.random.normal(mean, std))
            else:
                # Sample from quantile-based distribution
                # Use triangular distribution between p10, p50, p90
                p10 = row['p10']
                p50 = row['p50']
                p90 = row['p90']
                
                # Sample uniformly and map to quantiles
                u = np.random.uniform(0, 1)
                if u < 0.1:
                    # Below p10: linear interpolation from 0 to p10
                    demand = p10 * (u / 0.1)
                elif u < 0.5:
                    # Between p10 and p50
                    demand = p10 + (p50 - p10) * ((u - 0.1) / 0.4)
                elif u < 0.9:
                    # Between p50 and p90
                    demand = p50 + (p90 - p50) * ((u - 0.5) / 0.4)
                else:
                    # Above p90: extrapolate with tail
                    demand = p90 + (p90 - p50) * ((u - 0.9) / 0.1)
                
                demand = max(0, demand)
            
            daily_demands.append(demand)
        
        return np.array(daily_demands)
    
    def simulate_lead_time_demand(
        self,
        forecast_df: pd.DataFrame,
        lead_time_days: int,
        distribution_type: str = 'normal'
    ) -> Dict[str, np.ndarray]:
        """
        Run Monte Carlo simulation for cumulative demand during lead time.
        
        Args:
            forecast_df: Forecast DataFrame
            lead_time_days: Lead time in days
            distribution_type: 'normal' or 'quantile'
            
        Returns:
            Dictionary with:
            - cumulative_demand: Array of cumulative demand for each simulation
            - daily_demands: Array of shape (n_simulations, lead_time_days)
            - stockout_days: Array of day when stockout occurs (NaN if no stockout)
        """
        cumulative_demands = []
        all_daily_demands = []
        stockout_days = []
        
        for sim in range(self.n_simulations):
            daily_demand = self.simulate_demand_path(forecast_df, lead_time_days, distribution_type)
            cumulative_demand = np.sum(daily_demand)
            
            cumulative_demands.append(cumulative_demand)
            all_daily_demands.append(daily_demand)
            stockout_days.append(np.nan)  # Will be updated in simulate_inventory_depletion
        
        return {
            'cumulative_demand': np.array(cumulative_demands),
            'daily_demands': np.array(all_daily_demands),
            'stockout_days': np.array(stockout_days)
        }
    
    def simulate_inventory_depletion(
        self,
        forecast_df: pd.DataFrame,
        current_inventory: float,
        lead_time_days: int,
        distribution_type: str = 'normal'
    ) -> Dict[str, np.ndarray]:
        """
        Simulate inventory depletion day-by-day during lead time.
        
        Args:
            forecast_df: Forecast DataFrame
            current_inventory: Current inventory level
            lead_time_days: Lead time in days
            distribution_type: 'normal' or 'quantile'
            
        Returns:
            Dictionary with:
            - cumulative_demand: Total demand during lead time for each simulation
            - stockout_days: Day when stockout occurs (NaN if no stockout)
            - ending_inventory: Inventory level at end of lead time (can be negative)
            - stockout_probability: Probability of stockout during lead time
        """
        cumulative_demands = []
        stockout_days = []
        ending_inventories = []
        
        for sim in range(self.n_simulations):
            daily_demand = self.simulate_demand_path(forecast_df, lead_time_days, distribution_type)
            cumulative_demand = np.sum(daily_demand)
            
            # Simulate day-by-day depletion
            inventory = current_inventory
            stockout_day = np.nan
            
            for day, demand in enumerate(daily_demand):
                inventory -= demand
                if inventory < 0 and np.isnan(stockout_day):
                    stockout_day = day + 1  # Day 1-indexed
            
            cumulative_demands.append(cumulative_demand)
            stockout_days.append(stockout_day)
            ending_inventories.append(inventory)
        
        stockout_days = np.array(stockout_days)
        stockout_probability = np.sum(~np.isnan(stockout_days)) / self.n_simulations
        
        return {
            'cumulative_demand': np.array(cumulative_demands),
            'stockout_days': stockout_days,
            'ending_inventory': np.array(ending_inventories),
            'stockout_probability': stockout_probability
        }
    
    def get_demand_statistics(
        self,
        simulation_results: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """
        Compute summary statistics from simulation results.
        
        Args:
            simulation_results: Output from simulate_inventory_depletion()
            
        Returns:
            Dictionary with mean, std, percentiles of cumulative demand
        """
        cumulative_demand = simulation_results['cumulative_demand']
        
        return {
            'mean': np.mean(cumulative_demand),
            'std': np.std(cumulative_demand),
            'p10': np.percentile(cumulative_demand, 10),
            'p50': np.percentile(cumulative_demand, 50),
            'p90': np.percentile(cumulative_demand, 90),
            'p95': np.percentile(cumulative_demand, 95),
            'p99': np.percentile(cumulative_demand, 99)
        }
    
    def get_stockout_statistics(
        self,
        simulation_results: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """
        Compute stockout-related statistics.
        
        Args:
            simulation_results: Output from simulate_inventory_depletion()
            
        Returns:
            Dictionary with stockout probability, expected stockout day, etc.
        """
        stockout_days = simulation_results['stockout_days']
        stockout_prob = simulation_results['stockout_probability']
        
        valid_stockout_days = stockout_days[~np.isnan(stockout_days)]
        
        stats = {
            'stockout_probability': stockout_prob,
            'expected_stockout_day': np.nan,
            'median_stockout_day': np.nan
        }
        
        if len(valid_stockout_days) > 0:
            stats['expected_stockout_day'] = np.mean(valid_stockout_days)
            stats['median_stockout_day'] = np.median(valid_stockout_days)
        
        return stats

