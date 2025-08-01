"""
pywinsor2: Python implementation of Stata's winsor2 command

This module provides tools for winsorizing and trimming data,
equivalent to Stata's winsor2 command functionality.
Part of the PyStataR package.
"""

__version__ = "0.1.0"
__author__ = "Bryce Wang"
__email__ = "brycew6m@stanford.edu"

from .core import winsor2
from .utils import compute_percentiles, validate_inputs

__all__ = [
    "winsor2",
    "validate_inputs",
    "compute_percentiles",
]
