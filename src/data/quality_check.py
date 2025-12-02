"""
Data Quality Check Module
Validates data quality before processing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


class DataQualityChecker:
    """Performs comprehensive data quality checks"""
    
    def __init__(self, null_threshold: float = 0.01, required_columns: List[str] = None):
        """
        Initialize quality checker
        
        Args:
            null_threshold: Maximum allowed percentage of null values (default 1%)
            required_columns: List of columns that must be present
        """
        self.null_threshold = null_threshold
        self.required_columns = required_columns or ['open', 'high', 'low', 'close', 'volume']
        self.checks_passed = {}
        self.issues = []
    
    def check_schema(self, df: pd.DataFrame) -> bool:
        """Check if all required columns are present"""
        missing_columns = set(self.required_columns) - set(df.columns)
        
        if missing_columns:
            self.issues.append(f"Missing required columns: {missing_columns}")
            self.checks_passed['schema'] = False
            return False
        
        self.checks_passed['schema'] = True
        return True
    
    def check_null_values(self, df: pd.DataFrame) -> bool:
        """Check if null values exceed threshold"""
        total_cells = df.shape[0] * df.shape[1]
        null_count = df.isnull().sum().sum()
        null_percentage = (null_count / total_cells) * 100
        
        if null_percentage > self.null_threshold * 100:
            self.issues.append(
                f"Null values ({null_percentage:.2f}%) exceed threshold ({self.null_threshold * 100}%)"
            )
            self.checks_passed['null_values'] = False
            return False
        
        self.checks_passed['null_values'] = True
        return True
    
    def check_data_types(self, df: pd.DataFrame) -> bool:
        """Check if numeric columns contain valid numbers"""
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        
        for col in numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    self.issues.append(f"Column '{col}' is not numeric type")
                    self.checks_passed['data_types'] = False
                    return False
        
        self.checks_passed['data_types'] = True
        return True
    
    def check_value_ranges(self, df: pd.DataFrame) -> bool:
        """Check if values are within reasonable ranges"""
        issues_found = False
        
        # Check for negative prices
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if col in df.columns:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    self.issues.append(f"Found {negative_count} negative values in '{col}'")
                    issues_found = True
        
        # Check for negative volume
        if 'volume' in df.columns:
            negative_volume = (df['volume'] < 0).sum()
            if negative_volume > 0:
                self.issues.append(f"Found {negative_volume} negative volume values")
                issues_found = True
        
        # Check high >= low
        if 'high' in df.columns and 'low' in df.columns:
            invalid_ranges = (df['high'] < df['low']).sum()
            if invalid_ranges > 0:
                self.issues.append(f"Found {invalid_ranges} rows where high < low")
                issues_found = True
        
        self.checks_passed['value_ranges'] = not issues_found
        return not issues_found
    
    def check_temporal_consistency(self, df: pd.DataFrame) -> bool:
        """Check for temporal issues in the data"""
        if not isinstance(df.index, pd.DatetimeIndex):
            self.issues.append("Index is not a DatetimeIndex")
            self.checks_passed['temporal'] = False
            return False
        
        # Check for duplicate timestamps
        duplicates = df.index.duplicated().sum()
        if duplicates > 0:
            self.issues.append(f"Found {duplicates} duplicate timestamps")
            self.checks_passed['temporal'] = False
            return False
        
        # Check if data is sorted
        if not df.index.is_monotonic_increasing:
            self.issues.append("Data is not sorted chronologically")
            self.checks_passed['temporal'] = False
            return False
        
        self.checks_passed['temporal'] = True
        return True
    
    def check_sufficient_data(self, df: pd.DataFrame, min_rows: int = 100) -> bool:
        """Check if there's sufficient data for analysis"""
        if len(df) < min_rows:
            self.issues.append(f"Insufficient data: {len(df)} rows (minimum: {min_rows})")
            self.checks_passed['sufficient_data'] = False
            return False
        
        self.checks_passed['sufficient_data'] = True
        return True
    
    def run_all_checks(self, df: pd.DataFrame, min_rows: int = 100) -> Tuple[bool, Dict, List[str]]:
        """
        Run all quality checks
        
        Args:
            df: DataFrame to check
            min_rows: Minimum number of rows required
        
        Returns:
            Tuple of (all_passed, checks_dict, issues_list)
        """
        self.checks_passed = {}
        self.issues = []
        
        # Run all checks
        self.check_schema(df)
        self.check_null_values(df)
        self.check_data_types(df)
        self.check_value_ranges(df)
        self.check_temporal_consistency(df)
        self.check_sufficient_data(df, min_rows)
        
        # Determine overall status
        all_passed = all(self.checks_passed.values())
        
        return all_passed, self.checks_passed, self.issues
    
    def generate_report(self, df: pd.DataFrame) -> str:
        """Generate a detailed quality report"""
        all_passed, checks, issues = self.run_all_checks(df)
        
        report = f"""
DATA QUALITY REPORT
==================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Dataset Shape: {df.shape}

CHECK RESULTS:
"""
        for check, passed in checks.items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            report += f"  {check.upper()}: {status}\n"
        
        if issues:
            report += f"\nISSUES FOUND ({len(issues)}):\n"
            for i, issue in enumerate(issues, 1):
                report += f"  {i}. {issue}\n"
        else:
            report += "\n✓ No issues found!\n"
        
        report += f"\nOVERALL STATUS: {'PASSED' if all_passed else 'FAILED'}\n"
        report += "=" * 50 + "\n"
        
        return report


def main():
    """Test the quality checker"""
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=200, freq='1H')
    df = pd.DataFrame({
        'open': np.random.uniform(100, 200, 200),
        'high': np.random.uniform(100, 200, 200),
        'low': np.random.uniform(100, 200, 200),
        'close': np.random.uniform(100, 200, 200),
        'volume': np.random.randint(1000000, 10000000, 200)
    }, index=dates)
    
    # Run quality checks
    checker = DataQualityChecker()
    report = checker.generate_report(df)
    print(report)


if __name__ == "__main__":
    main()
