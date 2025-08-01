"""
PyStataR: Comprehensive Python package providing Stata-equivalent commands for pandas DataFrames

This package brings the familiar functionality of Stata's most essential data manipulation 
and statistical commands to Python, making the transition from Stata to Python seamless 
for researchers and data analysts.

Modules:
--------
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
>>> from pystatar.pyegen import rank, rowmean
>>> from pystatar.pdtab import tabulate
>>> from pystatar.pywinsor2 import winsor2
"""

__version__ = "0.1.0"
__author__ = "Bryce Wang"
__email__ = "brycew6m@stanford.edu"
__license__ = "MIT"

# Import modules using namespace package pattern
from . import egen as pyegen
from . import winsor2 as pywinsor2
from . import pdtab
from . import utils

# Import key functions for direct access (optional convenience)
from .egen import (
    rank, rowmean, rowtotal, rowmax, rowmin, rowcount, rowsd,
    tag, count, mean, sum, max, min, sd, seq, group, pc, iqr
)
from .pdtab import tabulate, oneway, twoway
from .winsor2 import winsor2

__all__ = [
    # Main modules (recommended usage)
    'pyegen',
    'pywinsor2', 
    'pdtab',
    'utils',
    
    # Direct function access (convenience)
    # Egen functions
    'rank',
    'rowmean',
    'rowtotal',
    'rowmax',
    'rowmin',
    'rowcount',
    'rowsd',
    'tag',
    'count',
    'mean',
    'sum',
    'max',
    'min',
    'sd',
    'seq',
    'group',
    'pc',
    'iqr',
    
    # PDTab functions
    'tabulate',
    'oneway',
    'twoway',
    
    # Winsor2 functions  
    'winsor2'
]
