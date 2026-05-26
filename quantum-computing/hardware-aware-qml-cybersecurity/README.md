# Hardware-Aware QML for Cybersecurity (NISQ, No-QRAM)

This project reconstructs the white-paper implementation as a portfolio-ready, standalone experiment folder.

## Scope
- Hybrid classical + quantum pipeline for cybersecurity classification.
- NISQ-compatible design (shallow circuits, restricted gate overhead).
- Explicit **no-QRAM** dependency.
- Baselines and evaluation for:
  - URL maliciousness classification
  - Email-header anomaly classification

## Included
- Feature engineering for URL and email-header records.
- Angle-style and ZZ quantum feature-map experiments.
- VQC with COBYLA/SPSA options.
- Classical RBF-SVM baseline.
- Noise-model experiments (depolarizing noise in Aer simulator).
- Adversarial perturbation harness for feature-space evasion checks.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py --dataset url --csv data/urls_sample.csv --noise
python src/main.py --dataset email --csv data/email_headers_sample.csv --noise --adversarial
```

## Data schema
See `data/schema.md` for required CSV columns.

## Output
Metrics, confusion matrices, and run summaries are written to `results/`.
