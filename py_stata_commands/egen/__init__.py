"""
PyEgen: Python implementation of Stata's egen command

This package provides Stata-style data manipulation functions for pandas DataFrames,
making it easier for researchers to transition from Stata to Python.
"""

from .core import (
    # Basic functions
    rank,
    rowmean,
    rowtotal,
    rowmax,
    rowmin,
    rowcount,
    rowsd,
    
    # Grouping functions
    tag,
    count,
    mean,
    sum,
    max,
    min,
    sd,
    
    # Advanced functions
    seq,
    group,
    pc,
    iqr,
)

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

__all__ = [
    # Basic functions
    "rank",
    "rowmean", 
    "rowtotal",
    "rowmax",
    "rowmin",
    "rowcount",
    "rowsd",
    
    # Grouping functions
    "tag",
    "count",
    "mean",
    "sum",
    "max",
    "min", 
    "sd",
    
    # Advanced functions
    "seq",
    "group",
    "pc",
    "iqr",
    
    "__version__",
]
