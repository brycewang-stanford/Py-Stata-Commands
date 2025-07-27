"""
Core functionality for pywinsor2 package.

This module implements the main winsor2 function that provides
winsorizing and trimming capabilities for pandas DataFrames.
"""

import warnings
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from .utils import compute_percentiles, validate_inputs


def winsor2(
    data: pd.DataFrame,
    varlist: Union[str, List[str]],
    cuts: Tuple[float, float] = (1, 99),
    suffix: Optional[str] = None,
    replace: bool = False,
    trim: bool = False,
    by: Optional[Union[str, List[str]]] = None,
    label: bool = False,
    copy: bool = True,
) -> pd.DataFrame:
    """
    Winsorize or trim variables in a pandas DataFrame.

    This function replicates the functionality of Stata's winsor2 command,
    allowing you to winsorize (replace extreme values with percentile values)
    or trim (remove extreme values) variables in a DataFrame.

    Parameters
    ----------
    data : pd.DataFrame
        Input DataFrame containing the variables to process.
    varlist : str or list of str
        Variable name(s) to winsorize or trim.
    cuts : tuple of float, default (1, 99)
        Percentiles at which to winsorize/trim (lower, upper).
        Values should be between 0 and 100.
    suffix : str, optional
        Suffix for new variable names. If None, defaults to '_w' for
        winsorizing or '_tr' for trimming.
    replace : bool, default False
        If True, replace original variables. Cannot be used with suffix.
    trim : bool, default False
        If True, trim (set to NaN) instead of winsorize.
    by : str or list of str, optional
        Variable name(s) for group-wise processing.
    label : bool, default False
        If True, add descriptive labels to new variables.
    copy : bool, default True
        If True, return a copy of the DataFrame. If False, modify in place.

    Returns
    -------
    pd.DataFrame
        DataFrame with winsorized/trimmed variables.

    Examples
    --------
    >>> import pandas as pd
    >>> import pywinsor2 as pw2
    >>>
    >>> # Create sample data
    >>> data = pd.DataFrame({
    ...     'wage': [1, 2, 3, 4, 5, 6, 7, 8, 9, 100],
    ...     'industry': ['A'] * 5 + ['B'] * 5
    ... })
    >>>
    >>> # Basic winsorizing
    >>> result = pw2.winsor2(data, 'wage')
    >>>
    >>> # Winsorize with custom cuts
    >>> result = pw2.winsor2(data, 'wage', cuts=(5, 95))
    >>>
    >>> # Trim instead of winsorize
    >>> result = pw2.winsor2(data, 'wage', trim=True)
    >>>
    >>> # Group-wise processing
    >>> result = pw2.winsor2(data, 'wage', by='industry')
    """

    # Input validation
    data, varlist, cuts, suffix, by = validate_inputs(
        data, varlist, cuts, suffix, replace, trim, by
    )

    # Create working copy if needed
    if copy or not replace:
        df = data.copy()
    else:
        df = data

    # Set default suffix if not provided
    if suffix is None:
        suffix = "_tr" if trim else "_w"

    # Validate that new variables don't already exist (if not replacing)
    if not replace:
        for var in varlist:
            new_var = f"{var}{suffix}"
            if new_var in df.columns:
                raise ValueError(
                    f"Variable '{new_var}' already exists. "
                    f"Use a different suffix or set replace=True."
                )

    # Process each variable
    for var in varlist:
        if by is None:
            # Process without grouping
            df = _process_variable_ungrouped(
                df, var, cuts, suffix, replace, trim, label
            )
        else:
            # Process with grouping
            df = _process_variable_grouped(
                df, var, cuts, suffix, replace, trim, label, by
            )

    return df


def _process_variable_ungrouped(
    df: pd.DataFrame,
    var: str,
    cuts: Tuple[float, float],
    suffix: str,
    replace: bool,
    trim: bool,
    label: bool,
) -> pd.DataFrame:
    """Process a single variable without grouping."""

    # Get non-missing data for percentile calculation
    non_missing_mask = df[var].notna()

    if not non_missing_mask.any():
        warnings.warn(f"Variable '{var}' has no non-missing values.")
        # Create new variable if not replacing
        if not replace:
            new_var = f"{var}{suffix}"
            df[new_var] = np.nan
        return df

    # Compute percentiles
    lower_pct, upper_pct = compute_percentiles(df[var], cuts, non_missing_mask)

    # Create new variable name
    if replace:
        new_var = var
    else:
        new_var = f"{var}{suffix}"

    # Apply winsorizing or trimming
    if trim:
        # Trimming: set extreme values to NaN
        if replace:
            # Convert to float to allow NaN values
            if df[var].dtype != "float64":
                df[var] = df[var].astype(float)
            df.loc[non_missing_mask & (df[var] < lower_pct), var] = np.nan
            df.loc[non_missing_mask & (df[var] > upper_pct), var] = np.nan
        else:
            df[new_var] = df[var].copy().astype(float)
            df.loc[non_missing_mask & (df[var] < lower_pct), new_var] = np.nan
            df.loc[non_missing_mask & (df[var] > upper_pct), new_var] = np.nan
    else:
        # Winsorizing: replace extreme values with percentiles
        if replace:
            # Convert to float to avoid dtype incompatibility
            if df[var].dtype != "float64":
                df[var] = df[var].astype(float)
            df.loc[non_missing_mask & (df[var] < lower_pct), var] = lower_pct
            df.loc[non_missing_mask & (df[var] > upper_pct), var] = upper_pct
        else:
            df[new_var] = df[var].copy().astype(float)
            df.loc[non_missing_mask & (df[var] < lower_pct), new_var] = lower_pct
            df.loc[non_missing_mask & (df[var] > upper_pct), new_var] = upper_pct

    # Add label if requested
    if label and not replace:
        operation = "Trim" if trim else "Winsor"
        low_str = f"{cuts[0]:g}" if cuts[0] >= 1 else f"0{cuts[0]:g}"
        high_str = f"{cuts[1]:g}"

        # Try to preserve original label
        original_label = getattr(df[var], "name", var)
        new_label = f"{original_label}-{operation}(p{low_str},p{high_str})"

        # Use setattr to avoid pandas warning about attribute assignment
        if not hasattr(df, "_labels"):
            object.__setattr__(df, "_labels", {})
        df._labels[new_var] = new_label

    return df


def _process_variable_grouped(
    df: pd.DataFrame,
    var: str,
    cuts: Tuple[float, float],
    suffix: str,
    replace: bool,
    trim: bool,
    label: bool,
    by: Union[str, List[str]],
) -> pd.DataFrame:
    """Process a single variable with grouping."""

    # Create new variable name
    if replace:
        new_var = var
        # We need a temporary variable for group processing
        temp_var = f"_temp_{var}"
        df[temp_var] = df[var].copy()
        source_var = temp_var
    else:
        new_var = f"{var}{suffix}"
        source_var = var

    # Get group-wise percentiles
    def compute_group_percentiles(group):
        non_missing_mask = group[source_var].notna()
        if not non_missing_mask.any():
            return pd.Series([np.nan, np.nan], index=["lower_pct", "upper_pct"])

        lower_pct, upper_pct = compute_percentiles(
            group[source_var], cuts, non_missing_mask
        )
        return pd.Series([lower_pct, upper_pct], index=["lower_pct", "upper_pct"])

    # Compute percentiles for each group
    group_percentiles = df.groupby(by).apply(
        compute_group_percentiles, include_groups=False
    )

    # Merge percentiles back to main dataframe
    if isinstance(by, str):
        by_list = [by]
    else:
        by_list = by

    # Reset index to get group variables as columns
    group_percentiles = group_percentiles.reset_index()

    # Merge with original data
    df_with_pcts = df.merge(group_percentiles, on=by_list, how="left")

    # Apply winsorizing or trimming
    non_missing_mask = df[var].notna()

    # Initialize new variable
    if replace:
        new_var = var
        # Convert to float for proper assignment
        if df[var].dtype != "float64":
            df[var] = df[var].astype(float)
    else:
        new_var = f"{var}{suffix}"
        df[new_var] = df[var].astype(float)

    if trim:
        # Trimming: set extreme values to NaN
        mask_lower = non_missing_mask & (df[var] < df_with_pcts["lower_pct"])
        mask_upper = non_missing_mask & (df[var] > df_with_pcts["upper_pct"])

        df.loc[mask_lower, new_var] = np.nan
        df.loc[mask_upper, new_var] = np.nan
    else:
        # Winsorizing: replace extreme values with percentiles
        mask_lower = non_missing_mask & (df[var] < df_with_pcts["lower_pct"])
        mask_upper = non_missing_mask & (df[var] > df_with_pcts["upper_pct"])

        df.loc[mask_lower, new_var] = df_with_pcts.loc[mask_lower, "lower_pct"]
        df.loc[mask_upper, new_var] = df_with_pcts.loc[mask_upper, "upper_pct"]

    # Clean up temporary variable if used
    if replace and temp_var in df.columns:
        df.drop(columns=[temp_var], inplace=True)

    # Add label if requested
    if label and not replace:
        operation = "Trim" if trim else "Winsor"
        low_str = f"{cuts[0]:g}" if cuts[0] >= 1 else f"0{cuts[0]:g}"
        high_str = f"{cuts[1]:g}"

        original_label = getattr(df[var], "name", var)
        new_label = f"{original_label}-{operation}(p{low_str},p{high_str})"

        # Use setattr to avoid pandas warning about attribute assignment
        if not hasattr(df, "_labels"):
            object.__setattr__(df, "_labels", {})
        df._labels[new_var] = new_label

    return df
