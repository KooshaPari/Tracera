# Visual Reference: Specification Provenance Architecture

## System Architecture Diagrams

### 1. Complete System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                   SPECIFICATION PROVENANCE SYSTEM                   │
└─────────────────────────────────────────────────────────────────────┘

User Interface
     ↓
┌──────────────────────────────────────────────────────────────┐
│  API Layer (REST/GraphQL)                                    │
│  ├─ POST /specifications (create with provenance)            │
│  ├─ GET /specifications/{id}/provenance                      │
│  ├─ POST /specifications/{id}/verify-requirement             │
│  ├─ GET /specifications/{id}/audit-trail                     │
│  └─ GET /did/{did}                                           │
└──────────────────────────────────────────────────────────────┘
     ↓
┌──────────────────────────────────────────────────────────────┐
│  Service Layer                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ IPFS Service │  │ Merkle Svc   │  │  DID Service │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  NFT Service │  │ Event Svc    │  │Provenance Svc│       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
     ↓                    ↓                    ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   IPFS       │   │ PostgreSQL   │   │  Blockchain  │
│   Network    │   │   Database   │   │ (Ethereum)   │
│              │   │              │   │              │
│ Immutable    │   │ Audit Trail  │   │ NFT Minting  │
│ Content      │   │ Provenance   │   │ Events       │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

### 2. Data Flow: Create Specification

```
User submits specification
     ↓
Store on IPFS (immutable content)
     ↓
Generate Merkle Tree (requirement verification)
     ↓
Create DID (global identifier)
     ↓
Register in database
     ↓
Emit event (audit log)
     ↓
(Optional) Mint NFT (blockchain binding)
     ↓
(Optional) Add provenance node
     ↓
Return specification object with full provenance
```

---

### 3. Data Storage Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                   SPECIFICATION OBJECT                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ON-CHAIN (Immutable + Verifiable)                          │
│  ├─ Merkle Root: 0x7f3c2a1d...                             │
│  ├─ Requirement Count: 42                                   │
│  └─ Last Updated Block: 19123456                            │
│                                                              │
│  OFF-CHAIN / IPFS (Immutable + Content-Addressed)           │
│  ├─ Full Spec Document: bafybeibxz...                      │
│  ├─ Requirement Details: bafybei2222...                    │
│  └─ Supporting Docs: bafybei3333...                        │
│                                                              │
│  DATABASE (Local + Queryable)                              │
│  ├─ Specification Metadata                                  │
│  ├─ Audit Trail Events (100+)                             │
│  ├─ Provenance Nodes (5-10)                               │
│  ├─ DID Document                                           │
│  └─ User Permissions                                       │
│                                                              │
│  COMPUTED (Derived on-demand)                              │
│  ├─ Merkle Proofs (per requirement)                        │
│  ├─ Integrity Verification (CID match)                     │
│  └─ Compliance Score (ZK proof)                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 4. Merkle Tree Structure

```
                         Root Hash
                        0x7f3c2a1d
                         /        \
                        /          \
                   Hash1            Hash2
                   0x1111           0x2222
                   /    \           /    \
                  /      \         /      \
              H3       H4      H5       H6
            0x11    0x12     0x21    0x22
           /  \     /  \     /  \    /  \
          /    \   /    \   /    \  /    \
        Req1  Req2 Req3 Req4 Req5 Req6 Req7 Req8
        (R)   (O)  (A)  (U)  (T)  (H)  (2)  (-)


Requirement:    REQ-001 (OAuth2)
Hash:           0x11
Proof:          [0x12, 0x2222, 0x2222]  ← 3 hashes to verify
Root:           0x7f3c2a1d
Proof Size:     96 bytes (3 × 32-byte hashes)

Verification:   Compute hash(0x11 + 0x12) = 0x1111
                Compute hash(0x1111 + 0x2222) = 0x7f3c2a1d ✓
                Root matches!
```

---

### 5. Supply Chain Provenance Chain

```
Timeline →
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  Node 1              Node 2              Node 3             │
│ ┌─────────┐        ┌─────────┐        ┌─────────┐          │
│ │CREATED  │        │MODIFIED │        │APPROVED │          │
│ │         │──────→ │         │──────→ │         │          │
│ │by Alice │        │by Bob   │        │by Carol │          │
│ │v 1.0.0  │        │v 2.0.0  │        │v 2.1.0  │          │
│ │hash:xxx │        │hash:yyy │        │hash:zzz │          │
│ │sig:abc  │        │sig:def  │        │sig:ghi  │          │
│ └─────────┘        └─────────┘        └─────────┘          │
│                                                              │
│  2024-01-15         2024-06-01         2024-12-15          │
│  10:30 UTC          09:00 UTC           16:30 UTC           │
│                                                              │
│ Each node cryptographically links to previous:             │
│ Node 2.linked_to = Node 1.id                              │
│ Node 3.linked_to = Node 2.id                              │
│                                                              │
│ Integrity proof: Hash chain from creation to present        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 6. Event Audit Trail

```
Timeline ──────────────────────────────────────────────────────→

Event 1: SpecCreated
├─ Timestamp: 2024-01-15T10:30:00Z
├─ Actor: alice@example.com
├─ Data: version=1.0.0, ipfsHash=bafybei1111...
└─ TxHash: 0xabcd1234...

Event 2: RequirementAdded (×40)
├─ Timestamp: 2024-01-15T11:00:00Z
├─ Actor: alice@example.com
├─ Data: requirementId=REQ-001, hash=0x1111...
└─ TxHash: 0xabcd5678...

Event 3: SpecStatusChanged
├─ Timestamp: 2024-06-01T09:00:00Z
├─ Actor: bob@example.com
├─ Data: oldStatus=draft, newStatus=review
└─ TxHash: 0xefgh5678...

Event 4: RequirementModified
├─ Timestamp: 2024-06-01T09:30:00Z
├─ Actor: bob@example.com
├─ Data: requirementId=REQ-001, changes=...
└─ TxHash: 0xijkl9012...

Event 5: ApprovalAdded
├─ Timestamp: 2024-12-15T16:30:00Z
├─ Actor: charlie@example.com
├─ Data: role=security-lead, action=approved
└─ TxHash: 0xmnop3456...

Event 6: SpecStatusChanged
├─ Timestamp: 2024-12-15T16:45:00Z
├─ Actor: charlie@example.com
├─ Data: oldStatus=review, newStatus=approved
└─ TxHash: 0xqrst7890...

         ↓
    Complete audit trail
    (immutable and searchable)
```

---

### 7. DID Resolution Chain

```
User has specification ID:
    "spec-auth-001"

System generates DID:
    "did:web:specs.example.com:specifications:auth-001:v2.1.0"

Browser resolves DID by fetching:
    https://specs.example.com/.well-known/did.json

DID Document contains:
    {
      "id": "did:web:specs.example.com:...",
      "publicKey": [
        {
          "id": "...:v2.1.0#key-1",
          "publicKeyPem": "-----BEGIN PUBLIC KEY-----..."
        }
      ],
      "service": [
        {
          "id": "...:v2.1.0#ipfs",
          "type": "IpfsGateway",
          "serviceEndpoint": "ipfs://bafybeibxz..."
        },
        {
          "id": "...:v2.1.0#api",
          "type": "SpecificationApi",
          "serviceEndpoint": "https://api.example.com/v1/specifications/spec-auth-001"
        }
      ]
    }

User now has:
    ✓ Global unique identifier
    ✓ Cryptographic proof of ownership
    ✓ Link to immutable IPFS content
    ✓ Link to specification API
    ✓ Public key for verification
```

---

### 8. Verification Process

```
┌──────────────────────────────────────────────────────────┐
│  VERIFICATION: Is requirement in baseline?                │
├──────────────────────────────────────────────────────────┤
│                                                            │
│ Input:                                                     │
│  • RequirementHash: 0xabcd1234...                        │
│  • MerkleProof: [0x1111..., 0x2222..., 0x3333...]       │
│  • MerkleRoot: 0x7f3c2a1d...                            │
│                                                            │
│ Process:                                                   │
│  1. computedHash = require Hash = 0xabcd1234            │
│  2. computedHash = hash(0xabcd + 0x1111) = 0xdef0      │
│  3. computedHash = hash(0xdef0 + 0x2222) = 0xghi1      │
│  4. computedHash = hash(0xghi1 + 0x3333) = 0x7f3c      │
│  5. Compare with root: 0x7f3c2a1d == 0x7f3c? ✓         │
│                                                            │
│ Output:                                                    │
│  {                                                         │
│    "verified": true,                                       │
│    "merkleRoot": "0x7f3c2a1d",                           │
│    "verifiedAt": "2024-12-29T14:45:00Z"                 │
│  }                                                         │
│                                                            │
│ Proof size: 96 bytes (3 hashes)                          │
│ Verification time: <1ms                                  │
│ Cost: ~200 gas (on-chain) or free (off-chain)          │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

---

### 9. Cost Comparison

```
┌─────────────────────────────────────────────────────────┐
│                  COST COMPARISON                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ OPERATION          ETHEREUM    POLYGON    LAYER2       │
│ ─────────────────────────────────────────────────────  │
│ Mint NFT           $100        $2         $5-10        │
│ Update Status      $20         $0.50      $1-2         │
│ Emit Event         $1          $0.02      $0.05-0.10   │
│ Approve (event)    $0.50       $0.01      $0.02-0.05   │
│                                                          │
│ Monthly (10 specs, 50 ops)                            │
│ ─────────────────────────────────────────────────────  │
│ Transactions:      $1,500      $25        $50-100      │
│ IPFS Pinning:      $20         $20        $20          │
│ Database:          $20         $20        $20          │
│ ─────────────────────────────────────────────────────  │
│ TOTAL:             $1,540      $65        $90-140      │
│                                                          │
│ Recommendation: Use Polygon or Arbitrum for cost       │
│ efficiency while maintaining security                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

### 10. Specification Evolution Visualization

```
Specification Lifecycle
═════════════════════════════════════════════════════════

                          Deprecated
                             ↑
                             │ (decision)
                             │
  Draft  →  Review  →  Approved  →  Active
   ↓         ↓          ↓            ↓
 Node 1   Node 2     Node 3        Node 4
  v1.0    v1.1       v2.0          v2.1
  2024-01 2024-06    2024-09       2024-12

Each version:
  • Gets new IPFS hash
  • Gets new Merkle root
  • Gets new DID (optional)
  • Gets new NFT token (optional)
  • Gets event entry
  • Gets provenance node

Viewers can:
  • See entire evolution history
  • Access any historical version via IPFS
  • Verify requirements in any version
  • Track who made changes
  • Find when deprecation happened
```

---

### 11. Multi-Layer Security

```
┌────────────────────────────────────────────────────────┐
│  SECURITY LAYERS                                        │
├────────────────────────────────────────────────────────┤
│                                                         │
│ Layer 1: Content Integrity                            │
│ ├─ IPFS CID (hash-based addressing)                  │
│ ├─ Merkle root verification                          │
│ └─ Content immutability guaranteed                   │
│   Status: ✓ CRYPTOGRAPHIC PROOF                      │
│                                                         │
│ Layer 2: Identity Verification                       │
│ ├─ DID with public key                               │
│ ├─ Cryptographic signature verification              │
│ └─ Non-repudiation                                   │
│   Status: ✓ SIGNATURE VERIFIED                       │
│                                                         │
│ Layer 3: Audit Trail                                 │
│ ├─ Smart contract events (blockchain)                │
│ ├─ Event logs (queryable)                            │
│ └─ Immutable timestamp                               │
│   Status: ✓ BLOCKCHAIN IMMUTABLE                     │
│                                                         │
│ Layer 4: Chain of Custody                            │
│ ├─ Provenance nodes (linked)                         │
│ ├─ Signatures on each transition                     │
│ └─ Version tracking                                  │
│   Status: ✓ CRYPTOGRAPHICALLY LINKED                │
│                                                         │
│ Layer 5: Privacy (Optional)                          │
│ ├─ Zero-knowledge proofs                             │
│ ├─ Prove compliance without revealing content        │
│ └─ Privacy-preserving verification                   │
│   Status: ✓ PRIVACY ENABLED                          │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

### 12. Integration Architecture

```
┌────────────────────────────────────────────────────┐
│  YOUR SYSTEM (TracerTM)                            │
├────────────────────────────────────────────────────┤
│                                                     │
│ Existing:                   NEW Provenance Layer: │
│ • Specifications      ──→   • IPFS storage        │
│ • Requirements        ──→   • Merkle trees        │
│ • Tests               ──→   • DIDs                │
│ • Approvals           ──→   • Events              │
│ • Audit logs          ──→   • Supply chain        │
│                             • NFTs (optional)     │
│                                                     │
│ All existing code continues to work               │
│ New features are additive/optional               │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

## Implementation Decision Tree

```
START: Do you need specification provenance?
│
├─ NO → Stop here
│
└─ YES → Do you have blockchain expertise?
   │
   ├─ NO → Start with IPFS + Merkle (Week 1)
   │       ├─ Cost: $20/month
   │       ├─ Time: 1 week
   │       └─ Then add blockchain later (optional)
   │
   └─ YES → Choose architecture:
      │
      ├─ LIGHT (Single organization)
      │ ├─ IPFS + DIDs only
      │ ├─ Cost: $20-50/month
      │ └─ Timeline: 2 weeks
      │
      ├─ MEDIUM (Multi-organization)
      │ ├─ Add smart contracts + events
      │ ├─ Cost: $200-500/month
      │ └─ Timeline: 4 weeks
      │
      └─ HEAVY (Supply chain)
         ├─ Add full provenance chain + ZK
         ├─ Cost: $500-2000/month
         └─ Timeline: 6-8 weeks
```

---

## Key Metrics Dashboard

```
┌─────────────────────────────────────────────────┐
│  SPECIFICATION PROVENANCE METRICS                │
├─────────────────────────────────────────────────┤
│                                                  │
│  Immutability Score:        99.99%              │
│  ├─ Content addressed on IPFS: ✓               │
│  ├─ Hash verified: ✓                           │
│  └─ Can't be modified: ✓                       │
│                                                  │
│  Auditability Score:        100%                │
│  ├─ Complete event trail: ✓                    │
│  ├─ Timestamped: ✓                             │
│  ├─ Actor tracked: ✓                           │
│  └─ Immutable logs: ✓                          │
│                                                  │
│  Verification Efficiency:   O(log n)            │
│  ├─ Merkle proofs: 30 bytes for 1B items       │
│  ├─ Verification time: <1ms                    │
│  └─ No need to download entire spec: ✓        │
│                                                  │
│  Decentralization Score:    100%                │
│  ├─ No single point of failure: ✓             │
│  ├─ Content replicated across IPFS: ✓         │
│  ├─ DIDs require no central registry: ✓       │
│  └─ Smart contracts on public blockchain: ✓   │
│                                                  │
│  Cost Efficiency:           ~$100-500/month     │
│  ├─ Much cheaper than manual audit              │
│  ├─ Automated verification                     │
│  └─ Scalable to 1M+ specifications              │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Summary: From Concept to Implementation

```
Week 1                Week 2              Week 3             Week 4
┌────────┐          ┌────────┐          ┌────────┐         ┌────────┐
│ IPFS   │  ──→    │ Merkle │  ──→    │DIDs &  │  ──→   │ Supply │
│Storage │         │ Trees  │         │NFTs    │        │ Chain  │
└────────┘         └────────┘         └────────┘        └────────┘
   ↓                  ↓                  ↓                  ↓
Immutable       Efficient          Global          Complete
Content         Verification       Identity        Provenance

$20/mo         Free               Free-$100       $500-2000/mo
(light)        (light)            (medium)        (heavy)

All documented with:
  ✓ Complete data models
  ✓ API specifications
  ✓ Database migrations
  ✓ Code examples
  ✓ Testing strategies
```

---

**These visual references complement the detailed documentation. Use them to explain concepts to stakeholders or to design your implementation.**
