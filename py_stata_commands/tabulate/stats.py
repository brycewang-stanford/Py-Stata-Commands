"""
Statistical tests for pandas-tabulate.

This module implements various statistical tests commonly used
with cross-tabulation, including chi-square, Fisher exact test,
and measures of association.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, Union
import warnings


class StatisticalTests:
    """
    Class containing statistical tests for tabulation.
    """
    
    def chi_square_test(self, table: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform chi-square test of independence.
        
        Parameters:
        -----------
        table : pd.DataFrame
            Cross-tabulation table (without margins)
            
        Returns:
        --------
        dict
            Dictionary containing test results
        """
        # Convert to numpy array for scipy
        observed = table.values
        
        try:
            chi2_stat, p_value, dof, expected = stats.chi2_contingency(observed)
            
            # Check assumptions
            warnings_list = []
            if np.any(expected < 5):
                min_expected = np.min(expected)
                warnings_list.append(f"Minimum expected frequency is {min_expected:.2f} (< 5)")
            
            # Critical value at 0.05 level
            critical_value = stats.chi2.ppf(0.95, dof)
            
            return {
                'statistic': round(chi2_stat, 4),
                'p_value': round(p_value, 4),
                'df': dof,
                'critical_value': round(critical_value, 4),
                'expected': expected,
                'warnings': warnings_list,
                'significant': p_value < 0.05
            }
            
        except Exception as e:
            return {
                'error': f"Chi-square test failed: {str(e)}",
                'statistic': None,
                'p_value': None
            }
    
    def fisher_exact_test(self, table: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform Fisher exact test.
        
        Parameters:
        -----------
        table : pd.DataFrame
            Cross-tabulation table (2x2 for exact test)
            
        Returns:
        --------
        dict
            Dictionary containing test results
        """
        observed = table.values
        
        if observed.shape != (2, 2):
            # For larger tables, use alternative approach or warning
            return {
                'error': "Fisher exact test requires 2x2 table",
                'p_value': None,
                'odds_ratio': None
            }
        
        try:
            odds_ratio, p_value = stats.fisher_exact(observed)
            
            return {
                'odds_ratio': round(odds_ratio, 4),
                'p_value': round(p_value, 4),
                'significant': p_value < 0.05
            }
            
        except Exception as e:
            return {
                'error': f"Fisher exact test failed: {str(e)}",
                'p_value': None,
                'odds_ratio': None
            }
    
    def cramers_v(self, table: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Cramér's V measure of association.
        
        Parameters:
        -----------
        table : pd.DataFrame
            Cross-tabulation table
            
        Returns:
        --------
        dict
            Dictionary containing Cramér's V and interpretation
        """
        observed = table.values
        
        try:
            chi2_stat, _, _, _ = stats.chi2_contingency(observed)
            n = observed.sum()
            min_dim = min(observed.shape) - 1
            
            cramers_v_value = np.sqrt(chi2_stat / (n * min_dim))
            
            # Interpretation
            if cramers_v_value < 0.1:
                interpretation = "negligible association"
            elif cramers_v_value < 0.3:
                interpretation = "weak association"
            elif cramers_v_value < 0.5:
                interpretation = "moderate association"
            else:
                interpretation = "strong association"
            
            return {
                'value': round(cramers_v_value, 4),
                'interpretation': interpretation
            }
            
        except Exception as e:
            return {
                'error': f"Cramér's V calculation failed: {str(e)}",
                'value': None
            }
    
    def likelihood_ratio_test(self, table: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform likelihood ratio test of independence.
        
        Parameters:
        -----------
        table : pd.DataFrame
            Cross-tabulation table
            
        Returns:
        --------
        dict
            Dictionary containing test results
        """
        observed = table.values
        
        try:
            # Calculate expected frequencies
            row_totals = observed.sum(axis=1)
            col_totals = observed.sum(axis=0)
            total = observed.sum()
            
            expected = np.outer(row_totals, col_totals) / total
            
            # Avoid log(0) by adding small constant where needed
            mask = observed > 0
            lr_stat = 2 * np.sum(observed[mask] * np.log(observed[mask] / expected[mask]))
            
            # Degrees of freedom
            dof = (observed.shape[0] - 1) * (observed.shape[1] - 1)
            
            # P-value
            p_value = 1 - stats.chi2.cdf(lr_stat, dof)
            
            return {
                'statistic': round(lr_stat, 4),
                'p_value': round(p_value, 4),
                'df': dof,
                'significant': p_value < 0.05
            }
            
        except Exception as e:
            return {
                'error': f"Likelihood ratio test failed: {str(e)}",
                'statistic': None,
                'p_value': None
            }
    
    def phi_coefficient(self, table: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate phi coefficient for 2x2 tables.
        
        Parameters:
        -----------
        table : pd.DataFrame
            Cross-tabulation table (should be 2x2)
            
        Returns:
        --------
        dict
            Dictionary containing phi coefficient
        """
        observed = table.values
        
        if observed.shape != (2, 2):
            return {
                'error': "Phi coefficient requires 2x2 table",
                'value': None
            }
        
        try:
            a, b = observed[0, 0], observed[0, 1]
            c, d = observed[1, 0], observed[1, 1]
            
            numerator = a * d - b * c
            denominator = np.sqrt((a + b) * (c + d) * (a + c) * (b + d))
            
            if denominator == 0:
                phi = 0
            else:
                phi = numerator / denominator
            
            return {
                'value': round(phi, 4),
                'interpretation': "correlation-like measure for 2x2 tables"
            }
            
        except Exception as e:
            return {
                'error': f"Phi coefficient calculation failed: {str(e)}",
                'value': None
            }
