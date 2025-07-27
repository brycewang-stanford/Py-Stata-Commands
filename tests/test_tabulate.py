"""
Test cases for pandas-tabulate core functionality.
"""

import pytest
import pandas as pd
import numpy as np
import pandas_tabulate as ptab


class TestOnewayTabulation:
    """Test one-way tabulation functionality."""
    
    def setup_method(self):
        """Set up test data."""
        self.simple_data = pd.Series(['A', 'B', 'A', 'C', 'B', 'A', 'C', 'A'])
        self.missing_data = pd.Series(['A', 'B', np.nan, 'A', 'C', np.nan, 'B'])
    
    def test_basic_oneway(self):
        """Test basic one-way tabulation."""
        result = ptab.oneway(self.simple_data)
        
        assert result.table_type == "oneway"
        assert len(result.data['frequencies']) == 3
        assert result.data['total'] == 8
        
        # Check frequencies
        freq = result.data['frequencies']
        assert freq['A'] == 4
        assert freq['B'] == 2
        assert freq['C'] == 2
    
    def test_oneway_with_percentages(self):
        """Test one-way tabulation with percentages."""
        result = ptab.oneway(self.simple_data, percent=True)
        
        assert 'percentages' in result.data
        pct = result.data['percentages']
        assert pct['A'] == 50.0  # 4/8 * 100
        assert pct['B'] == 25.0  # 2/8 * 100
    
    def test_oneway_with_cumulative(self):
        """Test one-way tabulation with cumulative statistics."""
        result = ptab.oneway(self.simple_data, cumulative=True)
        
        assert 'cumulative_freq' in result.data
        assert 'cumulative_pct' in result.data
    
    def test_oneway_missing_exclude(self):
        """Test one-way tabulation excluding missing values."""
        result = ptab.oneway(self.missing_data, missing=False)
        
        assert result.data['total'] == 5  # Excludes 2 NaN values
        assert '__MISSING__' not in result.data['frequencies'].index
    
    def test_oneway_missing_include(self):
        """Test one-way tabulation including missing values."""
        result = ptab.oneway(self.missing_data, missing=True)
        
        assert result.data['total'] == 7  # Includes all values
        assert '__MISSING__' in result.data['frequencies'].index
        assert result.data['frequencies']['__MISSING__'] == 2


class TestTwowayTabulation:
    """Test two-way tabulation functionality."""
    
    def setup_method(self):
        """Set up test data."""
        self.var1 = pd.Series(['M', 'F', 'M', 'F', 'M', 'F'])
        self.var2 = pd.Series(['A', 'B', 'A', 'A', 'B', 'B'])
        
        # Data with missing values
        self.var1_missing = pd.Series(['M', 'F', np.nan, 'M', 'F'])
        self.var2_missing = pd.Series(['A', np.nan, 'B', 'A', 'B'])
    
    def test_basic_twoway(self):
        """Test basic two-way tabulation."""
        result = ptab.twoway(self.var1, self.var2)
        
        assert result.table_type == "twoway"
        assert 'crosstab' in result.data
        assert 'core_table' in result.data
        
        # Check dimensions
        core_table = result.data['core_table']
        assert core_table.shape == (2, 2)  # 2 genders x 2 categories
    
    def test_twoway_percentages(self):
        """Test two-way tabulation with percentages."""
        result = ptab.twoway(self.var1, self.var2, 
                           row_percent=True, 
                           col_percent=True, 
                           cell_percent=True)
        
        assert 'row_percentages' in result.data
        assert 'col_percentages' in result.data
        assert 'cell_percentages' in result.data
    
    def test_twoway_chi_square(self):
        """Test two-way tabulation with chi-square test."""
        result = ptab.twoway(self.var1, self.var2, chi2=True)
        
        assert 'statistics' in result.data
        assert 'chi2' in result.data['statistics']
        
        chi2_result = result.data['statistics']['chi2']
        assert 'statistic' in chi2_result
        assert 'p_value' in chi2_result
        assert 'df' in chi2_result
    
    def test_twoway_fisher_exact(self):
        """Test two-way tabulation with Fisher exact test."""
        result = ptab.twoway(self.var1, self.var2, exact=True)
        
        assert 'statistics' in result.data
        assert 'exact' in result.data['statistics']
        
        exact_result = result.data['statistics']['exact']
        assert 'p_value' in exact_result
        assert 'odds_ratio' in exact_result
    
    def test_twoway_cramers_v(self):
        """Test two-way tabulation with Cramér's V."""
        result = ptab.twoway(self.var1, self.var2, cramers_v=True)
        
        assert 'statistics' in result.data
        assert 'cramers_v' in result.data['statistics']
        
        cramers_result = result.data['statistics']['cramers_v']
        assert 'value' in cramers_result
        assert 'interpretation' in cramers_result
    
    def test_twoway_missing_values(self):
        """Test two-way tabulation with missing values."""
        # Exclude missing
        result_exclude = ptab.twoway(self.var1_missing, self.var2_missing, 
                                   missing=False)
        
        # Only complete pairs should be included
        assert result_exclude.data['core_table'].sum().sum() < 5
        
        # Include missing
        result_include = ptab.twoway(self.var1_missing, self.var2_missing, 
                                   missing=True)
        
        assert result_include.data['core_table'].sum().sum() == 5


class TestMainTabulate:
    """Test main tabulate function."""
    
    def setup_method(self):
        """Set up test data."""
        self.var1 = pd.Series(['A', 'B', 'A', 'C'])
        self.var2 = pd.Series(['X', 'Y', 'X', 'Y'])
    
    def test_tabulate_oneway(self):
        """Test main tabulate function for one-way."""
        result = ptab.tabulate(self.var1)
        
        assert result.table_type == "oneway"
        assert len(result.data['frequencies']) == 3
    
    def test_tabulate_twoway(self):
        """Test main tabulate function for two-way."""
        result = ptab.tabulate(self.var1, self.var2)
        
        assert result.table_type == "twoway"
        assert 'crosstab' in result.data


class TestResultsDisplay:
    """Test results display functionality."""
    
    def test_oneway_display(self):
        """Test one-way results display."""
        var = pd.Series(['A', 'B', 'A', 'B', 'C'])
        result = ptab.oneway(var, percent=True)
        
        display_str = result.display()
        assert "One-way Tabulation" in display_str
        assert "Freq." in display_str
        assert "Percent" in display_str
    
    def test_twoway_display(self):
        """Test two-way results display."""
        var1 = pd.Series(['M', 'F', 'M', 'F'])
        var2 = pd.Series(['A', 'B', 'A', 'B'])
        result = ptab.twoway(var1, var2, chi2=True)
        
        display_str = result.display()
        assert "Two-way Tabulation" in display_str
        assert "Frequencies:" in display_str
        assert "Chi-square test:" in display_str


class TestInputValidation:
    """Test input validation."""
    
    def test_invalid_input_type(self):
        """Test error handling for invalid input types."""
        with pytest.raises(TypeError):
            ptab.oneway("not_a_series")
    
    def test_mismatched_lengths(self):
        """Test error handling for mismatched variable lengths."""
        var1 = pd.Series(['A', 'B'])
        var2 = pd.Series(['X', 'Y', 'Z'])
        
        with pytest.raises(ValueError):
            ptab.twoway(var1, var2)
    
    def test_array_like_input(self):
        """Test that array-like inputs are converted to Series."""
        list_input = ['A', 'B', 'A', 'C']
        result = ptab.oneway(list_input)
        
        assert result.table_type == "oneway"
        assert result.data['total'] == 4
