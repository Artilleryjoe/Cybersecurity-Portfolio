#!/usr/bin/env python3
"""
anomaly_detection.py
Prototype anomaly detection tool using scikit-learn's IsolationForest.
Generates synthetic data, trains a model, and flags anomalies.
"""

import argparse
import json
from pathlib import Path
from typing import Optional, Tuple

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


def train_model(X: np.ndarray, *, contamination: float = 0.05, random_state: int = 42) -> IsolationForest:
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
    model = IsolationForest(random_state=random_state, contamination=contamination)
    model.fit(X)
    return model


def detect(model: IsolationForest, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
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
    scores = model.decision_function(X)
    # IsolationForest returns -1 for anomaly, 1 for normal
    return np.where(preds == -1, 1, 0), scores


def load_dataset_from_csv(path: Path) -> np.ndarray:
    """Load a numeric dataset from CSV, automatically skipping headers."""

    try:
        data = np.loadtxt(path, delimiter=",", ndmin=2)
    except ValueError:
        data = np.loadtxt(path, delimiter=",", ndmin=2, skiprows=1)
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    return data


def summarize_results(preds: np.ndarray, scores: np.ndarray, labels: Optional[np.ndarray]) -> dict:
    """Return human-friendly metrics for CLI output and JSON export."""

    total = preds.size
    anomalies = int(preds.sum())
    summary = {
        "total_samples": int(total),
        "detected_anomalies": anomalies,
        "detection_rate": round(anomalies / total, 4) if total else 0.0,
        "score_range": [float(scores.min()), float(scores.max())],
    }
    if labels is not None and labels.size == preds.size:
        tp = int(((preds == 1) & (labels == 1)).sum())
        fp = int(((preds == 1) & (labels == 0)).sum())
        fn = int(((preds == 0) & (labels == 1)).sum())
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        summary.update(
            {
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "true_positives": tp,
                "false_positives": fp,
            }
        )
    return summary


def export_findings(path: Path, X: np.ndarray, preds: np.ndarray, scores: np.ndarray, top_n: int) -> None:
    """Persist the most suspicious points to disk for later review."""

    suspicious_idx = np.where(preds == 1)[0]
    sorted_idx = suspicious_idx[np.argsort(scores[suspicious_idx])]
    top_idx = sorted_idx[:top_n]
    payload = [
        {
            "index": int(idx),
            "score": float(scores[idx]),
            "vector": X[idx].tolist(),
        }
        for idx in top_idx
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prototype anomaly detection with IsolationForest")
    parser.add_argument("--samples", type=int, default=1000, help="Number of normal samples")
    parser.add_argument("--anomalies", type=int, default=50, help="Number of anomalies")
    parser.add_argument("--input", type=Path, help="CSV file with telemetry to analyze")
    parser.add_argument("--export", type=Path, help="Write the top anomalies to a JSON file")
    parser.add_argument("--top", type=int, default=20, help="Number of anomalies to export (default: 20)")
    parser.add_argument(
        "--contamination",
        type=float,
        default=0.05,
        help="Approximate expected fraction of anomalies (0 < c <= 0.5)",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    if args.input:
        X = load_dataset_from_csv(args.input)
        y_true = None
    else:
        X, y_true = generate_data(args.samples, args.anomalies)

    X_scaled = preprocess(X)
    model = train_model(X_scaled, contamination=args.contamination, random_state=args.seed)
    y_pred, scores = detect(model, X_scaled)
    summary = summarize_results(y_pred, scores, y_true)
    print(json.dumps(summary, indent=2))

    if args.export:
        export_findings(args.export, X_scaled, y_pred, scores, args.top)
        print(f"[+] Top anomalies exported to {args.export}")


if __name__ == "__main__":
    main()
