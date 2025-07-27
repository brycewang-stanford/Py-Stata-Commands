"""
Regression results class for PyRegHDFE.
"""

from typing import Optional, List, Union, Dict, Any
import numpy as np
import pandas as pd
from scipy import stats
from tabulate import tabulate


class RegressionResults:
    """
    Results class for reghdfe estimations.
    
    This class contains estimation results and provides methods for displaying
    and accessing regression outputs, similar to statsmodels results.
    
    Attributes
    ----------
    params : pd.Series
        Estimated coefficients
    bse : pd.Series
        Standard errors of coefficients
    tvalues : pd.Series
        t-statistics for coefficients
    pvalues : pd.Series
        p-values for coefficients
    nobs : int
        Number of observations
    df_resid : int
        Degrees of freedom for residuals
    df_model : int
        Degrees of freedom for model
    rsquared : float
        R-squared
    rsquared_within : float
        Within R-squared (after fixed effects)
    rsquared_adj : float
        Adjusted R-squared
    fvalue : float
        F-statistic for overall significance
    f_pvalue : float
        p-value for F-statistic
    """
    
    def __init__(
        self,
        params: np.ndarray,
        cov_matrix: np.ndarray,
        var_names: List[str],
        nobs: int,
        df_resid: int,
        df_model: int,
        rsquared: float,
        rsquared_within: float,
        rsquared_adj: float,
        fvalue: float,
        f_pvalue: float,
        y_name: str,
        fe_info: Dict[str, Any],
        cluster_info: Optional[Dict[str, Any]] = None,
        weights_info: Optional[Dict[str, Any]] = None,
        iterations: Optional[int] = None,
        converged: bool = True,
        cov_type: str = "robust",
    ) -> None:
        """
        Initialize regression results.
        
        Parameters
        ----------
        params : np.ndarray
            Coefficient estimates
        cov_matrix : np.ndarray
            Covariance matrix of coefficients
        var_names : List[str]
            Names of variables
        nobs : int
            Number of observations
        df_resid : int
            Residual degrees of freedom
        df_model : int
            Model degrees of freedom
        rsquared : float
            R-squared
        rsquared_within : float
            Within R-squared
        rsquared_adj : float
            Adjusted R-squared
        fvalue : float
            F-statistic
        f_pvalue : float
            F-statistic p-value
        y_name : str
            Name of dependent variable
        fe_info : Dict[str, Any]
            Information about fixed effects
        cluster_info : Optional[Dict[str, Any]]
            Information about clustering
        weights_info : Optional[Dict[str, Any]]
            Information about weights
        iterations : Optional[int]
            Number of iterations for HDFE solver
        converged : bool
            Whether estimation converged
        cov_type : str
            Type of covariance matrix used
        """
        
        # Store core results
        self.params = pd.Series(params, index=var_names, name="coef")
        self.bse = pd.Series(np.sqrt(np.diag(cov_matrix)), index=var_names, name="std_err")
        self.tvalues = pd.Series(self.params / self.bse, index=var_names, name="t")
        self.pvalues = pd.Series(2 * (1 - stats.t.cdf(np.abs(self.tvalues), df_resid)), 
                                index=var_names, name="P>|t|")
        
        # Store degrees of freedom for confidence interval calculation
        self._df_resid = df_resid
        
        # Store other attributes
        self.nobs = nobs
        self.df_resid = df_resid
        self.df_model = df_model
        self.rsquared = rsquared
        self.rsquared_within = rsquared_within
        self.rsquared_adj = rsquared_adj
        self.fvalue = fvalue
        self.f_pvalue = f_pvalue
        self.y_name = y_name
        self.fe_info = fe_info
        self.cluster_info = cluster_info
        self.weights_info = weights_info
        self.iterations = iterations
        self.converged = converged
        self.cov_type = cov_type
        
        # Store full covariance matrix
        self.cov_matrix = pd.DataFrame(cov_matrix, index=var_names, columns=var_names)
        
    @property
    def vcov(self) -> pd.DataFrame:
        """Variance-covariance matrix of coefficients."""
        return self.cov_matrix
    
    def conf_int(self, alpha: float = 0.05) -> pd.DataFrame:
        """
        Confidence intervals for coefficients.
        
        Parameters
        ----------
        alpha : float, optional
            Significance level. Default is 0.05 for 95% confidence intervals.
            
        Returns
        -------
        pd.DataFrame
            DataFrame with lower and upper confidence bounds
        """
        t_crit = stats.t.ppf(1 - alpha/2, self._df_resid)
        lower_bound = self.params - t_crit * self.bse
        upper_bound = self.params + t_crit * self.bse
        
        return pd.DataFrame({
            f"{alpha/2:.3f}": lower_bound,
            f"{1-alpha/2:.3f}": upper_bound
        }, index=self.params.index)
        
    def summary(self, alpha: float = 0.05) -> str:
        """
        Generate summary table similar to reghdfe output.
        
        Parameters
        ----------
        alpha : float
            Significance level for confidence intervals
            
        Returns
        -------
        str
            Formatted summary table
        """
        
        lines = []
        
        # Header
        lines.append("=" * 78)
        lines.append(f"HDFE Linear regression")
        lines.append(f"Number of obs      = {self.nobs:>10,}")
        
        # Fixed effects info
        if self.fe_info:
            lines.append(f"Absorbing {len(self.fe_info['names'])} HDFE group(s)")
            
        lines.append("")
        
        # Statistics
        stats_table = [
            ["", ""],
            [f"R-squared", f"{self.rsquared:.4f}"],
            [f"Within R-sq.", f"{self.rsquared_within:.4f}"],
            [f"Adj. R-squared", f"{self.rsquared_adj:.4f}"],
            [f"F({self.df_model}, {self.df_resid})", f"{self.fvalue:.2f}"],
            [f"Prob > F", f"{self.f_pvalue:.4f}"],
        ]
        
        lines.append(tabulate(stats_table, tablefmt="plain"))
        lines.append("")
        
        # Coefficients table
        t_crit = stats.t.ppf(1 - alpha/2, self.df_resid)
        conf_low = self.params - t_crit * self.bse  
        conf_high = self.params + t_crit * self.bse
        
        coef_data = []
        coef_data.append([self.y_name, "Coef.", "Std. Err.", "t", "P>|t|", 
                         f"[{alpha:.1%} Conf. Interval]", ""])
        coef_data.append(["-" * 12, "-" * 10, "-" * 10, "-" * 8, "-" * 8, 
                         "-" * 13, "-" * 13])
        
        for var in self.params.index:
            coef_data.append([
                var,
                f"{self.params[var]:10.6f}",
                f"{self.bse[var]:10.6f}",
                f"{self.tvalues[var]:8.2f}",
                f"{self.pvalues[var]:8.3f}",
                f"{conf_low[var]:10.6f}",
                f"{conf_high[var]:10.6f}"
            ])
            
        lines.append(tabulate(coef_data, tablefmt="plain"))
        lines.append("")
        
        # Fixed effects and clustering info
        if self.fe_info:
            lines.append("Fixed effects:")
            for i, (name, info) in enumerate(zip(self.fe_info['names'], self.fe_info['counts'])):
                lines.append(f"  {name}: {info} groups")
                
        if self.cluster_info:
            lines.append(f"\nClustered standard errors: {self.cluster_info['method']}")
            if 'n_clusters' in self.cluster_info:
                for dim, n_clust in enumerate(self.cluster_info['n_clusters']):
                    lines.append(f"  Dimension {dim+1}: {n_clust} clusters")
                    
        if self.iterations:
            convergence_str = "converged" if self.converged else "did not converge"
            lines.append(f"\nHDFE algorithm {convergence_str} in {self.iterations} iterations")
            
        lines.append("=" * 78)
        
        return "\n".join(lines)
        
    def __repr__(self) -> str:
        """String representation."""
        return f"<PyRegHDFE Results: {len(self.params)} coefficients, {self.nobs} observations>"
        
    def __str__(self) -> str:
        """String representation using summary."""
        return self.summary()