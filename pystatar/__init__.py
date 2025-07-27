"""
PyStataR: Comprehensive Python package providing Stata-equivalent commands for pandas DataFrames

This package brings the familiar functionality of Stata's most essential data manipulation 
and statistical commands to Python, making the transition from Stata to Python seamless 
for researchers and data analysts.

Modules:
--------
- tabulate: Cross-tabulation and frequency analysis (Stata's `tabulate`)
- egen: Extended data generation functions (Stata's `egen`)  
- reghdfe: High-dimensional fixed effects regression (Stata's `reghdfe`)
- winsor2: Data winsorizing and trimming (Stata's `winsor2`)

Examples:
---------
>>> import pandas as pd
>>> from pystatar import tabulate, egen, reghdfe, winsor2

>>> # Cross-tabulation
>>> result = tabulate.tabulate(df['var1'], df['var2'])

>>> # Data generation
>>> df['rank_var'] = egen.rank(df['income'])

>>> # Fixed effects regression
>>> result = reghdfe.reghdfe(df, 'wage', ['experience'], absorb=['firm_id'])

>>> # Winsorizing
>>> result = winsor2.winsor2(df, ['income'], cuts=(1, 99))
"""

__version__ = "0.1.0"
__author__ = "Bryce Wang"
__email__ = "brycew6m@stanford.edu"
__license__ = "MIT"

# Import main modules for convenient access
from . import tabulate as tabulate_module
from . import egen as egen_module
from . import reghdfe as reghdfe_module
from . import winsor2 as winsor2_module
from . import utils

# Import key functions for direct access
from .tabulate import tabulate, oneway, twoway
from .egen import (
    rank, rowmean, rowtotal, rowmax, rowmin, rowcount, rowsd,
    tag, count, mean, sum, max, min, sd, seq, group, pc, iqr
)
from .reghdfe import reghdfe
from .winsor2 import winsor2

__all__ = [
    # Modules
    'tabulate_module',
    'egen_module', 
    'reghdfe_module',
    'winsor2_module',
    'utils',
    # Tabulate functions
    'tabulate',
    'oneway',
    'twoway',
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
    # Reghdfe functions
    'reghdfe',
    # Winsor2 functions
    'winsor2'
]
