"""Pydantic models describing canonical log and batch metadata structures.

These schemas provide a single source of truth for the logging pipeline.
They enforce deterministic serialization, which is critical for hashing
and reproducible verification.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, root_validator

ISOFORMAT = "%Y-%m-%dT%H:%M:%SZ"


class LogEntry(BaseModel):
    """Normalized log entry expected by the batcher."""

    ts: datetime = Field(..., description="UTC timestamp when the event occurred.")
    source_id: str = Field(..., description="Identifier of the log source emitting the entry.")
    level: str = Field(..., description="Severity level (INFO, WARN, ERROR, ...).")
    msg: str = Field(..., description="Human-readable description of the event.")
    fields: Dict[str, Any] = Field(default_factory=dict, description="Additional structured data.")

    class Config:
        extra = "allow"

    @root_validator(pre=True)
    def normalize_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D401 - pydantic hook
        """Ensure optional fields are collected under ``fields`` for canonical encoding."""

        dynamic_fields: Dict[str, Any] = {}
        base_keys = {"ts", "source_id", "level", "msg", "fields"}

        for key in list(values.keys()):
            if key not in base_keys:
                dynamic_fields[key] = values.pop(key)

        if "fields" in values:
            merged = dict(values["fields"])
            merged.update(dynamic_fields)
            values["fields"] = merged
        else:
            values["fields"] = dynamic_fields

        return values


class BatchMeta(BaseModel):
    """Metadata captured for each anchored batch."""

    batch_id: str
    count: int
    window_start: datetime
    window_end: datetime
    hash_alg: str = Field(default="SHA-256")
    leaf_order: str = Field(default="ts_asc_seq")
    signer_alg: str = Field(default="ECDSA_secp256k1")
    signer_pub: Optional[str] = None
    prev_merkle_root: Optional[str] = Field(default=None, regex="^0x[0-9a-fA-F]{64}$")
    root: Optional[str] = Field(default=None, regex="^0x[0-9a-fA-F]{64}$")
    sig: Optional[str] = Field(default=None, description="Base64-encoded signature blob.")

    class Config:
        json_encoders = {datetime: lambda v: v.strftime(ISOFORMAT)}
        orm_mode = True


__all__ = ["BatchMeta", "LogEntry", "ISOFORMAT"]
