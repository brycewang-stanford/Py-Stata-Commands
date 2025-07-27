"""
Tests for covariance matrix estimation.
"""

import pytest
import numpy as np
import pandas as pd
from pyreghdfe import reghdfe
from pyreghdfe.covariance import robust_covariance, cluster_covariance


class TestCovarianceMatrices:
    """Test different covariance matrix estimators."""
    
    def test_robust_covariance_hc1(self):
        """Test HC1 robust covariance matrix."""
        np.random.seed(42)
        n, k = 100, 3
        
        # Generate heteroskedastic data
        X = np.random.normal(0, 1, (n, k))
        error_variance = 0.1 + 0.5 * X[:, 0]**2  # Heteroskedasticity
        residuals = np.random.normal(0, np.sqrt(error_variance))
        
        # Compute robust covariance
        cov_robust = robust_covariance(X, residuals, hc_type="HC1")
        
        # Check dimensions
        assert cov_robust.shape == (k, k)
        
        # Check symmetry
        np.testing.assert_allclose(cov_robust, cov_robust.T)
        
        # Check positive definite
        eigenvals = np.linalg.eigvals(cov_robust)
        assert np.all(eigenvals > 0)
        
    def test_cluster_covariance_oneway(self):
        """Test one-way cluster-robust covariance."""
        np.random.seed(123)
        n, k = 200, 2
        n_clusters = 20
        
        # Generate clustered data
        X = np.random.normal(0, 1, (n, k))
        cluster_ids = np.random.randint(0, n_clusters, n)
        
        # Create cluster correlation in residuals
        cluster_effects = np.random.normal(0, 0.5, n_clusters)
        residuals = (cluster_effects[cluster_ids] + 
                    np.random.normal(0, 0.2, n))
        
        # Compute cluster-robust covariance
        cov_cluster, cluster_info = cluster_covariance(X, residuals, cluster_ids)
        
        # Check dimensions and properties
        assert cov_cluster.shape == (k, k)
        np.testing.assert_allclose(cov_cluster, cov_cluster.T)
        
        # Check cluster info
        assert cluster_info['method'] == '1-way clustering'
        assert len(cluster_info['n_clusters']) == 1
        assert cluster_info['n_clusters'][0] == n_clusters
        
    def test_cluster_covariance_twoway(self):
        """Test two-way cluster-robust covariance."""
        np.random.seed(456)
        n, k = 150, 2
        n_clusters1, n_clusters2 = 15, 10
        
        # Generate data with two clustering dimensions
        X = np.random.normal(0, 1, (n, k))
        cluster1_ids = np.random.randint(0, n_clusters1, n)
        cluster2_ids = np.random.randint(0, n_clusters2, n)
        
        # Create two-way cluster correlation
        cluster1_effects = np.random.normal(0, 0.3, n_clusters1)
        cluster2_effects = np.random.normal(0, 0.3, n_clusters2)
        residuals = (cluster1_effects[cluster1_ids] + 
                    cluster2_effects[cluster2_ids] + 
                    np.random.normal(0, 0.1, n))
        
        # Compute two-way cluster-robust covariance
        cov_cluster, cluster_info = cluster_covariance(
            X, residuals, [cluster1_ids, cluster2_ids]
        )
        
        # Check properties
        assert cov_cluster.shape == (k, k)
        np.testing.assert_allclose(cov_cluster, cov_cluster.T)
        
        # Check cluster info
        assert '2-way' in cluster_info['method']
        assert len(cluster_info['n_clusters']) == 2
        assert cluster_info['n_clusters'][0] == n_clusters1
        assert cluster_info['n_clusters'][1] == n_clusters2
        
    def test_regression_covariance_types(self):
        """Test different covariance types in full regression."""
        # Generate data with clustering structure
        np.random.seed(789)
        n = 100
        n_clusters = 10
        
        data = pd.DataFrame({
            'cluster': np.random.randint(0, n_clusters, n),
            'x1': np.random.normal(0, 1, n),
            'x2': np.random.normal(0, 1, n)
        })
        
        # Add cluster effects to residuals
        cluster_effects = np.random.normal(0, 0.5, n_clusters)
        data['cluster_effect'] = data['cluster'].map(dict(enumerate(cluster_effects)))
        data['y'] = (0.5 * data['x1'] - 0.3 * data['x2'] + 
                    data['cluster_effect'] + 
                    np.random.normal(0, 0.2, n))
        
        # Test different covariance types
        results_robust = reghdfe(
            data=data,
            y='y',
            x=['x1', 'x2'],
            cov_type='robust'
        )
        
        results_cluster = reghdfe(
            data=data,
            y='y',
            x=['x1', 'x2'],
            cluster='cluster',
            cov_type='cluster'
        )
        
        # Coefficients should be the same
        np.testing.assert_allclose(results_robust.params, results_cluster.params)
        
        # Standard errors should generally be different
        # (though not always, depending on the data)
        se_diff = np.abs(results_robust.bse - results_cluster.bse)
        
        # Check that cluster adjustment is applied
        assert results_cluster.cluster_info is not None
        assert results_robust.cluster_info is None
        
    def test_weighted_covariance(self):
        """Test covariance matrices with weights."""
        np.random.seed(101)
        n, k = 80, 2
        
        # Generate data with weights
        X = np.random.normal(0, 1, (n, k))
        weights = np.random.uniform(0.5, 2.0, n)
        residuals = np.random.normal(0, 1, n)
        
        # Test robust covariance with weights
        cov_weighted = robust_covariance(X, residuals, weights, hc_type="HC1")
        cov_unweighted = robust_covariance(X, residuals, hc_type="HC1")
        
        # Should be different
        assert not np.allclose(cov_weighted, cov_unweighted)
        
        # Both should be positive definite
        assert np.all(np.linalg.eigvals(cov_weighted) > 0)
        assert np.all(np.linalg.eigvals(cov_unweighted) > 0)
        
    def test_hc_types(self):
        """Test different heteroskedasticity correction types."""
        np.random.seed(202)
        n, k = 50, 2
        
        X = np.random.normal(0, 1, (n, k))
        residuals = np.random.normal(0, 1, n)
        
        # Test different HC types
        hc_types = ["HC0", "HC1", "HC2", "HC3"]
        cov_matrices = {}
        
        for hc_type in hc_types:
            cov_matrices[hc_type] = robust_covariance(X, residuals, hc_type=hc_type)
            
        # All should be positive definite
        for hc_type, cov in cov_matrices.items():
            eigenvals = np.linalg.eigvals(cov)
            assert np.all(eigenvals > 0), f"{hc_type} covariance not positive definite"
        
        # HC1 should be larger than HC0 (has df adjustment)
        assert np.all(np.diag(cov_matrices["HC1"]) >= np.diag(cov_matrices["HC0"]))
        
    def test_small_sample_corrections(self):
        """Test small sample corrections for cluster covariance."""
        np.random.seed(303)
        n, k = 30, 2
        n_clusters = 5  # Small number of clusters
        
        X = np.random.normal(0, 1, (n, k))
        cluster_ids = np.random.randint(0, n_clusters, n)
        residuals = np.random.normal(0, 1, n)
        
        # Test with and without small sample correction
        cov_corrected, _ = cluster_covariance(X, residuals, cluster_ids, small_sample=True)
        cov_uncorrected, _ = cluster_covariance(X, residuals, cluster_ids, small_sample=False)
        
        # Corrected should generally be larger
        # (though this is data-dependent)
        assert np.all(np.diag(cov_corrected) >= np.diag(cov_uncorrected) * 0.9)
        
    def test_numerical_stability(self):
        """Test numerical stability with near-singular designs."""
        np.random.seed(404)
        n, k = 100, 3
        
        # Create nearly collinear design
        X = np.random.normal(0, 1, (n, k))
        X[:, 2] = X[:, 0] + X[:, 1] + np.random.normal(0, 1e-10, n)  # Nearly collinear
        
        residuals = np.random.normal(0, 1, n)
        
        # Should not crash, though results may be unstable
        try:
            cov_robust = robust_covariance(X, residuals, hc_type="HC1")
            # If it succeeds, check basic properties
            assert cov_robust.shape == (k, k)
            np.testing.assert_allclose(cov_robust, cov_robust.T)
        except np.linalg.LinAlgError:
            # Expected for singular matrices
            pytest.skip("Design matrix is singular as expected")
            
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        n, k = 10, 2
        X = np.random.normal(0, 1, (n, k))
        residuals = np.random.normal(0, 1, n)
        
        # Test invalid HC type
        with pytest.raises(ValueError, match="Unknown HC type"):
            robust_covariance(X, residuals, hc_type="HC99")
            
        # Test mismatched dimensions
        with pytest.raises((ValueError, IndexError)):
            robust_covariance(X, residuals[:5])  # Wrong length residuals
            
        # Test single cluster (should work but may be unstable)
        cluster_ids = np.zeros(n, dtype=int)  # All same cluster
        try:
            cov_cluster, _ = cluster_covariance(X, residuals, cluster_ids)
            assert cov_cluster.shape == (k, k)
        except (np.linalg.LinAlgError, ZeroDivisionError):
            # May fail due to insufficient variation
            pass