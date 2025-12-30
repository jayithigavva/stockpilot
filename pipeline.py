"""
Pipeline Orchestration

End-to-end pipeline that:
1. Loads data
2. Runs forecast
3. Runs simulation
4. Computes risk
5. Optimizes reorder
6. Produces final recommendation + explanation
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.demand_forecast import DemandForecaster
from simulation.demand_simulation import DemandSimulator
from inventory.risk_estimator import RiskEstimator
from economics.cost_model import CostModel
from optimization.reorder_optimizer import ReorderOptimizer
from optimization.capital_allocator import CapitalAllocator
from explainability.decision_explainer import DecisionExplainer


class InventoryDecisionPipeline:
    """
    End-to-end pipeline for inventory decision optimization.
    """
    
    def __init__(
        self,
        unit_cost: float,
        selling_price: float,
        holding_cost_rate: float = 0.02,
        markdown_rate: float = 0.0,
        churn_penalty: float = 0.0,
        n_simulations: int = 5000,
        max_stockout_probability: float = 0.20
    ):
        """
        Initialize pipeline with cost parameters.
        
        Args:
            unit_cost: Cost per unit
            selling_price: Selling price per unit
            holding_cost_rate: Monthly holding cost rate
            markdown_rate: Fraction of excess inventory that becomes obsolete
            churn_penalty: Penalty per stockout event
            n_simulations: Number of Monte Carlo simulations
            max_stockout_probability: Maximum acceptable stockout probability
        """
        # Initialize components
        self.simulator = DemandSimulator(n_simulations=n_simulations)
        self.cost_model = CostModel(
            unit_cost=unit_cost,
            selling_price=selling_price,
            holding_cost_rate=holding_cost_rate,
            markdown_rate=markdown_rate,
            churn_penalty=churn_penalty,
            simulator=self.simulator
        )
        self.risk_estimator = RiskEstimator(simulator=self.simulator)
        self.optimizer = ReorderOptimizer(
            cost_model=self.cost_model,
            risk_estimator=self.risk_estimator,
            max_stockout_probability=max_stockout_probability
        )
        self.explainer = DecisionExplainer()
        
        # Forecasters (one per SKU)
        self.forecasters: Dict[str, DemandForecaster] = {}
    
    def load_data(
        self,
        file_path: str,
        date_col: str = 'date',
        demand_col: str = 'demand',
        sku_col: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load historical sales data.
        
        Args:
            file_path: Path to CSV file
            date_col: Name of date column
            demand_col: Name of demand/sales column
            sku_col: Optional SKU identifier column
            
        Returns:
            DataFrame with historical data
        """
        df = pd.read_csv(file_path)
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col).reset_index(drop=True)
        
        return df
    
    def train_forecaster(
        self,
        historical_data: pd.DataFrame,
        sku_id: str = 'default',
        date_col: str = 'date',
        demand_col: str = 'demand'
    ):
        """
        Train demand forecaster for a SKU.
        
        Args:
            historical_data: Historical sales data
            sku_id: SKU identifier
            date_col: Name of date column
            demand_col: Name of demand column
        """
        # Prepare data
        df = historical_data[[date_col, demand_col]].copy()
        df.columns = ['date', 'demand']
        
        # Store historical data for this SKU (needed for forecasting)
        if not hasattr(self, 'historical_data'):
            self.historical_data = {}
        self.historical_data[sku_id] = df
        
        # Create and train forecaster
        forecaster = DemandForecaster()
        forecaster.train(df, sku_id=sku_id)
        self.forecasters[sku_id] = forecaster
        
        print(f"✓ Trained forecaster for SKU: {sku_id}")
    
    def run_pipeline(
        self,
        sku_id: str,
        current_inventory: float,
        lead_time_days: int,
        forecast_horizon_days: int = 30,
        min_order_quantity: float = 0,
        max_order_quantity: float = 10000,
        order_multiple: float = 1.0,
        available_cash: Optional[float] = None,
        holding_period_months: float = 1.0,
        distribution_type: str = 'normal',
        naive_quantity: Optional[float] = None
    ) -> Dict:
        """
        Run complete pipeline for a single SKU.
        
        Args:
            sku_id: SKU identifier
            current_inventory: Current inventory level
            lead_time_days: Lead time in days
            forecast_horizon_days: Number of days to forecast
            min_order_quantity: MOQ
            max_order_quantity: Maximum order quantity
            order_multiple: Order multiple constraint
            available_cash: Available cash constraint
            holding_period_months: Expected holding period
            distribution_type: 'normal' or 'quantile'
            naive_quantity: Optional naive order quantity for comparison
            
        Returns:
            Dictionary with complete results
        """
        if sku_id not in self.forecasters:
            raise ValueError(f"Forecaster not trained for SKU: {sku_id}")
        
        forecaster = self.forecasters[sku_id]
        
        # Step 1: Generate forecast
        print(f"\n📊 Step 1: Generating demand forecast for {sku_id}...")
        
        # Get historical data for this SKU
        if not hasattr(self, 'historical_data') or sku_id not in self.historical_data:
            raise ValueError(f"Historical data not found for SKU: {sku_id}. Call train_forecaster() first.")
        
        historical_df = self.historical_data[sku_id]
        
        # Generate future dates
        last_date = historical_df['date'].max()
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=forecast_horizon_days,
            freq='D'
        )
        
        # Generate forecast
        forecast_df = forecaster.forecast(future_dates, historical_df)
        
        print(f"✓ Forecast generated for {forecast_horizon_days} days")
        
        # Step 2: Estimate current risk
        print(f"\n⚠️ Step 2: Estimating current stockout risk...")
        current_risk = self.risk_estimator.estimate_stockout_risk(
            forecast_df=forecast_df,
            current_inventory=current_inventory,
            lead_time_days=lead_time_days,
            distribution_type=distribution_type
        )
        print(f"✓ Current stockout probability: {current_risk['stockout_probability']*100:.1f}%")
        print(f"✓ Risk category: {current_risk['risk_category']}")
        
        # Step 3: Optimize reorder
        print(f"\n🎯 Step 3: Optimizing reorder quantity...")
        optimization_result = self.optimizer.optimize_reorder(
            forecast_df=forecast_df,
            current_inventory=current_inventory,
            lead_time_days=lead_time_days,
            min_order_quantity=min_order_quantity,
            max_order_quantity=max_order_quantity,
            order_multiple=order_multiple,
            available_cash=available_cash,
            holding_period_months=holding_period_months,
            distribution_type=distribution_type
        )
        print(f"✓ Optimal order quantity: {optimization_result['optimal_quantity']:.0f} units")
        print(f"✓ Expected loss: ₹{optimization_result['optimal_loss']:,.0f}")
        
        # Step 4: Compare with naive (if provided)
        comparison_result = None
        if naive_quantity is not None:
            print(f"\n📈 Step 4: Comparing with naive ordering...")
            comparison_result = self.optimizer.compare_with_naive(
                forecast_df=forecast_df,
                current_inventory=current_inventory,
                lead_time_days=lead_time_days,
                naive_quantity=naive_quantity,
                optimal_result=optimization_result,
                holding_period_months=holding_period_months,
                distribution_type=distribution_type
            )
            print(f"✓ Loss reduction: ₹{comparison_result['loss_reduction']:,.0f}")
        
        # Step 5: Generate explanation
        print(f"\n📝 Step 5: Generating explanation...")
        explanation = self.explainer.explain_reorder_decision(
            optimization_result=optimization_result,
            current_inventory=current_inventory,
            unit_cost=self.cost_model.unit_cost,
            selling_price=self.cost_model.selling_price,
            lead_time_days=lead_time_days,
            comparison_result=comparison_result
        )
        
        # Get cost breakdown
        cost_breakdown = self.cost_model.compute_expected_economic_loss(
            forecast_df=forecast_df,
            current_inventory=current_inventory,
            reorder_quantity=optimization_result['optimal_quantity'],
            lead_time_days=lead_time_days,
            holding_period_months=holding_period_months,
            distribution_type=distribution_type
        )
        
        return {
            'sku_id': sku_id,
            'forecast': forecast_df,
            'current_risk': current_risk,
            'optimization_result': optimization_result,
            'comparison_result': comparison_result,
            'explanation': explanation,
            'cost_breakdown': cost_breakdown
        }
    
    def run_multi_sku_pipeline(
        self,
        sku_configs: List[Dict],
        total_available_cash: float,
        baseline_quantities: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Run pipeline for multiple SKUs with capital allocation.
        
        Args:
            sku_configs: List of dictionaries, each containing SKU configuration
            total_available_cash: Total cash available
            baseline_quantities: Dictionary mapping SKU IDs to baseline quantities
            
        Returns:
            Dictionary with allocation results
        """
        # Create optimizers for each SKU
        optimizers = {}
        for config in sku_configs:
            sku_id = config['sku_id']
            # Create optimizer with SKU-specific cost model
            cost_model = CostModel(
                unit_cost=config['unit_cost'],
                selling_price=config['selling_price'],
                holding_cost_rate=config.get('holding_cost_rate', 0.02),
                markdown_rate=config.get('markdown_rate', 0.0),
                churn_penalty=config.get('churn_penalty', 0.0),
                simulator=self.simulator
            )
            risk_estimator = RiskEstimator(simulator=self.simulator)
            optimizer = ReorderOptimizer(
                cost_model=cost_model,
                risk_estimator=risk_estimator,
                max_stockout_probability=config.get('max_stockout_probability', 0.20)
            )
            optimizers[sku_id] = optimizer
        
        # Create capital allocator
        allocator = CapitalAllocator(optimizers)
        
        # Prepare SKU data for allocation
        sku_data = []
        for config in sku_configs:
            sku_data.append({
                'sku_id': config['sku_id'],
                'forecast_df': config['forecast_df'],
                'current_inventory': config['current_inventory'],
                'lead_time_days': config['lead_time_days'],
                'min_order_quantity': config['min_order_quantity'],
                'max_order_quantity': config['max_order_quantity'],
                'order_multiple': config.get('order_multiple', 1.0),
                'holding_period_months': config.get('holding_period_months', 1.0),
                'distribution_type': config.get('distribution_type', 'normal')
            })
        
        # Allocate capital
        allocation_result = allocator.allocate_capital(
            sku_data=sku_data,
            total_available_cash=total_available_cash,
            baseline_quantities=baseline_quantities
        )
        
        # Generate explanation
        explanation = self.explainer.explain_capital_allocation(
            allocation_result=allocation_result,
            total_available_cash=total_available_cash
        )
        
        return {
            'allocation_result': allocation_result,
            'explanation': explanation
        }


def main():
    """
    Example usage of the pipeline.
    """
    print("🚀 Inventory Decision Pipeline")
    print("=" * 50)
    
    # Example: Single SKU
    pipeline = InventoryDecisionPipeline(
        unit_cost=100,
        selling_price=150,
        holding_cost_rate=0.02,
        n_simulations=5000
    )
    
    # Load and prepare data (example)
    # In practice, load from actual data file
    print("\n📂 Loading data...")
    # df = pipeline.load_data('data/historical_sales.csv')
    # pipeline.train_forecaster(df, sku_id='SKU001')
    
    print("\n✅ Pipeline initialized. Ready to run optimization.")
    print("\nTo use the pipeline:")
    print("1. Load your historical data")
    print("2. Train forecasters for each SKU")
    print("3. Run pipeline.run_pipeline() for each SKU")
    print("4. Or use pipeline.run_multi_sku_pipeline() for capital allocation")


if __name__ == '__main__':
    main()

