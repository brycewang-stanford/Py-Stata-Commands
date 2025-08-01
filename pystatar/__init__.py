"""
PyStataR: Comprehensive Python package providing Stata-equivalent commands for pandas DataFrames

This package brings the familiar functionality of Stata's most essential data manipulation 
and statistical commands to Python, making the transition from Stata to Python seamless 
for researchers and data analysts.

Version: 0.2.0

This package serves as a unified interface to three mature PyPI packages:
- pyegen: Extended data generation functions (Stata's `egen`)
- pywinsor2: Data winsorizing and trimming (Stata's `winsor2`)  
- pdtab: Cross-tabulation and frequency analysis (Stata's `tabulate`)

Examples:
---------
>>> import pandas as pd
>>> from pystatar import pyegen, pywinsor2, pdtab

>>> # Cross-tabulation
>>> result = pdtab.tabulate(df, 'var1', 'var2')

>>> # Data generation
>>> df['rank_var'] = pyegen.rank(df['income'])

>>> # Winsorizing
>>> result = pywinsor2.winsor2(df, ['income'], cuts=(1, 99))

Direct access examples:
-----------------------
>>> from pystatar import rank, rowmean, winsor2, tabulate
"""

__version__ = "0.2.0"
__author__ = "Bryce Wang"
__email__ = "brycew6m@stanford.edu"
__license__ = "MIT"

# Import the original packages directly
try:
    import pyegen
    import pywinsor2
    import pdtab
except ImportError as e:
    raise ImportError(
        f"Missing required dependency: {e}. "
        "Please install with: pip install pyegen pywinsor2 pdtab"
    )

# For backward compatibility and convenience, provide direct access to key functions
from pyegen import (
    rank, rowmean, rowtotal, rowmax, rowmin, rowcount, rowsd,
    tag, count, mean, sum, max, min, sd, group, pc, iqr, pctile, 
    median, mode, std, seq, cut, diff, anycount, anymatch, anyvalue
)

from pywinsor2 import winsor2

from pdtab import tabulate, tab1, tab2, tabi

# Module-level exports for namespace access
__all__ = [
    # Module references
    'pyegen',
    'pywinsor2', 
    'pdtab',
    
    # Direct function access (convenience)
    # Egen functions
    'rank', 'rowmean', 'rowtotal', 'rowmax', 'rowmin', 'rowcount', 'rowsd',
    'tag', 'count', 'mean', 'sum', 'max', 'min', 'sd', 'group', 'pc', 'iqr',
    'pctile', 'median', 'mode', 'std', 'seq', 'cut', 'diff', 
    'anycount', 'anymatch', 'anyvalue',
    
    # PDTab functions
    'tabulate', 'tab1', 'tab2', 'tabi',
    
    # Winsor2 functions  
    'winsor2'
]

__version__ = "0.2.0"
__author__ = "Bryce Wang"
__email__ = "brycew6m@stanford.edu"
__license__ = "MIT"

# Module-level exports for namespace access
__all__ = [
    # Module references
    'pyegen',
    'pywinsor2', 
    'pdtab',
    
    # Direct function access (convenience)
    # Egen functions
    'rank', 'rowmean', 'rowtotal', 'rowmax', 'rowmin', 'rowcount', 'rowsd',
    'tag', 'count', 'mean', 'sum', 'max', 'min', 'sd', 'group', 'pc', 'iqr',
    'pctile', 'median', 'mode', 'std', 'seq', 'cut', 'diff', 
    'anycount', 'anymatch', 'anyvalue',
    
    # PDTab functions
    'tabulate', 'tab1', 'tab2', 'tabi',
    
    # Winsor2 functions  
    'winsor2'
]
