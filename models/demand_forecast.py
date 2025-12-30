"""
Demand Forecasting Module

Uses LightGBM with quantile regression to produce probabilistic demand forecasts.
Focus: Business outcomes, not forecast accuracy metrics.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import lightgbm as lgb
from sklearn.metrics import mean_pinball_loss


class DemandForecaster:
    """
    Probabilistic demand forecaster using LightGBM quantile regression.
    
    Produces P10, P50, P90 quantiles along with mean and std for each future time step.
    """
    
    def __init__(
        self,
        quantiles: List[float] = [0.1, 0.5, 0.9],
        n_estimators: int = 100,
        learning_rate: float = 0.05,
        max_depth: int = 7,
        min_child_samples: int = 20
    ):
        """
        Initialize the demand forecaster.
        
        Args:
            quantiles: List of quantiles to forecast (default: P10, P50, P90)
            n_estimators: Number of boosting rounds
            learning_rate: Learning rate for gradient boosting
            max_depth: Maximum tree depth
            min_child_samples: Minimum samples in leaf
        """
        self.quantiles = quantiles
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_child_samples = min_child_samples
        self.models: Dict[float, lgb.LGBMRegressor] = {}
        self.feature_names: List[str] = []
        
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create calendar and lag features from time series data.
        
        Args:
            df: DataFrame with 'date' and 'demand' columns
            
        Returns:
            DataFrame with engineered features
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # Calendar features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month
        df['day_of_month'] = df['date'].dt.day
        
        # Simple holiday flag (weekends)
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Lag features
        for lag in [1, 7, 14, 30]:
            df[f'lag_{lag}'] = df['demand'].shift(lag)
        
        # Rolling statistics
        for window in [7, 14, 30]:
            df[f'rolling_mean_{window}'] = df['demand'].rolling(window=window, min_periods=1).mean()
            df[f'rolling_std_{window}'] = df['demand'].rolling(window=window, min_periods=1).std().fillna(0)
        
        # Trend features
        df['demand_trend_7'] = df['demand'].rolling(window=7, min_periods=1).mean() - \
                               df['demand'].rolling(window=14, min_periods=1).mean()
        
        return df
    
    def _prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target for training.
        
        Args:
            df: DataFrame with features
            
        Returns:
            X: Feature matrix
            y: Target vector
        """
        feature_cols = [
            'day_of_week', 'week_of_year', 'month', 'day_of_month', 'is_weekend',
            'lag_1', 'lag_7', 'lag_14', 'lag_30',
            'rolling_mean_7', 'rolling_std_7',
            'rolling_mean_14', 'rolling_std_14',
            'rolling_mean_30', 'rolling_std_30',
            'demand_trend_7'
        ]
        
        # Drop rows with NaN (from lag features)
        df_clean = df.dropna(subset=feature_cols + ['demand'])
        
        X = df_clean[feature_cols]
        y = df_clean['demand']
        
        self.feature_names = feature_cols
        
        return X, y
    
    def train(self, historical_data: pd.DataFrame, sku_id: Optional[str] = None):
        """
        Train quantile regression models for demand forecasting.
        
        Args:
            historical_data: DataFrame with 'date' and 'demand' columns
            sku_id: Optional SKU identifier for logging
        """
        # Create features
        df_features = self._create_features(historical_data)
        X, y = self._prepare_training_data(df_features)
        
        if len(X) < 30:
            raise ValueError(f"Insufficient data for training. Need at least 30 samples, got {len(X)}")
        
        # Train one model per quantile
        self.models = {}
        
        for quantile in self.quantiles:
            model = lgb.LGBMRegressor(
                objective='quantile',
                alpha=quantile,
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                max_depth=self.max_depth,
                min_child_samples=self.min_child_samples,
                random_state=42,
                verbose=-1
            )
            
            model.fit(X, y)
            self.models[quantile] = model
        
        print(f"Trained {len(self.models)} quantile models for SKU: {sku_id or 'default'}")
    
    def forecast(
        self,
        future_dates: pd.DatetimeIndex,
        last_known_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate probabilistic demand forecast for future dates.
        
        Args:
            future_dates: DatetimeIndex of future dates to forecast
            last_known_data: Historical data up to the forecast start date
            
        Returns:
            DataFrame with columns: date, p10, p50, p90, mean, std
        """
        if not self.models:
            raise ValueError("Models not trained. Call train() first.")
        
        # Create features for future dates
        # We need to extend last_known_data to create lag features
        df_extended = self._create_features(last_known_data)
        
        forecasts = []
        
        for date in future_dates:
            # Create feature vector for this date
            features = pd.DataFrame({
                'day_of_week': [date.dayofweek],
                'week_of_year': [date.isocalendar().week],
                'month': [date.month],
                'day_of_month': [date.day],
                'is_weekend': [1 if date.dayofweek >= 5 else 0],
            })
            
            # Add lag features from recent history
            recent_demand = df_extended['demand'].tail(30).values
            if len(recent_demand) >= 30:
                features['lag_1'] = recent_demand[-1]
                features['lag_7'] = recent_demand[-7] if len(recent_demand) >= 7 else recent_demand[-1]
                features['lag_14'] = recent_demand[-14] if len(recent_demand) >= 14 else recent_demand[-1]
                features['lag_30'] = recent_demand[-30]
            else:
                # Fallback for insufficient history
                last_val = recent_demand[-1] if len(recent_demand) > 0 else df_extended['demand'].mean()
                features['lag_1'] = last_val
                features['lag_7'] = last_val
                features['lag_14'] = last_val
                features['lag_30'] = last_val
            
            # Rolling statistics from recent history
            if len(recent_demand) >= 7:
                features['rolling_mean_7'] = np.mean(recent_demand[-7:])
                features['rolling_std_7'] = np.std(recent_demand[-7:])
            else:
                features['rolling_mean_7'] = np.mean(recent_demand) if len(recent_demand) > 0 else 0
                features['rolling_std_7'] = np.std(recent_demand) if len(recent_demand) > 0 else 0
            
            if len(recent_demand) >= 14:
                features['rolling_mean_14'] = np.mean(recent_demand[-14:])
                features['rolling_std_14'] = np.std(recent_demand[-14:])
            else:
                features['rolling_mean_14'] = features['rolling_mean_7']
                features['rolling_std_14'] = features['rolling_std_7']
            
            if len(recent_demand) >= 30:
                features['rolling_mean_30'] = np.mean(recent_demand[-30:])
                features['rolling_std_30'] = np.std(recent_demand[-30:])
            else:
                features['rolling_mean_30'] = features['rolling_mean_14']
                features['rolling_std_30'] = features['rolling_std_14']
            
            # Trend feature
            if len(recent_demand) >= 14:
                features['demand_trend_7'] = np.mean(recent_demand[-7:]) - np.mean(recent_demand[-14:])
            else:
                features['demand_trend_7'] = 0
            
            # Ensure feature order matches training
            features = features[self.feature_names]
            
            # Predict quantiles
            quantile_predictions = {}
            for quantile, model in self.models.items():
                pred = model.predict(features)[0]
                quantile_predictions[f'p{int(quantile*100)}'] = max(0, pred)  # Ensure non-negative
            
            # Estimate mean and std from quantiles
            p10 = quantile_predictions.get('p10', quantile_predictions.get('p50', 0) * 0.7)
            p50 = quantile_predictions.get('p50', 0)
            p90 = quantile_predictions.get('p90', quantile_predictions.get('p50', 0) * 1.3)
            
            # Approximate mean and std from quantiles
            # Using normal approximation: mean ≈ median, std ≈ (p90 - p10) / (2 * 1.28)
            mean_demand = p50  # Use median as mean approximation
            std_demand = (p90 - p10) / 2.56 if (p90 - p10) > 0 else p50 * 0.2
            
            forecasts.append({
                'date': date,
                'p10': p10,
                'p50': p50,
                'p90': p90,
                'mean': mean_demand,
                'std': std_demand
            })
            
            # Update extended data for next iteration (using p50 as proxy)
            new_row = pd.DataFrame({
                'date': [date],
                'demand': [p50]
            })
            df_extended = pd.concat([df_extended, new_row], ignore_index=True)
            df_extended = self._create_features(df_extended)
        
        return pd.DataFrame(forecasts)
    
    def get_forecast_distribution(
        self,
        forecast_df: pd.DataFrame,
        day_index: int = 0
    ) -> Dict[str, float]:
        """
        Extract demand distribution parameters for a specific day.
        
        Args:
            forecast_df: Output from forecast()
            day_index: Index of the day in the forecast (0 = first day)
            
        Returns:
            Dictionary with mean, std, p10, p50, p90
        """
        if day_index >= len(forecast_df):
            raise ValueError(f"day_index {day_index} exceeds forecast length {len(forecast_df)}")
        
        row = forecast_df.iloc[day_index]
        return {
            'mean': row['mean'],
            'std': row['std'],
            'p10': row['p10'],
            'p50': row['p50'],
            'p90': row['p90']
        }

