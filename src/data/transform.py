"""
Data Transformation and Feature Engineering Module
Creates time-series features for stock price prediction
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import os


class StockDataTransformer:
    """Transform stock data and engineer features for volatility prediction"""
    
    def __init__(self, target_column: str = 'close'):
        """
        Initialize transformer
        
        Args:
            target_column: Column to use for target variable creation
        """
        self.target_column = target_column
        self.feature_names = []
    
    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate returns and log returns"""
        df = df.copy()
        
        # Simple returns
        df['returns'] = df[self.target_column].pct_change()
        
        # Log returns
        df['log_returns'] = np.log(df[self.target_column] / df[self.target_column].shift(1))
        
        self.feature_names.extend(['returns', 'log_returns'])
        return df
    
    def calculate_volatility(self, df: pd.DataFrame, windows: List[int] = [3, 5, 10]) -> pd.DataFrame:
        """
        Calculate rolling volatility (standard deviation of returns)
        
        Args:
            windows: List of window sizes for rolling calculations (reduced for daily data)
        """
        df = df.copy()
        
        if 'returns' not in df.columns:
            df = self.calculate_returns(df)
        
        for window in windows:
            col_name = f'volatility_{window}'
            df[col_name] = df['returns'].rolling(window=window).std()
            self.feature_names.append(col_name)
        
        return df
    
    def create_lag_features(self, df: pd.DataFrame, columns: List[str], lags: List[int] = [1, 2, 3]) -> pd.DataFrame:
        """
        Create lagged features
        
        Args:
            columns: Columns to create lags for
            lags: Number of periods to lag (reduced for daily data)
        """
        df = df.copy()
        
        for col in columns:
            if col in df.columns:
                for lag in lags:
                    lag_col_name = f'{col}_lag_{lag}'
                    df[lag_col_name] = df[col].shift(lag)
                    self.feature_names.append(lag_col_name)
        
        return df
    
    def create_rolling_features(self, df: pd.DataFrame, windows: List[int] = [3, 5, 10]) -> pd.DataFrame:
        """
        Create rolling statistical features
        
        Args:
            windows: Window sizes for rolling calculations (reduced for daily data)
        """
        df = df.copy()
        
        for window in windows:
            # Rolling mean
            df[f'close_ma_{window}'] = df[self.target_column].rolling(window=window).mean()
            
            # Rolling std
            df[f'close_std_{window}'] = df[self.target_column].rolling(window=window).std()
            
            # Rolling min/max
            df[f'close_min_{window}'] = df[self.target_column].rolling(window=window).min()
            df[f'close_max_{window}'] = df[self.target_column].rolling(window=window).max()
            
            # Bollinger bands
            df[f'bb_upper_{window}'] = df[f'close_ma_{window}'] + (2 * df[f'close_std_{window}'])
            df[f'bb_lower_{window}'] = df[f'close_ma_{window}'] - (2 * df[f'close_std_{window}'])
            
            self.feature_names.extend([
                f'close_ma_{window}',
                f'close_std_{window}',
                f'close_min_{window}',
                f'close_max_{window}',
                f'bb_upper_{window}',
                f'bb_lower_{window}'
            ])
        
        return df
    
    def create_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create common technical indicators"""
        df = df.copy()
        
        # RSI (Relative Strength Index) - reduced window for daily data
        delta = df[self.target_column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD (Moving Average Convergence Divergence)
        exp1 = df[self.target_column].ewm(span=12, adjust=False).mean()
        exp2 = df[self.target_column].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_diff'] = df['macd'] - df['macd_signal']
        
        # Price momentum (reduced windows for daily data)
        df['momentum_3'] = df[self.target_column] - df[self.target_column].shift(3)
        df['momentum_5'] = df[self.target_column] - df[self.target_column].shift(5)
        
        # Volume indicators
        if 'volume' in df.columns:
            df['volume_ma_5'] = df['volume'].rolling(window=5).mean()
            df['volume_ma_10'] = df['volume'].rolling(window=10).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma_10']
            
            self.feature_names.extend(['volume_ma_5', 'volume_ma_10', 'volume_ratio'])
        
        self.feature_names.extend([
            'rsi', 'macd', 'macd_signal', 'macd_diff',
            'momentum_3', 'momentum_5'
        ])
        
        return df
    
    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        df = df.copy()
        
        # Check if we have intraday data (has hour information)
        has_hour = hasattr(df.index, 'hour') and (df.index.hour != 0).any()
        
        if has_hour:
            # Intraday data - include hour features
            df['hour'] = df.index.hour
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
            self.feature_names.extend(['hour', 'hour_sin', 'hour_cos'])
        else:
            # Daily data - set hour features to default values
            df['hour'] = 0
            df['hour_sin'] = 0.0
            df['hour_cos'] = 1.0
            self.feature_names.extend(['hour', 'hour_sin', 'hour_cos'])
        
        # These work for both intraday and daily data
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        
        # Cyclical encoding for day of week
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        self.feature_names.extend([
            'day_of_week', 'day_of_month', 'month', 'quarter',
            'day_sin', 'day_cos'
        ])
        
        return df
    
    def create_target_variable(self, df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
        """
        Create target variable: future volatility
        
        Args:
            horizon: Number of periods ahead to predict
        """
        df = df.copy()
        
        # Calculate future returns
        df['future_returns'] = df['returns'].shift(-horizon)
        
        # Target: absolute value of future returns (volatility proxy)
        df['target_volatility'] = df['future_returns'].abs()
        
        # Alternative target: use rolling std of returns as realized volatility
        # Use forward-looking window (next N days volatility)
        if horizon > 1:
            df['target_realized_vol'] = df['returns'].shift(-horizon).rolling(window=horizon).std()
        else:
            # For horizon=1, use same as target_volatility
            df['target_realized_vol'] = df['target_volatility']
        
        return df
    
    def transform(self, df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
        """
        Apply all transformations
        
        Args:
            df: Input DataFrame with OHLCV data
            horizon: Prediction horizon
        
        Returns:
            Transformed DataFrame with all features
        """
        self.feature_names = []
        
        print("Starting data transformation...")
        
        # Calculate returns
        df = self.calculate_returns(df)
        print(f"  ✓ Calculated returns")
        
        # Calculate volatility
        df = self.calculate_volatility(df)
        print(f"  ✓ Calculated volatility measures")
        
        # Create lag features
        df = self.create_lag_features(df, columns=['close', 'returns', 'volume'])
        print(f"  ✓ Created lag features")
        
        # Create rolling features
        df = self.create_rolling_features(df)
        print(f"  ✓ Created rolling features")
        
        # Create technical indicators
        df = self.create_technical_indicators(df)
        print(f"  ✓ Created technical indicators")
        
        # Create time features
        df = self.create_time_features(df)
        print(f"  ✓ Created time features")
        
        # Create target variable
        df = self.create_target_variable(df, horizon=horizon)
        print(f"  ✓ Created target variable")
        
        # Drop rows with NaN values (due to rolling windows and lags)
        initial_rows = len(df)
        df = df.dropna()
        print(f"  ✓ Dropped {initial_rows - len(df)} rows with missing values")
        
        print(f"\nTransformation complete! Final shape: {df.shape}")
        print(f"Total features created: {len(self.feature_names)}")
        
        return df
    
    def save_processed_data(self, df: pd.DataFrame, output_path: str, symbol: str) -> str:
        """Save processed data"""
        os.makedirs(output_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"processed_stock_data_{symbol}_{timestamp}.csv"
        filepath = os.path.join(output_path, filename)
        
        df.to_csv(filepath, index=True)
        print(f"Processed data saved to: {filepath}")
        
        return filepath


def main():
    """Test the transformer"""
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=500, freq='1H')
    df = pd.DataFrame({
        'open': np.random.uniform(100, 200, 500),
        'high': np.random.uniform(100, 200, 500),
        'low': np.random.uniform(100, 200, 500),
        'close': np.random.uniform(100, 200, 500),
        'volume': np.random.randint(1000000, 10000000, 500),
        'symbol': 'TEST'
    }, index=dates)
    
    # Transform data
    transformer = StockDataTransformer()
    df_transformed = transformer.transform(df, horizon=1)
    
    print(f"\nOriginal shape: {df.shape}")
    print(f"Transformed shape: {df_transformed.shape}")
    print(f"\nFeature columns: {df_transformed.columns.tolist()}")
    print(f"\nSample data:\n{df_transformed.head()}")


if __name__ == "__main__":
    main()
