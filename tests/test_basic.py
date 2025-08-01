"""
Basic tests for PyStataR functionality.
"""

import pytest
import numpy as np
import pandas as pd
import pystatar


class TestBasicFunctionality:
    """Test basic package functionality."""
    
    def test_import(self):
        """Test that package imports correctly."""
        assert hasattr(pystatar, 'pyegen')
        assert hasattr(pystatar, 'pywinsor2')
        assert hasattr(pystatar, 'pdtab')
        assert pystatar.__version__ == "0.3.1"
        
    def test_module_imports(self):
        """Test that individual modules import correctly."""
        from pystatar import pyegen, pywinsor2, pdtab
        
        # Test pyegen functions
        assert hasattr(pyegen, 'rank')
        assert hasattr(pyegen, 'rowmean')
        
        # Test pywinsor2 functions  
        assert hasattr(pywinsor2, 'winsor2')
        
        # Test pdtab functions
        assert hasattr(pdtab, 'tabulate')
        assert hasattr(pdtab, 'tab1')
        assert hasattr(pdtab, 'tab2')
    
    def test_direct_function_access(self):
        """Test direct function access."""
        from pystatar import rank, rowmean, winsor2, tabulate
        
        assert callable(rank)
        assert callable(rowmean)
        assert callable(winsor2)
        assert callable(tabulate)
    
    def test_basic_functionality(self):
        """Test basic functionality of main functions."""
        # Create test data
        np.random.seed(42)
        data = pd.DataFrame({
            'value': [1, 2, 3, 4, 5, 100],  # with outlier
            'group': ['A', 'A', 'B', 'B', 'A', 'B'],
            'category': ['X', 'Y', 'X', 'Y', 'X', 'Y']
        })
        
        # Test pyegen rank function
        from pystatar import rank
        ranked = rank(data['value'])
        assert len(ranked) == len(data)
        
        # Test pdtab tabulate function
        from pystatar import tabulate
        result = tabulate(data, 'group', 'category')
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__])