import numpy as np


def perturb_features(X, epsilon: float = 0.08, seed: int = 42):
    rng = np.random.default_rng(seed)
    noise = rng.uniform(-epsilon, epsilon, size=X.shape)
    return np.clip(X + noise, 0.0, np.pi)
