"""
Unit tests for data transformation module
"""

import pytest
import pandas as pd
import numpy as np
from src.data.transform import StockDataTransformer


def create_sample_data():
    """Create sample stock data"""
    dates = pd.date_range('2024-01-01', periods=500, freq='1H')
    df = pd.DataFrame({
        'open': np.random.uniform(100, 200, 500),
        'high': np.random.uniform(100, 200, 500),
        'low': np.random.uniform(100, 200, 500),
        'close': np.random.uniform(100, 200, 500),
        'volume': np.random.randint(1000000, 10000000, 500)
    }, index=dates)
    return df


def test_transformer_initialization():
    """Test transformer initialization"""
    transformer = StockDataTransformer(target_column='close')
    assert transformer.target_column == 'close'
    assert transformer.feature_names == []


def test_calculate_returns():
    """Test returns calculation"""
    df = create_sample_data()
    transformer = StockDataTransformer()
    
    df_with_returns = transformer.calculate_returns(df)
    
    assert 'returns' in df_with_returns.columns
    assert 'log_returns' in df_with_returns.columns
    assert len(transformer.feature_names) > 0


def test_calculate_volatility():
    """Test volatility calculation"""
    df = create_sample_data()
    transformer = StockDataTransformer()
    
    df = transformer.calculate_returns(df)
    df_with_vol = transformer.calculate_volatility(df, windows=[5, 10])
    
    assert 'volatility_5' in df_with_vol.columns
    assert 'volatility_10' in df_with_vol.columns


def test_create_lag_features():
    """Test lag feature creation"""
    df = create_sample_data()
    transformer = StockDataTransformer()
    
    df_with_lags = transformer.create_lag_features(
        df, columns=['close'], lags=[1, 2, 3]
    )
    
    assert 'close_lag_1' in df_with_lags.columns
    assert 'close_lag_2' in df_with_lags.columns
    assert 'close_lag_3' in df_with_lags.columns


def test_create_rolling_features():
    """Test rolling feature creation"""
    df = create_sample_data()
    transformer = StockDataTransformer()
    
    df_with_rolling = transformer.create_rolling_features(df, windows=[5, 10])
    
    assert 'close_ma_5' in df_with_rolling.columns
    assert 'close_std_5' in df_with_rolling.columns
    assert 'bb_upper_5' in df_with_rolling.columns


def test_create_technical_indicators():
    """Test technical indicator creation"""
    df = create_sample_data()
    transformer = StockDataTransformer()
    
    df_with_indicators = transformer.create_technical_indicators(df)
    
    assert 'rsi' in df_with_indicators.columns
    assert 'macd' in df_with_indicators.columns
    assert 'macd_signal' in df_with_indicators.columns


def test_create_time_features():
    """Test time feature creation"""
    df = create_sample_data()
    transformer = StockDataTransformer()
    
    df_with_time = transformer.create_time_features(df)
    
    assert 'hour' in df_with_time.columns
    assert 'day_of_week' in df_with_time.columns
    assert 'hour_sin' in df_with_time.columns
    assert 'hour_cos' in df_with_time.columns


def test_create_target_variable():
    """Test target variable creation"""
    df = create_sample_data()
    transformer = StockDataTransformer()
    
    df = transformer.calculate_returns(df)
    df_with_target = transformer.create_target_variable(df, horizon=1)
    
    assert 'target_volatility' in df_with_target.columns
    assert 'future_returns' in df_with_target.columns


def test_transform_full_pipeline():
    """Test full transformation pipeline"""
    df = create_sample_data()
    transformer = StockDataTransformer()
    
    df_transformed = transformer.transform(df, horizon=1)
    
    # Check that data is not empty
    assert not df_transformed.empty
    
    # Check that features were created
    assert len(transformer.feature_names) > 10
    
    # Check that target exists
    assert 'target_volatility' in df_transformed.columns
    
    # Check that there are no NaN values
    assert df_transformed.isnull().sum().sum() == 0


def test_save_processed_data(tmp_path):
    """Test saving processed data"""
    df = create_sample_data()
    transformer = StockDataTransformer()
    df_transformed = transformer.transform(df)
    
    filepath = transformer.save_processed_data(
        df_transformed, str(tmp_path), "TEST"
    )
    
    assert filepath.endswith('.csv')
    loaded_df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    assert loaded_df.shape[0] == df_transformed.shape[0]
