#!/usr/bin/env python3
"""
anomaly_detection.py
Prototype anomaly detection tool using scikit-learn's IsolationForest.
Generates synthetic data, trains a model, and flags anomalies.
"""

import argparse
from typing import Tuple

import numpy as np
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
except ModuleNotFoundError as e:
    raise SystemExit("scikit-learn is required to run this script") from e


def generate_data(n_samples: int = 1000, n_anomalies: int = 50) -> Tuple[np.ndarray, np.ndarray]:
    """Generate synthetic dataset with injected anomalies.

    Parameters
    ----------
    n_samples: int
        Number of normal data points to generate.
    n_anomalies: int
        Number of anomaly points to inject.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Feature matrix and label array where 1 indicates anomaly.
    """
    rng = np.random.RandomState(42)
    normal_data = rng.normal(loc=0.0, scale=1.0, size=(n_samples, 2))
    anomalies = rng.uniform(low=-6, high=6, size=(n_anomalies, 2))

    X = np.vstack([normal_data, anomalies])
    y = np.hstack([np.zeros(n_samples), np.ones(n_anomalies)])
    return X, y


def preprocess(X: np.ndarray) -> np.ndarray:
    """Scale features to zero mean and unit variance.

    Parameters
    ----------
    X: np.ndarray
        Raw feature matrix.

    Returns
    -------
    np.ndarray
        Scaled feature matrix.
    """
    scaler = StandardScaler()
    return scaler.fit_transform(X)


def train_model(X: np.ndarray) -> IsolationForest:
    """Train IsolationForest on the provided dataset.

    Parameters
    ----------
    X: np.ndarray
        Preprocessed feature matrix.

    Returns
    -------
    IsolationForest
        Trained anomaly detection model.
    """
    model = IsolationForest(random_state=42, contamination=0.05)
    model.fit(X)
    return model


def detect(model: IsolationForest, X: np.ndarray) -> np.ndarray:
    """Use the trained model to predict anomalies.

    Parameters
    ----------
    model: IsolationForest
        Trained IsolationForest model.
    X: np.ndarray
        Feature matrix to evaluate.

    Returns
    -------
    np.ndarray
        Array of anomaly predictions (1 for anomaly, 0 for normal).
    """
    preds = model.predict(X)
    # IsolationForest returns -1 for anomaly, 1 for normal
    return np.where(preds == -1, 1, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prototype anomaly detection with IsolationForest")
    parser.add_argument("--samples", type=int, default=1000, help="Number of normal samples")
    parser.add_argument("--anomalies", type=int, default=50, help="Number of anomalies")
    args = parser.parse_args()

    X, y_true = generate_data(args.samples, args.anomalies)
    X_scaled = preprocess(X)
    model = train_model(X_scaled)
    y_pred = detect(model, X_scaled)

    detected = int(y_pred.sum())
    print(f"Detected {detected} anomalies out of {len(y_true)} total points")


if __name__ == "__main__":
    main()
