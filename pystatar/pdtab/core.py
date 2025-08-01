"""
PDTab Core: Core tabulation and cross-tabulation functions

Provides the main functionality for frequency analysis and statistical testing.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Union, List, Optional, Tuple, Any
import warnings


class TabulationResult:
    """Results container for tabulation operations"""
    
    def __init__(self, table: pd.DataFrame, stats_results: dict = None, test_type: str = 'oneway'):
        self.table = table
        self.stats_results = stats_results or {}
        self.test_type = test_type
    
    def __str__(self):
        """Stata-style string representation"""
        output = []
        
        if self.test_type == 'oneway':
            output.append("One-way frequency table")
            output.append("=" * 40)
            output.append(self.table.to_string())
        
        elif self.test_type == 'twoway':
            output.append("Two-way cross-tabulation")
            output.append("=" * 50)
            output.append(self.table.to_string())
            
            # Add statistical test results
            if 'chi2' in self.stats_results:
                chi2_result = self.stats_results['chi2']
                output.append(f"\nPearson chi2({chi2_result['df']}) = {chi2_result['statistic']}")
                output.append(f"Pr = {chi2_result['p_value']}")
        
        return "\n".join(output)
    
    def to_csv(self, filename: str):
        """Export table to CSV"""
        self.table.to_csv(filename)
        
    def summary(self):
        """Statistical summary"""
        summary_info = {
            'table_shape': self.table.shape,
            'total_observations': self.table.sum().sum() if self.test_type == 'twoway' else self.table['Freq'].sum()
        }
        
        if self.stats_results:
            summary_info['statistical_tests'] = list(self.stats_results.keys())
            
        return summary_info


def oneway(data: pd.DataFrame, var: str, missing: bool = False, sort: bool = True) -> TabulationResult:
    """
    Generate one-way frequency table
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input DataFrame
    var : str
        Variable name for tabulation
    missing : bool, default False
        Include missing values in tabulation
    sort : bool, default True
        Sort results by frequency
        
    Returns:
    --------
    TabulationResult
        Tabulation results with frequencies and percentages
    """
    # Handle missing values
    if missing:
        series = data[var].copy()
    else:
        series = data[var].dropna()
    
    # Calculate frequencies
    freq_table = series.value_counts(sort=sort, dropna=not missing)
    
    # Calculate percentages and cumulative percentages
    total = len(series)
    percentages = (freq_table / total * 100).round(2)
    cumulative = percentages.cumsum().round(2)
    
    # Build result DataFrame
    result_df = pd.DataFrame({
        'Freq': freq_table,
        'Percent': percentages,
        'Cum': cumulative
    })
    
    return TabulationResult(result_df, test_type='oneway')


def twoway(data: pd.DataFrame, row_var: str, col_var: str, 
           missing: bool = False, chi2: bool = True, exact: bool = False, 
           gamma: bool = False, all_stats: bool = False) -> TabulationResult:
    """
    Generate two-way cross-tabulation
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input DataFrame
    row_var : str
        Row variable name
    col_var : str
        Column variable name
    missing : bool, default False
        Include missing values
    chi2 : bool, default True
        Perform chi-square test
    exact : bool, default False
        Perform Fisher's exact test
    gamma : bool, default False
        Calculate gamma coefficient
    all_stats : bool, default False
        Calculate all available statistics
        
    Returns:
    --------
    TabulationResult
        Cross-tabulation results with optional statistical tests
    """
    # Create cross-tabulation
    if missing:
        ct = pd.crosstab(data[row_var], data[col_var], 
                        dropna=False, margins=True)
    else:
        ct = pd.crosstab(data[row_var], data[col_var], 
                        dropna=True, margins=True)
    
    # Perform statistical tests
    stats_results = {}
    
    if chi2 or all_stats:
        stats_results['chi2'] = chi2_test(ct.iloc[:-1, :-1])
    
    if exact or all_stats:
        stats_results['fisher'] = fisher_exact_test(ct.iloc[:-1, :-1])
    
    if gamma or all_stats:
        stats_results['cramers_v'] = cramers_v(ct.iloc[:-1, :-1])
    
    return TabulationResult(ct, stats_results=stats_results, test_type='twoway')


def tabulate(data: pd.DataFrame, *args, **kwargs) -> TabulationResult:
    """
    Main tabulate function - dispatches to oneway or twoway
    
    Parameters:
    -----------
    data : pd.DataFrame
        Input DataFrame
    *args : str
        Variable names (1 for oneway, 2 for twoway)
    **kwargs : dict
        Additional options passed to specific functions
        
    Returns:
    --------
    TabulationResult
        Tabulation results
    """
    if len(args) == 1:
        return oneway(data, args[0], **kwargs)
    elif len(args) == 2:
        return twoway(data, args[0], args[1], **kwargs)
    else:
        raise ValueError("tabulate() takes 1 or 2 variable names")


def chi2_test(table: pd.DataFrame) -> dict:
    """
    Perform chi-square independence test
    
    Parameters:
    -----------
    table : pd.DataFrame
        Contingency table
        
    Returns:
    --------
    dict
        Test results including statistic, p-value, degrees of freedom
    """
    observed = table.values
    chi2_stat, p_value, dof, expected = stats.chi2_contingency(observed)
    
    # Check assumptions
    warnings_list = []
    if np.any(expected < 5):
        min_expected = np.min(expected)
        warnings_list.append(f"Minimum expected frequency: {min_expected:.2f} (< 5)")
    
    return {
        'statistic': round(chi2_stat, 4),
        'p_value': round(p_value, 4),
        'df': dof,
        'expected': expected,
        'warnings': warnings_list,
        'significant': p_value < 0.05
    }


def fisher_exact_test(table: pd.DataFrame) -> dict:
    """
    Perform Fisher's exact test (2x2 tables only)
    
    Parameters:
    -----------
    table : pd.DataFrame
        2x2 contingency table
        
    Returns:
    --------
    dict
        Test results including odds ratio and p-value
    """
    observed = table.values
    
    if observed.shape != (2, 2):
        return {'error': "Fisher's exact test requires 2x2 table"}
    
    odds_ratio, p_value = stats.fisher_exact(observed)
    
    return {
        'odds_ratio': round(odds_ratio, 4),
        'p_value': round(p_value, 4),
        'significant': p_value < 0.05
    }


def cramers_v(table: pd.DataFrame) -> dict:
    """
    Calculate Cramér's V association measure
    
    Parameters:
    -----------
    table : pd.DataFrame
        Contingency table
        
    Returns:
    --------
    dict
        Cramér's V value and interpretation
    """
    observed = table.values
    chi2_stat, _, _, _ = stats.chi2_contingency(observed)
    n = observed.sum()
    min_dim = min(observed.shape) - 1
    
    cramers_v_value = np.sqrt(chi2_stat / (n * min_dim))
    
    # Interpretation
    if cramers_v_value < 0.1:
        interpretation = "Very weak association"
    elif cramers_v_value < 0.3:
        interpretation = "Weak association"
    elif cramers_v_value < 0.5:
        interpretation = "Moderate association"
    else:
        interpretation = "Strong association"
    
    return {
        'value': round(cramers_v_value, 4),
        'interpretation': interpretation
    }
