# Practical Implementation Patterns for Specification Provenance

## Quick Reference: JSON Schemas for Specification Objects

### 1. Specification Document with IPFS Content Addressing

```json
{
  "schemaVersion": "1.0.0",
  "specification": {
    "id": "spec-auth-core-001",
    "type": "security-requirements",
    "metadata": {
      "title": "Authentication System - Core Requirements",
      "version": "2.1.0",
      "createdAt": "2024-01-15T10:30:00Z",
      "updatedAt": "2024-12-29T14:45:00Z",
      "organization": "TechCorp",
      "department": "Security",
      "status": "approved"
    },
    "contentAddressing": {
      "ipfsHash": "bafybeibxzrmwuryq7h5j6rqfvd45cbhmvmhj44qmyozr6d7ht37z7hyf4",
      "cidVersion": 1,
      "hashAlgorithm": "sha2-256",
      "contentSize": 2048576,
      "pinningService": "pinata",
      "pinningStatus": "pinned"
    },
    "merkleVerification": {
      "rootHash": "0x7f3c2a1d4e5b9c8d2a1f9e8d7c6b5a4f3e2d1c0b",
      "requirementCount": 42,
      "merkleTreeLevels": 6,
      "verificationProof": {
        "leaf": "0xabcd1234...",
        "proof": [
          "0x1111111111111111111111111111111111111111111111111111111111111111",
          "0x2222222222222222222222222222222222222222222222222222222222222222",
          "0x3333333333333333333333333333333333333333333333333333333333333333"
        ]
      }
    },
    "blockchainBinding": {
      "nftTokenId": 42,
      "nftAddress": "0x1234567890123456789012345678901234567890",
      "chainId": 1,
      "mintedAt": 1704067200,
      "merkleRootOnChain": "0x7f3c2a1d4e5b9c8d2a1f9e8d7c6b5a4f3e2d1c0b"
    }
  },
  "identity": {
    "did": "did:web:specs.techcorp.com:specifications:auth-core:v2.1.0",
    "publicKeyId": "did:web:specs.techcorp.com:specifications:auth-core:v2.1.0#key-1",
    "publicKey": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBg...",
    "createdAt": "2024-01-15T10:30:00Z",
    "verificationMethod": "rsa-signature-2018"
  },
  "ownership": {
    "creator": {
      "did": "did:web:specs.techcorp.com:users:alice",
      "email": "alice@techcorp.com",
      "role": "specification-author"
    },
    "contributors": [
      {
        "did": "did:web:specs.techcorp.com:users:bob",
        "email": "bob@techcorp.com",
        "role": "reviewer",
        "contributedAt": "2024-06-01T09:00:00Z"
      },
      {
        "did": "did:web:specs.techcorp.com:users:charlie",
        "email": "charlie@techcorp.com",
        "role": "approver",
        "approvedAt": "2024-12-15T16:30:00Z"
      }
    ],
    "vault": {
      "vaultTokenId": 101,
      "vaultAddress": "0x9876543210987654321098765432109876543210",
      "totalShares": 1000,
      "shares": [
        {
          "holder": "0x1111...",
          "shares": 600,
          "percentage": 60
        },
        {
          "holder": "0x2222...",
          "shares": 400,
          "percentage": 40
        }
      ]
    }
  },
  "auditTrail": {
    "events": [
      {
        "id": "evt-001",
        "timestamp": "2024-01-15T10:30:00Z",
        "blockNumber": 12345678,
        "transactionHash": "0xabcd1234...",
        "eventType": "SpecCreated",
        "actor": "0x1111...",
        "data": {
          "version": "1.0.0",
          "ipfsHash": "bafybei...",
          "status": "draft"
        }
      },
      {
        "id": "evt-002",
        "timestamp": "2024-06-01T09:00:00Z",
        "blockNumber": 18765432,
        "transactionHash": "0xefgh5678...",
        "eventType": "RequirementAdded",
        "actor": "0x2222...",
        "data": {
          "requirementId": "REQ-001",
          "requirementHash": "0x1111...",
          "requirementTitle": "OAuth2 Support"
        }
      },
      {
        "id": "evt-003",
        "timestamp": "2024-12-15T16:30:00Z",
        "blockNumber": 21234567,
        "transactionHash": "0xijkl9012...",
        "eventType": "SpecStatusChanged",
        "actor": "0x3333...",
        "data": {
          "oldStatus": "review",
          "newStatus": "approved"
        }
      }
    ],
    "summary": {
      "totalEvents": 3,
      "createdAt": "2024-01-15T10:30:00Z",
      "lastModifiedAt": "2024-12-29T14:45:00Z",
      "lastModifiedBy": "0x3333..."
    }
  },
  "supplyChain": {
    "provenance": [
      {
        "nodeId": "node-001",
        "timestamp": "2024-01-15T10:30:00Z",
        "action": "created",
        "actor": "alice@techcorp.com",
        "version": "1.0.0",
        "contentHash": "bafybei...",
        "merkleRoot": "0x7f3c2a1d...",
        "previousHash": "0x0",
        "currentHash": "0xabcd1234...",
        "signature": "0xsig1234...",
        "linkedTo": [],
        "metadata": {
          "department": "Security",
          "role": "author",
          "location": "San Francisco"
        }
      },
      {
        "nodeId": "node-002",
        "timestamp": "2024-06-01T09:00:00Z",
        "action": "modified",
        "actor": "bob@techcorp.com",
        "version": "1.5.0",
        "contentHash": "bafybej...",
        "merkleRoot": "0x8e4d3b2c...",
        "previousHash": "0xabcd1234...",
        "currentHash": "0xefgh5678...",
        "signature": "0xsig5678...",
        "linkedTo": ["node-001"],
        "metadata": {
          "department": "Security",
          "role": "developer",
          "changeReason": "Added OAuth2 requirements"
        }
      },
      {
        "nodeId": "node-003",
        "timestamp": "2024-12-15T16:30:00Z",
        "action": "approved",
        "actor": "charlie@techcorp.com",
        "version": "2.1.0",
        "contentHash": "bafybek...",
        "merkleRoot": "0x7f3c2a1d...",
        "previousHash": "0xefgh5678...",
        "currentHash": "0xijkl9012...",
        "signature": "0xsig9012...",
        "linkedTo": ["node-002"],
        "metadata": {
          "department": "Quality Assurance",
          "role": "approver"
        }
      }
    ],
    "chainIntegrity": {
      "valid": true,
      "verifiedAt": "2024-12-29T14:45:00Z",
      "headHash": "0xijkl9012...",
      "chainLength": 3
    }
  },
  "compliance": {
    "zkProofs": [
      {
        "proofId": "zk-proof-001",
        "statement": "At least 90% of requirements have test coverage",
        "publicInputs": {
          "specificationHash": "0x7f3c2a1d...",
          "requirementCount": 42,
          "complianceLevel": 95
        },
        "proof": "0xproof_data_here...",
        "verifier": "0xVerifierAddress",
        "verifiedAt": "2024-12-25T10:00:00Z",
        "isValid": true
      }
    ]
  },
  "metadata": {
    "schema": "specification-provenance-v1.0.0",
    "generatedAt": "2024-12-29T14:45:00Z",
    "signature": "0xsignature...",
    "signedBy": "did:web:specs.techcorp.com:users:alice"
  }
}
```

---

## 2. Requirement-Level Merkle Verification

```json
{
  "requirement": {
    "id": "REQ-001",
    "title": "OAuth2 Support",
    "description": "System must support OAuth2 authentication flow",
    "priority": "critical",
    "acceptanceCriteria": [
      "Must support authorization code flow",
      "Must support PKCE extension",
      "Must validate scopes",
      "Must issue refresh tokens"
    ]
  },
  "merkleVerification": {
    "requirementHash": "0xabcd1234567890abcd1234567890abcd1234567890abcd1234567890abcd1234",
    "proof": [
      "0x1111111111111111111111111111111111111111111111111111111111111111",
      "0x2222222222222222222222222222222222222222222222222222222222222222",
      "0x3333333333333333333333333333333333333333333333333333333333333333",
      "0x4444444444444444444444444444444444444444444444444444444444444444"
    ],
    "merkleRoot": "0x7f3c2a1d4e5b9c8d2a1f9e8d7c6b5a4f3e2d1c0b",
    "treeIndex": 0,
    "treeDepth": 6,
    "verificationScript": {
      "language": "solidity",
      "functionName": "verifyRequirement",
      "parameters": {
        "requirementHash": "0xabcd1234...",
        "proof": ["0x1111...", "0x2222...", "0x3333...", "0x4444..."],
        "root": "0x7f3c2a1d..."
      }
    }
  },
  "testCoverage": {
    "hasTests": true,
    "testCount": 12,
    "testCases": [
      {
        "id": "TEST-001",
        "name": "Authorization Code Flow",
        "acceptanceCriteria": "Must support authorization code flow",
        "status": "passing",
        "lastRun": "2024-12-28T15:00:00Z"
      },
      {
        "id": "TEST-002",
        "name": "PKCE Extension",
        "acceptanceCriteria": "Must support PKCE extension",
        "status": "passing",
        "lastRun": "2024-12-28T15:02:00Z"
      }
    ],
    "coveragePercent": 100
  }
}
```

---

## 3. Smart Contract Event Schema for Audit Logs

```solidity
// Event definitions with indexed parameters for efficient searching
pragma solidity ^0.8.0;

contract SpecificationEvents {
    // Event 1: Specification Created
    event SpecCreated(
        indexed uint256 specId,          // topic 0
        indexed address creator,          // topic 1
        string version,                   // data
        bytes32 ipfsHash,                 // data
        uint256 timestamp                 // data
    );

    // Event 2: Status Changed
    event SpecStatusChanged(
        indexed uint256 specId,          // topic 0
        indexed address changer,          // topic 1
        string newStatus,                 // data
        uint256 timestamp                 // data
    );

    // Event 3: Requirement Added
    event RequirementAdded(
        indexed uint256 specId,          // topic 0
        indexed bytes32 requirementHash,  // topic 1
        string requirementId,             // data
        address author,                   // data
        uint256 timestamp                 // data
    );

    // Event 4: Approval
    event ApprovalAdded(
        indexed uint256 specId,          // topic 0
        indexed address approver,         // topic 1
        string role,                      // data
        uint256 timestamp                 // data
    );

    // Event 5: Merkle Root Updated
    event MerkleRootUpdated(
        indexed uint256 specId,          // topic 0
        bytes32 newRoot,                  // data
        uint256 requirementCount,         // data
        uint256 timestamp                 // data
    );
}

// Reading events in JavaScript/TypeScript
interface EventLog {
    blockNumber: number;
    transactionHash: string;
    logIndex: number;
    timestamp: number;
    eventType: string;
    topics: string[]; // indexed parameters
    data: string;     // non-indexed parameters
}

const eventSchema = {
    "SpecCreated": {
        "signature": "0x7f3c2a1d4e5b9c8d2a1f9e8d7c6b5a4f3e2d1c0b",
        "topics": ["specId", "creator"],
        "data": ["version", "ipfsHash", "timestamp"]
    },
    "SpecStatusChanged": {
        "signature": "0x8e4d3b2c5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c",
        "topics": ["specId", "changer"],
        "data": ["newStatus", "timestamp"]
    }
};
```

---

## 4. DID Document JSON-LD Format

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://specs.example.com/ns/specification/v1"
  ],
  "id": "did:web:specs.example.com:specifications:core-auth:v2.1.0",
  "controller": "did:web:specs.example.com",
  "created": "2024-01-15T10:30:00Z",
  "updated": "2024-12-29T14:45:00Z",
  "publicKey": [
    {
      "id": "did:web:specs.example.com:specifications:core-auth:v2.1.0#keys-1",
      "type": "RsaVerificationKey2018",
      "controller": "did:web:specs.example.com:specifications:core-auth:v2.1.0",
      "publicKeyPem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
    }
  ],
  "authentication": [
    "did:web:specs.example.com:specifications:core-auth:v2.1.0#keys-1"
  ],
  "service": [
    {
      "id": "did:web:specs.example.com:specifications:core-auth:v2.1.0#ipfs",
      "type": "IpfsGateway",
      "serviceEndpoint": "https://ipfs.example.com/ipfs/bafybeibxz...",
      "description": "IPFS gateway for full specification document"
    },
    {
      "id": "did:web:specs.example.com:specifications:core-auth:v2.1.0#blockchain",
      "type": "EthereumSmartContract",
      "serviceEndpoint": "0x1234567890123456789012345678901234567890",
      "description": "Smart contract storing NFT metadata"
    },
    {
      "id": "did:web:specs.example.com:specifications:core-auth:v2.1.0#audit",
      "type": "AuditLog",
      "serviceEndpoint": "https://specs.example.com/api/specifications/core-auth/v2.1.0/audit",
      "description": "Complete audit trail and event history"
    }
  ],
  "relatedResource": [
    {
      "id": "did:web:specs.example.com:specifications:core-auth:v1.0.0",
      "relationship": "parent-version",
      "description": "Previous version of this specification"
    },
    {
      "id": "did:web:specs.example.com:specifications:oauth2-implementation",
      "relationship": "related-specification",
      "description": "OAuth2 implementation guide"
    }
  ],
  "proof": {
    "type": "RsaSignature2018",
    "created": "2024-01-15T10:30:00Z",
    "signatureValue": "SflKxwRJSMeKKF2QT4fwpgAFiVA72PAM...",
    "verificationMethod": "did:web:specs.example.com:specifications:core-auth:v2.1.0#keys-1"
  }
}
```

---

## 5. Database Schema for Local Storage

### PostgreSQL Tables

```sql
-- Specifications table
CREATE TABLE specifications (
    id UUID PRIMARY KEY,
    spec_id VARCHAR(255) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    version VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft', -- draft, review, approved, deprecated
    description TEXT,
    ipfs_hash VARCHAR(255),
    cid_version INT DEFAULT 1,
    merkle_root VARCHAR(255),
    requirement_count INT,
    nft_token_id BIGINT,
    nft_contract_address VARCHAR(255),
    did VARCHAR(500) UNIQUE,
    organization_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255),
    INDEX idx_spec_id (spec_id),
    INDEX idx_status (status),
    INDEX idx_version (version),
    INDEX idx_did (did)
);

-- Requirements table
CREATE TABLE requirements (
    id UUID PRIMARY KEY,
    spec_id UUID NOT NULL REFERENCES specifications(id),
    requirement_id VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    acceptance_criteria JSON,
    priority VARCHAR(50), -- critical, high, medium, low
    requirement_hash VARCHAR(255),
    merkle_index INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(spec_id, requirement_id),
    INDEX idx_spec_id (spec_id),
    INDEX idx_requirement_id (requirement_id),
    INDEX idx_requirement_hash (requirement_hash)
);

-- Events table (audit trail)
CREATE TABLE events (
    id UUID PRIMARY KEY,
    spec_id UUID NOT NULL REFERENCES specifications(id),
    event_type VARCHAR(100) NOT NULL, -- SpecCreated, SpecStatusChanged, RequirementAdded, etc.
    actor VARCHAR(255),
    actor_role VARCHAR(100),
    transaction_hash VARCHAR(255),
    block_number BIGINT,
    event_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_spec_id (spec_id),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at),
    INDEX idx_transaction_hash (transaction_hash)
);

-- Provenance chain (supply chain)
CREATE TABLE provenance_nodes (
    id UUID PRIMARY KEY,
    spec_id UUID NOT NULL REFERENCES specifications(id),
    node_index INT,
    action VARCHAR(50) NOT NULL, -- created, modified, reviewed, approved, deprecated
    actor VARCHAR(255),
    version VARCHAR(50),
    content_hash VARCHAR(255),
    merkle_root VARCHAR(255),
    previous_hash VARCHAR(255),
    current_hash VARCHAR(255),
    signature VARCHAR(255),
    linked_to VARCHAR(255), -- previous node ID
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_spec_id (spec_id),
    INDEX idx_action (action),
    INDEX idx_current_hash (current_hash),
    FOREIGN KEY (spec_id) REFERENCES specifications(id)
);

-- Approvals table
CREATE TABLE approvals (
    id UUID PRIMARY KEY,
    spec_id UUID NOT NULL REFERENCES specifications(id),
    approver VARCHAR(255),
    approver_role VARCHAR(100),
    approval_status VARCHAR(50), -- approved, rejected, requested_changes
    comments TEXT,
    signature VARCHAR(255),
    transaction_hash VARCHAR(255),
    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_spec_id (spec_id),
    INDEX idx_approver (approver),
    INDEX idx_approval_status (approval_status)
);

-- Vault contributions (ERC-4626)
CREATE TABLE vault_contributions (
    id UUID PRIMARY KEY,
    spec_id UUID NOT NULL REFERENCES specifications(id),
    vault_token_id BIGINT,
    contributor VARCHAR(255),
    amount NUMERIC(30, 0), -- for ERC-20 tokens
    shares NUMERIC(30, 0), -- vault shares
    requirement_id VARCHAR(255),
    contributed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_spec_id (spec_id),
    INDEX idx_vault_token_id (vault_token_id),
    INDEX idx_contributor (contributor)
);

-- ZK Proofs table
CREATE TABLE zk_proofs (
    id UUID PRIMARY KEY,
    spec_id UUID NOT NULL REFERENCES specifications(id),
    proof_type VARCHAR(100), -- coverage, compliance, etc.
    statement TEXT,
    public_inputs JSON,
    proof_data TEXT,
    verifier_address VARCHAR(255),
    is_valid BOOLEAN,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_spec_id (spec_id),
    INDEX idx_proof_type (proof_type),
    INDEX idx_is_valid (is_valid)
);
```

---

## 6. API Request/Response Examples

### Create Specification with Provenance

**Request:**
```bash
POST /api/v1/specifications
Content-Type: application/json

{
  "specificationId": "spec-auth-001",
  "title": "Authentication System Requirements",
  "description": "Core security requirements for authentication",
  "version": "2.1.0",
  "organizationId": "org-123",
  "requirements": [
    {
      "id": "REQ-001",
      "title": "OAuth2 Support",
      "description": "System must support OAuth2",
      "priority": "critical",
      "acceptanceCriteria": [
        "Must support authorization code flow",
        "Must support PKCE"
      ]
    }
  ],
  "ipfsHash": "bafybeibxz...",
  "merkleRoot": "0x7f3c2a1d...",
  "creatorDid": "did:web:example.com:users:alice"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "specification": {
    "id": "uuid-123",
    "specificationId": "spec-auth-001",
    "did": "did:web:specs.example.com:specifications:auth-001:v2.1.0",
    "nftTokenId": 42,
    "nftAddress": "0x1234567890...",
    "ipfsHash": "bafybeibxz...",
    "merkleRoot": "0x7f3c2a1d...",
    "status": "draft",
    "createdAt": "2024-12-29T14:45:00Z"
  },
  "transaction": {
    "hash": "0xabcd1234...",
    "blockNumber": 19123456,
    "gasUsed": 523456
  },
  "events": [
    {
      "id": "evt-001",
      "eventType": "SpecCreated",
      "transactionHash": "0xabcd1234..."
    }
  ]
}
```

### Verify Requirement Membership

**Request:**
```bash
POST /api/v1/specifications/spec-auth-001/verify-requirement
Content-Type: application/json

{
  "requirementId": "REQ-001",
  "requirementHash": "0xabcd1234...",
  "merkleProof": [
    "0x1111111111111111111111111111111111111111111111111111111111111111",
    "0x2222222222222222222222222222222222222222222222222222222222222222",
    "0x3333333333333333333333333333333333333333333333333333333333333333"
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "verified": true,
  "requirementId": "REQ-001",
  "specificationId": "spec-auth-001",
  "requirementHash": "0xabcd1234...",
  "merkleRoot": "0x7f3c2a1d...",
  "proofValid": true,
  "verifiedAt": "2024-12-29T14:45:00Z",
  "details": {
    "treeIndex": 0,
    "treeDepth": 6,
    "computedHash": "0x7f3c2a1d...",
    "matchesRoot": true
  }
}
```

### Get Audit Trail

**Request:**
```bash
GET /api/v1/specifications/spec-auth-001/audit?limit=50&from=2024-01-01
```

**Response (200 OK):**
```json
{
  "success": true,
  "specificationId": "spec-auth-001",
  "auditTrail": {
    "events": [
      {
        "id": "evt-001",
        "timestamp": "2024-01-15T10:30:00Z",
        "eventType": "SpecCreated",
        "actor": "alice@example.com",
        "data": {
          "version": "1.0.0",
          "status": "draft"
        },
        "transactionHash": "0xabcd1234...",
        "blockNumber": 12345678
      },
      {
        "id": "evt-002",
        "timestamp": "2024-06-01T09:00:00Z",
        "eventType": "SpecStatusChanged",
        "actor": "bob@example.com",
        "data": {
          "oldStatus": "draft",
          "newStatus": "review"
        },
        "transactionHash": "0xefgh5678...",
        "blockNumber": 18765432
      },
      {
        "id": "evt-003",
        "timestamp": "2024-12-29T14:45:00Z",
        "eventType": "SpecStatusChanged",
        "actor": "charlie@example.com",
        "data": {
          "oldStatus": "review",
          "newStatus": "approved"
        },
        "transactionHash": "0xijkl9012...",
        "blockNumber": 21234567
      }
    ],
    "summary": {
      "totalEvents": 3,
      "createdAt": "2024-01-15T10:30:00Z",
      "lastModifiedAt": "2024-12-29T14:45:00Z",
      "eventTypes": {
        "SpecCreated": 1,
        "SpecStatusChanged": 2
      }
    }
  }
}
```

### Resolve DID

**Request:**
```bash
GET /api/v1/did/resolve/did:web:specs.example.com:specifications:auth-001:v2.1.0
```

**Response (200 OK):**
```json
{
  "success": true,
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:web:specs.example.com:specifications:auth-001:v2.1.0",
  "specification": {
    "title": "Authentication Requirements",
    "version": "2.1.0",
    "status": "approved",
    "ipfsHash": "bafybeibxz..."
  },
  "publicKey": [
    {
      "id": "did:web:specs.example.com:specifications:auth-001:v2.1.0#key-1",
      "type": "RsaVerificationKey2018",
      "publicKeyPem": "-----BEGIN PUBLIC KEY-----..."
    }
  ],
  "service": [
    {
      "id": "did:web:specs.example.com:specifications:auth-001:v2.1.0#ipfs",
      "type": "IpfsGateway",
      "serviceEndpoint": "https://ipfs.example.com/ipfs/bafybeibxz..."
    }
  ]
}
```

---

## 7. TypeScript Type Definitions

```typescript
// Core types for specification provenance

export interface SpecificationMetadata {
  id: string;
  specificationId: string;
  title: string;
  version: string;
  status: 'draft' | 'review' | 'approved' | 'deprecated';
  description: string;
  organizationId: string;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  updatedBy: string;
}

export interface ContentAddressing {
  ipfsHash: string;
  cidVersion: 0 | 1;
  hashAlgorithm: string;
  contentSize: number;
  pinningService: string;
  pinningStatus: 'pinned' | 'unpinned' | 'pending';
}

export interface MerkleVerification {
  rootHash: string;
  requirementCount: number;
  merkleTreeLevels: number;
  verificationProof: {
    leaf: string;
    proof: string[];
  };
}

export interface BlockchainBinding {
  nftTokenId: number;
  nftAddress: string;
  chainId: number;
  mintedAt: number;
  merkleRootOnChain: string;
}

export interface SpecificationIdentity {
  did: string;
  publicKeyId: string;
  publicKey: string;
  createdAt: Date;
  verificationMethod: string;
}

export interface Requirement {
  id: string;
  specId: string;
  title: string;
  description: string;
  acceptanceCriteria: string[];
  priority: 'critical' | 'high' | 'medium' | 'low';
  requirementHash: string;
  merkleIndex: number;
}

export interface ProvenanceNode {
  nodeId: string;
  timestamp: Date;
  action: 'created' | 'modified' | 'reviewed' | 'approved' | 'deprecated';
  actor: string;
  version: string;
  contentHash: string;
  merkleRoot: string;
  previousHash: string;
  currentHash: string;
  signature: string;
  linkedTo: string[];
  metadata: {
    department: string;
    role: string;
    location?: string;
  };
}

export interface AuditEvent {
  id: string;
  specId: string;
  eventType: string;
  actor: string;
  timestamp: Date;
  transactionHash: string;
  blockNumber: number;
  data: Record<string, any>;
}

export interface SpecificationProvenance {
  metadata: SpecificationMetadata;
  contentAddressing: ContentAddressing;
  merkleVerification: MerkleVerification;
  blockchainBinding: BlockchainBinding;
  identity: SpecificationIdentity;
  requirements: Requirement[];
  auditTrail: AuditEvent[];
  supplyChain: ProvenanceNode[];
}

export interface MerkleProofData {
  requirementHash: string;
  proof: string[];
  merkleRoot: string;
  treeIndex: number;
  treeDepth: number;
}

export interface ZKComplianceProof {
  proofId: string;
  statement: string;
  publicInputs: {
    specificationHash: string;
    requirementCount: number;
    complianceLevel: number;
  };
  proof: string;
  verifier: string;
  verifiedAt: Date;
  isValid: boolean;
}

export interface DIDDocument {
  '@context': string[];
  id: string;
  controller: string;
  created: Date;
  updated: Date;
  publicKey: Array<{
    id: string;
    type: string;
    controller: string;
    publicKeyPem: string;
  }>;
  authentication: string[];
  service: Array<{
    id: string;
    type: string;
    serviceEndpoint: string;
    description: string;
  }>;
  relatedResource?: Array<{
    id: string;
    relationship: string;
    description: string;
  }>;
  proof?: {
    type: string;
    created: Date;
    signatureValue: string;
    verificationMethod: string;
  };
}

export interface SupplyChainEntry {
  specId: string;
  version: string;
  timestamp: Date;
  actor: string;
  action: string;
  previousHash: string;
  currentHash: string;
  ipfsHash: string;
  signature: string;
  metadata: Record<string, any>;
}

export interface VaultContribution {
  contributor: string;
  amount: bigint;
  shares: bigint;
  requirementId: string;
  contributedAt: Date;
}

export interface SpecificationDIDRegistry {
  registerSpecification(
    organizationDomain: string,
    specId: string,
    version: string,
    creatorDid: string,
    creatorKey: string,
    metadata: Record<string, any>
  ): string;

  resolveDid(did: string): DIDDocument | null;

  verifyDidOwnership(
    did: string,
    signature: string,
    publicKey: string
  ): Promise<boolean>;

  addEndorsement(
    specDid: string,
    endorserDid: string,
    endorserKey: string
  ): void;
}
```

---

## 8. Integration Checklist

- [ ] Set up IPFS node or pinning service (Pinata, Estuary, NFT.Storage)
- [ ] Deploy smart contracts (ERC-721 for NFT, ERC-4626 for vaults)
- [ ] Configure database (PostgreSQL with audit tables)
- [ ] Implement DID resolver (W3C compliant)
- [ ] Set up Merkle tree library (ethers.js, circom for ZK)
- [ ] Configure event indexing (The Graph, Subgraph)
- [ ] Implement webhook handlers for contract events
- [ ] Set up HTTPS and security headers for DID resolution
- [ ] Configure backup/redundancy for IPFS content
- [ ] Implement monitoring and alerting for provenance chains

---

## 9. Cost Estimates (Ethereum Mainnet)

| Operation | Gas Cost | USD Cost |
|-----------|----------|----------|
| Mint NFT (ERC-721) | 500,000 | ~$50-100 |
| Update specification status | 100,000 | ~$10-20 |
| Add approval (event only) | 5,000 | ~$0.50-1 |
| Emit audit event | 375 + 8/byte | ~$0.05-0.50 |
| **Monthly (10 specs, 50 updates)** | **~7,000,000** | **~$700-1,400** |

**Layer 2 Cost Estimates (Polygon/Arbitrum):**
- ~90% cheaper than mainnet
- Mint NFT: ~$5-10
- Update status: ~$1-2
- **Monthly**: ~$70-140

---

## 10. Testing Strategy

```typescript
// Jest test examples

describe('SpecificationProvenance', () => {
  describe('IPFS Content Addressing', () => {
    it('should generate deterministic CID from content', async () => {
      const spec = { title: 'Auth', version: '1.0.0' };
      const cid1 = await ipfs.add(JSON.stringify(spec));
      const cid2 = await ipfs.add(JSON.stringify(spec));
      expect(cid1.cid.toString()).toBe(cid2.cid.toString());
    });

    it('should detect content modification via CID change', async () => {
      const spec1 = { title: 'Auth', version: '1.0.0' };
      const spec2 = { title: 'Auth', version: '1.0.1' };
      const cid1 = await ipfs.add(JSON.stringify(spec1));
      const cid2 = await ipfs.add(JSON.stringify(spec2));
      expect(cid1.cid.toString()).not.toBe(cid2.cid.toString());
    });
  });

  describe('Merkle Verification', () => {
    it('should verify requirement membership in merkle tree', () => {
      const requirements = [
        { id: 'REQ-001', title: 'OAuth2' },
        { id: 'REQ-002', title: 'MFA' }
      ];
      const tree = new RequirementMerkleTree(requirements);
      const proof = tree.getProof(0);
      const root = tree.getRoot();

      const leafHash = hashRequirement(requirements[0]);
      const isValid = MerkleTree.verify(proof, leafHash, root);
      expect(isValid).toBe(true);
    });
  });

  describe('Smart Contract Events', () => {
    it('should emit SpecCreated event with correct parameters', async () => {
      const tx = await contract.createSpecification(
        1,
        'Test Spec',
        'ipfs://QmXxxx'
      );
      const receipt = await tx.wait();

      const event = receipt.events.find(e => e.event === 'SpecCreated');
      expect(event.args.specId).toBe(1);
      expect(event.args.version).toBe('Test Spec');
    });
  });

  describe('DID Resolution', () => {
    it('should resolve DID to specification metadata', async () => {
      const did = 'did:web:specs.example.com:specifications:auth:v1.0.0';
      const resolved = await resolveDid(did);

      expect(resolved.specification.specId).toBe('auth');
      expect(resolved.specification.version).toBe('v1.0.0');
    });
  });

  describe('Supply Chain Integrity', () => {
    it('should maintain linked chain of provenance nodes', () => {
      const manager = new SpecificationSupplyChainManager();
      const node1 = manager.createSpecification(
        'spec-1',
        'Test',
        'alice',
        'ipfs://Qm1',
        '0x111'
      );
      const node2 = manager.modifySpecification(
        'spec-1',
        'v1.1.0',
        'bob',
        'ipfs://Qm2',
        '0x222'
      );

      expect(node2.linkedTo).toContain(node1.id);
      const isValid = manager.verifyChainIntegrity('spec-1');
      expect(isValid).toBe(true);
    });
  });
});
```

This comprehensive implementation guide provides production-ready patterns adaptable to your TracerTM system.
