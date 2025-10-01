"""Minimal orchestration client for the Blockchain Secure Logging API."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

API_ROOT = "http://localhost:8000/api/v1"


def _pretty_print(title: str, payload: Dict[str, Any]) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2))


@dataclass
class BatchContext:
    batch_id: str
    manifest_path: str
    root: str
    prev_root: Optional[str]


def generate_batch(batch_id: str) -> BatchContext:
    response = requests.post(
        f"{API_ROOT}/batches",
        json={"batch_id": batch_id},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    _pretty_print("Batch Generated", data)
    return BatchContext(
        batch_id=data["batch_id"],
        manifest_path=data["manifest_path"],
        root=data["root"],
        prev_root=data.get("prev_merkle_root"),
    )


def anchor_batch(context: BatchContext) -> str:
    response = requests.post(
        f"{API_ROOT}/anchors",
        json={"batch_id": context.batch_id, "merkle_root": context.root},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    _pretty_print("Anchor Submitted", data)
    return data["tx_hash"]


def verify_batch(context: BatchContext, tx_hash: str) -> None:
    response = requests.post(
        f"{API_ROOT}/verifications",
        json={"batch_id": context.batch_id, "log_entry": {}},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    data.setdefault("tx_hash", tx_hash)
    _pretty_print("Verification Result", data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python api/orchestrate_stub.py <batch_id>", file=sys.stderr)
        raise SystemExit(1)

    ctx = generate_batch(sys.argv[1])
    tx = anchor_batch(ctx)
    verify_batch(ctx, tx)
