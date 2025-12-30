"""
Example usage of the StockPilot inventory decision system.

This script demonstrates how to use the pipeline for single SKU and multi-SKU scenarios.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pipeline import InventoryDecisionPipeline


def generate_sample_data(n_days=365, base_demand=100, trend=0.1, seasonality=True):
    """
    Generate sample historical sales data for demonstration.
    
    Args:
        n_days: Number of days of historical data
        base_demand: Base daily demand
        trend: Daily trend (demand increases by this amount per day)
        seasonality: Whether to add weekly seasonality
        
    Returns:
        DataFrame with date and demand columns
    """
    dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')
    
    # Base demand with trend
    demand = base_demand + np.arange(n_days) * trend
    
    # Add weekly seasonality (lower on weekends)
    day_of_week = dates.dayofweek
    demand = demand * (1 - 0.3 * (day_of_week >= 5))  # 30% reduction on weekends
    
    # Add random noise
    demand = demand + np.random.normal(0, base_demand * 0.2, n_days)
    demand = np.maximum(demand, 0)  # Ensure non-negative
    
    # Add some outliers
    outlier_indices = np.random.choice(n_days, size=int(n_days * 0.05), replace=False)
    demand[outlier_indices] *= np.random.uniform(1.5, 2.5, len(outlier_indices))
    
    df = pd.DataFrame({
        'date': dates,
        'demand': demand
    })
    
    return df


def example_single_sku():
    """
    Example: Single SKU optimization
    """
    print("=" * 60)
    print("Example 1: Single SKU Optimization")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = InventoryDecisionPipeline(
        unit_cost=100,           # ₹100 per unit
        selling_price=150,        # ₹150 selling price
        holding_cost_rate=0.02,   # 2% per month holding cost
        markdown_rate=0.05,       # 5% of excess inventory becomes obsolete
        churn_penalty=5000,       # ₹5,000 penalty per stockout event
        n_simulations=5000,
        max_stockout_probability=0.20  # Max 20% stockout risk
    )
    
    # Generate sample historical data
    print("\n📂 Generating sample historical data...")
    historical_data = generate_sample_data(n_days=365, base_demand=100)
    print(f"✓ Generated {len(historical_data)} days of data")
    print(f"  Average demand: {historical_data['demand'].mean():.1f} units/day")
    
    # Train forecaster
    print("\n🎓 Training demand forecaster...")
    pipeline.train_forecaster(historical_data, sku_id='SKU001')
    
    # Run optimization
    print("\n🚀 Running optimization pipeline...")
    result = pipeline.run_pipeline(
        sku_id='SKU001',
        current_inventory=500,        # Current stock: 500 units
        lead_time_days=14,            # 14-day lead time
        forecast_horizon_days=30,      # Forecast 30 days ahead
        min_order_quantity=100,        # MOQ: 100 units
        max_order_quantity=5000,       # Max order: 5000 units
        order_multiple=10,             # Order in multiples of 10
        available_cash=500000,         # ₹5 lakh available
        holding_period_months=1.0,     # 1 month holding period
        distribution_type='normal',
        naive_quantity=2000            # Compare with naive order of 2000 units
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(result['explanation'])
    
    # Display cost breakdown
    print("\n" + "=" * 60)
    print("COST BREAKDOWN")
    print("=" * 60)
    cost = result['cost_breakdown']
    print(f"Expected Overstock Cost:  ₹{cost['expected_overstock_cost']:,.0f}")
    print(f"Expected Understock Cost: ₹{cost['expected_understock_cost']:,.0f}")
    print(f"Total Expected Loss:      ₹{cost['total_expected_loss']:,.0f}")
    print(f"Stockout Probability:      {cost['stockout_probability']*100:.1f}%")
    
    return result


def example_multi_sku():
    """
    Example: Multi-SKU capital allocation
    """
    print("\n\n" + "=" * 60)
    print("Example 2: Multi-SKU Capital Allocation")
    print("=" * 60)
    
    # Initialize pipeline (will create SKU-specific optimizers)
    base_pipeline = InventoryDecisionPipeline(
        unit_cost=100,  # Default, will be overridden per SKU
        selling_price=150,
        n_simulations=5000
    )
    
    # Generate forecasts for multiple SKUs
    sku_configs = []
    
    for i, sku_id in enumerate(['SKU001', 'SKU002', 'SKU003'], 1):
        print(f"\n📊 Preparing {sku_id}...")
        
        # Generate sample data
        historical_data = generate_sample_data(
            n_days=365,
            base_demand=100 * i,  # Different base demand per SKU
            trend=0.1 * i
        )
        
        # Train forecaster
        base_pipeline.train_forecaster(historical_data, sku_id=sku_id)
        
        # Generate forecast
        forecaster = base_pipeline.forecasters[sku_id]
        last_date = historical_data['date'].max()
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=30,
            freq='D'
        )
        forecast_df = forecaster.forecast(future_dates, historical_data)
        
        # SKU configuration
        sku_configs.append({
            'sku_id': sku_id,
            'forecast_df': forecast_df,
            'current_inventory': 500 * i,
            'lead_time_days': 10 + i * 5,  # Different lead times
            'unit_cost': 100 * i,          # Different costs
            'selling_price': 150 * i,
            'min_order_quantity': 50 * i,
            'max_order_quantity': 5000,
            'order_multiple': 10,
            'holding_period_months': 1.0,
            'distribution_type': 'normal',
            'max_stockout_probability': 0.20
        })
    
    # Run multi-SKU allocation
    print("\n💼 Allocating capital across SKUs...")
    allocation_result = base_pipeline.run_multi_sku_pipeline(
        sku_configs=sku_configs,
        total_available_cash=1000000,  # ₹10 lakh total
        baseline_quantities={
            'SKU001': 1500,
            'SKU002': 1200,
            'SKU003': 1000
        }
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("CAPITAL ALLOCATION RESULTS")
    print("=" * 60)
    print(allocation_result['explanation'])
    
    # Display rankings
    print("\n" + "=" * 60)
    print("SKU RANKINGS (by efficiency)")
    print("=" * 60)
    rankings = allocation_result['allocation_result']['rankings']
    print(rankings[['sku_id', 'loss_avoided_per_rupee', 'optimal_quantity', 'optimal_cash']].to_string(index=False))
    
    return allocation_result


if __name__ == '__main__':
    # Run examples
    try:
        # Example 1: Single SKU
        result1 = example_single_sku()
        
        # Example 2: Multi-SKU
        result2 = example_multi_sku()
        
        print("\n\n✅ Examples completed successfully!")
        print("\nTo use with your own data:")
        print("1. Load your historical sales data (CSV with 'date' and 'demand' columns)")
        print("2. Initialize pipeline with your cost parameters")
        print("3. Train forecasters for each SKU")
        print("4. Run pipeline.run_pipeline() or pipeline.run_multi_sku_pipeline()")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

