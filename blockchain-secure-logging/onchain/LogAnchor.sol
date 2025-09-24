// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title LogAnchor
/// @notice Minimal registry contract for anchoring Merkle roots representing log batches.
contract LogAnchor {
    event BatchAnchored(bytes32 indexed batchId, bytes32 merkleRoot, bytes32 prevMerkleRoot, string metaCID);

    mapping(bytes32 => bool) public seenBatches;
    bytes32 public latestRoot;

    function anchor(bytes32 batchId, bytes32 merkleRoot, bytes32 prevMerkleRoot, string calldata metaCID) external {
        require(!seenBatches[batchId], "batch-id-reused");
        require(prevMerkleRoot == latestRoot, "prev-root-mismatch");

        seenBatches[batchId] = true;
        latestRoot = merkleRoot;

        emit BatchAnchored(batchId, merkleRoot, prevMerkleRoot, metaCID);
    }
}
