"""
Public API for PyRegHDFE.

This module provides the main user-facing function for estimating
linear regressions with high-dimensional fixed effects.
"""

from typing import Optional, Union, List, Literal, Dict, Any
import pandas as pd

from .core import estimate_reghdfe
from .results import RegressionResults


def reghdfe(
    data: pd.DataFrame,
    y: str,
    x: Union[List[str], str],
    fe: Optional[Union[List[str], str]] = None,
    cluster: Optional[Union[List[str], str]] = None,
    weights: Optional[str] = None,
    drop_singletons: bool = True,
    absorb_tolerance: float = 1e-8,
    robust: bool = True,
    cov_type: Literal["robust", "cluster"] = "robust",
    ddof: Optional[int] = None,
    absorb_method: Optional[str] = None,
    absorb_options: Optional[Dict[str, Any]] = None
) -> RegressionResults:
    """
    Estimate linear regression with high-dimensional fixed effects.
    
    This function replicates the core functionality of Stata's reghdfe command,
    providing efficient estimation of linear models with multiple high-dimensional
    fixed effects using the pyhdfe library for fixed effect absorption.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset containing all variables
    y : str
        Name of the dependent variable
    x : Union[List[str], str]
        Name(s) of independent variables. Can be a single string or list of strings.
    fe : Optional[Union[List[str], str]], default None
        Name(s) of fixed effect variables. If None, no fixed effects are absorbed.
        Can be a single string or list of strings for multiple dimensions.
    cluster : Optional[Union[List[str], str]], default None
        Name(s) of cluster variables for cluster-robust standard errors.
        Supports 1-way and 2-way clustering. If None, uses robust standard errors.
    weights : Optional[str], default None
        Name of weight variable for weighted least squares. Uses frequency/analytic weights.
    drop_singletons : bool, default True
        Whether to drop singleton groups (groups with only one observation).
        Recommended to keep True for proper degrees of freedom calculation.
    absorb_tolerance : float, default 1e-8
        Convergence tolerance for iterative fixed effect absorption algorithms.
    robust : bool, default True
        Whether to use heteroskedasticity-robust standard errors when cluster is None.
    cov_type : Literal["robust", "cluster"], default "robust"
        Type of covariance matrix estimation:
        - "robust": Heteroskedasticity-robust (HC1)
        - "cluster": Cluster-robust (requires cluster variables)
    ddof : Optional[int], default None
        Degrees of freedom correction. If None, computed automatically as
        k_vars + n_absorbed_fe where k_vars is number of regressors and
        n_absorbed_fe is number of absorbed fixed effect parameters.
    absorb_method : Optional[str], default None
        Algorithm for fixed effect absorption:
        - None: Auto-select (within transform for 1 FE, MAP for multiple)
        - "within": Within transform (only for single fixed effect)
        - "map": Method of alternating projections
        - "lsmr": LSMR sparse solver
        - "sw": Somaini-Wolak method (only for 2 fixed effects)
    absorb_options : Optional[Dict[str, Any]], default None
        Additional options passed to the pyhdfe absorption algorithm.
        See pyhdfe documentation for available options.
        
    Returns
    -------
    RegressionResults
        Estimation results containing coefficients, standard errors, test statistics,
        R-squared measures, and other regression diagnostics. Provides a summary()
        method for formatted output similar to Stata's reghdfe.
        
    Raises
    ------
    ValueError
        - If required variables are missing from the dataset
        - If there are insufficient degrees of freedom
        - If fixed effect variables have insufficient variation
        - If cluster variables are specified but cov_type != "cluster"
        - If weights contain non-positive values
        
    Examples
    --------
    Basic regression with firm and year fixed effects:
    
    >>> import pandas as pd
    >>> from pyreghdfe import reghdfe
    >>> 
    >>> # Load your data
    >>> df = pd.read_csv("wage_data.csv")
    >>> 
    >>> # Estimate model
    >>> results = reghdfe(
    ...     data=df,
    ...     y="log_wage",
    ...     x=["experience", "education", "tenure"],
    ...     fe=["firm_id", "year"],
    ...     cluster="firm_id"
    ... )
    >>> 
    >>> # Display results
    >>> print(results.summary())
    >>> 
    >>> # Access coefficients
    >>> print(results.params)
    >>> print(results.bse)
    
    Regression with weights and custom absorption options:
    
    >>> results = reghdfe(
    ...     data=df,
    ...     y="outcome",
    ...     x=["treatment", "control_var"],
    ...     fe=["state", "year"],
    ...     weights="survey_weight",
    ...     absorb_method="lsmr",
    ...     absorb_options={"tol": 1e-10, "iteration_limit": 5000}
    ... )
    
    Two-way clustered standard errors:
    
    >>> results = reghdfe(
    ...     data=df,
    ...     y="returns",
    ...     x=["beta", "size", "momentum"],
    ...     fe=["firm", "date"],
    ...     cluster=["firm", "industry"],
    ...     cov_type="cluster"
    ... )
        
    Notes
    -----
    This implementation follows the algorithms described in:
    
    - Correia, S. (2017). Linear Models with High-Dimensional Fixed Effects: 
      An Efficient and Feasible Estimator. Working Paper.
    - Guimarães, P. and Portugal, P. (2010). A simple approach to quantify the bias
      of estimators in non-linear panel models. Journal of Econometrics, 157(2), 334-344.
      
    The function uses the Frisch-Waugh-Lovell theorem to partial out fixed effects
    before running OLS, which is computationally efficient for high-dimensional problems.
    
    Standard error calculations follow:
    - Robust: HC1 heteroskedasticity-robust (White/Huber-White)
    - Cluster: Liang-Zeger cluster-robust with small-sample corrections
    - Two-way cluster: Cameron-Gelbach-Miller method
    
    See Also
    --------
    RegressionResults : Results class with summary methods and diagnostics
    """
    
    # Input validation
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
        
    if data.empty:
        raise ValueError("data cannot be empty")
        
    # Validate covariance type and cluster consistency
    if cov_type == "cluster" and cluster is None:
        raise ValueError("cluster variables must be specified when cov_type='cluster'")
        
    if cluster is not None and cov_type != "cluster":
        # Auto-switch to cluster covariance if cluster vars provided
        cov_type = "cluster"
        
    # Validate absorb_method for fixed effects dimensions
    if absorb_method is not None:
        valid_methods = ["within", "map", "lsmr", "sw", "dummy"]
        if absorb_method not in valid_methods:
            raise ValueError(f"absorb_method must be one of {valid_methods}")
            
        # Check method compatibility with FE dimensions
        if fe is not None:
            fe_vars = [fe] if isinstance(fe, str) else fe
            n_fe_dims = len(fe_vars)
            
            if absorb_method == "within" and n_fe_dims > 1:
                raise ValueError("within method only supports single fixed effect")
            elif absorb_method == "sw" and n_fe_dims != 2:
                raise ValueError("sw method only supports exactly 2 fixed effects")
                
    # Validate cluster dimensions
    if cluster is not None:
        cluster_vars = [cluster] if isinstance(cluster, str) else cluster
        if len(cluster_vars) > 2:
            raise ValueError("Only 1-way and 2-way clustering are supported")
            
    # Call core estimation function
    try:
        results = estimate_reghdfe(
            data=data,
            y=y,
            x=x,
            fe=fe,
            cluster=cluster,
            weights=weights,
            drop_singletons=drop_singletons,
            absorb_tolerance=absorb_tolerance,
            robust=robust,
            cov_type=cov_type,
            ddof=ddof,
            absorb_method=absorb_method,
            absorb_options=absorb_options
        )
        
        return results
        
    except Exception as e:
        # Re-raise with more context
        raise ValueError(f"Estimation failed: {str(e)}") from e


# Convenience alias for backwards compatibility and alternative naming
hdfe_regression = reghdfe