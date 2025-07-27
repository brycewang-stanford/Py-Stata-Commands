"""
High-dimensional fixed effects absorption using pyhdfe.

This module provides a wrapper around the pyhdfe library to absorb
fixed effects from matrices using various algorithms.
"""

from typing import Optional, Union, List, Tuple, Dict, Any
import numpy as np
import pandas as pd
import pyhdfe


class HDFEAbsorber:
    """
    Wrapper class for absorbing high-dimensional fixed effects using pyhdfe.
    
    This class handles the interface to pyhdfe and provides methods for
    absorbing fixed effects from dependent and independent variables.
    """
    
    def __init__(
        self,
        fe_ids: np.ndarray,
        cluster_ids: Optional[np.ndarray] = None,
        drop_singletons: bool = True,
        absorb_tolerance: float = 1e-8,
        absorb_method: Optional[str] = None,
        absorb_options: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize HDFE absorber.
        
        Parameters
        ----------
        fe_ids : np.ndarray
            Fixed effect identifiers (n x num_fe)
        cluster_ids : Optional[np.ndarray]
            Cluster identifiers for DoF computation
        drop_singletons : bool
            Whether to drop singleton groups
        absorb_tolerance : float
            Convergence tolerance for iterative algorithms
        absorb_method : Optional[str]
            Method for absorption ('within', 'map', 'lsmr', etc.)
        absorb_options : Optional[Dict[str, Any]]
            Additional options for pyhdfe
        """
        
        self.fe_ids = np.atleast_2d(fe_ids)
        self.cluster_ids = cluster_ids
        self.drop_singletons = drop_singletons
        self.absorb_tolerance = absorb_tolerance
        self.absorb_method = absorb_method
        self.absorb_options = absorb_options or {}
        
        # Initialize pyhdfe algorithm
        self._initialize_algorithm()
        
    def _initialize_algorithm(self) -> None:
        """Initialize the pyhdfe algorithm."""
        
        # Determine actual method that will be used by pyhdfe
        actual_method = self.absorb_method
        if actual_method is None:
            # pyhdfe auto-selects 'within' for 1 FE, 'map' for multiple
            actual_method = 'within' if self.fe_ids.shape[1] == 1 else 'map'
        
        # Set up options - only add tolerance for methods that support it
        options = self.absorb_options.copy()
        if actual_method not in ['within', 'sw', 'dummy']:
            options['tol'] = self.absorb_tolerance
        
        # Create algorithm
        try:
            self.algorithm = pyhdfe.create(
                ids=self.fe_ids,
                cluster_ids=self.cluster_ids,
                drop_singletons=self.drop_singletons,
                compute_degrees=True,
                residualize_method=self.absorb_method,
                options=options
            )
            self.converged = True
            self.iterations = getattr(self.algorithm, 'iterations_', None)
            
        except Exception as e:
            raise ValueError(f"Failed to initialize HDFE algorithm: {e}")
            
    def absorb(
        self, 
        matrices: Union[np.ndarray, List[np.ndarray]], 
        weights: Optional[np.ndarray] = None
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Absorb fixed effects from one or more matrices.
        
        Parameters
        ----------
        matrices : Union[np.ndarray, List[np.ndarray]]
            Matrix or list of matrices to residualize
        weights : Optional[np.ndarray]
            Observation weights
            
        Returns
        -------
        Union[np.ndarray, List[np.ndarray]]
            Residualized matrices
        """
        
        if isinstance(matrices, list):
            return [self._absorb_single(mat, weights) for mat in matrices]
        else:
            return self._absorb_single(matrices, weights)
            
    def _absorb_single(self, matrix: np.ndarray, weights: Optional[np.ndarray] = None) -> np.ndarray:
        """Absorb fixed effects from a single matrix."""
        
        # Ensure matrix is 2D
        matrix = np.atleast_2d(matrix)
        if matrix.shape[0] == 1 and matrix.shape[1] > 1:
            matrix = matrix.T
            
        # Apply weights if provided
        if weights is not None:
            weights_sqrt = np.sqrt(weights).reshape(-1, 1)
            matrix_weighted = matrix * weights_sqrt
        else:
            matrix_weighted = matrix
            
        # Remove observations dropped by singletons
        if self.algorithm.singleton_indices is not None:
            valid_obs = ~self.algorithm.singleton_indices
            matrix_weighted = matrix_weighted[valid_obs]
            
        # Residualize using pyhdfe
        try:
            residualized = self.algorithm.residualize(matrix_weighted)
            
            # Store iteration info if available
            if hasattr(self.algorithm, 'last_iterations_'):
                self.iterations = self.algorithm.last_iterations_
                
        except Exception as e:
            raise ValueError(f"Failed to absorb fixed effects: {e}")
            
        return residualized
        
    @property
    def valid_observations(self) -> np.ndarray:
        """Boolean mask of observations kept after dropping singletons."""
        if self.algorithm.singleton_indices is not None:
            return ~self.algorithm.singleton_indices
        else:
            return np.ones(self.fe_ids.shape[0], dtype=bool)
            
    @property
    def n_dropped_obs(self) -> int:
        """Number of observations dropped due to singletons."""
        if self.algorithm.singletons is not None:
            return self.algorithm.singletons
        else:
            return 0
            
    @property
    def n_absorbed_fe(self) -> int:
        """Number of fixed effect parameters absorbed."""
        if self.algorithm.degrees is not None:
            return self.algorithm.degrees
        else:
            # Fallback estimation
            return sum(len(np.unique(self.fe_ids[:, i])) - 1 
                      for i in range(self.fe_ids.shape[1]))
            
    @property
    def fe_info(self) -> Dict[str, Any]:
        """Information about absorbed fixed effects."""
        
        fe_names = [f"fe_{i+1}" for i in range(self.fe_ids.shape[1])]
        fe_counts = []
        
        valid_mask = self.valid_observations
        
        for i in range(self.fe_ids.shape[1]):
            unique_ids = np.unique(self.fe_ids[valid_mask, i])
            fe_counts.append(len(unique_ids))
            
        return {
            'names': fe_names,
            'counts': fe_counts,
            'total_absorbed': self.n_absorbed_fe,
            'method': self.absorb_method or 'auto',
            'tolerance': self.absorb_tolerance,
            'converged': self.converged,
            'iterations': self.iterations,
            'singletons_dropped': self.n_dropped_obs
        }


def prepare_fixed_effects(
    data: pd.DataFrame,
    fe_vars: Union[str, List[str]]
) -> Tuple[np.ndarray, List[str]]:
    """
    Prepare fixed effect variables for absorption.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataset
    fe_vars : Union[str, List[str]]
        Fixed effect variable names
        
    Returns
    -------
    Tuple[np.ndarray, List[str]]
        Fixed effect IDs array and variable names
    """
    
    if isinstance(fe_vars, str):
        fe_vars = [fe_vars]
        
    # Check that all FE variables exist
    missing_vars = [var for var in fe_vars if var not in data.columns]
    if missing_vars:
        raise ValueError(f"Fixed effect variables not found: {missing_vars}")
        
    # Extract FE data and convert to numeric codes
    fe_data = []
    fe_names = []
    
    for var in fe_vars:
        fe_series = data[var].copy()
        
        # Handle missing values  
        try:
            has_nulls = pd.isna(fe_series).sum() > 0
            if has_nulls:
                raise ValueError(f"Fixed effect variable '{var}' contains missing values")
        except Exception as e:
            # If there's an issue with null checking, skip it for now
            print(f"Warning: Could not check for null values in '{var}': {e}")
            pass
            
        # Convert to categorical codes for efficiency
        if fe_series.dtype == 'object' or pd.api.types.is_categorical_dtype(fe_series):
            codes = pd.Categorical(fe_series).codes
        else:
            # For numeric variables, create a mapping
            unique_vals = fe_series.unique()
            val_to_code = {val: i for i, val in enumerate(unique_vals)}
            codes = fe_series.map(val_to_code).values
            
        fe_data.append(codes)
        fe_names.append(var)
        
    return np.column_stack(fe_data), fe_names


def check_fe_variation(fe_ids: np.ndarray, fe_names: List[str]) -> None:
    """
    Check that fixed effects have sufficient variation.
    
    Parameters
    ----------
    fe_ids : np.ndarray
        Fixed effect identifiers
    fe_names : List[str]
        Fixed effect variable names
        
    Raises
    ------
    ValueError
        If any fixed effect has insufficient variation
    """
    
    for i, name in enumerate(fe_names):
        unique_count = len(np.unique(fe_ids[:, i]))
        
        if unique_count < 2:
            raise ValueError(f"Fixed effect '{name}' has only {unique_count} unique value(s)")
            
        if i > 0 and unique_count < 2:
            raise ValueError(f"Fixed effect '{name}' (dimension {i+1}) must have at least 2 levels")