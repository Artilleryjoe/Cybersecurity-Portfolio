# Enterprise Anomaly Detection Pipeline

The prototype IsolationForest demo has been rebuilt into an enterprise-ready
workflow that supports repeatable training, model promotion, CI-ready demos,
and automated reporting/export controls.

## Highlights

- **Dedicated CLI subcommands** for `train`, `score`, and `demo` operations.
- **Config-driven deployments** via YAML/JSON (contamination, estimator count,
  severity bands, etc.).
- **Model lifecycle management** – persist and reload scaler/model bundles with
  `joblib` for deterministic scoring across environments.
- **Operational exports** – JSON (top N anomalies), CSV scorecards, and summary
  reports for SIEM/SOAR ingestion.
- **Severity orchestration** – percentile-based `critical/high/medium/info`
  bucketing with optional score floors for alert routing.
- **Telemetry flexibility** – accepts labeled or unlabeled CSV telemetry with a
  configurable delimiter.

## Installation

From the repo root:

```bash
pip install -r Security_Scripts/requirements.txt
```

PyYAML is optional unless you plan to load YAML configs:

```bash
pip install pyyaml
```

## Example Config

```yaml
contamination: 0.015
n_estimators: 400
max_samples: auto
random_state: 1337
severity_bands: [0.005, 0.02, 0.1]
score_floor: -0.3
```

Save the file (e.g., `configs/anomaly.yaml`) and reference it via
`--config configs/anomaly.yaml`.

## Usage

### Train a Model

```bash
python anomaly_detection.py train \
  --input data/baseline.csv \
  --labels data/baseline_labels.csv \
  --config configs/anomaly.yaml \
  --model-out artifacts/isoforest.joblib \
  --export-json exports/top.json \
  --export-csv exports/scorecard.csv \
  --report exports/train-summary.json
```

### Score New Telemetry

```bash
python anomaly_detection.py score \
  --input data/prod_batch.csv \
  --model artifacts/isoforest.joblib \
  --export-json exports/prod-top.json \
  --export-csv exports/prod-scorecard.csv \
  --report exports/prod-summary.json
```

If you provide `--labels`, precision/recall metrics will be appended to the
report for validation or offline testing.

### Synthetic Demo / CI Smoke Test

```bash
python anomaly_detection.py demo \
  --samples 5000 \
  --anomalies 200 \
  --export-json exports/demo-top.json \
  --report exports/demo-summary.json
```

Add `--persist artifacts/demo.joblib` to create a reference model for pipeline
checks or to validate downstream integrations.

## Output Artifacts

| Artifact        | Description                                                        |
|-----------------|--------------------------------------------------------------------|
| JSON export     | Top-N anomalous records (index, score, severity, feature vector).   |
| CSV scorecard   | Full dataset with per-row severity and `is_anomaly` flag.           |
| Summary report  | Metrics (counts, detection rate, precision/recall, config values).  |
| Model artifacts | Joblib bundle containing the fitted scaler, model, and config.      |

## Operational Notes

- Scores closer to zero are more benign; the CLI automatically ranks anomalies
  and applies severity bands for triage.
- `--delimiter` lets you ingest TSV or pipe-delimited telemetry without
  modifying source files.
- Logging is standardized (`--log-level DEBUG|INFO|...`) for easy integration
  with existing observability stacks.

## Roadmap Ideas

- Pluggable detectors (e.g., LOF, autoencoders) behind the same config schema.
- Kafka/Kinesis stream adapters for real-time enrichment.
- Metrics forwarding (Prometheus/OpenTelemetry) for SOC dashboards.
