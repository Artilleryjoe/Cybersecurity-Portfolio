"""Merkle tree utilities for log anchoring."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable, List, Sequence, Tuple

from .schemas import ISOFORMAT, LogEntry


def canonical_leaf(entry: LogEntry) -> bytes:
    """Serialize a :class:`LogEntry` into canonical JSON bytes."""

    payload = {
        "ts": entry.ts.strftime(ISOFORMAT),
        "source_id": entry.source_id,
        "level": entry.level,
        "msg": entry.msg,
    }
    if entry.fields:
        payload.update(entry.fields)

    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def leaf_hash(entry: LogEntry) -> bytes:
    """Compute the SHA-256 hash of a canonicalized log entry."""

    return hashlib.sha256(canonical_leaf(entry)).digest()


def _pairwise(iterable: Sequence[bytes]) -> Iterable[Tuple[bytes, bytes]]:
    for i in range(0, len(iterable), 2):
        left = iterable[i]
        right = iterable[i + 1] if i + 1 < len(iterable) else iterable[i]
        yield left, right


def merkle_root(leaves: Sequence[bytes]) -> bytes:
    """Return the Merkle root for the given list of leaf hashes."""

    if not leaves:
        raise ValueError("Cannot compute Merkle root with no leaves")

    level: List[bytes] = list(leaves)
    while len(level) > 1:
        next_level: List[bytes] = []
        for left, right in _pairwise(level):
            next_level.append(hashlib.sha256(left + right).digest())
        level = next_level
    return level[0]


def merkle_proof(target_index: int, leaves: Sequence[bytes]) -> List[Tuple[str, bytes]]:
    """Generate a Merkle proof for the leaf at ``target_index``."""

    if not 0 <= target_index < len(leaves):
        raise IndexError("target_index out of bounds")

    proof: List[Tuple[str, bytes]] = []
    idx = target_index
    level = list(leaves)

    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])

        sibling_idx = idx ^ 1
        direction = "left" if sibling_idx < idx else "right"
        proof.append((direction, level[sibling_idx]))

        next_level: List[bytes] = []
        for left, right in _pairwise(level):
            next_level.append(hashlib.sha256(left + right).digest())

        level = next_level
        idx //= 2

    return proof


def verify_proof(leaf: bytes, proof: Sequence[Tuple[str, bytes]], expected_root: bytes) -> bool:
    """Verify that ``leaf`` is part of the tree defined by ``expected_root``."""

    computed = leaf
    for direction, sibling in proof:
        if direction == "right":
            computed = hashlib.sha256(computed + sibling).digest()
        elif direction == "left":
            computed = hashlib.sha256(sibling + computed).digest()
        else:
            raise ValueError(f"Unknown direction {direction}")
    return computed == expected_root


__all__ = [
    "canonical_leaf",
    "leaf_hash",
    "merkle_root",
    "merkle_proof",
    "verify_proof",
]
