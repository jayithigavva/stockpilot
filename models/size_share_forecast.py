"""
Footwear-Specific Size Share Forecasting

Predicts relative size demand distribution, not per-SKU demand.
Key insight: Demand is joint across sizes, not independent.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import lightgbm as lgb
from scipy.optimize import minimize
from scipy.special import softmax


class SizeShareForecaster:
    """
    Footwear-specific forecaster that predicts:
    1. Total style demand (P10/P50/P90)
    2. Size-share distribution (constrained to sum to 1)
    
    Combines to get size-level demand scenarios.
    """
    
    def __init__(
        self,
        quantiles: List[float] = [0.1, 0.5, 0.9],
        n_estimators: int = 100,
        learning_rate: floa
        t = 0.05,
        max_depth: int = 7
    ):
        """
        Initialize size-share forecaster.
        
        Args:
            quantiles: Quantiles for total demand forecast
            n_estimators: Number of boosting rounds
            learning_rate: Learning rate
            max_depth: Max tree depth
        """
        self.quantiles = quantiles
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        
        # Models for total style demand
        self.style_models: Dict[float, lgb.LGBMRegressor] = {}
        
        # Models for size shares (one per size)
        self.size_share_models: Dict[str, lgb.LGBMRegressor] = {}
        
        self.sizes: List[str] = []
        self.feature_names: List[str] = []
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create calendar and lag features."""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # Calendar features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Lag features
        for lag in [1, 7, 14, 30]:
            df[f'lag_{lag}'] = df['demand'].shift(lag)
        
        # Rolling statistics
        for window in [7, 14, 30]:
            df[f'rolling_mean_{window}'] = df['demand'].rolling(window=window, min_periods=1).mean()
            df[f'rolling_std_{window}'] = df['demand'].rolling(window=window, min_periods=1).std().fillna(0)
        
        return df
    
    def train(
        self,
        sales_df: pd.DataFrame,
        style_id: str,
        sizes: List[str]
    ):
        """
        Train models on style-level aggregated data.
        
        Args:
            sales_df: DataFrame with columns: date, size, demand, revenue
            style_id: Style identifier
            sizes: List of sizes (e.g., ["6", "7", "8", "9", "10", "11"])
        """
        self.sizes = sizes
        
        # Aggregate to style level (total demand per day)
        style_demand = sales_df.groupby('date')['demand'].sum().reset_index()
        style_demand.columns = ['date', 'demand']
        style_demand = style_demand.sort_values('date').reset_index(drop=True)
        
        # Create features for style-level demand
        style_features = self._create_features(style_demand)
        self.feature_names = [col for col in style_features.columns if col not in ['date', 'demand']]
        
        # Prepare training data
        X = style_features[self.feature_names].fillna(0)
        y = style_features['demand']
        
        # Remove rows with NaN targets
        valid_mask = ~y.isna()
        X = X[valid_mask]
        y = y[valid_mask]
        
        if len(X) < 30:
            raise ValueError(f"Insufficient data for style {style_id}: need at least 30 days")
        
        # Train quantile models for total style demand
        for quantile in self.quantiles:
            model = lgb.LGBMRegressor(
                objective='quantile',
                alpha=quantile,
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                max_depth=self.max_depth,
                verbose=-1
            )
            model.fit(X, y)
            self.style_models[quantile] = model
        
        # Train size-share models
        # For each size, predict its share of total style demand
        for size in sizes:
            size_sales = sales_df[sales_df['size'] == size].copy()
            if len(size_sales) < 10:
                continue  # Skip sizes with insufficient data
            
            # Merge with style totals to compute shares
            size_with_total = size_sales.merge(
                style_demand,
                on='date',
                suffixes=('_size', '_total')
            )
            size_with_total['size_share'] = (
                size_with_total['demand_size'] / 
                size_with_total['demand_total'].clip(lower=0.01)  # Avoid division by zero
            )
            
            # Create features
            size_features = self._create_features(
                size_with_total[['date', 'demand_size']].rename(columns={'demand_size': 'demand'})
            )
            
            X_size = size_features[self.feature_names].fillna(0)
            y_size = size_with_total['size_share']
            
            valid_mask = ~y_size.isna() & (y_size >= 0) & (y_size <= 1)
            X_size = X_size[valid_mask]
            y_size = y_size[valid_mask]
            
            if len(X_size) < 10:
                continue
            
            # Train model to predict size share
            model = lgb.LGBMRegressor(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                max_depth=self.max_depth,
                verbose=-1
            )
            model.fit(X_size, y_size.clip(0, 1))  # Constrain to [0, 1]
            self.size_share_models[size] = model
    
    def forecast(
        self,
        forecast_horizon_days: int,
        last_date: Optional[pd.Timestamp] = None
    ) -> Dict:
        """
        Forecast total style demand and size-share distribution.
        
        Args:
            forecast_horizon_days: Number of days to forecast
            last_date: Last date in training data (for feature creation)
            
        Returns:
            Dictionary with:
            - total_demand: {p10: [...], p50: [...], p90: [...]}
            - size_shares: {size: {mean: float, std: float}}
            - size_demands: {size: {p10: [...], p50: [...], p90: [...]}}
        """
        if last_date is None:
            last_date = pd.Timestamp.now()
        
        # Generate future dates
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=forecast_horizon_days,
            freq='D'
        )
        
        # Create features for future dates
        future_df = pd.DataFrame({'date': future_dates, 'demand': 0})
        future_features = self._create_features(future_df)
        X_future = future_features[self.feature_names].fillna(0)
        
        # Forecast total style demand
        total_forecast = {}
        for quantile in self.quantiles:
            if quantile in self.style_models:
                predictions = self.style_models[quantile].predict(X_future)
                total_forecast[f'p{int(quantile * 100)}'] = predictions.tolist()
        
        # Forecast size shares
        size_shares = {}
        size_demands = {}
        
        for size in self.sizes:
            if size in self.size_share_models:
                share_predictions = self.size_share_models[size].predict(X_future)
                # Constrain to [0, 1]
                share_predictions = np.clip(share_predictions, 0, 1)
                
                size_shares[size] = {
                    'mean': float(np.mean(share_predictions)),
                    'std': float(np.std(share_predictions)),
                    'values': share_predictions.tolist()
                }
                
                # Combine total demand × size share = demand per size
                size_demands[size] = {
                    'p10': (total_forecast.get('p10', [0]) * share_predictions).tolist(),
                    'p50': (total_forecast.get('p50', [0]) * share_predictions).tolist(),
                    'p90': (total_forecast.get('p90', [0]) * share_predictions).tolist(),
                }
            else:
                # Default: equal share if no model
                default_share = 1.0 / len(self.sizes)
                size_shares[size] = {
                    'mean': default_share,
                    'std': 0.0,
                    'values': [default_share] * forecast_horizon_days
                }
                size_demands[size] = {
                    'p10': (total_forecast.get('p10', [0]) * default_share).tolist(),
                    'p50': (total_forecast.get('p50', [0]) * default_share).tolist(),
                    'p90': (total_forecast.get('p90', [0]) * default_share).tolist(),
                }
        
        # Normalize size shares to sum to 1 (constraint)
        for i in range(forecast_horizon_days):
            total_share = sum(
                size_shares[size]['values'][i] 
                for size in self.sizes 
                if size in size_shares
            )
            if total_share > 0:
                for size in self.sizes:
                    if size in size_shares:
                        size_shares[size]['values'][i] /= total_share
                        # Update size demands with normalized shares
                        for quantile in ['p10', 'p50', 'p90']:
                            if quantile in total_forecast:
                                size_demands[size][quantile][i] = (
                                    total_forecast[quantile][i] * 
                                    size_shares[size]['values'][i]
                                )
        
        return {
            'total_demand': total_forecast,
            'size_shares': size_shares,
            'size_demands': size_demands,
            'forecast_dates': future_dates.tolist()
        }





