"""
PDTab: Python implementation of Stata's tabulate command

This package provides comprehensive frequency analysis and cross-tabulation 
capabilities for pandas DataFrames, replicating Stata's tabulate functionality.
"""

from .core import (
    # Main tabulation functions
    tabulate,
    oneway,
    twoway,
    
    # Statistical test functions
    chi2_test,
    fisher_exact_test,
    cramers_v,
    
    # Result formatting
    TabulationResult,
)

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

__all__ = [
    # Main functions
    "tabulate",
    "oneway", 
    "twoway",
    
    # Statistical tests
    "chi2_test",
    "fisher_exact_test", 
    "cramers_v",
    
    # Result classes
    "TabulationResult",
    
    "__version__",
]
