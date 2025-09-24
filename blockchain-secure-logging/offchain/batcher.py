"""Batch logs, compute Merkle roots, and anchor them on-chain.

This module sketches the core pipeline without implementing chain
transaction submission. It focuses on demonstrating how logs should be
canonicalized, hashed, and assembled into batches. Future work can plug
in Web3.py calls where indicated.

Usage example::

    python offchain/batcher.py \
        --config offchain/config.yaml \
        --batch-id 2025-09-23T19:00Z_authsvc_0001

"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Sequence

import yaml

from . import merkle
from .schemas import BatchMeta, LogEntry


@dataclass
class BatchInputs:
    """Normalized data ready for hashing."""

    entries: List[LogEntry]
    prev_root: str | None


def load_config(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_jsonl(path: pathlib.Path) -> Iterable[LogEntry]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            yield LogEntry.parse_raw(line)


def gather_entries(config: dict) -> BatchInputs:
    entries: List[LogEntry] = []
    for source in config.get("sources", []):
        source_path = pathlib.Path(source["path"])
        entries.extend(read_jsonl(source_path))
    prev_root = config.get("state", {}).get("prev_merkle_root")
    entries.sort(key=lambda e: e.ts)
    return BatchInputs(entries=entries, prev_root=prev_root)


def build_manifest(batch_id: str, entries: Sequence[LogEntry], prev_root: str | None) -> dict:
    leaves = [merkle.leaf_hash(entry) for entry in entries]
    root = merkle.merkle_root(leaves)
    batch_meta = BatchMeta(
        batch_id=batch_id,
        count=len(entries),
        window_start=entries[0].ts if entries else datetime.now(timezone.utc),
        window_end=entries[-1].ts if entries else datetime.now(timezone.utc),
        prev_merkle_root=prev_root,
        root="0x" + root.hex(),
    )

    manifest = {
        "batch": json.loads(batch_meta.json()),
        "leaves": [leaf.hex() for leaf in leaves],
        "proofs": {},
    }
    return manifest


def persist_manifest(manifest: dict, batch_id: str, out_dir: pathlib.Path) -> pathlib.Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / f"{batch_id}.manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    return manifest_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=pathlib.Path, required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--manifest-dir", type=pathlib.Path, default=pathlib.Path("manifests"))
    args = parser.parse_args(argv)

    config = load_config(args.config)
    batch_inputs = gather_entries(config)

    if not batch_inputs.entries:
        print("No entries to batch", file=sys.stderr)
        return 1

    manifest = build_manifest(args.batch_id, batch_inputs.entries, batch_inputs.prev_root)
    manifest_path = persist_manifest(manifest, args.batch_id, args.manifest_dir)
    print(f"Manifest written to {manifest_path}")

    # TODO: Submit transaction via Web3.py or raw transaction pattern.
    # Placeholder for signing logic to keep scaffolding minimal.

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
