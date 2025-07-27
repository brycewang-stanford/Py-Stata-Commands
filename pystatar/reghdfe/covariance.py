"""
Covariance matrix estimation for PyRegHDFE.

This module provides robust and cluster-robust covariance matrix estimators
for linear models with high-dimensional fixed effects.
"""

from typing import Optional, Union, List, Tuple, Dict, Any
import numpy as np
import pandas as pd
from scipy import sparse


def robust_covariance(
    X: np.ndarray,
    residuals: np.ndarray,
    weights: Optional[np.ndarray] = None,
    hc_type: str = "HC1"
) -> np.ndarray:
    """
    Compute heteroskedasticity-robust covariance matrix (White/Huber-White).
    
    Parameters
    ----------
    X : np.ndarray
        Design matrix (n x k)
    residuals : np.ndarray  
        Regression residuals (n x 1)
    weights : Optional[np.ndarray]
        Regression weights (n x 1)
    hc_type : str
        Type of heteroskedasticity correction: HC0, HC1, HC2, HC3
        
    Returns
    -------
    np.ndarray
        Robust covariance matrix (k x k)
    """
    
    n, k = X.shape
    
    # Apply weights if provided
    if weights is not None:
        # Ensure weights is 1D
        if weights.ndim > 1:
            weights = weights.flatten()
        
        # Apply weights: multiply each row by sqrt(weight)
        sqrt_weights = np.sqrt(weights)
        X_weighted = X * sqrt_weights.reshape(-1, 1)
        residuals_weighted = residuals.flatten() * sqrt_weights
    else:
        X_weighted = X
        residuals_weighted = residuals.flatten() if residuals.ndim > 1 else residuals
        
    # Compute (X'X)^(-1)
    XTX_inv = np.linalg.inv(X_weighted.T @ X_weighted)
    
    # Compute residual adjustments based on HC type
    if hc_type == "HC0":
        # No adjustment
        residual_adj = residuals_weighted
    elif hc_type == "HC1":
        # Degrees of freedom adjustment
        df_adj = n / (n - k)
        residual_adj = residuals_weighted * np.sqrt(df_adj)
    elif hc_type == "HC2":
        # Leverage adjustment
        H = X_weighted @ XTX_inv @ X_weighted.T
        h_ii = np.diag(H)
        residual_adj = residuals_weighted / np.sqrt(1 - h_ii)
    elif hc_type == "HC3":
        # Squared leverage adjustment  
        H = X_weighted @ XTX_inv @ X_weighted.T
        h_ii = np.diag(H)
        residual_adj = residuals_weighted / (1 - h_ii)
    else:
        raise ValueError(f"Unknown HC type: {hc_type}")
    
    # Compute meat matrix
    meat = np.zeros((k, k))
    
    for i in range(n):
        xi = X_weighted[i, :].reshape(-1, 1)  # Ensure k x 1 shape (k params x 1)
        ei = residual_adj[i]
        
        # Outer product: (k x 1) @ (1 x k) = (k x k)
        outer_product = xi @ xi.T
        
        # Add to meat matrix
        meat += ei**2 * outer_product
    
    # Sandwich formula: (X'X)^(-1) * meat * (X'X)^(-1)
    return XTX_inv @ meat @ XTX_inv


def cluster_covariance(
    X: np.ndarray,
    residuals: np.ndarray,
    cluster_ids: Union[np.ndarray, List[np.ndarray]],
    weights: Optional[np.ndarray] = None,
    small_sample: bool = True
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Compute cluster-robust covariance matrix (Liang-Zeger).
    
    Supports both one-way and two-way clustering.
    
    Parameters
    ----------
    X : np.ndarray
        Design matrix (n x k)
    residuals : np.ndarray
        Regression residuals (n x 1)
    cluster_ids : Union[np.ndarray, List[np.ndarray]]
        Cluster identifiers. For 2-way clustering, pass list of two arrays.
    weights : Optional[np.ndarray]
        Regression weights (n x 1)
    small_sample : bool
        Whether to apply small-sample corrections
        
    Returns
    -------
    Tuple[np.ndarray, Dict[str, Any]]
        Cluster-robust covariance matrix and cluster info
    """
    
    n, k = X.shape
    
    # Apply weights if provided
    if weights is not None:
        # Ensure weights is 1D
        if weights.ndim > 1:
            weights = weights.flatten()
        
        # Apply weights: multiply each row by sqrt(weight)
        sqrt_weights = np.sqrt(weights)
        X_weighted = X * sqrt_weights.reshape(-1, 1)
        residuals_weighted = residuals.flatten() * sqrt_weights
    else:
        X_weighted = X
        residuals_weighted = residuals.flatten() if residuals.ndim > 1 else residuals
        
    # Compute (X'X)^(-1)
    XTX_inv = np.linalg.inv(X_weighted.T @ X_weighted)
    
    # Handle single cluster dimension
    if not isinstance(cluster_ids, list):
        cluster_ids = [cluster_ids]
        
    n_cluster_dims = len(cluster_ids)
    
    if n_cluster_dims == 1:
        # One-way clustering
        cov_matrix, cluster_info = _oneway_cluster_covariance(
            X_weighted, residuals_weighted, cluster_ids[0], XTX_inv, small_sample
        )
    elif n_cluster_dims == 2:
        # Two-way clustering
        cov_matrix, cluster_info = _twoway_cluster_covariance(
            X_weighted, residuals_weighted, cluster_ids, XTX_inv, small_sample
        )
    else:
        raise ValueError("Only 1-way and 2-way clustering are supported")
        
    return cov_matrix, cluster_info


def _oneway_cluster_covariance(
    X: np.ndarray,
    residuals: np.ndarray,
    cluster_ids: np.ndarray,
    XTX_inv: np.ndarray,
    small_sample: bool = True
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Compute one-way cluster-robust covariance matrix."""
    
    n, k = X.shape
    
    # Get unique clusters and create mapping
    clusters = pd.Series(cluster_ids)
    unique_clusters = clusters.unique()
    n_clusters = len(unique_clusters)
    
    # Compute cluster sums
    meat = np.zeros((k, k))
    
    for cluster in unique_clusters:
        # Get observations in this cluster
        cluster_mask = (clusters == cluster).values
        cluster_size = cluster_mask.sum()
        
        if cluster_size == 0:
            continue
            
        # Sum residuals and regressors within cluster
        X_cluster = X[cluster_mask, :]  # nc x k
        resid_cluster = residuals[cluster_mask]  # nc x 1
        
        # Compute cluster contribution to meat matrix
        cluster_score = X_cluster.T @ resid_cluster  # k x 1
        meat += cluster_score @ cluster_score.T
    
    # Small sample correction
    if small_sample:
        # Standard correction: (G/(G-1)) * ((n-1)/(n-k))
        g_correction = n_clusters / (n_clusters - 1)
        df_correction = (n - 1) / (n - k)
        correction = g_correction * df_correction
        meat *= correction
    
    # Sandwich formula
    cov_matrix = XTX_inv @ meat @ XTX_inv
    
    cluster_info = {
        "method": "1-way clustering",
        "n_clusters": [n_clusters],
        "correction": "small-sample" if small_sample else "none"
    }
    
    return cov_matrix, cluster_info


def _twoway_cluster_covariance(
    X: np.ndarray,
    residuals: np.ndarray,
    cluster_ids: List[np.ndarray],
    XTX_inv: np.ndarray,
    small_sample: bool = True
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Compute two-way cluster-robust covariance matrix using Cameron-Gelbach-Miller."""
    
    n, k = X.shape
    cluster1_ids, cluster2_ids = cluster_ids
    
    # Compute individual cluster covariance matrices
    meat1 = _compute_cluster_meat(X, residuals, cluster1_ids)
    meat2 = _compute_cluster_meat(X, residuals, cluster2_ids)
    
    # Compute intersection clusters
    intersection_ids = np.array([f"{c1}_{c2}" for c1, c2 in zip(cluster1_ids, cluster2_ids)])
    meat_intersection = _compute_cluster_meat(X, residuals, intersection_ids)
    
    # Cameron-Gelbach-Miller formula: V1 + V2 - V_intersection
    meat = meat1 + meat2 - meat_intersection
    
    # Small sample corrections
    if small_sample:
        n_clusters1 = len(pd.Series(cluster1_ids).unique())
        n_clusters2 = len(pd.Series(cluster2_ids).unique())
        n_clusters_intersection = len(pd.Series(intersection_ids).unique())
        
        # Apply corrections to each component
        g1_correction = n_clusters1 / (n_clusters1 - 1)
        g2_correction = n_clusters2 / (n_clusters2 - 1)
        gi_correction = n_clusters_intersection / (n_clusters_intersection - 1)
        
        df_correction = (n - 1) / (n - k)
        
        # Adjust meat components
        meat = (g1_correction * df_correction * meat1 + 
                g2_correction * df_correction * meat2 - 
                gi_correction * df_correction * meat_intersection)
    
    # Sandwich formula
    cov_matrix = XTX_inv @ meat @ XTX_inv
    
    cluster_info = {
        "method": "2-way clustering (Cameron-Gelbach-Miller)",
        "n_clusters": [len(pd.Series(cluster1_ids).unique()), 
                      len(pd.Series(cluster2_ids).unique())],
        "correction": "small-sample" if small_sample else "none"
    }
    
    return cov_matrix, cluster_info


def _compute_cluster_meat(X: np.ndarray, residuals: np.ndarray, cluster_ids: np.ndarray) -> np.ndarray:
    """Compute meat matrix for a single clustering dimension."""
    
    k = X.shape[1]
    clusters = pd.Series(cluster_ids)
    unique_clusters = clusters.unique()
    
    meat = np.zeros((k, k))
    
    for cluster in unique_clusters:
        cluster_mask = (clusters == cluster).values
        
        if cluster_mask.sum() == 0:
            continue
            
        # Sum within cluster
        X_cluster = X[cluster_mask, :]
        resid_cluster = residuals[cluster_mask]
        
        # Cluster score
        cluster_score = X_cluster.T @ resid_cluster
        meat += cluster_score @ cluster_score.T
        
    return meat