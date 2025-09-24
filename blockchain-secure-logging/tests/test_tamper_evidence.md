# Tamper Evidence Test Plan

## Objective
Ensure that the Merkle batching and blockchain anchoring pipeline detects unauthorized modifications, deletions, or insertions in historical log data.

## Test Matrix

| Test | Description | Expected Result |
| ---- | ----------- | --------------- |
| Deterministic Hashing | Hash the same log entry twice. | Identical leaf hash outputs. |
| Merkle Root Stability | Build a Merkle tree from sample logs. | Root matches known value `0xf4b5…` (update after implementation). |
| E2E Happy Path | Run batcher on `sample_logs/authsvc.jsonl` and anchor the batch. | Manifest stored, root present on-chain. |
| Mutation Detection | Modify one log field and re-run verification. | Merkle proof fails (hash mismatch). |
| Deletion Detection | Remove a log entry and recompute. | Merkle proof fails due to missing leaf. |
| Re-anchor Protection | Attempt to anchor the same `batch_id` with different root. | Contract/monitor rejects duplicate or flags conflict. |
| Node Rollback | Simulate rollback to prior snapshot. | Checkpoint/audit process detects divergence. |

## Workflow Steps

1. **Setup Ganache** using `infra/ganache-config.json` or the CLI quick start.
2. **Deploy Contract (Optional)** using `onchain/LogAnchor.sol` with Truffle/Hardhat or anchor via raw transactions.
3. **Run Batcher** to ingest sample logs, produce `manifests/<batch_id>.manifest.json`, and anchor the Merkle root.
4. **Record Transaction Hash** for audit trail.
5. **Perform Verification** by recomputing Merkle proofs for selected entries.
6. **Introduce Tampering** (e.g., edit `authsvc.jsonl`) and repeat verification to confirm detection.
7. **Document Results** in this file with timestamps and observations.

## Notes

- Store manifests and proofs in append-only storage to support historical audits.
- Consider exporting periodic blockchain checkpoints to off-site storage for rollback detection.
- Extend test coverage with PQC signature validation once available.
