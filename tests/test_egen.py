"""
Tests for PyEgen core functions.
"""

import pytest
import pandas as pd
import numpy as np
import pyegen as egen


class TestBasicFunctions:
    """Test basic PyEgen functions."""
    
    def setup_method(self):
        """Set up test data."""
        self.df = pd.DataFrame({
            'var1': [1, 2, 3, 4, 5],
            'var2': [10, 20, 30, 40, 50],
            'var3': [100, 200, 300, 400, 500],
            'group': ['A', 'A', 'B', 'B', 'C']
        })
    
    def test_rank(self):
        """Test rank function."""
        result = egen.rank(self.df['var1'])
        expected = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], name='var1')
        pd.testing.assert_series_equal(result, expected)
    
    def test_rowmean(self):
        """Test rowmean function."""
        result = egen.rowmean(self.df, ['var1', 'var2'])
        expected = pd.Series([5.5, 11.0, 16.5, 22.0, 27.5])
        pd.testing.assert_series_equal(result, expected)
    
    def test_rowtotal(self):
        """Test rowtotal function."""
        result = egen.rowtotal(self.df, ['var1', 'var2'])
        expected = pd.Series([11, 22, 33, 44, 55])
        pd.testing.assert_series_equal(result, expected)
    
    def test_rowmax(self):
        """Test rowmax function."""
        result = egen.rowmax(self.df, ['var1', 'var2'])
        expected = pd.Series([10, 20, 30, 40, 50])
        pd.testing.assert_series_equal(result, expected)
    
    def test_rowmin(self):
        """Test rowmin function."""
        result = egen.rowmin(self.df, ['var1', 'var2'])
        expected = pd.Series([1, 2, 3, 4, 5])
        pd.testing.assert_series_equal(result, expected)
    
    def test_rowcount(self):
        """Test rowcount function."""
        # Add some missing values
        df_with_missing = self.df.copy()
        df_with_missing.loc[0, 'var2'] = np.nan
        
        result = egen.rowcount(df_with_missing, ['var1', 'var2'])
        expected = pd.Series([1, 2, 2, 2, 2])
        pd.testing.assert_series_equal(result, expected)


class TestGroupingFunctions:
    """Test grouping functions."""
    
    def setup_method(self):
        """Set up test data."""
        self.df = pd.DataFrame({
            'value': [10, 20, 30, 40, 50, 60],
            'group': ['A', 'A', 'B', 'B', 'C', 'C'],
            'subgroup': [1, 2, 1, 2, 1, 2]
        })
    
    def test_tag(self):
        """Test tag function."""
        result = egen.tag(self.df, ['group'])
        expected = pd.Series([1, 0, 1, 0, 1, 0])
        pd.testing.assert_series_equal(result, expected)
    
    def test_count_by_group(self):
        """Test count function with grouping."""
        result = egen.count(self.df['value'], by=self.df['group'])
        expected = pd.Series([2, 2, 2, 2, 2, 2])
        pd.testing.assert_series_equal(result, expected)
    
    def test_mean_by_group(self):
        """Test mean function with grouping."""
        result = egen.mean(self.df['value'], by=self.df['group'])
        expected = pd.Series([15.0, 15.0, 35.0, 35.0, 55.0, 55.0])
        pd.testing.assert_series_equal(result, expected)
    
    def test_group_function(self):
        """Test group identifier function."""
        result = egen.group(self.df, ['group'])
        # Should create group IDs 1, 2, 3 for groups A, B, C
        expected = pd.Series([1, 1, 2, 2, 3, 3])
        pd.testing.assert_series_equal(result, expected)


class TestValidation:
    """Test input validation."""
    
    def test_invalid_dataframe(self):
        """Test error handling for invalid DataFrame input."""
        with pytest.raises(TypeError):
            egen.rowmean("not a dataframe", ['col1'])
    
    def test_invalid_series(self):
        """Test error handling for invalid Series input."""
        with pytest.raises(TypeError):
            egen.rank("not a series")
    
    def test_missing_columns(self):
        """Test error handling for missing columns."""
        df = pd.DataFrame({'col1': [1, 2, 3]})
        with pytest.raises(ValueError):
            egen.rowmean(df, ['col1', 'missing_col'])


class TestEdgeCases:
    """Test edge cases and missing values."""
    
    def test_all_missing_values(self):
        """Test behavior with all missing values."""
        df = pd.DataFrame({
            'var1': [np.nan, np.nan, np.nan],
            'var2': [np.nan, np.nan, np.nan]
        })
        
        result = egen.rowmean(df, ['var1', 'var2'])
        assert result.isna().all()
    
    def test_empty_dataframe(self):
        """Test behavior with empty DataFrame."""
        df = pd.DataFrame()
        with pytest.raises(ValueError):
            egen.rowmean(df, ['col1'])
    
    def test_single_row(self):
        """Test behavior with single row."""
        df = pd.DataFrame({'var1': [1], 'var2': [2]})
        result = egen.rowmean(df, ['var1', 'var2'])
        expected = pd.Series([1.5])
        pd.testing.assert_series_equal(result, expected)
