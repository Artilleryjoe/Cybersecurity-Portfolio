#!/usr/bin/env python3
"""Enterprise-ready anomaly detection pipeline built on IsolationForest."""

from __future__ import annotations

import argparse
import csv
import json
import logging
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    from joblib import dump, load
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
except ModuleNotFoundError as exc:  # pragma: no cover - enforced by runtime
    raise SystemExit("scikit-learn and joblib are required to run this script") from exc

try:  # optional dependency for YAML config parsing
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional
    yaml = None


LOGGER = logging.getLogger("anomaly_detection")


def configure_logging(level: str) -> None:
    """Configure module-level logging."""

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(message)s",
    )


@dataclass
class DetectionConfig:
    """Model and severity parameters for the anomaly pipeline."""

    contamination: float = 0.02
    n_estimators: int = 300
    max_samples: str | int = "auto"
    random_state: int = 42
    severity_bands: Tuple[float, float, float] = (0.01, 0.05, 0.15)
    score_floor: Optional[float] = None

    @classmethod
    def from_mapping(cls, mapping: Dict[str, object]) -> "DetectionConfig":
        known_fields = {field.name for field in fields(cls)}
        filtered = {k: v for k, v in mapping.items() if k in known_fields}
        return cls(**filtered)

    def to_dict(self) -> Dict[str, object]:
        return {
            "contamination": self.contamination,
            "n_estimators": self.n_estimators,
            "max_samples": self.max_samples,
            "random_state": self.random_state,
            "severity_bands": self.severity_bands,
            "score_floor": self.score_floor,
        }


@dataclass
class PipelineArtifacts:
    """Serializable bundle holding everything needed to score telemetry."""

    scaler: StandardScaler
    model: IsolationForest
    config: DetectionConfig = field(default_factory=DetectionConfig)


def generate_data(n_samples: int = 1000, n_anomalies: int = 50) -> Tuple[np.ndarray, np.ndarray]:
    """Generate synthetic dataset with injected anomalies."""

    rng = np.random.RandomState(42)
    normal_data = rng.normal(loc=0.0, scale=1.0, size=(n_samples, 4))
    anomalies = rng.uniform(low=-8, high=8, size=(n_anomalies, 4))

    X = np.vstack([normal_data, anomalies])
    y = np.hstack([np.zeros(n_samples), np.ones(n_anomalies)])
    return X, y


def preprocess(X: np.ndarray, scaler: Optional[StandardScaler] = None) -> Tuple[np.ndarray, StandardScaler]:
    """Scale features to zero mean and unit variance."""

    scaler = scaler or StandardScaler()
    return scaler.fit_transform(X), scaler


def train_model(X: np.ndarray, *, config: DetectionConfig) -> IsolationForest:
    """Train IsolationForest on the provided dataset."""

    model = IsolationForest(
        random_state=config.random_state,
        contamination=config.contamination,
        n_estimators=config.n_estimators,
        max_samples=config.max_samples,
    )
    model.fit(X)
    return model


def detect(model: IsolationForest, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Use the trained model to predict anomalies."""

    preds = model.predict(X)
    scores = model.decision_function(X)
    return np.where(preds == -1, 1, 0), scores


def load_dataset_from_csv(path: Path, *, delimiter: str = ",") -> np.ndarray:
    """Load a numeric dataset from CSV, automatically skipping headers."""

    LOGGER.info("Loading telemetry from %s", path)
    try:
        data = np.loadtxt(path, delimiter=delimiter, ndmin=2)
    except ValueError:
        data = np.loadtxt(path, delimiter=delimiter, ndmin=2, skiprows=1)
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    return data


def load_labels_from_csv(path: Path, *, delimiter: str = ",") -> np.ndarray:
    """Load label vector with optional header."""

    LOGGER.info("Loading label vector from %s", path)
    try:
        data = np.loadtxt(path, delimiter=delimiter, ndmin=1)
    except ValueError:
        data = np.loadtxt(path, delimiter=delimiter, ndmin=1, skiprows=1)
    if data.ndim > 1:
        data = data[:, 0]
    return data.astype(int)


def summarize_results(
    preds: np.ndarray,
    scores: np.ndarray,
    labels: Optional[np.ndarray],
    *,
    config: DetectionConfig,
    mode: str,
) -> Dict[str, object]:
    """Return human-friendly metrics for CLI output and JSON export."""

    total = preds.size
    anomalies = int(preds.sum())
    summary: Dict[str, object] = {
        "mode": mode,
        "total_samples": int(total),
        "detected_anomalies": anomalies,
        "detection_rate": round(anomalies / total, 4) if total else 0.0,
        "score_range": [float(scores.min()), float(scores.max())],
        "config": config.to_dict(),
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
    if config.score_floor is not None:
        summary["score_floor"] = config.score_floor
    return summary


def severity_labels(scores: np.ndarray, config: DetectionConfig) -> List[str]:
    """Map anomaly scores to qualitative severity buckets."""

    order = np.argsort(scores)
    percentiles = np.empty_like(scores, dtype=float)
    percentiles[order] = np.linspace(0, 1, len(scores), endpoint=False)
    critical, high, medium = config.severity_bands

    def bucket(pct: float) -> str:
        if pct <= critical:
            return "critical"
        if pct <= high:
            return "high"
        if pct <= medium:
            return "medium"
        return "info"

    return [bucket(pct) for pct in percentiles]


def export_findings(
    path: Path,
    X: np.ndarray,
    preds: np.ndarray,
    scores: np.ndarray,
    severity: Sequence[str],
    top_n: int,
) -> None:
    """Persist the most suspicious points to disk for later review."""

    suspicious_idx = np.where(preds == 1)[0]
    if suspicious_idx.size == 0:
        LOGGER.warning("No anomalies detected, skipping export to %s", path)
        return
    sorted_idx = suspicious_idx[np.argsort(scores[suspicious_idx])]
    top_idx = sorted_idx[:top_n]
    payload = [
        {
            "index": int(idx),
            "score": float(scores[idx]),
            "severity": severity[idx],
            "vector": X[idx].tolist(),
        }
        for idx in top_idx
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    LOGGER.info("Exported %d anomalies to %s", len(payload), path)


def export_csv(path: Path, preds: np.ndarray, scores: np.ndarray, severity: Sequence[str]) -> None:
    """Export all scored points with severity in CSV format."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as csv_handle:
        writer = csv.DictWriter(csv_handle, fieldnames=["index", "score", "severity", "is_anomaly"])
        writer.writeheader()
        for idx, (score, sev, pred) in enumerate(zip(scores, severity, preds)):
            writer.writerow(
                {
                    "index": idx,
                    "score": float(score),
                    "severity": sev,
                    "is_anomaly": int(pred),
                }
            )
    LOGGER.info("Wrote CSV export to %s", path)


def write_report(path: Path, summary: Dict[str, object]) -> None:
    """Serialize summary JSON to disk."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    LOGGER.info("Report written to %s", path)


def persist_artifacts(path: Path, artifacts: PipelineArtifacts) -> None:
    """Persist the trained scaler, model, and config."""

    path.parent.mkdir(parents=True, exist_ok=True)
    dump(artifacts, path)
    LOGGER.info("Model artifacts saved to %s", path)


def load_artifacts(path: Path) -> PipelineArtifacts:
    """Load persisted scaler, model, and config bundle."""

    artifacts = load(path)
    if not isinstance(artifacts, PipelineArtifacts):  # pragma: no cover - runtime safety
        raise ValueError("Model file does not contain expected PipelineArtifacts")
    LOGGER.info("Loaded model artifacts from %s", path)
    return artifacts


def load_config(path: Optional[Path], fallback: Optional[DetectionConfig] = None) -> DetectionConfig:
    """Load configuration from YAML/JSON. If absent, fallback to defaults."""

    if path is None:
        return fallback or DetectionConfig()
    if not path.exists():
        raise FileNotFoundError(f"Config file {path} not found")
    raw: Dict[str, object]
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise SystemExit("PyYAML is required to parse YAML configs")
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        raw = json.loads(path.read_text(encoding="utf-8"))
    return DetectionConfig.from_mapping(raw)


def run_train(args: argparse.Namespace) -> None:
    """Train a model from supplied telemetry and persist artifacts."""

    config = load_config(args.config)
    X = load_dataset_from_csv(args.input, delimiter=args.delimiter)
    y_true = load_labels_from_csv(args.labels, delimiter=args.delimiter) if args.labels else None
    X_scaled, scaler = preprocess(X)
    model = train_model(X_scaled, config=config)
    preds, scores = detect(model, X_scaled)
    severity = severity_labels(scores, config)
    summary = summarize_results(preds, scores, y_true, config=config, mode="train")
    print(json.dumps(summary, indent=2))
    persist_artifacts(args.model_out, PipelineArtifacts(scaler=scaler, model=model, config=config))
    _maybe_export(args, X, preds, scores, severity, summary)


def run_score(args: argparse.Namespace) -> None:
    """Score telemetry with a persisted model."""

    artifacts = load_artifacts(args.model)
    config = load_config(args.config, artifacts.config)
    X = load_dataset_from_csv(args.input, delimiter=args.delimiter)
    y_true = load_labels_from_csv(args.labels, delimiter=args.delimiter) if args.labels else None
    X_scaled = artifacts.scaler.transform(X)
    preds, scores = detect(artifacts.model, X_scaled)
    severity = severity_labels(scores, config)
    summary = summarize_results(preds, scores, y_true, config=config, mode="score")
    print(json.dumps(summary, indent=2))
    _maybe_export(args, X, preds, scores, severity, summary)


def run_demo(args: argparse.Namespace) -> None:
    """Synthetic data harness for tabletop exercises and CI validation."""

    config = load_config(args.config)
    X, y_true = generate_data(args.samples, args.anomalies)
    X_scaled, scaler = preprocess(X)
    model = train_model(X_scaled, config=config)
    preds, scores = detect(model, X_scaled)
    severity = severity_labels(scores, config)
    summary = summarize_results(preds, scores, y_true, config=config, mode="demo")
    print(json.dumps(summary, indent=2))
    if args.persist:
        persist_artifacts(args.persist, PipelineArtifacts(scaler=scaler, model=model, config=config))
    _maybe_export(args, X, preds, scores, severity, summary)


def _maybe_export(
    args: argparse.Namespace,
    X: np.ndarray,
    preds: np.ndarray,
    scores: np.ndarray,
    severity: Sequence[str],
    summary: Dict[str, object],
) -> None:
    """Common export helper across train/score/demo."""

    if getattr(args, "export_json", None):
        export_findings(args.export_json, X, preds, scores, severity, args.top)
    if getattr(args, "export_csv", None):
        export_csv(args.export_csv, preds, scores, severity)
    if getattr(args, "report", None):
        write_report(args.report, summary)


def build_parser() -> argparse.ArgumentParser:
    """Create CLI parser with enterprise subcommands."""

    parser = argparse.ArgumentParser(description="Enterprise anomaly detection with IsolationForest")
    parser.add_argument("--log-level", default="INFO", help="Python logging level (default: INFO)")
    parser.add_argument(
        "--delimiter",
        default=",",
        help="Column delimiter for CSV/label files (default: ',')",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Train and persist a model from telemetry")
    train_parser.add_argument("--input", type=Path, required=True, help="CSV file with telemetry vectors")
    train_parser.add_argument("--labels", type=Path, help="Optional CSV file with 0/1 labels")
    train_parser.add_argument("--config", type=Path, help="YAML/JSON config for the detector")
    train_parser.add_argument("--model-out", type=Path, required=True, help="Path to persist trained model")
    _add_common_outputs(train_parser)
    train_parser.set_defaults(func=run_train)

    score_parser = subparsers.add_parser("score", help="Score telemetry using a saved model")
    score_parser.add_argument("--input", type=Path, required=True, help="CSV file with telemetry vectors")
    score_parser.add_argument("--labels", type=Path, help="Optional CSV file with 0/1 labels for evaluation")
    score_parser.add_argument("--config", type=Path, help="Override severity/config during scoring")
    score_parser.add_argument("--model", type=Path, required=True, help="Path to persisted model artifacts")
    _add_common_outputs(score_parser)
    score_parser.set_defaults(func=run_score)

    demo_parser = subparsers.add_parser("demo", help="Generate synthetic data for tabletop demos")
    demo_parser.add_argument("--samples", type=int, default=2000, help="Number of baseline samples")
    demo_parser.add_argument("--anomalies", type=int, default=100, help="Number of synthetic anomalies")
    demo_parser.add_argument("--config", type=Path, help="Optional config file for demo")
    demo_parser.add_argument(
        "--persist",
        type=Path,
        help="Persist the synthetic model artifacts for CI smoke-tests",
    )
    _add_common_outputs(demo_parser)
    demo_parser.set_defaults(func=run_demo)

    return parser


def _add_common_outputs(sub_parser: argparse.ArgumentParser) -> None:
    """Attach shared output arguments to a subcommand parser."""

    sub_parser.add_argument("--export-json", type=Path, help="Write top anomalies to JSON file")
    sub_parser.add_argument(
        "--export-csv",
        type=Path,
        help="Export full scorecard as CSV (index, score, severity, is_anomaly)",
    )
    sub_parser.add_argument("--report", type=Path, help="Persist summary metrics to JSON")
    sub_parser.add_argument("--top", type=int, default=25, help="Number of anomalies to capture in JSON export")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(args.log_level)
    args.func(args)


if __name__ == "__main__":
    main()
