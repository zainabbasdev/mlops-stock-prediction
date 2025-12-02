"""
Unit tests for data quality check module
"""

import pytest
import pandas as pd
import numpy as np
from src.data.quality_check import DataQualityChecker


def create_sample_data(with_issues=False):
    """Helper to create sample data"""
    dates = pd.date_range('2024-01-01', periods=200, freq='1H')
    df = pd.DataFrame({
        'open': np.random.uniform(100, 200, 200),
        'high': np.random.uniform(100, 200, 200),
        'low': np.random.uniform(100, 200, 200),
        'close': np.random.uniform(100, 200, 200),
        'volume': np.random.randint(1000000, 10000000, 200)
    }, index=dates)
    
    if with_issues:
        # Introduce issues
        df.loc[df.index[0], 'close'] = np.nan  # Null value
        df.loc[df.index[1], 'close'] = -100    # Negative value
        df.loc[df.index[2], 'high'] = 50       # High < Low
        df.loc[df.index[2], 'low'] = 150
    
    return df


def test_check_schema_pass():
    """Test schema check passes with valid data"""
    df = create_sample_data()
    checker = DataQualityChecker()
    
    assert checker.check_schema(df) is True
    assert checker.checks_passed['schema'] is True


def test_check_schema_fail():
    """Test schema check fails with missing columns"""
    df = pd.DataFrame({'price': [100, 101]})
    checker = DataQualityChecker()
    
    assert checker.check_schema(df) is False
    assert len(checker.issues) > 0


def test_check_null_values_pass():
    """Test null value check passes"""
    df = create_sample_data()
    checker = DataQualityChecker(null_threshold=0.01)
    
    assert checker.check_null_values(df) is True


def test_check_null_values_fail():
    """Test null value check fails with too many nulls"""
    df = create_sample_data()
    df.loc[df.index[:50], 'close'] = np.nan  # 25% nulls
    
    checker = DataQualityChecker(null_threshold=0.01)
    assert checker.check_null_values(df) is False


def test_check_value_ranges():
    """Test value range validation"""
    df = create_sample_data(with_issues=True)
    checker = DataQualityChecker()
    
    result = checker.check_value_ranges(df)
    assert result is False
    assert len(checker.issues) > 0


def test_check_temporal_consistency():
    """Test temporal consistency check"""
    df = create_sample_data()
    checker = DataQualityChecker()
    
    assert checker.check_temporal_consistency(df) is True


def test_run_all_checks():
    """Test running all checks"""
    df = create_sample_data()
    checker = DataQualityChecker()
    
    all_passed, checks, issues = checker.run_all_checks(df)
    
    assert all_passed is True
    assert len(checks) > 0
    assert len(issues) == 0


def test_generate_report():
    """Test report generation"""
    df = create_sample_data()
    checker = DataQualityChecker()
    
    report = checker.generate_report(df)
    
    assert "DATA QUALITY REPORT" in report
    assert "PASSED" in report or "FAILED" in report
