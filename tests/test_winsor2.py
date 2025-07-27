"""
Tests for pywinsor2 package.

This module contains comprehensive tests for the winsor2 functionality,
covering basic usage, edge cases, and error conditions.
"""

import numpy as np
import pandas as pd
import pytest

from pywinsor2 import winsor2
from pywinsor2.utils import compute_percentiles, validate_inputs


class TestWinsor2Basic:
    """Test basic winsor2 functionality."""

    def setup_method(self):
        """Set up test data."""
        # Create test data with outliers
        self.data = pd.DataFrame(
            {
                "wage": [1, 2, 3, 4, 5, 6, 7, 8, 9, 100],  # Clear outlier: 100
                "age": [20, 25, 30, 35, 40, 45, 50, 55, 60, 25],
                "industry": ["A", "A", "A", "A", "A", "B", "B", "B", "B", "B"],
            }
        )

        # Data with missing values
        self.data_missing = pd.DataFrame(
            {
                "wage": [1, 2, np.nan, 4, 5, 6, 7, 8, 9, 100],
                "age": [20, 25, 30, np.nan, 40, 45, 50, 55, 60, 25],
            }
        )

    def test_basic_winsorize(self):
        """Test basic winsorizing without options."""
        result = winsor2(self.data, "wage")

        # Check that new variable is created
        assert "wage_w" in result.columns

        # Check that outlier is winsorized
        # With 10 observations, 1st percentile ≈ 1.09, 99th percentile ≈ 9.91
        assert result["wage_w"].max() < 100  # Outlier should be reduced
        assert result["wage_w"].min() >= 1  # Should not go below minimum

    def test_basic_trim(self):
        """Test basic trimming."""
        result = winsor2(self.data, "wage", trim=True)

        # Check that new variable is created
        assert "wage_tr" in result.columns

        # Check that outliers are set to NaN
        # The extreme values should become NaN
        assert result["wage_tr"].isna().sum() > 0

    def test_custom_cuts(self):
        """Test custom percentile cuts."""
        result = winsor2(self.data, "wage", cuts=(10, 90))

        # With more aggressive cuts, more values should be affected
        winsorized_values = result["wage_w"]
        original_values = self.data["wage"]

        # Check that some values were changed
        assert not winsorized_values.equals(original_values)

    def test_multiple_variables(self):
        """Test processing multiple variables."""
        result = winsor2(self.data, ["wage", "age"])

        # Check that both new variables are created
        assert "wage_w" in result.columns
        assert "age_w" in result.columns

    def test_replace_option(self):
        """Test replace option."""
        data_copy = self.data.copy()
        result = winsor2(data_copy, "wage", replace=True)

        # Check that original variable is modified
        assert "wage_w" not in result.columns  # No new variable created
        assert not result["wage"].equals(self.data["wage"])  # Original modified

    def test_custom_suffix(self):
        """Test custom suffix."""
        result = winsor2(self.data, "wage", suffix="_clean")

        # Check that custom suffix is used
        assert "wage_clean" in result.columns
        assert "wage_w" not in result.columns

    def test_by_group(self):
        """Test group-wise processing."""
        result = winsor2(self.data, "wage", by="industry")

        # Check that new variable is created
        assert "wage_w" in result.columns

        # Group-wise winsorizing should handle groups separately
        # Values should be different from overall winsorizing
        overall_result = winsor2(self.data, "wage")
        assert not result["wage_w"].equals(overall_result["wage_w"])


class TestWinsor2EdgeCases:
    """Test edge cases and error conditions."""

    def test_missing_values(self):
        """Test handling of missing values."""
        data_missing = pd.DataFrame(
            {"wage": [1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 100]}
        )

        result = winsor2(data_missing, "wage")

        # Missing values should remain missing
        assert result["wage_w"].isna().sum() == data_missing["wage"].isna().sum()

    def test_all_missing_variable(self):
        """Test variable with all missing values."""
        data_all_missing = pd.DataFrame(
            {"wage": [np.nan] * 10, "age": [20, 25, 30, 35, 40, 45, 50, 55, 60, 25]}
        )

        # Should issue warning but not crash
        with pytest.warns(UserWarning):
            result = winsor2(data_all_missing, "wage")

        # All values should remain missing
        assert result["wage_w"].isna().all()

    def test_single_value(self):
        """Test with variable having single unique value."""
        data_single = pd.DataFrame({"wage": [5] * 10})

        result = winsor2(data_single, "wage")

        # All values should remain the same
        assert (result["wage_w"] == 5).all()

    def test_extreme_cuts(self):
        """Test extreme percentile cuts."""
        data = pd.DataFrame({"wage": range(100)})

        # Very narrow range
        result = winsor2(data, "wage", cuts=(45, 55))

        # Most values should be winsorized
        unique_values = result["wage_w"].nunique()
        assert unique_values < len(data)  # Should have fewer unique values


class TestInputValidation:
    """Test input validation."""

    def test_invalid_data_type(self):
        """Test invalid data type."""
        with pytest.raises(TypeError):
            winsor2("not a dataframe", "wage")

    def test_empty_dataframe(self):
        """Test empty DataFrame."""
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError):
            winsor2(empty_df, "wage")

    def test_nonexistent_variable(self):
        """Test nonexistent variable."""
        data = pd.DataFrame({"wage": [1, 2, 3, 4, 5]})
        with pytest.raises(ValueError):
            winsor2(data, "salary")  # Variable doesn't exist

    def test_invalid_cuts(self):
        """Test invalid cuts."""
        data = pd.DataFrame({"wage": [1, 2, 3, 4, 5]})

        # Cuts out of range
        with pytest.raises(ValueError):
            winsor2(data, "wage", cuts=(-1, 50))

        with pytest.raises(ValueError):
            winsor2(data, "wage", cuts=(50, 150))

        # No-op cuts
        with pytest.raises(ValueError):
            winsor2(data, "wage", cuts=(0, 100))

    def test_replace_with_suffix(self):
        """Test incompatible replace and suffix options."""
        data = pd.DataFrame({"wage": [1, 2, 3, 4, 5]})

        with pytest.raises(ValueError):
            winsor2(data, "wage", suffix="_test", replace=True)

    def test_existing_variable_conflict(self):
        """Test conflict with existing variable names."""
        data = pd.DataFrame(
            {"wage": [1, 2, 3, 4, 5], "wage_w": [1, 2, 3, 4, 5]}  # Already exists
        )

        with pytest.raises(ValueError):
            winsor2(data, "wage")  # Would create wage_w which already exists

    def test_invalid_by_variable(self):
        """Test invalid by variable."""
        data = pd.DataFrame({"wage": [1, 2, 3, 4, 5]})

        with pytest.raises(ValueError):
            winsor2(data, "wage", by="industry")  # Doesn't exist


class TestUtilityFunctions:
    """Test utility functions."""

    def test_validate_inputs(self):
        """Test input validation function."""
        data = pd.DataFrame({"wage": [1, 2, 3, 4, 5]})

        # Valid inputs
        result = validate_inputs(data, "wage", (1, 99), None, False, False, None)
        assert result[1] == ["wage"]  # varlist should be converted to list

    def test_compute_percentiles(self):
        """Test percentile computation."""
        series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        lower, upper = compute_percentiles(series, (10, 90))

        # Check that percentiles are reasonable
        assert lower < upper
        assert lower >= series.min()
        assert upper <= series.max()


class TestStataBehaviorCompatibility:
    """Test compatibility with Stata winsor2 behavior."""

    def test_cuts_order_independence(self):
        """Test that cuts(1 99) and cuts(99 1) give same result."""
        data = pd.DataFrame({"wage": [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]})

        result1 = winsor2(data, "wage", cuts=(1, 99))
        result2 = winsor2(data, "wage", cuts=(99, 1))

        # Results should be identical
        pd.testing.assert_series_equal(result1["wage_w"], result2["wage_w"])

    def test_fractional_percentiles(self):
        """Test fractional percentiles like 0.5, 99.5."""
        data = pd.DataFrame({"wage": range(1000)})  # Large dataset

        result = winsor2(data, "wage", cuts=(0.5, 99.5))

        # Should work without errors
        assert "wage_w" in result.columns

    def test_label_functionality(self):
        """Test label functionality."""
        data = pd.DataFrame({"wage": [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]})

        result = winsor2(data, "wage", label=True)

        # Should create labels (stored in _labels attribute)
        assert hasattr(result, "_labels")
        assert "wage_w" in result._labels
