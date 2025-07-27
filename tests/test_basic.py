"""
Basic tests for PyRegHDFE functionality.
"""

import pytest
import numpy as np
import pandas as pd
from pyreghdfe import reghdfe


class TestBasicFunctionality:
    """Test basic regression functionality."""
    
    def test_import(self):
        """Test that package imports correctly."""
        from pyreghdfe import reghdfe, RegressionResults, __version__
        assert callable(reghdfe)
        assert __version__ == "0.1.0"
        
    def test_simple_ols_no_fe(self):
        """Test OLS regression without fixed effects."""
        # Generate simple test data
        np.random.seed(42)
        n = 100
        
        data = pd.DataFrame({
            'y': np.random.normal(0, 1, n),
            'x1': np.random.normal(0, 1, n),
            'x2': np.random.normal(0, 1, n)
        })
        
        # Add true relationship
        data['y'] = 1.0 + 0.5 * data['x1'] - 0.3 * data['x2'] + np.random.normal(0, 0.1, n)
        
        # Estimate model
        results = reghdfe(
            data=data,
            y='y',
            x=['x1', 'x2']
        )
        
        # Basic checks
        assert len(results.params) == 2
        assert 'x1' in results.params.index
        assert 'x2' in results.params.index
        assert results.nobs == n
        assert results.df_resid == n - 2
        assert 0 <= results.rsquared <= 1
        
        # Check that coefficients are roughly correct
        assert abs(results.params['x1'] - 0.5) < 0.1
        assert abs(results.params['x2'] - (-0.3)) < 0.1
        
    def test_simple_fe_regression(self):
        """Test regression with single fixed effect."""
        # Generate test data with fixed effects
        np.random.seed(123)
        n = 200
        n_groups = 10
        
        data = pd.DataFrame({
            'group': np.random.randint(0, n_groups, n),
            'x': np.random.normal(0, 1, n),
        })
        
        # Add group fixed effects
        group_effects = np.random.normal(0, 1, n_groups)
        data['alpha'] = data['group'].map(dict(enumerate(group_effects)))
        data['y'] = data['alpha'] + 0.8 * data['x'] + np.random.normal(0, 0.2, n)
        
        # Estimate with fixed effects
        results = reghdfe(
            data=data,
            y='y',
            x='x',
            fe='group'
        )
        
        # Check results
        assert len(results.params) == 1
        assert 'x' in results.params.index
        assert results.fe_info['names'] == ['group']
        assert abs(results.params['x'] - 0.8) < 0.1
        
    def test_cluster_robust_se(self):
        """Test cluster-robust standard errors."""
        # Generate clustered data
        np.random.seed(456)
        n = 150
        n_clusters = 15
        
        data = pd.DataFrame({
            'cluster': np.random.randint(0, n_clusters, n),
            'x': np.random.normal(0, 1, n),
        })
        
        # Add cluster correlation
        cluster_effects = np.random.normal(0, 0.5, n_clusters)
        data['cluster_effect'] = data['cluster'].map(dict(enumerate(cluster_effects)))
        data['y'] = 0.6 * data['x'] + data['cluster_effect'] + np.random.normal(0, 0.3, n)
        
        # Estimate with cluster-robust SE
        results = reghdfe(
            data=data,
            y='y',
            x='x',
            cluster='cluster',
            cov_type='cluster'
        )
        
        # Check that clustering info is stored
        assert results.cluster_info is not None
        assert '1-way' in results.cluster_info['method']
        assert len(results.cluster_info['n_clusters']) == 1
        assert results.cluster_info['n_clusters'][0] == n_clusters
        
    def test_weights(self):
        """Test weighted regression."""
        np.random.seed(789)
        n = 100
        
        data = pd.DataFrame({
            'y': np.random.normal(1, 1, n),
            'x': np.random.normal(0, 1, n),
            'weight': np.random.uniform(0.5, 2.0, n)
        })
        
        # True relationship
        data['y'] = 0.7 * data['x'] + np.random.normal(0, 0.2, n)
        
        # Estimate with weights
        results = reghdfe(
            data=data,
            y='y',
            x='x',
            weights='weight'
        )
        
        assert results.weights_info is not None
        assert results.weights_info['variable'] == 'weight'
        assert abs(results.params['x'] - 0.7) < 0.2
        
    def test_summary_output(self):
        """Test that summary output is generated correctly."""
        np.random.seed(101)
        n = 50
        
        data = pd.DataFrame({
            'y': np.random.normal(0, 1, n),
            'x1': np.random.normal(0, 1, n),
            'x2': np.random.normal(0, 1, n),
            'fe': np.random.randint(0, 5, n)
        })
        
        data['y'] = 0.4 * data['x1'] - 0.2 * data['x2'] + np.random.normal(0, 0.1, n)
        
        results = reghdfe(
            data=data,
            y='y',
            x=['x1', 'x2'],
            fe='fe'
        )
        
        summary = results.summary()
        
        # Check that summary contains expected elements
        assert 'HDFE Linear regression' in summary
        assert 'Number of obs' in summary
        assert 'R-squared' in summary
        assert 'Within R-sq' in summary
        assert 'x1' in summary
        assert 'x2' in summary
        assert 'Fixed effects:' in summary
        
    def test_error_handling(self):
        """Test that appropriate errors are raised for invalid inputs."""
        data = pd.DataFrame({
            'y': [1, 2, 3],
            'x': [1, 2, 3]
        })
        
        # Test missing variable
        with pytest.raises(ValueError, match="Variables not found"):
            reghdfe(data=data, y='y', x='missing_var')
            
        # Test empty data
        with pytest.raises(ValueError):
            reghdfe(data=pd.DataFrame(), y='y', x='x')
            
        # Test invalid cov_type
        with pytest.raises(ValueError, match="cluster variables must be specified"):
            reghdfe(data=data, y='y', x='x', cov_type='cluster')


class TestDataGeneration:
    """Helper methods for generating test data."""
    
    @staticmethod
    def generate_panel_data(n_units=50, n_time=10, n_x_vars=3, seed=42):
        """Generate balanced panel data with unit and time fixed effects."""
        np.random.seed(seed)
        
        # Create panel structure
        units = np.repeat(range(n_units), n_time)
        time = np.tile(range(n_time), n_units)
        n_obs = n_units * n_time
        
        # Generate regressors
        X = np.random.normal(0, 1, (n_obs, n_x_vars))
        
        # True coefficients
        beta = np.array([0.5, -0.3, 0.8])
        
        # Unit and time fixed effects
        unit_fe = np.random.normal(0, 1, n_units)
        time_fe = np.random.normal(0, 0.5, n_time)
        
        # Generate dependent variable
        y = (X @ beta + 
             unit_fe[units] + 
             time_fe[time] + 
             np.random.normal(0, 0.2, n_obs))
        
        # Create DataFrame
        data = pd.DataFrame({
            'y': y,
            'unit': units,
            'time': time
        })
        
        for i in range(n_x_vars):
            data[f'x{i+1}'] = X[:, i]
            
        return data, beta
        
    def test_panel_data_estimation(self):
        """Test estimation on panel data with two-way fixed effects."""
        data, true_beta = self.generate_panel_data(n_units=30, n_time=8, n_x_vars=2)
        
        results = reghdfe(
            data=data,
            y='y',
            x=['x1', 'x2'],
            fe=['unit', 'time']
        )
        
        # Check that we recover true coefficients reasonably well
        assert abs(results.params['x1'] - true_beta[0]) < 0.1
        assert abs(results.params['x2'] - true_beta[1]) < 0.1
        
        # Check fixed effects info
        assert len(results.fe_info['names']) == 2
        assert 'unit' in results.fe_info['names']
        assert 'time' in results.fe_info['names']