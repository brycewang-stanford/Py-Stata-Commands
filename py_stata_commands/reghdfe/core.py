"""
Core regression estimation for PyRegHDFE.

This module implements the main regression functionality including
OLS estimation, R-squared calculations, and degrees of freedom corrections.
"""

from typing import Optional, Union, List, Tuple, Dict, Any, Literal
import numpy as np
import pandas as pd
from scipy import stats

from .hdfe import HDFEAbsorber, prepare_fixed_effects, check_fe_variation
from .covariance import robust_covariance, cluster_covariance
from .results import RegressionResults


def estimate_reghdfe(
    data: pd.DataFrame,
    y: str,
    x: Union[str, List[str]],
    fe: Optional[Union[str, List[str]]] = None,
    cluster: Optional[Union[str, List[str]]] = None,
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
    
    This is the core estimation function that implements the full reghdfe
    algorithm using the Frisch-Waugh-Lovell theorem.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    y : str
        Dependent variable name
    x : Union[str, List[str]]
        Independent variable names
    fe : Optional[Union[str, List[str]]]
        Fixed effect variable names
    cluster : Optional[Union[str, List[str]]]
        Cluster variable names for robust standard errors
    weights : Optional[str]
        Weight variable name
    drop_singletons : bool
        Whether to drop singleton groups
    absorb_tolerance : float
        Convergence tolerance for HDFE absorption
    robust : bool
        Whether to use heteroskedasticity-robust standard errors
    cov_type : Literal["robust", "cluster"]
        Type of covariance matrix estimation
    ddof : Optional[int]
        Degrees of freedom correction (if None, computed automatically)
    absorb_method : Optional[str]
        Method for fixed effect absorption
    absorb_options : Optional[Dict[str, Any]]
        Additional options for absorption algorithm
        
    Returns
    -------
    RegressionResults
        Estimation results
    """
    
    # Prepare variables
    y_var, x_vars, fe_vars, cluster_vars, weight_var = _prepare_variables(
        data, y, x, fe, cluster, weights
    )
    
    # Get clean data (no missing values)
    clean_data, valid_mask = _get_clean_data(data, y_var, x_vars, fe_vars, cluster_vars, weight_var)
    
    # Extract arrays
    y_array = clean_data[y_var].values.reshape(-1, 1)
    X_array = clean_data[x_vars].values
    weight_array = clean_data[weight_var].values if weight_var else None
    
    # Prepare fixed effects if specified
    hdfe_absorber = None
    if fe_vars:
        fe_ids, fe_names = prepare_fixed_effects(clean_data, fe_vars)
        check_fe_variation(fe_ids, fe_names)
        
        # Prepare cluster IDs for DoF computation
        cluster_ids_for_dof = None
        if cluster_vars:
            cluster_ids_for_dof, _ = prepare_fixed_effects(clean_data, cluster_vars)
            
        hdfe_absorber = HDFEAbsorber(
            fe_ids=fe_ids,
            cluster_ids=cluster_ids_for_dof,
            drop_singletons=drop_singletons,
            absorb_tolerance=absorb_tolerance,
            absorb_method=absorb_method,
            absorb_options=absorb_options
        )
        
        # Absorb fixed effects from y and X
        y_resid = hdfe_absorber.absorb(y_array, weight_array)
        X_resid = hdfe_absorber.absorb(X_array, weight_array)
        
        # Update valid observations after singleton dropping
        additional_mask = hdfe_absorber.valid_observations
        final_valid_mask = valid_mask.copy()
        final_valid_mask[valid_mask] = additional_mask
        
    else:
        # No fixed effects - use original data
        y_resid = y_array
        X_resid = X_array
        final_valid_mask = valid_mask
        
    # Apply weights to residualized data if specified
    if weight_var:
        if hdfe_absorber:
            # Weights already applied during absorption
            weight_final = weight_array[hdfe_absorber.valid_observations] if hdfe_absorber else weight_array
        else:
            weight_final = weight_array
            # Apply sqrt weights for WLS
            weight_sqrt = np.sqrt(weight_final).reshape(-1, 1)
            y_resid = y_resid * weight_sqrt
            X_resid = X_resid * weight_sqrt
    else:
        weight_final = None
        
    # Estimate OLS on residualized data
    coefficients, residuals = _estimate_ols(X_resid, y_resid)
    
    # Compute R-squared statistics
    r2_stats = _compute_r_squared(
        data=data[final_valid_mask],
        y_var=y_var,
        X_original=X_array if not hdfe_absorber else clean_data[x_vars].values[hdfe_absorber.valid_observations],
        y_resid=y_resid,
        X_resid=X_resid, 
        residuals=residuals,
        coefficients=coefficients,
        weights=weight_final,
        has_fe=fe_vars is not None
    )
    
    # Compute degrees of freedom
    n_obs = len(y_resid)
    k_vars = len(x_vars)
    
    if ddof is not None:
        df_model = ddof
    else:
        df_model = k_vars
        if hdfe_absorber:
            df_model += hdfe_absorber.n_absorbed_fe
            
    df_resid = n_obs - df_model
    
    if df_resid <= 0:
        raise ValueError(f"Insufficient degrees of freedom: {df_resid}")
        
    # Compute covariance matrix
    cluster_info = None
    if cov_type == "cluster" and cluster_vars:
        # Prepare cluster IDs for covariance calculation
        cluster_data = clean_data[cluster_vars]
        if hdfe_absorber:
            cluster_data = cluster_data[hdfe_absorber.valid_observations]
            
        if len(cluster_vars) == 1:
            cluster_ids_cov = cluster_data.iloc[:, 0].values
        else:
            cluster_ids_cov = [cluster_data.iloc[:, i].values for i in range(len(cluster_vars))]
            
        cov_matrix, cluster_info = cluster_covariance(
            X_resid, residuals, cluster_ids_cov, weight_final
        )
        
    elif robust or cov_type == "robust":
        cov_matrix = robust_covariance(X_resid, residuals, weight_final, hc_type="HC1")
        
    else:
        # Classical covariance matrix
        sigma2 = np.sum(residuals**2) / df_resid
        XTX_inv = np.linalg.inv(X_resid.T @ X_resid)
        cov_matrix = sigma2 * XTX_inv
        
    # Compute F-statistic
    fvalue, f_pvalue = _compute_f_statistic(coefficients, cov_matrix, df_resid)
    
    # Gather fixed effects info
    fe_info = hdfe_absorber.fe_info if hdfe_absorber else {}
    
    # Gather weights info
    weights_info = {"variable": weight_var, "type": "frequency"} if weight_var else None
    
    # Create results object
    results = RegressionResults(
        params=coefficients,
        cov_matrix=cov_matrix,
        var_names=x_vars,
        nobs=n_obs,
        df_resid=df_resid,
        df_model=df_model,
        rsquared=r2_stats["r2"],
        rsquared_within=r2_stats["r2_within"],
        rsquared_adj=r2_stats["r2_adj"],
        fvalue=fvalue,
        f_pvalue=f_pvalue,
        y_name=y_var,
        fe_info=fe_info,
        cluster_info=cluster_info,
        weights_info=weights_info,
        iterations=hdfe_absorber.iterations if hdfe_absorber else None,
        converged=hdfe_absorber.converged if hdfe_absorber else True,
        cov_type=cov_type if cov_type == "cluster" else "robust" if robust else "classical"
    )
    
    return results


def _prepare_variables(
    data: pd.DataFrame,
    y: str,
    x: Union[str, List[str]],
    fe: Optional[Union[str, List[str]]],
    cluster: Optional[Union[str, List[str]]],
    weights: Optional[str]
) -> Tuple[str, List[str], Optional[List[str]], Optional[List[str]], Optional[str]]:
    """Prepare and validate variable names."""
    
    # Convert to lists
    x_vars = [x] if isinstance(x, str) else x
    fe_vars = [fe] if isinstance(fe, str) and fe is not None else fe
    cluster_vars = [cluster] if isinstance(cluster, str) and cluster is not None else cluster
    
    # Check that all variables exist
    all_vars = [y] + x_vars
    if fe_vars:
        all_vars.extend(fe_vars)
    if cluster_vars:
        all_vars.extend(cluster_vars)
    if weights:
        all_vars.append(weights)
        
    missing_vars = [var for var in all_vars if var not in data.columns]
    if missing_vars:
        raise ValueError(f"Variables not found in data: {missing_vars}")
        
    # Check for duplicates
    if len(set(x_vars)) != len(x_vars):
        raise ValueError("Duplicate variables in x")
        
    if y in x_vars:
        raise ValueError("Dependent variable cannot be in independent variables")
        
    return y, x_vars, fe_vars, cluster_vars, weights


def _get_clean_data(
    data: pd.DataFrame,
    y_var: str,
    x_vars: List[str],
    fe_vars: Optional[List[str]],
    cluster_vars: Optional[List[str]],
    weight_var: Optional[str]
) -> Tuple[pd.DataFrame, np.ndarray]:
    """Get clean data without missing values."""
    
    # Determine all variables needed - use set to avoid duplicates
    all_vars = [y_var] + x_vars
    if fe_vars:
        all_vars.extend(fe_vars)
    if cluster_vars:
        all_vars.extend(cluster_vars)
    if weight_var:
        all_vars.append(weight_var)
    
    # Remove duplicates while preserving order
    all_vars = list(dict.fromkeys(all_vars))
        
    # Select relevant columns
    subset_data = data[all_vars].copy()
    
    # Identify complete cases
    valid_mask = subset_data.notna().all(axis=1).values
    
    if not valid_mask.any():
        raise ValueError("No complete observations found")
        
    clean_data = subset_data[valid_mask].copy()
    
    # Validate weights if provided
    if weight_var:
        weights = clean_data[weight_var]
        if (weights <= 0).any():
            raise ValueError("All weights must be positive")
            
    return clean_data, valid_mask


def _estimate_ols(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Estimate OLS coefficients and compute residuals."""
    
    # Check for perfect collinearity
    try:
        coefficients = np.linalg.solve(X.T @ X, X.T @ y.ravel())
    except np.linalg.LinAlgError:
        # Try with SVD for numerical stability
        try:
            U, s, Vt = np.linalg.svd(X, full_matrices=False)
            # Filter out small singular values
            s_inv = np.where(s > 1e-12, 1/s, 0)
            coefficients = Vt.T @ (s_inv[:, np.newaxis] * (U.T @ y.ravel())[:, np.newaxis]).ravel()
        except:
            raise ValueError("Design matrix is singular (perfect collinearity)")
    
    # Compute residuals
    residuals = (y.ravel() - X @ coefficients).reshape(-1, 1)
    
    return coefficients, residuals


def _compute_r_squared(
    data: pd.DataFrame,
    y_var: str,
    X_original: np.ndarray,
    y_resid: np.ndarray,
    X_resid: np.ndarray,
    residuals: np.ndarray,
    coefficients: np.ndarray,
    weights: Optional[np.ndarray],
    has_fe: bool
) -> Dict[str, float]:
    """Compute R-squared statistics."""
    
    # Get original y values
    y_original = data[y_var].values.reshape(-1, 1)
    
    # Apply weights if needed
    if weights is not None:
        weight_sqrt = np.sqrt(weights).reshape(-1, 1)
        y_original_w = y_original * weight_sqrt
        y_resid_w = y_resid
        residuals_w = residuals
    else:
        y_original_w = y_original
        y_resid_w = y_resid
        residuals_w = residuals
    
    # Total sum of squares (original y)
    if weights is not None:
        y_mean_original = np.average(y_original.ravel(), weights=weights.ravel())
        tss_original = np.sum(weights.ravel() * (y_original.ravel() - y_mean_original)**2)
    else:
        y_mean_original = np.mean(y_original)
        tss_original = np.sum((y_original - y_mean_original)**2)
    
    # Total sum of squares (after FE absorption)
    if weights is not None:
        y_mean_resid = np.average(y_resid.ravel(), weights=weights.ravel())
        tss_within = np.sum(weights.ravel() * (y_resid.ravel() - y_mean_resid)**2)
    else:
        y_mean_resid = np.mean(y_resid)
        tss_within = np.sum((y_resid - y_mean_resid)**2)
    
    # Explained sum of squares (within, after FE absorption)
    fitted_resid = X_resid @ coefficients
    if weights is not None:
        ess_within = np.sum(weights.ravel() * (fitted_resid.ravel() - y_mean_resid)**2)
    else:
        ess_within = np.sum((fitted_resid - y_mean_resid)**2)
    
    # Residual sum of squares
    if weights is not None:
        rss = np.sum(weights.ravel() * residuals_w.ravel()**2)
    else:
        rss = np.sum(residuals_w**2)
    
    # Compute R-squared measures
    r2_within = ess_within / tss_within if tss_within > 0 else 0.0
    
    if has_fe:
        # Overall R-squared: compare fitted values to original y
        fitted_original = fitted_resid  # This is the within-variation explained
        r2_overall = 1 - rss / tss_original if tss_original > 0 else 0.0
    else:
        # No fixed effects case
        r2_overall = r2_within
    
    # Adjusted R-squared  
    n = len(y_resid)
    k = len(coefficients)
    r2_adj = 1 - (1 - r2_overall) * (n - 1) / (n - k) if n > k else 0.0
    
    return {
        "r2": r2_overall,
        "r2_within": r2_within, 
        "r2_adj": r2_adj,
        "tss": tss_original,
        "ess": ess_within,
        "rss": rss
    }


def _compute_f_statistic(
    coefficients: np.ndarray,
    cov_matrix: np.ndarray,
    df_resid: int
) -> Tuple[float, float]:
    """Compute F-statistic for overall significance."""
    
    k = len(coefficients)
    
    if k == 0:
        return 0.0, 1.0
    
    try:
        # Wald test: coefficients' (V^-1) coefficients
        wald_stat = coefficients.T @ np.linalg.inv(cov_matrix) @ coefficients
        fvalue = wald_stat / k
        f_pvalue = 1 - stats.f.cdf(fvalue, k, df_resid)
        
        return float(fvalue), float(f_pvalue)
        
    except np.linalg.LinAlgError:
        # Singular covariance matrix
        return np.nan, np.nan