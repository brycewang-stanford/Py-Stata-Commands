"""
pandas-tabulate: Python implementation of Stata's tabulate command

This package provides comprehensive cross-tabulation and frequency analysis
tools for pandas DataFrames, with an API inspired by Stata's tabulate command.
"""

__version__ = "0.1.0"

from .core import tabulate, oneway, twoway
from .results import TabulationResult

__all__ = ["tabulate", "oneway", "twoway", "TabulationResult"]
