"""
Tests for pdtab module
"""

import pytest
import pandas as pd
import numpy as np
from pystatar.pdtab import tabulate, oneway, twoway, TabulationResult


class TestPDTab:
    """Test suite for PDTab functionality"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        np.random.seed(42)
        return pd.DataFrame({
            'gender': ['Male', 'Female'] * 50,
            'education': ['High School', 'College', 'Graduate'] * 33 + ['High School'],
            'income_level': ['Low', 'Medium', 'High'] * 33 + ['Low'],
            'age': np.random.randint(18, 65, 100)
        })
    
    def test_oneway_basic(self, sample_data):
        """Test basic one-way tabulation"""
        result = oneway(sample_data, 'gender')
        
        assert isinstance(result, TabulationResult)
        assert result.test_type == 'oneway'
        assert 'Freq' in result.table.columns
        assert 'Percent' in result.table.columns
        assert 'Cum' in result.table.columns
        
        # Check frequencies
        assert result.table.loc['Male', 'Freq'] == 50
        assert result.table.loc['Female', 'Freq'] == 50
        
        # Check percentages
        assert abs(result.table.loc['Male', 'Percent'] - 50.0) < 0.01
        assert abs(result.table.loc['Female', 'Percent'] - 50.0) < 0.01
    
    def test_twoway_basic(self, sample_data):
        """Test basic two-way tabulation"""
        result = twoway(sample_data, 'gender', 'education')
        
        assert isinstance(result, TabulationResult)
        assert result.test_type == 'twoway'
        assert 'chi2' in result.stats_results
        
        # Check that margins are included
        assert 'All' in result.table.index
        assert 'All' in result.table.columns
    
    def test_tabulate_dispatch(self, sample_data):
        """Test main tabulate function dispatching"""
        # One-way
        result1 = tabulate(sample_data, 'gender')
        assert result1.test_type == 'oneway'
        
        # Two-way
        result2 = tabulate(sample_data, 'gender', 'education')
        assert result2.test_type == 'twoway'
        
        # Invalid number of arguments
        with pytest.raises(ValueError):
            tabulate(sample_data, 'gender', 'education', 'income_level')
    
    def test_missing_values(self):
        """Test handling of missing values"""
        data_with_missing = pd.DataFrame({
            'var1': ['A', 'B', None, 'A', 'B'],
            'var2': ['X', 'Y', 'X', None, 'Y']
        })
        
        # Without missing values
        result1 = oneway(data_with_missing, 'var1', missing=False)
        assert len(result1.table) == 2  # Only A and B
        
        # With missing values
        result2 = oneway(data_with_missing, 'var1', missing=True)
        assert len(result2.table) == 3  # A, B, and NaN
    
    def test_statistical_tests(self, sample_data):
        """Test statistical tests in two-way tabulation"""
        result = twoway(sample_data, 'gender', 'education', 
                       chi2=True, exact=False, all_stats=False)
        
        assert 'chi2' in result.stats_results
        chi2_result = result.stats_results['chi2']
        assert 'statistic' in chi2_result
        assert 'p_value' in chi2_result
        assert 'df' in chi2_result
        assert 'significant' in chi2_result
    
    def test_result_methods(self, sample_data):
        """Test TabulationResult methods"""
        result = oneway(sample_data, 'gender')
        
        # Test string representation
        str_repr = str(result)
        assert 'One-way frequency table' in str_repr
        
        # Test summary
        summary = result.summary()
        assert 'table_shape' in summary
        assert 'total_observations' in summary
        
        # Test CSV export (mock)
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            result.to_csv(tmp.name)
            assert os.path.exists(tmp.name)
            os.unlink(tmp.name)


if __name__ == "__main__":
    pytest.main([__file__])
