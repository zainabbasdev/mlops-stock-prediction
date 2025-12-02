"""
Unit tests for data extraction module
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.data.extract import DataExtractor


def test_data_extractor_initialization():
    """Test DataExtractor initialization"""
    with pytest.raises(ValueError):
        DataExtractor(api_key=None)
    
    extractor = DataExtractor(api_key="test_key", symbol="AAPL")
    assert extractor.api_key == "test_key"
    assert extractor.symbol == "AAPL"


@patch('src.data.extract.requests.get')
def test_fetch_intraday_data_success(mock_get):
    """Test successful data fetch"""
    # Mock API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "Time Series (60min)": {
            "2024-01-01 09:00:00": {
                "1. open": "150.0",
                "2. high": "151.0",
                "3. low": "149.0",
                "4. close": "150.5",
                "5. volume": "1000000"
            }
        }
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    extractor = DataExtractor(api_key="test_key")
    df = extractor.fetch_intraday_data()
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'close' in df.columns


@patch('src.data.extract.requests.get')
def test_fetch_intraday_data_api_error(mock_get):
    """Test API error handling"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "Error Message": "Invalid API key"
    }
    mock_get.return_value = mock_response
    
    extractor = DataExtractor(api_key="invalid_key")
    
    with pytest.raises(ValueError):
        extractor.fetch_intraday_data()


def test_save_raw_data(tmp_path):
    """Test data saving functionality"""
    # Create sample data
    df = pd.DataFrame({
        'open': [100, 101],
        'high': [102, 103],
        'low': [99, 100],
        'close': [101, 102],
        'volume': [1000, 1100]
    })
    
    extractor = DataExtractor(api_key="test_key", symbol="TEST")
    filepath = extractor.save_raw_data(df, str(tmp_path))
    
    assert filepath.endswith('.csv')
    assert pd.read_csv(filepath).shape[0] == 2
