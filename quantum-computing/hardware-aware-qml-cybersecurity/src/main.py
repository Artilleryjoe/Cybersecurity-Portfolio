import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from adversarial import perturb_features
from evaluate import metrics
from feature_extract import email_header_features, url_features
from models import build_angle_qsvc, build_classical_svm, build_vqc, build_zz_qsvc
from preprocess import scale_for_quantum_angles


def load_dataset(csv_path: str, dataset: str):
    df = pd.read_csv(csv_path)
    if dataset == "url":
        X = np.array([url_features(url) for url in df["url"].astype(str).tolist()], dtype=float)
    else:
        features = []
        for _, row in df.iterrows():
            features.append(email_header_features(row.to_dict()))
        X = np.array(features, dtype=float)
    y = df["label"].astype(int).to_numpy()
    return X, y


def run(args):
    X_raw, y = load_dataset(args.csv, args.dataset)
    X, _ = scale_for_quantum_angles(X_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42, stratify=y
    )

    results = {}

    angle_qsvc, angle_fmap = build_angle_qsvc(X_train.shape[1])
    angle_qsvc.fit(X_train, y_train)
    angle_pred = angle_qsvc.predict(X_test)
    results["angle_qsvc"] = metrics(y_test, angle_pred)
    results["angle_qsvc"]["circuit_depth"] = angle_fmap.decompose().depth()

    zz_qsvc, zz_fmap = build_zz_qsvc(X_train.shape[1], reps=args.zz_reps)
    zz_qsvc.fit(X_train, y_train)
    zz_pred = zz_qsvc.predict(X_test)
    results["zz_qsvc"] = metrics(y_test, zz_pred)
    results["zz_qsvc"]["circuit_depth"] = zz_fmap.decompose().depth()

    svm = build_classical_svm()
    svm.fit(X_train, y_train)
    svm_pred = svm.predict(X_test)
    results["rbf_svm"] = metrics(y_test, svm_pred)

    if args.vqc:
        vqc = build_vqc(X_train.shape[1], optimizer_name=args.optimizer, maxiter=args.maxiter)
        vqc.fit(X_train, y_train)
        vqc_pred = vqc.predict(X_test)
        results["vqc"] = metrics(y_test, vqc_pred)

    if args.adversarial:
        X_test_adv = perturb_features(X_test, epsilon=args.epsilon)
        angle_adv_pred = angle_qsvc.predict(X_test_adv)
        results["angle_qsvc_adversarial"] = metrics(y_test, angle_adv_pred)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_file = out_dir / f"results_{args.dataset}.json"
    output_file.write_text(json.dumps(results, indent=2))

    print(json.dumps(results, indent=2))
    print(f"Saved results to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hardware-aware QML cybersecurity experiments")
    parser.add_argument("--dataset", choices=["url", "email"], required=True)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--test-size", type=float, default=0.33)
    parser.add_argument("--zz-reps", type=int, default=2)
    parser.add_argument("--vqc", action="store_true")
    parser.add_argument("--optimizer", default="COBYLA", choices=["COBYLA", "SPSA"])
    parser.add_argument("--maxiter", type=int, default=100)
    parser.add_argument("--adversarial", action="store_true")
    parser.add_argument("--epsilon", type=float, default=0.08)
    parser.add_argument("--noise", action="store_true", help="Reserved flag for future Aer primitive wiring")
    parser.add_argument("--output", default="results")
    run(parser.parse_args())
