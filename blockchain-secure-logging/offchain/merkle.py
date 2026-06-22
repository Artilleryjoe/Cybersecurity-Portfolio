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
        reserved_keys = payload.keys() & entry.fields.keys()
        if reserved_keys:
            reserved = ", ".join(sorted(reserved_keys))
            raise ValueError(f"Log entry fields cannot override reserved keys: {reserved}")
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


def merkle_tree_levels(leaves: Sequence[bytes]) -> List[List[bytes]]:
    """Build and return every level in a Merkle tree.

    The returned list starts with the original leaf level and ends with the
    single root hash level. Odd-width levels are duplicated before parent
    hashes are calculated so sibling lookups can reuse the cached structure.
    """

    if not leaves:
        raise ValueError("Cannot build Merkle tree with no leaves")

    levels: List[List[bytes]] = [list(leaves)]
    while len(levels[-1]) > 1:
        level = list(levels[-1])
        if len(level) % 2 == 1:
            level.append(level[-1])

        next_level: List[bytes] = []
        for left, right in _pairwise(level):
            next_level.append(hashlib.sha256(left + right).digest())
        levels.append(next_level)

    return levels

def merkle_root(leaves: Sequence[bytes]) -> bytes:
    """Return the Merkle root for the given list of leaf hashes."""

    try:
        return merkle_tree_levels(leaves)[-1][0]
    except ValueError as exc:
        raise ValueError("Cannot compute Merkle root with no leaves") from exc


def merkle_proof_from_levels(target_index: int, levels: Sequence[Sequence[bytes]]) -> List[Tuple[str, bytes]]:
    """Generate a Merkle proof for ``target_index`` from cached tree levels."""

    if not levels or not 0 <= target_index < len(levels[0]):
        raise IndexError("target_index out of bounds")

    proof: List[Tuple[str, bytes]] = []
    idx = target_index
    for raw_level in levels[:-1]:
        level = list(raw_level)
        if len(level) % 2 == 1:
            level.append(level[-1])

        sibling_idx = idx ^ 1
        direction = "left" if sibling_idx < idx else "right"
        proof.append((direction, level[sibling_idx]))
        idx //= 2

    return proof


def merkle_proof(target_index: int, leaves: Sequence[bytes]) -> List[Tuple[str, bytes]]:
    """Generate a Merkle proof for the leaf at ``target_index``."""

    return merkle_proof_from_levels(target_index, merkle_tree_levels(leaves))


def merkle_proofs(leaves: Sequence[bytes]) -> List[List[Tuple[str, bytes]]]:
    """Generate proofs for all leaves while building tree levels only once."""

    levels = merkle_tree_levels(leaves)
    return [merkle_proof_from_levels(index, levels) for index in range(len(leaves))]


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
    "merkle_tree_levels",
    "merkle_proof_from_levels",
    "merkle_proof",
    "merkle_proofs",
    "verify_proof",
]
