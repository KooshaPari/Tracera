# Specification Provenance with Blockchain & NFT Standards - Quick Start

## Overview

This quick start guide helps you understand and implement blockchain-based provenance for specification objects using industry standards.

**Key Insight**: Combine content-addressed storage (IPFS), smart contracts (ERC-721/4626), and immutable audit trails (events) to create tamper-proof, verifiable specification systems.

---

## 1. Choose Your Architecture

### Option A: Lightweight (Single Organization)

```
Specs → IPFS (content) → PostgreSQL (metadata) → Event logs
└─ Use: DIDs for identity, no blockchain needed initially
└─ Cost: ~$100-200/month
└─ Scalability: 10K+ specifications
```

### Option B: Enterprise (Multi-Organization)

```
Specs → IPFS → Smart Contracts (ERC-721) → Ethereum/L2
       ↓
     DIDs → DID Registry (W3C)
       ↓
  Merkle Trees → Verification proofs
       ↓
  Events → Audit trail (query-able)
```

Cost: ~$500-2000/month (depending on transaction volume)

### Option C: Supply Chain (Fully Decentralized)

```
IBM Food Trust style:
Specs → IPFS → Hyperledger/Fabric → Permissioned blockchain
        ↓
    Provenance Nodes (linked chain)
        ↓
    Stakeholder Access Control
```

---

## 2. Five-Minute Implementation Path

### Step 1: Store Specification on IPFS

```typescript
import * as fs from 'fs';
import * as IPFS from 'ipfs-core';

// 1. Create IPFS node
const ipfs = await IPFS.create();

// 2. Add specification to IPFS
const specContent = {
  title: "Authentication Requirements",
  version: "2.1.0",
  requirements: [
    { id: "REQ-001", title: "OAuth2 Support", priority: "critical" }
  ]
};

const result = await ipfs.add(JSON.stringify(specContent, null, 2));
const cid = result.cid.toString();

console.log(`Content stored at: ipfs://${cid}`);
// Output: ipfs://bafybeibxzrmwuryq7h5j6rqfvd45cbhmvmhj44qmyozr6d7ht37z7hyf4

// 3. Immutability guarantee
// If content changes, CID changes automatically
const modifiedSpec = { ...specContent, version: "2.1.1" };
const result2 = await ipfs.add(JSON.stringify(modifiedSpec, null, 2));
console.log(`Modified content has different CID: ${result2.cid.toString()}`);
```

**Why this matters**: The IPFS CID is a cryptographic hash of the content. Change any character in your specification, and you get a different CID. This is your immutability guarantee.

---

### Step 2: Create Merkle Tree for Requirements

```typescript
import { MerkleTree } from 'merkletreejs';
import * as crypto from 'crypto';

// Hash each requirement
const requirements = [
  { id: "REQ-001", title: "OAuth2" },
  { id: "REQ-002", title: "MFA" },
  { id: "REQ-003", title: "Rate Limiting" }
];

const leaves = requirements.map(req => {
  const json = JSON.stringify(req, Object.keys(req).sort());
  return crypto.createHash('sha256').update(json).digest();
});

// Build tree
const tree = new MerkleTree(
  leaves,
  crypto.createHash('sha256')
);

const root = tree.getRoot().toString('hex');
console.log(`Merkle Root: 0x${root}`);
// 0x7f3c2a1d4e5b9c8d2a1f9e8d7c6b5a4f3e2d1c0b

// Verify requirement is in the baseline
const proof = tree.getProof(leaves[0]);
const isValid = MerkleTree.verify(
  proof,
  leaves[0],
  Buffer.from(root, 'hex')
);
console.log(`REQ-001 in baseline: ${isValid}`);
```

**Why this matters**: You can prove a requirement is in a specification without downloading the entire spec. The proof is only ~32 bytes per requirement level.

---

### Step 3: Register with DID

```typescript
// Create decentralized identifier for your specification
const did = "did:web:specs.example.com:specifications:auth:v2.1.0";

// DID Document (self-signed)
const didDocument = {
  "@context": "https://www.w3.org/ns/did/v1",
  "id": did,
  "created": new Date().toISOString(),
  "publicKey": [{
    "id": `${did}#key-1`,
    "type": "RsaVerificationKey2018",
    "publicKeyPem": "-----BEGIN PUBLIC KEY-----\nMIIBIjAN..." // Your org's public key
  }],
  "service": [{
    "id": `${did}#ipfs`,
    "type": "IpfsGateway",
    "serviceEndpoint": `ipfs://bafybeibxz...` // Your IPFS CID
  }]
};

// Store DID document at: https://specs.example.com/.well-known/did.json
// Anyone can now resolve your specification via DID
```

**Why this matters**: DIDs are globally unique, verifiable identifiers. You don't need a central registry. Anyone can verify your specification's provenance by resolving the DID.

---

### Step 4: Emit Events for Audit Trail

```typescript
// Solidity smart contract
pragma solidity ^0.8.0;

contract SpecificationAudit {
    event SpecCreated(
        indexed uint256 specId,
        indexed address creator,
        string version,
        bytes32 ipfsHash,
        bytes32 merkleRoot,
        uint256 timestamp
    );

    function createSpecification(
        uint256 specId,
        string memory version,
        bytes32 ipfsHash,
        bytes32 merkleRoot
    ) public {
        emit SpecCreated(
            specId,
            msg.sender,
            version,
            ipfsHash,
            merkleRoot,
            block.timestamp
        );
    }
}

// JavaScript reading the event
const filter = contract.filters.SpecCreated(specId);
const events = await contract.queryFilter(filter);

events.forEach(event => {
    console.log({
        version: event.args.version,
        creator: event.args.creator,
        ipfsHash: event.args.ipfsHash,
        merkleRoot: event.args.merkleRoot,
        timestamp: new Date(event.args.timestamp * 1000)
    });
});
```

**Why this matters**: Events are stored in blockchain logs (immutable), but cost only 375 gas + 8 gas/byte. Way cheaper than storing data in contract state.

---

### Step 5: Track Supply Chain

```typescript
// Simple provenance chain
const provenanceChain = [
  {
    nodeId: "node-1",
    action: "created",
    actor: "alice@example.com",
    version: "1.0.0",
    ipfsHash: "bafybei1111...",
    merkleRoot: "0x1111...",
    timestamp: Date.now(),
    signature: "0xsig1111...",
    linkedTo: [] // First node
  },
  {
    nodeId: "node-2",
    action: "modified",
    actor: "bob@example.com",
    version: "2.0.0",
    ipfsHash: "bafybei2222...",
    merkleRoot: "0x2222...",
    timestamp: Date.now(),
    signature: "0xsig2222...",
    linkedTo: ["node-1"] // Linked to previous
  },
  {
    nodeId: "node-3",
    action: "approved",
    actor: "charlie@example.com",
    version: "2.1.0",
    ipfsHash: "bafybei3333...",
    merkleRoot: "0x3333...",
    timestamp: Date.now(),
    signature: "0xsig3333...",
    linkedTo: ["node-2"] // Linked to previous
  }
];

// Verify chain integrity
function verifyChain(chain) {
  for (let i = 1; i < chain.length; i++) {
    if (!chain[i].linkedTo.includes(chain[i-1].nodeId)) {
      return false; // Chain broken
    }
  }
  return true;
}

console.log(`Chain valid: ${verifyChain(provenanceChain)}`);
```

**Why this matters**: You have a cryptographic proof of who changed what and when. Each node links to the previous one, forming an unbreakable chain.

---

## 3. Data Model Template

Copy this JSON structure for your specifications:

```json
{
  "specification": {
    "id": "spec-auth-001",
    "title": "Authentication Requirements",
    "version": "2.1.0",
    "status": "approved"
  },
  "contentAddressing": {
    "ipfsHash": "bafybeibxz...",
    "contentSize": 2048576,
    "cidVersion": 1
  },
  "identity": {
    "did": "did:web:specs.example.com:specifications:auth:v2.1.0",
    "created": "2024-01-15T10:30:00Z"
  },
  "verification": {
    "merkleRoot": "0x7f3c2a1d4e5b9c8d2a1f9e8d7c6b5a4f3e2d1c0b",
    "requirementCount": 42
  },
  "blockchain": {
    "nftTokenId": 42,
    "nftAddress": "0x1234567890...",
    "chainId": 1,
    "transactionHash": "0xabcd..."
  },
  "supplyChain": {
    "createdBy": "alice@example.com",
    "approvedBy": "charlie@example.com",
    "nodes": [
      {
        "action": "created",
        "actor": "alice@example.com",
        "timestamp": "2024-01-15T10:30:00Z"
      },
      {
        "action": "approved",
        "actor": "charlie@example.com",
        "timestamp": "2024-12-15T16:30:00Z"
      }
    ]
  },
  "auditTrail": [
    {
      "eventType": "SpecCreated",
      "timestamp": "2024-01-15T10:30:00Z",
      "actor": "alice@example.com",
      "transactionHash": "0xabcd..."
    },
    {
      "eventType": "SpecStatusChanged",
      "timestamp": "2024-12-15T16:30:00Z",
      "actor": "charlie@example.com",
      "newStatus": "approved"
    }
  ]
}
```

---

## 4. Cost-Benefit Analysis

| Aspect | Benefit | Cost |
|--------|---------|------|
| **IPFS + CID** | Immutable content addressing | Pinning service: $5-50/month |
| **Merkle Trees** | Efficient verification proofs | Library included in ethers.js |
| **DIDs** | Decentralized identity | Self-hosted .well-known endpoint |
| **Smart Contracts** | Immutable blockchain audit trail | $50-100 per spec (L2: $5-10) |
| **Events** | Gas-efficient logging | ~0.50-1 USD per approval |
| **Total/Month** | Complete tamper-proof system | $100-500 depending on scale |

---

## 5. Integration Checklist

### Week 1: Foundation
- [ ] Set up IPFS node or pinning service
- [ ] Create DID resolver endpoint
- [ ] Set up PostgreSQL for metadata
- [ ] Implement Merkle tree generation

### Week 2: Blockchain
- [ ] Deploy ERC-721 NFT contract
- [ ] Deploy event logging contract
- [ ] Set up contract interaction library
- [ ] Configure event indexing (The Graph)

### Week 3: Integration
- [ ] API endpoints for specification creation
- [ ] API endpoints for verification
- [ ] Audit trail retrieval
- [ ] DID resolution

### Week 4: Testing & Documentation
- [ ] End-to-end tests
- [ ] Performance benchmarks
- [ ] User documentation
- [ ] Operations runbook

---

## 6. Common Patterns

### Pattern 1: Add Specification
```typescript
async function addSpecification(spec) {
  // 1. Store on IPFS
  const ipfsResult = await ipfs.add(JSON.stringify(spec));

  // 2. Generate Merkle tree
  const merkleTree = new RequirementMerkleTree(spec.requirements);

  // 3. Register DID
  const did = registerDid(spec.id, spec.version);

  // 4. Mint NFT
  const txHash = await contract.mintSpecification(
    spec.id,
    spec.version,
    ipfsResult.cid.toString(),
    merkleTree.getRoot()
  );

  // 5. Return provenance object
  return {
    ipfsHash: ipfsResult.cid.toString(),
    did: did,
    nftTokenId: tokenId,
    merkleRoot: merkleTree.getRoot(),
    txHash: txHash
  };
}
```

### Pattern 2: Verify Requirement
```typescript
async function verifyRequirement(specId, requirementId, merkleProof) {
  // 1. Get specification metadata
  const spec = await getSpecification(specId);

  // 2. Verify proof matches root
  const isValid = verifyMerkleProof(
    requirementId,
    merkleProof,
    spec.merkleRoot
  );

  // 3. Return result with timestamp
  return {
    valid: isValid,
    specId: specId,
    merkleRoot: spec.merkleRoot,
    verifiedAt: Date.now()
  };
}
```

### Pattern 3: Track Modification
```typescript
async function modifySpecification(specId, newVersion, changes) {
  // 1. Create new IPFS entry
  const newContent = await updateSpecContent(specId, changes);
  const ipfsResult = await ipfs.add(JSON.stringify(newContent));

  // 2. Regenerate Merkle tree
  const merkleTree = new RequirementMerkleTree(newContent.requirements);

  // 3. Emit event
  await contract.emit('SpecificationUpdated', {
    specId: specId,
    version: newVersion,
    ipfsHash: ipfsResult.cid.toString(),
    merkleRoot: merkleTree.getRoot()
  });

  // 4. Add provenance node
  addProvenanceNode({
    specId: specId,
    action: 'modified',
    version: newVersion,
    ipfsHash: ipfsResult.cid.toString(),
    actor: getCurrentUser(),
    linkedTo: getPreviousNode(specId)
  });
}
```

---

## 7. Troubleshooting

| Problem | Solution |
|---------|----------|
| IPFS content disappears | Use paid pinning service (Pinata, Estuary) |
| Merkle proof verification fails | Ensure consistent hashing (SHA-256) and leaf ordering |
| DID resolution timeout | Check .well-known endpoint CORS headers |
| High gas costs | Use Layer 2 (Polygon, Arbitrum, Optimism) |
| Event logs not indexing | Use The Graph or Goldsky subgraph |

---

## 8. Security Considerations

1. **IPFS Pinning**: Use redundant pinning services
2. **Private Keys**: Store creator/approver keys securely
3. **Access Control**: Implement fine-grained permissions for updates
4. **Signature Verification**: Always verify signatures on critical operations
5. **Rate Limiting**: Protect API endpoints from abuse

---

## 9. Recommended Next Steps

1. **Start Small**: Begin with Option A (lightweight)
2. **Add NFTs**: Upgrade to Option B once you need ownership tracking
3. **Go Decentralized**: Move to Option C if you need multi-org collaboration
4. **Enhance Privacy**: Add ZK proofs for sensitive specifications

---

## 10. Resources

### Standards
- [ERC-721 NFT Standard](https://eips.ethereum.org/EIPS/eip-721)
- [ERC-4626 Vault Standard](https://eips.ethereum.org/EIPS/eip-4626)
- [W3C Decentralized Identifiers](https://www.w3.org/TR/did-1.1/)
- [IPFS Specification](https://github.com/ipfs/specs)

### Libraries
- [ethers.js](https://docs.ethers.org/) - Ethereum interaction
- [web3.js](https://web3js.readthedocs.io/) - Alternative to ethers
- [merkletreejs](https://github.com/miguelmota/merkletreejs) - Merkle trees
- [did-resolver](https://github.com/decentralized-identity/did-resolver) - DID resolution

### Services
- [Pinata](https://www.pinata.cloud/) - IPFS pinning
- [Estuary](https://estuary.tech/) - Distributed IPFS
- [The Graph](https://thegraph.com/) - Event indexing
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/) - Battle-tested smart contracts

---

## Summary

**The Stack:**
1. IPFS for immutable content storage
2. Merkle trees for efficient verification
3. DIDs for decentralized identity
4. Smart contracts for NFT minting and events
5. Audit logs for complete traceability

**The Result:**
- Tamper-proof specifications
- Verifiable ownership and contribution
- Complete audit trail
- No central point of failure
- Industry-standard interoperability

**Time to Launch:** 4 weeks | **Cost:** $100-500/month | **Scalability:** 10K+ specs/month

---

## Implementation Resources

See the accompanying documents for:
- **BLOCKCHAIN_NFT_SPECIFICATION_PROVENANCE_RESEARCH.md** - Comprehensive technical deep-dive
- **IMPLEMENTATION_PATTERNS_SPECIFICATION_PROVENANCE.md** - Production-ready code patterns and schemas

Good luck implementing blockchain-based specification provenance!
