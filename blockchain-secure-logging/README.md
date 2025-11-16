# Blockchain Secure Logging Scaffold

This scaffold provides a starting point for a tamper-evident logging pipeline that batches normalized log entries, builds Merkle trees, and anchors the resulting roots onto a private Ethereum-compatible blockchain. The repository is organized to keep the on-chain footprint minimal while storing full log data in append-only off-chain storage.

## Repository Structure

```
blockchain-secure-logging/
├── README.md
├── docker/
├── infra/
│   └── ganache-config.json
├── offchain/
│   ├── batcher.py
│   ├── config.yaml
│   ├── merkle.py
│   ├── schemas.py
│   └── storage/
│       └── local_store.py
├── onchain/
│   ├── LogAnchor.sol
│   ├── abi/
│   └── addresses/
└── tests/
    ├── sample_logs/
    └── test_tamper_evidence.md
```

## Local Run

Use this quickstart to exercise the scaffold end-to-end on a laptop or lab jump box.

1. **Start Ganache** – launch the deterministic chain with the provided config so the Merkle anchor pipeline has a predictable target:

   ```bash
   npx ganache --config infra/ganache-config.json
   ```

2. **Create a Python environment** – install the lightweight tools the stubbed API and orchestration client require:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install requests
   ```

3. **Launch the API service stub** – run the development server that exposes the batching, anchoring, and verification endpoints used by downstream demos:

   ```bash
   python api/service_stub.py
   ```

4. **Hit the endpoints** – either drive the workflow with raw `curl` or rely on the bundled orchestration helper:

   ```bash
   # Using curl
   curl -X POST http://127.0.0.1:8000/api/v1/batches -H 'Content-Type: application/json' \
     -d '{"batch_id": "2025-09-23T18:05Z_authsvc_demo"}'

   # Using the stub agent
   python api/orchestrate_stub.py 2025-09-23T18:05Z_authsvc_demo
   ```

   The stub agent walks the same sequence outlined in the accompanying runbooks for this project: generate a batch, request an anchor, and ask the service to verify the result.

## High-Level Flow

1. **Collect & Normalize Logs** – Log sources emit structured JSON that conforms to `offchain/schemas.LogEntry`.
2. **Batching** – `offchain/batcher.py` gathers new logs using the cadence defined in `offchain/config.yaml`.
3. **Leaf Hashing** – Each normalized entry is canonicalized and hashed using SHA-256 (see `offchain/merkle.py`).
4. **Merkle Tree Construction** – The batcher builds a deterministic Merkle tree and produces a Merkle root per batch.
5. **Anchoring** – The batcher either submits a raw transaction containing the batch metadata or calls the optional `LogAnchor` contract to emit an anchor event. Each on-chain record contains:
   - `batch_id`
   - `merkle_root`
   - `prev_merkle_root`
   - `metaCID` or inline metadata reference
6. **Off-chain Storage** – Raw logs, manifests, and optional signatures are written to write-once (WORM) storage using the `storage.local_store` pattern.
7. **Verification** – Auditors recompute a log entry’s hash, derive a Merkle proof, and confirm the on-chain root and monotonic `prev_merkle_root` linkage.

## Components

- **offchain/** – Python utilities for reading logs, building Merkle trees, signing batches, and interacting with the chain via Web3.py.
- **onchain/** – Minimal Solidity contract interface (`LogAnchor.sol`) plus directories for compiled ABIs and deployed addresses.
- **infra/** – Configuration for running a deterministic local chain (Ganache).
- **tests/** – Manual and automated test plans plus sample logs for exercising the flow.

### Sample Fixture Narrative

The repository ships with `tests/sample_logs/authsvc.jsonl`, a three-entry `.jsonl` feed that simulates an authentication service inside a retail bank’s risk organization. The entries depict an orderly startup, a high-value user login, and a performance warning that would elevate the session’s fraud scoring if it persisted. Running the batcher against this file produces a single banking risk assessment batch whose Merkle root represents the tamper-evident snapshot auditors expect when evaluating this project end-to-end. 【F:blockchain-secure-logging/tests/sample_logs/authsvc.jsonl†L1-L4】

### Automated Proof of Concept Checks

To prove the concept quickly to stakeholders or interview panels, run the deterministic regression tests that back the sample narrative:

```bash
pytest tests/test_merkle_pipeline.py
```

The suite verifies three critical claims:

1. JSON parsing folds arbitrary fields under `LogEntry.fields`, ensuring canonical hashing input.
2. The Merkle root derived from `tests/sample_logs/authsvc.jsonl` always equals `0x5fbcb1b4c120926c62b1dd0550ce8288e7694bedda40740f0bf8480d2dc00dec`.
3. Any mutation to a batched log entry invalidates the stored Merkle proof, demonstrating tamper evidence without having to spin up Ganache.

Because the tests only rely on the standard library, they execute in restricted lab environments where `pip` access may be limited.

## Next Steps

1. Create a Python virtual environment and install dependencies listed in `offchain/batcher.py` docstring.
2. Populate `tests/sample_logs/` with `.jsonl` fixtures and run the batcher to produce a manifest and anchor transaction.
3. Extend the batcher to include ECDSA signatures today and PQC signatures (e.g., Dilithium) in future iterations.
4. Integrate the verification workflow to detect tampering by recomputing Merkle proofs and checking on-chain anchors.


## End-to-End Demo Scenario

The default demo chains the local components into a deterministic rehearsal of a production flow tailored for this repository:

1. **Generate** – call the `POST /api/v1/batches` endpoint (or run `python api/orchestrate_stub.py <batch_id>`) to build a manifest from the current `.jsonl` fixtures.
2. **Anchor** – instruct the service to anchor the new Merkle root on Ganache via `POST /api/v1/anchors`; Ganache provides instant block finality for workshop timelines.
3. **Verify** – confirm integrity by invoking `POST /api/v1/verifications`, which recomputes the leaf and compares the root against the transaction recorded on the chain.

Reference materials for running the scenario:

- Full API contract: [`api/openapi.yaml`](api/openapi.yaml)
- Orchestration helper used in demos: [`api/orchestrate_stub.py`](api/orchestrate_stub.py)

These assets mirror the flow exercised when showcasing this project—operators can swap in production credentials and change `infra/ganache-config.json` to point at a long-lived network when graduating beyond the stubbed environment.


## Orchestrate Automation Stub

The helper script at `offchain/orchestrate_stub.py` provides a lightweight integration point for Orchestrate or other
automation tooling. It loads credentials/configuration, POSTs a demo batch to `/anchor_batch`, and immediately invokes
`/verify` for the same `batch_id`, logging request/response bodies alongside simple assertions so the flow can double as an
automated smoke test.

### Configuration & Environment Variables

The stub pulls its settings from environment variables and, optionally, an overridable YAML file referenced by
`ORCHESTRATE_STUB_CONFIG_PATH`. At minimum you should define:

- `ORCHESTRATE_API_BASE_URL` – Base URL (e.g., `http://127.0.0.1:8000`) hosting the `anchor_batch` and `verify` endpoints.
- `GANACHE_RPC_URL` – RPC endpoint used by the verification metadata (defaults to `http://127.0.0.1:8545`).
- `ORCHESTRATE_BATCH_ID` – Demo batch identifier used for both anchoring and verification.

Optional overrides include:

- `ORCHESTRATE_API_TOKEN` – Bearer token for authenticated APIs.
- `ORCHESTRATE_MERKLE_ROOT` / `ORCHESTRATE_PREV_MERKLE_ROOT` / `ORCHESTRATE_NETWORK` – Override demo payload values.
- `ORCHESTRATE_STUB_CONFIG_PATH` – Path to a YAML file that can define `api_base_url`, `anchor_payload`, `verify_params`, and
  `ganache_rpc_url` defaults consumed by the stub.

## Running the Off-chain API

The off-chain components can also be orchestrated via a FastAPI service that batches logs, submits Merkle roots to Ganache, and verifies anchored entries. Start the development server with:

```bash
uvicorn offchain.api:app --reload --host 0.0.0.0 --port 8000
```

The API exposes `POST /anchor_batch` for building and anchoring new manifests and `GET /verify` for recomputing Merkle proofs against the on-chain root.


## Threat Model Snapshot

- **Goal** – Detect unauthorized edits, deletions, or reordering of historical log entries.
- **Immutability Anchor** – Private Ethereum chain guarantees transaction immutability; optional periodic checkpoints to a public chain provide extra assurance.
- **Backdating Deterrence** – Each batch references the prior Merkle root, forming a singly linked list anchored by block timestamps.
- **Key Management** – Separate keys for anchoring transactions and node administration. Rotate regularly and store in secure keystores (file-based, HSM, or TPM).
- **Node Rollback** – Pin finalized blocks, export checkpoints, and consider anchoring snapshots publicly to prevent rollback attacks.
- **Source Authenticity** – Sign logs at the edge or use authenticated transport; include `source_id` in each leaf hash.

## Development Shortcuts

- Run Ganache locally with `ganache --port 8545 --deterministic --chain.hardfork istanbul`.
- Choose anchoring pattern:
  - **Pattern A (Raw TX)** – Encode metadata into a zero-value transaction to a known account.
  - **Pattern B (LogAnchor Contract)** – Call `anchor` to emit a structured event for better indexing.

## Verification Workflow (Summary)

1. Canonicalize the target log entry and compute its SHA-256 leaf hash.
2. Load the batch manifest to retrieve sibling hashes and compute the Merkle root.
3. Fetch the on-chain anchor (tx receipt or contract event) and compare the stored root.
4. Verify chain continuity via `prev_merkle_root` pointers.
5. Optionally validate the batch signature (ECDSA today, PQC later).

## Testing Checklist

- ✅ Unit: deterministic leaf hashing and Merkle roots.
- ✅ E2E: mutate raw log and ensure verification fails.
- ✅ Adversarial: detect deletions/insertions via Merkle proof mismatch.
- ✅ Rollback: ensure conflicting `batch_id` anchors are rejected or detected.

