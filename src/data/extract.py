"""
Data Extraction Module for Stock Market Data
Fetches time-series data from Alpha Vantage API
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, Optional
from dotenv import load_dotenv
import time

load_dotenv()


class DataExtractor:
    """Extract stock market data from Alpha Vantage API"""
    
    def __init__(self, api_key: Optional[str] = None, symbol: str = "AAPL"):
        """
        Initialize the data extractor
        
        Args:
            api_key: Alpha Vantage API key
            symbol: Stock symbol to fetch data for
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.symbol = symbol
        self.base_url = "https://www.alphavantage.co/query"
        
        if not self.api_key:
            raise ValueError("API key not provided. Set ALPHA_VANTAGE_API_KEY environment variable.")
    
    def fetch_intraday_data(self, interval: str = "60min", outputsize: str = "full") -> pd.DataFrame:
        """
        Fetch intraday stock data
        
        Args:
            interval: Time interval (1min, 5min, 15min, 30min, 60min)
            outputsize: 'compact' (latest 100 data points) or 'full' (full-length time series)
        
        Returns:
            DataFrame with stock data
        """
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": self.symbol,
            "interval": interval,
            "apikey": self.api_key,
            "outputsize": outputsize,
            "datatype": "json"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                raise ValueError(f"API Error: {data['Error Message']}")
            
            if "Note" in data:
                raise ValueError(f"API Rate Limit: {data['Note']}")
            
            # Extract time series data
            time_series_key = f"Time Series ({interval})"
            if time_series_key not in data:
                raise ValueError(f"Unexpected API response structure: {list(data.keys())}")
            
            time_series = data[time_series_key]
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            
            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Add metadata
            df['symbol'] = self.symbol
            df['fetch_timestamp'] = datetime.now()
            
            return df
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch data from API: {str(e)}")
    
    def fetch_daily_data(self, outputsize: str = "full") -> pd.DataFrame:
        """
        Fetch daily stock data
        
        Args:
            outputsize: 'compact' (latest 100 data points) or 'full' (20+ years)
        
        Returns:
            DataFrame with daily stock data
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": self.symbol,
            "apikey": self.api_key,
            "outputsize": outputsize,
            "datatype": "json"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data:
                raise ValueError(f"API Error: {data['Error Message']}")
            
            if "Note" in data:
                raise ValueError(f"API Rate Limit: {data['Note']}")
            
            time_series = data["Time Series (Daily)"]
            
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['symbol'] = self.symbol
            df['fetch_timestamp'] = datetime.now()
            
            return df
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch data from API: {str(e)}")
    
    def save_raw_data(self, df: pd.DataFrame, output_path: str) -> str:
        """
        Save raw data with timestamp
        
        Args:
            df: DataFrame to save
            output_path: Directory to save the data
        
        Returns:
            Path to saved file
        """
        os.makedirs(output_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"raw_stock_data_{self.symbol}_{timestamp}.csv"
        filepath = os.path.join(output_path, filename)
        
        df.to_csv(filepath, index=True)
        print(f"Raw data saved to: {filepath}")
        
        # Also save metadata
        metadata = {
            "symbol": self.symbol,
            "fetch_timestamp": timestamp,
            "rows": len(df),
            "columns": list(df.columns),
            "date_range": {
                "start": str(df.index.min()),
                "end": str(df.index.max())
            }
        }
        
        metadata_path = filepath.replace(".csv", "_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return filepath


def main():
    """Main function to test data extraction"""
    symbol = os.getenv("STOCK_SYMBOL", "AAPL")
    extractor = DataExtractor(symbol=symbol)
    
    print(f"Fetching intraday data for {symbol}...")
    df = extractor.fetch_intraday_data(interval="60min", outputsize="full")
    
    print(f"Fetched {len(df)} rows of data")
    print(f"Date range: {df.index.min()} to {df.index.max()}")
    print(f"\nFirst few rows:\n{df.head()}")
    
    output_path = "./data/raw"
    saved_file = extractor.save_raw_data(df, output_path)
    print(f"\nData saved successfully!")


if __name__ == "__main__":
    main()
