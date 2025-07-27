"""
Common utilities shared across all PyStataR modules.

This module provides shared functionality used by tabulate, egen, reghdfe, and winsor2.
"""

import pandas as pd
import numpy as np
from typing import Union, List, Optional, Any, Tuple


def validate_dataframe(df: pd.DataFrame, name: str = "DataFrame") -> None:
    """
    Validate that input is a pandas DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to validate
    name : str, default "DataFrame"
        Name to use in error message
        
    Raises
    ------
    TypeError
        If df is not a pandas DataFrame
    ValueError
        If df is empty
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"{name} must be a pandas DataFrame, got {type(df)}")
    
    if df.empty:
        raise ValueError(f"{name} cannot be empty")


def validate_columns(df: pd.DataFrame, columns: Union[str, List[str]], 
                    name: str = "columns") -> List[str]:
    """
    Validate that columns exist in DataFrame and return as list.
    
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to check
    columns : str or list of str
        Column name(s) to validate
    name : str, default "columns"
        Name to use in error message
        
    Returns
    -------
    list of str
        List of validated column names
        
    Raises
    ------
    ValueError
        If any column is not found in DataFrame
    """
    if isinstance(columns, str):
        columns = [columns]
    
    missing_cols = [col for col in columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"{name} {missing_cols} not found in DataFrame. "
                        f"Available columns: {list(df.columns)}")
    
    return columns


def handle_missing_values(series: pd.Series, method: str = "exclude") -> pd.Series:
    """
    Handle missing values in a pandas Series.
    
    Parameters
    ----------
    series : pd.Series
        Input series
    method : str, default "exclude"
        Method for handling missing values:
        - "exclude": Remove missing values
        - "include": Keep missing values as a separate category
        
    Returns
    -------
    pd.Series
        Series with missing values handled according to method
    """
    if method == "exclude":
        return series.dropna()
    elif method == "include":
        return series.fillna("Missing")
    else:
        raise ValueError(f"Unknown method '{method}'. Use 'exclude' or 'include'.")


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a proportion as a percentage string.
    
    Parameters
    ----------
    value : float
        Proportion to format (between 0 and 1)
    decimals : int, default 2
        Number of decimal places
        
    Returns
    -------
    str
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def safe_divide(numerator: Union[int, float, np.ndarray], 
                denominator: Union[int, float, np.ndarray],
                fill_value: float = np.nan) -> Union[float, np.ndarray]:
    """
    Safely divide two numbers/arrays, handling division by zero.
    
    Parameters
    ----------
    numerator : int, float, or np.ndarray
        Numerator value(s)
    denominator : int, float, or np.ndarray  
        Denominator value(s)
    fill_value : float, default np.nan
        Value to use when denominator is zero
        
    Returns
    -------
    float or np.ndarray
        Result of division, with fill_value where denominator is zero
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        result = numerator / denominator
        if np.isscalar(result):
            return fill_value if denominator == 0 else result
        else:
            result[denominator == 0] = fill_value
            return result


def get_group_indices(df: pd.DataFrame, by: Union[str, List[str]]) -> pd.Series:
    """
    Get group indices for groupby operations.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    by : str or list of str
        Column name(s) to group by
        
    Returns
    -------
    pd.Series
        Series with group indices
    """
    if isinstance(by, str):
        by = [by]
    
    validate_columns(df, by, "groupby columns")
    
    # Create group indices
    grouped = df.groupby(by, sort=False)
    group_indices = pd.Series(range(len(grouped)), index=grouped.indices.keys())
    
    # Map back to original DataFrame index
    group_map = {}
    for i, (name, group) in enumerate(grouped):
        for idx in group.index:
            group_map[idx] = i
    
    return pd.Series([group_map[idx] for idx in df.index], index=df.index)


def stata_summary_stats(series: pd.Series, weights: Optional[pd.Series] = None) -> dict:
    """
    Calculate summary statistics in Stata style.
    
    Parameters
    ----------
    series : pd.Series
        Data series
    weights : pd.Series, optional
        Weights for weighted statistics
        
    Returns
    -------
    dict
        Dictionary with summary statistics
    """
    clean_series = series.dropna()
    
    if weights is not None:
        weights = weights.loc[clean_series.index]
        # Weighted statistics
        mean_val = np.average(clean_series, weights=weights)
        var_val = np.average((clean_series - mean_val)**2, weights=weights)
        std_val = np.sqrt(var_val)
    else:
        mean_val = clean_series.mean()
        std_val = clean_series.std()
    
    return {
        'N': len(clean_series),
        'mean': mean_val,
        'std': std_val,
        'min': clean_series.min(),
        'max': clean_series.max(),
        'p25': clean_series.quantile(0.25),
        'p50': clean_series.quantile(0.50),
        'p75': clean_series.quantile(0.75)
    }


def print_stata_table(data: Union[pd.DataFrame, dict], title: str = "", 
                     float_format: str = ".3f") -> None:
    """
    Print a table in Stata style.
    
    Parameters
    ----------
    data : pd.DataFrame or dict
        Data to print as table
    title : str, default ""
        Table title
    float_format : str, default ".3f"
        Format string for floating point numbers
    """
    if title:
        print(title)
        print("-" * len(title))
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (int, float)):
                print(f"{key:>15} : {value:{float_format}}")
            else:
                print(f"{key:>15} : {value}")
    else:
        print(data.to_string(float_format=float_format))
    
    print()


class StataStyleResults:
    """
    Base class for storing and displaying results in Stata style.
    """
    
    def __init__(self, title: str = "Results"):
        self.title = title
        self.results = {}
        self.tables = {}
        
    def add_result(self, key: str, value: Any) -> None:
        """Add a result value."""
        self.results[key] = value
        
    def add_table(self, key: str, table: pd.DataFrame) -> None:
        """Add a result table."""
        self.tables[key] = table
        
    def summary(self) -> str:
        """Return formatted summary of results."""
        output = [self.title, "=" * len(self.title)]
        
        if self.results:
            output.append("\nResults:")
            for key, value in self.results.items():
                if isinstance(value, (int, float)):
                    output.append(f"  {key}: {value:.6f}")
                else:
                    output.append(f"  {key}: {value}")
        
        if self.tables:
            for key, table in self.tables.items():
                output.append(f"\n{key}:")
                output.append(table.to_string())
        
        return "\n".join(output)
    
    def __repr__(self) -> str:
        return self.summary()
    
    def __str__(self) -> str:
        return self.summary()
