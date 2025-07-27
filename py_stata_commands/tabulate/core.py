"""
Core tabulation functions for pandas-tabulate.

This module implements the main tabulation functionality, including one-way
and two-way frequency tables with statistical tests.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Union, Optional, Dict, Any
import warnings

from .results import TabulationResult
from .stats import StatisticalTests


def _validate_input(var: pd.Series, name: str = "variable") -> pd.Series:
    """Validate input variable."""
    if not isinstance(var, pd.Series):
        if hasattr(var, '__iter__') and not isinstance(var, str):
            var = pd.Series(var)
        else:
            raise TypeError(f"{name} must be a pandas Series or array-like")
    
    return var


def _handle_missing(var1: pd.Series, var2: Optional[pd.Series] = None, 
                   missing: bool = False) -> tuple:
    """Handle missing values in variables."""
    if missing:
        # Include missing values by replacing NaN with a special category
        var1 = var1.fillna('__MISSING__')
        if var2 is not None:
            var2 = var2.fillna('__MISSING__')
    else:
        # Exclude missing values
        if var2 is not None:
            mask = var1.notna() & var2.notna()
            var1 = var1[mask]
            var2 = var2[mask]
        else:
            var1 = var1.dropna()
    
    return (var1, var2) if var2 is not None else (var1,)


def oneway(variable: Union[pd.Series, list, np.ndarray],
          percent: bool = False,
          cumulative: bool = False,
          missing: bool = False,
          sort_values: bool = True) -> TabulationResult:
    """
    Generate one-way frequency table.
    
    Equivalent to Stata's: tabulate var1
    
    Parameters:
    -----------
    variable : pd.Series, list, or array-like
        Variable to tabulate
    percent : bool, default False
        Show percentages
    cumulative : bool, default False
        Show cumulative frequencies and percentages
    missing : bool, default False
        Include missing values in tabulation
    sort_values : bool, default True
        Sort output by variable values
        
    Returns:
    --------
    TabulationResult
        Object containing frequency table and statistics
    """
    # Validate and prepare input
    var = _validate_input(variable, "variable")
    var, = _handle_missing(var, missing=missing)
    
    # Create frequency table
    freq_table = var.value_counts(sort=sort_values)
    
    # Calculate percentages
    total = len(var)
    pct_table = (freq_table / total * 100).round(2)
    
    # Create result dictionary
    result_data = {
        'frequencies': freq_table,
        'total': total
    }
    
    if percent:
        result_data['percentages'] = pct_table
    
    if cumulative:
        cum_freq = freq_table.cumsum()
        cum_pct = (cum_freq / total * 100).round(2)
        result_data['cumulative_freq'] = cum_freq
        result_data['cumulative_pct'] = cum_pct
    
    return TabulationResult(
        table_type="oneway",
        data=result_data,
        options={'percent': percent, 'cumulative': cumulative, 'missing': missing}
    )


def twoway(var1: Union[pd.Series, list, np.ndarray],
          var2: Union[pd.Series, list, np.ndarray],
          row_percent: bool = False,
          col_percent: bool = False,
          cell_percent: bool = False,
          chi2: bool = False,
          exact: bool = False,
          cramers_v: bool = False,
          missing: bool = False) -> TabulationResult:
    """
    Generate two-way cross-tabulation table.
    
    Equivalent to Stata's: tabulate var1 var2
    
    Parameters:
    -----------
    var1 : pd.Series, list, or array-like
        Row variable
    var2 : pd.Series, list, or array-like
        Column variable
    row_percent : bool, default False
        Show row percentages
    col_percent : bool, default False
        Show column percentages
    cell_percent : bool, default False
        Show cell percentages (of total)
    chi2 : bool, default False
        Perform chi-square test of independence
    exact : bool, default False
        Perform Fisher exact test
    cramers_v : bool, default False
        Calculate Cramér's V measure of association
    missing : bool, default False
        Include missing values in tabulation
        
    Returns:
    --------
    TabulationResult
        Object containing cross-tabulation table and statistics
    """
    # Validate and prepare inputs
    var1 = _validate_input(var1, "var1")
    var2 = _validate_input(var2, "var2")
    
    # Check lengths match
    if len(var1) != len(var2):
        raise ValueError("Variables must have the same length")
    
    var1, var2 = _handle_missing(var1, var2, missing=missing)
    
    # Create cross-tabulation
    crosstab = pd.crosstab(var1, var2, margins=True)
    
    # Store the core table without margins for statistics
    core_table = crosstab.iloc[:-1, :-1]
    
    result_data = {
        'crosstab': crosstab,
        'core_table': core_table
    }
    
    # Calculate percentages if requested
    total = core_table.sum().sum()
    
    if row_percent:
        row_totals = core_table.sum(axis=1)
        row_pct = core_table.div(row_totals, axis=0) * 100
        result_data['row_percentages'] = row_pct.round(2)
    
    if col_percent:
        col_totals = core_table.sum(axis=0)
        col_pct = core_table.div(col_totals, axis=1) * 100
        result_data['col_percentages'] = col_pct.round(2)
    
    if cell_percent:
        cell_pct = (core_table / total * 100).round(2)
        result_data['cell_percentages'] = cell_pct
    
    # Perform statistical tests
    stats_results = {}
    test_calculator = StatisticalTests()
    
    if chi2:
        chi2_result = test_calculator.chi_square_test(core_table)
        stats_results['chi2'] = chi2_result
    
    if exact:
        exact_result = test_calculator.fisher_exact_test(core_table)
        stats_results['exact'] = exact_result
    
    if cramers_v:
        cramers_result = test_calculator.cramers_v(core_table)
        stats_results['cramers_v'] = cramers_result
    
    if stats_results:
        result_data['statistics'] = stats_results
    
    return TabulationResult(
        table_type="twoway",
        data=result_data,
        options={
            'row_percent': row_percent,
            'col_percent': col_percent, 
            'cell_percent': cell_percent,
            'chi2': chi2,
            'exact': exact,
            'cramers_v': cramers_v,
            'missing': missing
        }
    )


def tabulate(var1: Union[pd.Series, list, np.ndarray],
            var2: Optional[Union[pd.Series, list, np.ndarray]] = None,
            **kwargs) -> TabulationResult:
    """
    Main tabulation function - automatically detects one-way or two-way.
    
    This is the main entry point that mimics Stata's tabulate command.
    
    Parameters:
    -----------
    var1 : pd.Series, list, or array-like
        First variable (or only variable for one-way)
    var2 : pd.Series, list, or array-like, optional
        Second variable for cross-tabulation
    **kwargs : dict
        Additional options passed to oneway() or twoway()
        
    Returns:
    --------
    TabulationResult
        Object containing tabulation results and statistics
        
    Examples:
    ---------
    >>> # One-way tabulation
    >>> result = tabulate(df['gender'])
    
    >>> # Two-way tabulation with chi-square test
    >>> result = tabulate(df['gender'], df['education'], chi2=True)
    """
    if var2 is None:
        return oneway(var1, **kwargs)
    else:
        return twoway(var1, var2, **kwargs)
