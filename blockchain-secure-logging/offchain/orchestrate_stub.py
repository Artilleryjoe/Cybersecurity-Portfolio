"""Utility stub for orchestrating anchor/verify demo calls.

This module is intended to be imported by an automation runner (e.g. Orchestrate)
so that it can execute a minimal happy-path flow:

1. Load configuration/credentials from environment variables or an optional YAML
   file pointed to by ``ORCHESTRATE_STUB_CONFIG_PATH``.
2. Invoke ``POST /anchor_batch`` on the configured API gateway.
3. Invoke ``GET /verify`` for the same batch ID to demonstrate verification.

The script logs request and response payloads and performs simple assertions to
fail fast when the API deviates from the expected happy path.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import yaml

LOGGER = logging.getLogger(__name__)
DEFAULT_CONFIG_FILENAME = "stub_config.yaml"
DEFAULT_TIMEOUT = (5, 30)  # (connect, read) seconds


@dataclass
class StubSettings:
    """Runtime configuration for the orchestrate stub."""

    api_base_url: str
    api_token: Optional[str] = None
    ganache_rpc_url: Optional[str] = None
    anchor_payload: Dict[str, Any] = field(default_factory=dict)
    verify_params: Dict[str, Any] = field(default_factory=dict)

    @property
    def anchor_url(self) -> str:
        return f"{self.api_base_url.rstrip('/')}/anchor_batch"

    @property
    def verify_url(self) -> str:
        return f"{self.api_base_url.rstrip('/')}/verify"


def load_settings() -> StubSettings:
    """Load settings from environment variables and optional YAML configuration."""

    config: Dict[str, Any] = {}
    config_path = os.getenv("ORCHESTRATE_STUB_CONFIG_PATH")

    if config_path:
        path = Path(config_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Configured stub config not found: {path}")
        LOGGER.debug("Loading stub configuration from %s", path)
        config = yaml.safe_load(path.read_text()) or {}
    else:
        default_path = Path(__file__).with_name(DEFAULT_CONFIG_FILENAME)
        if default_path.exists():
            LOGGER.debug("Loading stub configuration from %s", default_path)
            config = yaml.safe_load(default_path.read_text()) or {}

    env_api_base = os.getenv("ORCHESTRATE_API_BASE_URL")
    api_base_url = env_api_base or config.get("api_base_url")
    if not api_base_url:
        raise RuntimeError(
            "API base URL is required. Set ORCHESTRATE_API_BASE_URL or add "
            "api_base_url to the stub config."
        )

    anchor_payload: Dict[str, Any] = config.get("anchor_payload", {}).copy()
    verify_params: Dict[str, Any] = config.get("verify_params", {}).copy()

    batch_id = os.getenv("ORCHESTRATE_BATCH_ID") or anchor_payload.get("batch_id")
    if not batch_id:
        batch_id = "demo-batch-001"
        anchor_payload.setdefault("batch_id", batch_id)
    else:
        anchor_payload["batch_id"] = batch_id

    anchor_payload.setdefault("merkle_root", os.getenv("ORCHESTRATE_MERKLE_ROOT", "0x" + "00" * 32))
    anchor_payload.setdefault(
        "prev_merkle_root",
        os.getenv("ORCHESTRATE_PREV_MERKLE_ROOT", "0x" + "11" * 32),
    )
    anchor_payload.setdefault(
        "network",
        os.getenv("ORCHESTRATE_NETWORK", "ganache-local"),
    )
    anchor_payload.setdefault(
        "metadata",
        {
            "ganache_rpc_url": os.getenv("GANACHE_RPC_URL")
            or config.get("ganache_rpc_url", "http://127.0.0.1:8545"),
        },
    )

    verify_params.setdefault("batch_id", batch_id)

    return StubSettings(
        api_base_url=api_base_url,
        api_token=os.getenv("ORCHESTRATE_API_TOKEN") or config.get("api_token"),
        ganache_rpc_url=os.getenv("GANACHE_RPC_URL") or config.get("ganache_rpc_url"),
        anchor_payload=anchor_payload,
        verify_params=verify_params,
    )


def _log_request(method: str, url: str, payload: Optional[Dict[str, Any]]) -> None:
    pretty_payload = json.dumps(payload, sort_keys=True, indent=2) if payload else "{}"
    LOGGER.info("%s %s\nRequest body:%s\n%s", method.upper(), url, os.linesep, pretty_payload)


def _log_response(response: requests.Response) -> None:
    try:
        body = response.json()
        pretty_body = json.dumps(body, sort_keys=True, indent=2)
    except ValueError:
        pretty_body = response.text
    LOGGER.info(
        "Response %s %s\nResponse body:%s\n%s",
        response.request.method,
        response.status_code,
        os.linesep,
        pretty_body,
    )


def run_demo(settings: Optional[StubSettings] = None) -> Dict[str, Any]:
    """Execute the anchor + verify flow and return combined results."""

    settings = settings or load_settings()

    session = requests.Session()
    if settings.api_token:
        session.headers.update({"Authorization": f"Bearer {settings.api_token}"})

    LOGGER.debug("Using API base URL: %s", settings.api_base_url)
    if settings.ganache_rpc_url:
        LOGGER.debug("Using Ganache RPC URL: %s", settings.ganache_rpc_url)

    # Anchor batch
    _log_request("POST", settings.anchor_url, settings.anchor_payload)
    anchor_resp = session.post(
        settings.anchor_url,
        json=settings.anchor_payload,
        timeout=DEFAULT_TIMEOUT,
    )
    _log_response(anchor_resp)
    anchor_resp.raise_for_status()
    anchor_data = anchor_resp.json()
    assert (
        anchor_data.get("batch_id") == settings.anchor_payload["batch_id"]
    ), "Anchor response batch_id mismatch"

    # Verify batch
    _log_request("GET", settings.verify_url, settings.verify_params)
    verify_resp = session.get(
        settings.verify_url,
        params=settings.verify_params,
        timeout=DEFAULT_TIMEOUT,
    )
    _log_response(verify_resp)
    verify_resp.raise_for_status()
    verify_data = verify_resp.json()
    assert verify_data.get("verified") is True, "Verification did not succeed"

    return {
        "anchor": anchor_data,
        "verify": verify_data,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    results = run_demo()
    LOGGER.info("Demo completed successfully: %s", json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
