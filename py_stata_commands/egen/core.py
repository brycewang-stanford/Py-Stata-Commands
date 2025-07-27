"""
Core implementation of PyEgen functions.

This module contains the main implementations of Stata's egen functions
adapted for pandas DataFrames.
"""

import numpy as np
import pandas as pd
from typing import Union, List, Optional, Any


def _validate_dataframe(df: pd.DataFrame) -> None:
    """Validate that input is a pandas DataFrame."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")


def _validate_series(series: pd.Series) -> None:
    """Validate that input is a pandas Series."""
    if not isinstance(series, pd.Series):
        raise TypeError("Input must be a pandas Series")


def _validate_columns(df: pd.DataFrame, columns: List[str]) -> None:
    """Validate that specified columns exist in DataFrame."""
    missing_cols = set(columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Columns not found in DataFrame: {missing_cols}")


# ============================================================================
# Basic Functions
# ============================================================================

def rank(series: pd.Series, method: str = 'average', ascending: bool = True) -> pd.Series:
    """
    Generate ranks for a pandas Series.
    
    Equivalent to Stata's: egen newvar = rank(var)
    
    Parameters:
    -----------
    series : pd.Series
        Input series to rank
    method : str, default 'average'
        How to rank tied values ('average', 'min', 'max', 'first', 'dense')
    ascending : bool, default True
        Whether to rank in ascending order
        
    Returns:
    --------
    pd.Series
        Ranked values
        
    Examples:
    ---------
    >>> import pandas as pd
    >>> import pyegen as egen
    >>> df = pd.DataFrame({'var': [10, 20, 30, 20, 40]})
    >>> df['rank_var'] = egen.rank(df['var'])
    """
    _validate_series(series)
    return series.rank(method=method, ascending=ascending)


def rowmean(df: pd.DataFrame, columns: List[str]) -> pd.Series:
    """
    Calculate row-wise mean across specified columns.
    
    Equivalent to Stata's: egen newvar = rowmean(var1-var3)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    columns : List[str]
        List of column names to calculate mean across
        
    Returns:
    --------
    pd.Series
        Row-wise means
        
    Examples:
    ---------
    >>> import pandas as pd
    >>> import pyegen as egen
    >>> df = pd.DataFrame({
    ...     'var1': [1, 2, 3],
    ...     'var2': [4, 5, 6],
    ...     'var3': [7, 8, 9]
    ... })
    >>> df['row_mean'] = egen.rowmean(df, ['var1', 'var2', 'var3'])
    """
    _validate_dataframe(df)
    _validate_columns(df, columns)
    return df[columns].mean(axis=1)


def rowtotal(df: pd.DataFrame, columns: List[str]) -> pd.Series:
    """
    Calculate row-wise sum across specified columns.
    
    Equivalent to Stata's: egen newvar = rowtotal(var1-var3)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    columns : List[str]
        List of column names to sum across
        
    Returns:
    --------
    pd.Series
        Row-wise sums
    """
    _validate_dataframe(df)
    _validate_columns(df, columns)
    return df[columns].sum(axis=1)


def rowmax(df: pd.DataFrame, columns: List[str]) -> pd.Series:
    """
    Calculate row-wise maximum across specified columns.
    
    Equivalent to Stata's: egen newvar = rowmax(var1-var3)
    """
    _validate_dataframe(df)
    _validate_columns(df, columns)
    return df[columns].max(axis=1)


def rowmin(df: pd.DataFrame, columns: List[str]) -> pd.Series:
    """
    Calculate row-wise minimum across specified columns.
    
    Equivalent to Stata's: egen newvar = rowmin(var1-var3)
    """
    _validate_dataframe(df)
    _validate_columns(df, columns)
    return df[columns].min(axis=1)


def rowcount(df: pd.DataFrame, columns: List[str]) -> pd.Series:
    """
    Count non-missing values across specified columns for each row.
    
    Equivalent to Stata's: egen newvar = rownonmiss(var1-var3)
    """
    _validate_dataframe(df)
    _validate_columns(df, columns)
    return df[columns].count(axis=1)


def rowsd(df: pd.DataFrame, columns: List[str]) -> pd.Series:
    """
    Calculate row-wise standard deviation across specified columns.
    
    Equivalent to Stata's: egen newvar = rowsd(var1-var3)
    """
    _validate_dataframe(df)
    _validate_columns(df, columns)
    return df[columns].std(axis=1)


# ============================================================================
# Grouping Functions
# ============================================================================

def tag(df: pd.DataFrame, columns: List[str]) -> pd.Series:
    """
    Tag the first occurrence in each group.
    
    Equivalent to Stata's: egen newvar = tag(group1 group2)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    columns : List[str]
        List of column names that define groups
        
    Returns:
    --------
    pd.Series
        Binary series (1 for first occurrence, 0 otherwise)
    """
    _validate_dataframe(df)
    _validate_columns(df, columns)
    
    # Create a copy to avoid modifying original
    temp_df = df[columns].copy()
    
    # Mark first occurrence of each combination
    is_first = ~temp_df.duplicated()
    
    return is_first.astype(int)


def count(series: pd.Series, by: Optional[pd.Series] = None) -> pd.Series:
    """
    Count non-missing observations, optionally by group.
    
    Equivalent to Stata's: egen newvar = count(var) [, by(group)]
    
    Parameters:
    -----------
    series : pd.Series
        Series to count
    by : pd.Series, optional
        Grouping variable
        
    Returns:
    --------
    pd.Series
        Count of non-missing observations (by group if specified)
    """
    _validate_series(series)
    
    if by is None:
        # Overall count
        total_count = series.count()
        return pd.Series([total_count] * len(series), index=series.index)
    else:
        # Group-wise count
        _validate_series(by)
        return series.groupby(by).transform('count')


def mean(series: pd.Series, by: Optional[pd.Series] = None) -> pd.Series:
    """
    Calculate mean, optionally by group.
    
    Equivalent to Stata's: egen newvar = mean(var) [, by(group)]
    """
    _validate_series(series)
    
    if by is None:
        overall_mean = series.mean()
        return pd.Series([overall_mean] * len(series), index=series.index)
    else:
        _validate_series(by)
        return series.groupby(by).transform('mean')


def sum(series: pd.Series, by: Optional[pd.Series] = None) -> pd.Series:
    """
    Calculate sum, optionally by group.
    
    Equivalent to Stata's: egen newvar = sum(var) [, by(group)]
    """
    _validate_series(series)
    
    if by is None:
        overall_sum = series.sum()
        return pd.Series([overall_sum] * len(series), index=series.index)
    else:
        _validate_series(by)
        return series.groupby(by).transform('sum')


def max(series: pd.Series, by: Optional[pd.Series] = None) -> pd.Series:
    """
    Calculate maximum, optionally by group.
    
    Equivalent to Stata's: egen newvar = max(var) [, by(group)]
    """
    _validate_series(series)
    
    if by is None:
        overall_max = series.max()
        return pd.Series([overall_max] * len(series), index=series.index)
    else:
        _validate_series(by)
        return series.groupby(by).transform('max')


def min(series: pd.Series, by: Optional[pd.Series] = None) -> pd.Series:
    """
    Calculate minimum, optionally by group.
    
    Equivalent to Stata's: egen newvar = min(var) [, by(group)]
    """
    _validate_series(series)
    
    if by is None:
        overall_min = series.min()
        return pd.Series([overall_min] * len(series), index=series.index)
    else:
        _validate_series(by)
        return series.groupby(by).transform('min')


def sd(series: pd.Series, by: Optional[pd.Series] = None) -> pd.Series:
    """
    Calculate standard deviation, optionally by group.
    
    Equivalent to Stata's: egen newvar = sd(var) [, by(group)]
    """
    _validate_series(series)
    
    if by is None:
        overall_sd = series.std()
        return pd.Series([overall_sd] * len(series), index=series.index)
    else:
        _validate_series(by)
        return series.groupby(by).transform('std')


# ============================================================================
# Advanced Functions
# ============================================================================

def seq() -> None:
    """
    Generate sequence numbers.
    
    Note: This function will be implemented in a future version.
    For now, use: pd.Series(range(1, len(df) + 1))
    """
    raise NotImplementedError("seq() function will be implemented in a future version")


def group(df: pd.DataFrame, columns: List[str]) -> pd.Series:
    """
    Create group identifiers.
    
    Equivalent to Stata's: egen newvar = group(var1 var2)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    columns : List[str]
        List of column names to group by
        
    Returns:
    --------
    pd.Series
        Group identifiers (integers starting from 1)
    """
    _validate_dataframe(df)
    _validate_columns(df, columns)
    
    # Create group identifiers
    grouped = df[columns].drop_duplicates().reset_index(drop=True)
    grouped['_group_id'] = range(1, len(grouped) + 1)
    
    # Merge back to original data
    result = df[columns].merge(grouped, on=columns, how='left')
    
    return result['_group_id']


def pc(series: pd.Series, by: Optional[pd.Series] = None) -> pd.Series:
    """
    Calculate percentile ranks.
    
    Equivalent to Stata's: egen newvar = pc(var) [, by(group)]
    """
    _validate_series(series)
    
    if by is None:
        return series.rank(pct=True) * 100
    else:
        _validate_series(by)
        return series.groupby(by).rank(pct=True) * 100


def iqr(series: pd.Series, by: Optional[pd.Series] = None) -> pd.Series:
    """
    Calculate interquartile range.
    
    Equivalent to Stata's: egen newvar = iqr(var) [, by(group)]
    """
    _validate_series(series)
    
    def _iqr(x):
        return x.quantile(0.75) - x.quantile(0.25)
    
    if by is None:
        overall_iqr = _iqr(series)
        return pd.Series([overall_iqr] * len(series), index=series.index)
    else:
        _validate_series(by)
        return series.groupby(by).transform(_iqr)
