"""Regression tests for API helper validation."""

from __future__ import annotations

import pathlib
import sys

import pytest
from fastapi import HTTPException, status

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from offchain.api import _bytes32


def test_bytes32_rejects_non_hex_input_with_http_400() -> None:
    with pytest.raises(HTTPException) as exc_info:
        _bytes32("0x" + "z" * 64)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Expected 32-byte hex value" in exc_info.value.detail
