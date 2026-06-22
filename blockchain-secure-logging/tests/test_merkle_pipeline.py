"""Regression tests for the Merkle batching pipeline.

These tests give stakeholders and hiring panels confidence that the sample
fixtures exercise deterministic hashing and tamper detection logic.
"""

from __future__ import annotations

import pathlib

import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from offchain import merkle
from offchain.batcher import build_manifest
from offchain.schemas import LogEntry

SAMPLE_LOG_PATH = pathlib.Path(__file__).resolve().parent / "sample_logs" / "authsvc.jsonl"
EXPECTED_ROOT = "0x5fbcb1b4c120926c62b1dd0550ce8288e7694bedda40740f0bf8480d2dc00dec"


def _load_entries() -> list[LogEntry]:
    entries = []
    for line in SAMPLE_LOG_PATH.read_text().splitlines():
        if not line.strip():
            continue
        entries.append(LogEntry.parse_raw(line))
    return entries


def test_log_entry_parsing_merges_dynamic_fields() -> None:
    entries = _load_entries()
    assert entries[0].fields["details"] == {"pid": 1234}
    assert entries[1].fields["user"] == "alice"


def test_canonical_leaf_rejects_reserved_field_overrides() -> None:
    entries = _load_entries()
    malicious = LogEntry(
        ts=entries[0].ts,
        source_id=entries[0].source_id,
        level=entries[0].level,
        msg=entries[0].msg,
        fields={"msg": "forged message"},
    )

    with pytest.raises(ValueError, match="reserved keys: msg"):
        merkle.canonical_leaf(malicious)


def test_merkle_root_matches_known_value() -> None:
    entries = _load_entries()
    leaves = [merkle.leaf_hash(entry) for entry in entries]
    root = merkle.merkle_root(leaves)
    assert "0x" + root.hex() == EXPECTED_ROOT


def test_merkle_proof_detects_tampering() -> None:
    entries = _load_entries()
    leaves = [merkle.leaf_hash(entry) for entry in entries]
    proof = merkle.merkle_proof(1, leaves)
    root = merkle.merkle_root(leaves)
    assert merkle.verify_proof(leaves[1], proof, root)

    # Modify the log entry and confirm the proof no longer verifies.
    tampered = LogEntry(
        ts=entries[1].ts,
        source_id=entries[1].source_id,
        level=entries[1].level,
        msg="User login",  # unchanged message
        fields={**entries[1].fields, "user": "mallory"},
    )
    tampered_leaf = merkle.leaf_hash(tampered)
    assert not merkle.verify_proof(tampered_leaf, proof, root)


def test_manifest_build_is_deterministic(tmp_path: pathlib.Path) -> None:
    entries = _load_entries()
    manifest = build_manifest("2025-09-23T18:05Z_authsvc_demo", entries, EXPECTED_ROOT)

    assert manifest["batch"]["batch_id"].endswith("authsvc_demo")
    assert manifest["batch"]["count"] == len(entries)
    assert manifest["batch"]["root"] == EXPECTED_ROOT
    assert manifest["batch"]["prev_merkle_root"] == EXPECTED_ROOT
    assert len(manifest["leaves"]) == len(entries)
    assert all(leaf.startswith("0x") for leaf in manifest["leaves"])
    assert set(manifest["proofs"]) == {str(index) for index in range(len(entries))}


def test_manifest_includes_verifiable_proofs_for_each_leaf() -> None:
    entries = _load_entries()
    manifest = build_manifest("2025-09-23T18:05Z_authsvc_demo", entries, EXPECTED_ROOT)
    expected_root = bytes.fromhex(manifest["batch"]["root"][2:])

    for index, leaf_hex in enumerate(manifest["leaves"]):
        proof = [
            (item["direction"], bytes.fromhex(item["hash"][2:]))
            for item in manifest["proofs"][str(index)]
        ]
        assert merkle.verify_proof(bytes.fromhex(leaf_hex[2:]), proof, expected_root)

