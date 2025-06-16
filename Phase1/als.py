# ALS algorithm for matrix factorization

import numpy as np

def als(R, K, steps=1000, alpha=0.01, beta=0.01):
    """
    ALS algorithm for matrix factorization
    """
    M, N = R.shape
    P = np.random.rand(M, K)
    Q = np.random.rand(N, K)