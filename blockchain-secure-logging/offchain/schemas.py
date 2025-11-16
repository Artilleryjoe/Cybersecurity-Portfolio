"""Lightweight schema helpers describing canonical log and batch metadata.

The original scaffold depended on Pydantic which is not available in the
offline execution environment used for validation.  The rewritten version
offers a tiny subset of the same ergonomics (``parse_raw``/``parse_obj`` and
``json`` helpers) implemented with dataclasses and stdlib utilities so the
rest of the pipeline keeps working unchanged.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

ISOFORMAT = "%Y-%m-%dT%H:%M:%SZ"


def _ensure_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        return datetime.strptime(value, ISOFORMAT).replace(tzinfo=timezone.utc)
    raise TypeError(f"Unsupported timestamp type: {type(value)!r}")


def _validate_hex32(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("Expected hex string for Merkle root metadata")
    normalized = value.lower()
    if not normalized.startswith("0x"):
        normalized = "0x" + normalized
    if len(normalized) != 66:
        raise ValueError(f"Expected 32-byte hex string, got {value}")
    hex_part = normalized[2:]
    if any(c not in "0123456789abcdef" for c in hex_part):
        raise ValueError(f"Expected hexadecimal characters, got {value}")
    return normalized


def _canonical_fields(payload: Mapping[str, Any]) -> Dict[str, Any]:
    base_keys = {"ts", "source_id", "level", "msg", "fields"}
    dynamic: Dict[str, Any] = {}
    for key, val in payload.items():
        if key not in base_keys:
            dynamic[key] = val
    fields_payload = dict(payload.get("fields") or {})
    fields_payload.update(dynamic)
    return fields_payload


@dataclass
class LogEntry:
    """Normalized log entry expected by the batcher."""

    ts: datetime
    source_id: str
    level: str
    msg: str
    fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def parse_obj(cls, payload: Mapping[str, Any]) -> "LogEntry":
        try:
            ts = _ensure_datetime(payload["ts"])
            source_id = str(payload["source_id"])
            level = str(payload["level"])
            msg = str(payload["msg"])
        except KeyError as exc:
            raise ValueError(f"Missing required field {exc.args[0]}") from exc

        fields = _canonical_fields(payload)
        return cls(ts=ts, source_id=source_id, level=level, msg=msg, fields=fields)

    @classmethod
    def parse_raw(cls, raw: str) -> "LogEntry":
        return cls.parse_obj(json.loads(raw))

    def dict(self) -> Dict[str, Any]:
        return {
            "ts": self.ts.strftime(ISOFORMAT),
            "source_id": self.source_id,
            "level": self.level,
            "msg": self.msg,
            "fields": self.fields,
        }

    def json(self) -> str:
        return json.dumps(self.dict(), separators=(",", ":"))


@dataclass
class BatchMeta:
    """Metadata captured for each anchored batch."""

    batch_id: str
    count: int
    window_start: datetime
    window_end: datetime
    hash_alg: str = "SHA-256"
    leaf_order: str = "ts_asc_seq"
    signer_alg: str = "ECDSA_secp256k1"
    signer_pub: Optional[str] = None
    prev_merkle_root: Optional[str] = None
    root: Optional[str] = None
    sig: Optional[str] = None

    def __post_init__(self) -> None:  # noqa: D401 - validation hook
        self.window_start = _ensure_datetime(self.window_start)
        self.window_end = _ensure_datetime(self.window_end)
        self.prev_merkle_root = _validate_hex32(self.prev_merkle_root)
        self.root = _validate_hex32(self.root)

    def dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "batch_id": self.batch_id,
            "count": self.count,
            "window_start": self.window_start.strftime(ISOFORMAT),
            "window_end": self.window_end.strftime(ISOFORMAT),
            "hash_alg": self.hash_alg,
            "leaf_order": self.leaf_order,
            "signer_alg": self.signer_alg,
            "signer_pub": self.signer_pub,
            "prev_merkle_root": self.prev_merkle_root,
            "root": self.root,
            "sig": self.sig,
        }
        return payload

    def json(self) -> str:
        return json.dumps(self.dict(), separators=(",", ":"))


__all__ = ["BatchMeta", "LogEntry", "ISOFORMAT"]
