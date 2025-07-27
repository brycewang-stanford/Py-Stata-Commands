"""
PyRegHDFE: Python implementation of Stata's reghdfe for high-dimensional fixed effects regression.

This package provides efficient estimation of linear models with multiple high-dimensional fixed effects,
using the pyhdfe library for fixed effect absorption and providing robust and cluster-robust standard errors.
"""

from .api import reghdfe
from .results import RegressionResults

__version__ = "0.1.1"
__all__ = ["reghdfe", "RegressionResults", "__version__"]