"""FastAPI application wiring the off-chain batching and verification helpers.

The service exposes two endpoints:

* ``POST /anchor_batch`` – Gather normalized log entries, build a manifest,
  persist it to append-only storage, and submit the Merkle root to the local
  Ganache instance configured in ``offchain/config.yaml``.
* ``GET /verify`` – Load a persisted manifest, recompute a Merkle proof for a
  requested entry, and compare the manifest's Merkle root with the value stored
  on-chain.

Run the API with::

    uvicorn offchain.api:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import copy
import json
import pathlib
from typing import Any, Dict, Iterable, List, MutableMapping, Optional, Tuple

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from web3 import Web3
from web3.exceptions import ContractLogicError

from . import merkle
from .batcher import build_manifest, gather_entries, load_config, persist_manifest
from .schemas import LogEntry

BASE_DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.yaml"
DEFAULT_MANIFEST_DIR = BASE_DIR / "manifests"

# Minimal ABI for the LogAnchor contract. Used when the configured ABI path is
# missing to keep the API self-contained.
DEFAULT_LOG_ANCHOR_ABI: List[Dict[str, Any]] = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "batchId", "type": "bytes32"},
            {"internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
            {"internalType": "bytes32", "name": "prevMerkleRoot", "type": "bytes32"},
            {"internalType": "string", "name": "metaCID", "type": "string"},
        ],
        "name": "anchor",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "latestRoot",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "name": "seenBatches",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
]


class AnchorBatchRequest(BaseModel):
    """Request payload for anchoring a batch."""

    batch_id: str = Field(..., description="Deterministic identifier for the batch.")
    overrides: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional configuration overrides merged into config.yaml.",
    )
    manifest_dir: Optional[str] = Field(
        default=None,
        description="Directory where manifests are persisted. Defaults to manifests/.",
    )
    wait_for_receipt: bool = Field(
        default=True,
        description="Wait for the transaction receipt before responding.",
    )


class AnchorBatchResponse(BaseModel):
    """Response returned after anchoring a batch."""

    batch_id: str
    manifest_path: str
    merkle_root: str
    transaction_hash: str
    receipt: Optional[Dict[str, Any]]
    entry_count: int


class VerificationResponse(BaseModel):
    """Response structure for Merkle proof verification."""

    batch_id: str
    entry_index: int
    leaf: str
    proof: List[Dict[str, str]]
    manifest_root: str
    on_chain_root: Optional[str]
    proof_valid: bool
    root_matches_chain: bool
    verified: bool


def _deep_update(target: MutableMapping[str, Any], overrides: MutableMapping[str, Any]) -> None:
    for key, value in overrides.items():
        if isinstance(value, MutableMapping) and isinstance(target.get(key), MutableMapping):
            _deep_update(target[key], value)  # type: ignore[index]
        else:
            target[key] = value


def _load_chain_abi(chain_cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    abi_path = chain_cfg.get("contract_abi_path")
    if not abi_path:
        return DEFAULT_LOG_ANCHOR_ABI

    resolved = (DEFAULT_CONFIG_PATH.parent / pathlib.Path(abi_path)).resolve()
    if not resolved.exists():
        return DEFAULT_LOG_ANCHOR_ABI

    with resolved.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _get_web3(chain_cfg: Dict[str, Any]) -> Web3:
    rpc_url = chain_cfg.get("rpc_url")
    if not rpc_url:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "RPC URL missing from chain configuration")

    provider = Web3.HTTPProvider(rpc_url)
    w3 = Web3(provider)
    if not w3.is_connected():
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Unable to connect to RPC at {rpc_url}")
    return w3


def _bytes32(value: Optional[str]) -> bytes:
    if not value:
        return b"\x00" * 32
    stripped = value[2:] if value.startswith("0x") else value
    if len(stripped) != 64:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Expected 32-byte hex value, got {value}")
    return bytes.fromhex(stripped)


def _resolve_manifest_dir(config: Dict[str, Any], override: Optional[str]) -> pathlib.Path:
    if override:
        override_path = pathlib.Path(override)
        if not override_path.is_absolute():
            override_path = (BASE_DIR / override_path).resolve()
        return override_path

    storage_cfg = config.get("storage", {})
    manifest_dir_cfg = storage_cfg.get("manifest_dir")
    if manifest_dir_cfg:
        manifest_path = pathlib.Path(manifest_dir_cfg)
        if not manifest_path.is_absolute():
            manifest_path = (BASE_DIR / manifest_path).resolve()
        return manifest_path

    return DEFAULT_MANIFEST_DIR


def _anchor_on_chain(
    config: Dict[str, Any], batch_id: str, manifest: Dict[str, Any], wait_for_receipt: bool
) -> Tuple[str, Optional[Dict[str, Any]]]:
    chain_cfg = config.get("chain", {})
    pattern = chain_cfg.get("anchoring_pattern", "contract")
    w3 = _get_web3(chain_cfg)

    root_hex = manifest["batch"]["root"]
    prev_root_hex = manifest["batch"].get("prev_merkle_root")

    root_bytes = _bytes32(root_hex)
    prev_bytes = _bytes32(prev_root_hex)

    if pattern != "contract":
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, f"Anchoring pattern '{pattern}' is not supported")

    abi = _load_chain_abi(chain_cfg)
    contract_address = chain_cfg.get("contract_address")
    if not contract_address:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Contract address missing from chain configuration")

    try:
        checksum_address = Web3.to_checksum_address(contract_address)
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid contract address: {contract_address}") from exc

    contract = w3.eth.contract(address=checksum_address, abi=abi)

    from_address = chain_cfg.get("from_address")
    if not from_address:
        accounts = w3.eth.accounts
        if not accounts:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "No unlocked accounts available on RPC node")
        from_address = accounts[0]

    batch_identifier = w3.keccak(text=batch_id)
    meta_cid = manifest["batch"].get("meta_cid", "")

    try:
        tx_hash = contract.functions.anchor(batch_identifier, root_bytes, prev_bytes, meta_cid).transact({"from": from_address})
    except ContractLogicError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Contract rejected anchor: {exc}") from exc

    receipt_data: Optional[Dict[str, Any]] = None
    if wait_for_receipt:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        receipt_data = {
            "transaction_hash": receipt.transactionHash.hex(),
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
            "status": receipt.status,
        }
        tx_hash_hex = receipt.transactionHash.hex()
    else:
        tx_hash_hex = tx_hash.hex()

    return tx_hash_hex, receipt_data


def _fetch_on_chain_root(config: Dict[str, Any]) -> Optional[str]:
    chain_cfg = config.get("chain", {})
    if not chain_cfg:
        return None

    w3 = _get_web3(chain_cfg)
    pattern = chain_cfg.get("anchoring_pattern", "contract")
    if pattern != "contract":
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, f"Anchoring pattern '{pattern}' is not supported")

    abi = _load_chain_abi(chain_cfg)
    contract_address = chain_cfg.get("contract_address")
    if not contract_address:
        return None

    checksum_address = Web3.to_checksum_address(contract_address)
    contract = w3.eth.contract(address=checksum_address, abi=abi)
    root_bytes = contract.functions.latestRoot().call()
    return Web3.to_hex(root_bytes)


def _load_manifest(path: pathlib.Path) -> Dict[str, Any]:
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Manifest not found at {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _prepare_entries(entries: Iterable[LogEntry]) -> List[Dict[str, Any]]:
    return [json.loads(entry.json()) for entry in entries]


def _reconstruct_entries(entries_payload: List[Dict[str, Any]]) -> List[LogEntry]:
    return [LogEntry.parse_obj(payload) for payload in entries_payload]


app = FastAPI(title="Secure Log Anchoring API", version="0.1.0")


@app.post("/anchor_batch", response_model=AnchorBatchResponse)
def anchor_batch(request: AnchorBatchRequest) -> AnchorBatchResponse:
    config = load_config(DEFAULT_CONFIG_PATH)
    if request.overrides:
        config_copy = copy.deepcopy(config)
        _deep_update(config_copy, request.overrides)
        config = config_copy

    manifest_dir = _resolve_manifest_dir(config, request.manifest_dir)

    batch_inputs = gather_entries(config)
    if not batch_inputs.entries:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No log entries available for batching")

    manifest = build_manifest(request.batch_id, batch_inputs.entries, batch_inputs.prev_root)
    manifest["entries"] = _prepare_entries(batch_inputs.entries)

    tx_hash, receipt_data = _anchor_on_chain(config, request.batch_id, manifest, request.wait_for_receipt)
    manifest["chain"] = {"tx_hash": tx_hash, "receipt": receipt_data}

    manifest_path = persist_manifest(manifest, request.batch_id, manifest_dir)

    return AnchorBatchResponse(
        batch_id=request.batch_id,
        manifest_path=str(manifest_path),
        merkle_root=manifest["batch"]["root"],
        transaction_hash=tx_hash,
        receipt=receipt_data,
        entry_count=len(batch_inputs.entries),
    )


@app.get("/verify", response_model=VerificationResponse)
def verify(
    batch_id: str = Query(..., description="Batch identifier to verify."),
    entry_index: int = Query(..., ge=0, description="Index of the entry within the batch."),
    manifest_dir: Optional[str] = Query(
        default=None, description="Override manifest directory used for lookup."
    ),
) -> VerificationResponse:
    config = load_config(DEFAULT_CONFIG_PATH)
    manifest_directory = _resolve_manifest_dir(config, manifest_dir)
    manifest_path = manifest_directory / f"{batch_id}.manifest.json"

    manifest = _load_manifest(manifest_path)
    manifest_batch = manifest.get("batch", {})
    if manifest_batch.get("batch_id") != batch_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Batch identifier mismatch in manifest")

    entries_payload = manifest.get("entries")
    if not entries_payload:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Manifest does not include serialized entries")

    try:
        entries = _reconstruct_entries(entries_payload)
    except Exception as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Failed to parse entries: {exc}") from exc

    if entry_index >= len(entries):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Entry index out of range for manifest")

    leaves = [merkle.leaf_hash(entry) for entry in entries]
    leaf = leaves[entry_index]

    proof = merkle.merkle_proof(entry_index, leaves)
    root_hex = manifest_batch.get("root")
    if not root_hex:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Manifest missing Merkle root")
    expected_root = _bytes32(root_hex)
    proof_valid = merkle.verify_proof(leaf, proof, expected_root)

    proof_serialized = [
        {"direction": direction, "hash": "0x" + sibling.hex()} for direction, sibling in proof
    ]

    on_chain_root = None
    try:
        on_chain_root = _fetch_on_chain_root(config)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - network related issues
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Failed to fetch on-chain root: {exc}") from exc

    root_matches_chain = bool(on_chain_root and on_chain_root.lower() == root_hex.lower())
    verified = proof_valid and root_matches_chain

    return VerificationResponse(
        batch_id=batch_id,
        entry_index=entry_index,
        leaf="0x" + leaf.hex(),
        proof=proof_serialized,
        manifest_root=root_hex,
        on_chain_root=on_chain_root,
        proof_valid=proof_valid,
        root_matches_chain=root_matches_chain,
        verified=verified,
    )


__all__ = ["app"]
