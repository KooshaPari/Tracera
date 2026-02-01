# Integration Guide: Blockchain Provenance for TracerTM Specifications

This document maps blockchain/NFT provenance concepts to your TracerTM system architecture.

---

## Current TracerTM Architecture

### Existing Models
- **Specification** - TracerTM's primary entity
- **ItemSpec** - Detailed item specifications
- **Requirements/Acceptance Criteria** - Core specification content
- **TestCase, TestRun, TestSuite** - Verification entities

### Current Storage
- PostgreSQL: Metadata and relationships
- IPFS (optional): Already considered for some storage
- Events: Limited event tracking

---

## Integration Points: Mapping to TracerTM

### 1. Specification Content Addressing

**Current State:**
```python
# tracertm/models/specification.py
class Specification(Base):
    id = Column(UUID, primary_key=True)
    name = Column(String)
    version = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Enhanced with Provenance:**
```python
class Specification(Base):
    id = Column(UUID, primary_key=True)
    name = Column(String)
    version = Column(String)
    description = Column(Text)

    # NEW: Content Addressing
    ipfs_hash = Column(String, nullable=True)  # bafybeibxz...
    cid_version = Column(Integer, default=1)  # CIDv1
    content_hash = Column(String, nullable=True)  # SHA-256
    merkle_root = Column(String, nullable=True)  # For requirements baseline

    # NEW: Identity
    did = Column(String, unique=True, nullable=True)  # Decentralized Identifier

    # NEW: Blockchain Binding
    nft_token_id = Column(BigInteger, nullable=True)
    nft_contract_address = Column(String, nullable=True)
    nft_chain_id = Column(Integer, nullable=True)  # 1=mainnet, 137=polygon
    nft_minted_at = Column(DateTime, nullable=True)

    # NEW: Audit
    content_locked = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. Requirement-Level Merkle Verification

**Current State:**
```python
# tracertm/models/item_spec.py
class ItemSpec(Base):
    id = Column(UUID, primary_key=True)
    specification_id = Column(UUID, ForeignKey('specification.id'))
    title = Column(String)
    description = Column(Text)
    acceptance_criteria = Column(JSON)
```

**Enhanced:**
```python
class ItemSpec(Base):
    id = Column(UUID, primary_key=True)
    specification_id = Column(UUID, ForeignKey('specification.id'))
    title = Column(String)
    description = Column(Text)
    acceptance_criteria = Column(JSON)

    # NEW: Merkle Verification
    requirement_hash = Column(String, nullable=True)  # SHA-256 of requirement
    merkle_index = Column(Integer, nullable=True)     # Position in merkle tree
    merkle_proof = Column(JSON, nullable=True)        # Proof of inclusion

    # Relationship back to spec's merkle root for verification
    def verify_in_baseline(self):
        """Verify this requirement is in specification's baseline"""
        spec = Specification.get(self.specification_id)
        if not spec.merkle_root or not self.merkle_proof:
            return False
        # Call smart contract or library to verify
        return verify_merkle_proof(
            self.requirement_hash,
            self.merkle_proof,
            spec.merkle_root
        )
```

### 3. Event-Based Audit Trail

**Current State:**
```python
# Minimal event tracking
# No structured audit trail for specification changes
```

**Enhanced:**
```python
from sqlalchemy import Column, String, DateTime, JSON, Enum

class SpecificationEvent(Base):
    __tablename__ = 'specification_events'

    id = Column(UUID, primary_key=True)
    specification_id = Column(UUID, ForeignKey('specification.id'), index=True)

    # Event metadata
    event_type = Column(String, index=True)  # SpecCreated, SpecStatusChanged, etc
    actor = Column(String)  # User who triggered event
    actor_role = Column(String)  # Author, Reviewer, Approver

    # Blockchain reference
    transaction_hash = Column(String, nullable=True)  # If on-chain
    block_number = Column(BigInteger, nullable=True)

    # Event details
    event_data = Column(JSON)  # Flexible schema for different event types

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Query helpers
    @classmethod
    def get_audit_trail(cls, spec_id: UUID, limit: int = 100):
        """Get complete audit trail for specification"""
        return cls.query.filter_by(
            specification_id=spec_id
        ).order_by(cls.created_at).limit(limit)
```

### 4. Supply Chain / Provenance Chain

**New Entity:**
```python
class SpecificationProvenanceNode(Base):
    __tablename__ = 'specification_provenance_nodes'

    id = Column(UUID, primary_key=True)
    specification_id = Column(UUID, ForeignKey('specification.id'), index=True)

    # Node info
    node_index = Column(Integer)  # Position in chain
    action = Column(String)  # created, modified, reviewed, approved, deprecated
    actor = Column(String)  # Who performed action

    # Version snapshot
    version = Column(String)
    content_hash = Column(String)  # IPFS hash at this version
    merkle_root = Column(String)

    # Chain linking
    previous_hash = Column(String)  # Hash of previous node
    current_hash = Column(String)   # Hash of this node
    linked_to = Column(String, nullable=True)  # Previous node ID
    signature = Column(String, nullable=True)  # Cryptographic signature

    # Context
    metadata = Column(JSON)  # Department, location, change reason, etc

    created_at = Column(DateTime, default=datetime.utcnow)

    def verify_chain_integrity(self):
        """Verify this node properly links to previous node"""
        if self.node_index == 0:
            return True  # First node is always valid

        previous = SpecificationProvenanceNode.query.filter(
            SpecificationProvenanceNode.specification_id == self.specification_id,
            SpecificationProvenanceNode.node_index == self.node_index - 1
        ).first()

        if not previous:
            return False

        return self.linked_to == previous.id
```

### 5. DID Integration

**New Service:**
```python
# tracertm/services/did_service.py
from typing import Optional
import json

class DidService:
    """Manage Decentralized Identifiers for specifications"""

    def __init__(self, domain: str = "specs.example.com"):
        self.domain = domain

    def generate_did(
        self,
        spec_id: str,
        version: str,
        organization: str
    ) -> str:
        """Generate DID for specification"""
        return f"did:web:{self.domain}:specifications:{spec_id}:v{version}"

    def create_did_document(
        self,
        did: str,
        spec: 'Specification',
        public_key: str
    ) -> dict:
        """Create W3C-compliant DID document"""
        return {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://specs.example.com/ns/specification/v1"
            ],
            "id": did,
            "created": spec.created_at.isoformat() + "Z",
            "updated": spec.updated_at.isoformat() + "Z",
            "publicKey": [{
                "id": f"{did}#key-1",
                "type": "RsaVerificationKey2018",
                "controller": did,
                "publicKeyPem": public_key
            }],
            "authentication": [f"{did}#key-1"],
            "service": [
                {
                    "id": f"{did}#ipfs",
                    "type": "IpfsGateway",
                    "serviceEndpoint": f"ipfs://{spec.ipfs_hash}" if spec.ipfs_hash else None,
                    "description": "Full specification document"
                },
                {
                    "id": f"{did}#api",
                    "type": "SpecificationApi",
                    "serviceEndpoint": f"https://api.example.com/v1/specifications/{spec.id}",
                    "description": "Specification API endpoint"
                }
            ]
        }

    async def register_did(
        self,
        spec: 'Specification',
        public_key: str
    ) -> str:
        """Register DID and store document at .well-known endpoint"""
        did = self.generate_did(spec.name, spec.version, spec.organization)
        doc = self.create_did_document(did, spec, public_key)

        # Store at https://example.com/.well-known/did.json
        # In production: write to S3, CDN, or dedicated DID resolver

        spec.did = did
        return did

    @staticmethod
    async def resolve_did(did: str) -> Optional[dict]:
        """Resolve DID to DID document"""
        # Parse DID
        parts = did.split(':')
        if parts[0] != 'did' or parts[1] != 'web':
            raise ValueError(f"Unsupported DID: {did}")

        domain = parts[2]
        # Fetch from https://{domain}/.well-known/did.json
        # In production: use did-resolver library
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

1. **Add IPFS Storage**
   ```python
   # tracertm/services/ipfs_service.py
   class IpfsService:
       async def store_specification(self, spec: Specification) -> str:
           """Store spec content on IPFS, return CID"""
           content = {
               "id": spec.id,
               "name": spec.name,
               "version": spec.version,
               "description": spec.description,
               "created_at": spec.created_at.isoformat()
           }
           # Use Pinata or local IPFS node
           result = await ipfs_client.add(json.dumps(content))
           return result['hash']  # CID
   ```

2. **Add Merkle Tree Generation**
   ```python
   # tracertm/services/merkle_service.py
   from merkletreejs import MerkleTree

   class MerkleService:
       @staticmethod
       def generate_tree(spec: Specification) -> str:
           """Generate Merkle tree for requirements"""
           requirements = spec.requirements
           leaves = [
               generate_leaf(req)
               for req in requirements
           ]
           tree = MerkleTree(leaves)
           return tree.getRoot()
   ```

3. **Create Event Logger**
   ```python
   # tracertm/services/event_service.py
   class EventService:
       @staticmethod
       async def log_event(
           spec_id: UUID,
           event_type: str,
           actor: str,
           actor_role: str,
           event_data: dict
       ) -> UUID:
           """Create audit event"""
           event = SpecificationEvent(
               specification_id=spec_id,
               event_type=event_type,
               actor=actor,
               actor_role=actor_role,
               event_data=event_data
           )
           db.session.add(event)
           await db.session.commit()
           return event.id
   ```

### Phase 2: Blockchain Integration (Week 3)

1. **Deploy Smart Contracts**
   ```solidity
   // Smart contract for specification NFTs
   // See: IMPLEMENTATION_PATTERNS_SPECIFICATION_PROVENANCE.md
   ```

2. **Add NFT Minting**
   ```python
   # tracertm/services/nft_service.py
   from web3 import Web3

   class NftService:
       def __init__(self, contract_address, private_key):
           self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
           self.contract = self.w3.eth.contract(
               address=contract_address,
               abi=SPECIFICATION_NFT_ABI
           )
           self.account = self.w3.eth.account.from_key(private_key)

       async def mint_specification(
           self,
           spec: Specification
       ) -> str:
           """Mint NFT for specification"""
           tx = self.contract.functions.mintSpecification(
               spec.name,
               spec.ipfs_hash,
               spec.merkle_root,
               len(spec.requirements),
               spec.created_by
           ).buildTransaction({
               'from': self.account.address,
               'nonce': self.w3.eth.get_transaction_count(self.account.address),
               'gas': 500000,
               'gasPrice': self.w3.eth.gas_price,
           })

           signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
           tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)

           spec.nft_token_id = token_id  # Get from event
           spec.nft_contract_address = self.contract.address
           spec.nft_minted_at = datetime.utcnow()

           return tx_hash.hex()
   ```

3. **Index Events**
   ```python
   # Set up The Graph subgraph or Goldsky indexer
   # Query specification events efficiently
   ```

### Phase 3: DID & Provenance (Week 4)

1. **Register DIDs**
   ```python
   async def create_specification(spec_data) -> Specification:
       # ... existing creation logic ...

       # NEW: Generate and register DID
       did_service = DidService()
       did = await did_service.register_did(spec, public_key)
       spec.did = did

       # NEW: Log provenance node
       node = await ProvenanceService.create_node(
           spec_id=spec.id,
           action='created',
           actor=current_user.id,
           version=spec.version,
           ipfs_hash=spec.ipfs_hash,
           merkle_root=spec.merkle_root
       )

       # NEW: Emit event
       await EventService.log_event(
           spec_id=spec.id,
           event_type='SpecCreated',
           actor=current_user.id,
           actor_role='author',
           event_data={
               'version': spec.version,
               'ipfs_hash': spec.ipfs_hash,
               'merkle_root': spec.merkle_root,
               'did': did
           }
       )

       return spec
   ```

---

## API Endpoints to Add

```python
# tracertm/api/routers/specification_provenance.py

from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List, Optional

router = APIRouter(prefix="/api/v1/specifications", tags=["provenance"])

@router.post("/{spec_id}/verify-requirement")
async def verify_requirement(
    spec_id: UUID,
    requirement_id: str,
    merkle_proof: List[str]
) -> dict:
    """Verify requirement is in baseline"""
    spec = await Specification.get(spec_id)
    if not spec.merkle_root:
        raise HTTPException(status_code=400, detail="No merkle root")

    is_valid = verify_merkle_proof(
        requirement_id,
        merkle_proof,
        spec.merkle_root
    )

    return {
        "valid": is_valid,
        "specification_id": spec_id,
        "requirement_id": requirement_id,
        "merkle_root": spec.merkle_root,
        "verified_at": datetime.utcnow()
    }

@router.get("/{spec_id}/audit")
async def get_audit_trail(
    spec_id: UUID,
    limit: int = 50,
    offset: int = 0
) -> dict:
    """Get complete audit trail"""
    events = await SpecificationEvent.query.filter_by(
        specification_id=spec_id
    ).order_by(SpecificationEvent.created_at).limit(limit).offset(offset)

    return {
        "specification_id": spec_id,
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "actor": e.actor,
                "timestamp": e.created_at,
                "data": e.event_data
            }
            for e in events
        ],
        "total": len(events)
    }

@router.get("/{spec_id}/provenance")
async def get_provenance_chain(spec_id: UUID) -> dict:
    """Get supply chain provenance"""
    nodes = await SpecificationProvenanceNode.query.filter_by(
        specification_id=spec_id
    ).order_by(SpecificationProvenanceNode.node_index)

    return {
        "specification_id": spec_id,
        "nodes": [
            {
                "node_id": n.id,
                "action": n.action,
                "actor": n.actor,
                "version": n.version,
                "timestamp": n.created_at,
                "signature": n.signature
            }
            for n in nodes
        ]
    }

@router.get("/{spec_id}/did")
async def get_did(spec_id: UUID) -> dict:
    """Get DID for specification"""
    spec = await Specification.get(spec_id)
    if not spec.did:
        raise HTTPException(status_code=404, detail="DID not registered")

    did_service = DidService()
    doc = await did_service.resolve_did(spec.did)

    return {
        "did": spec.did,
        "document": doc
    }

@router.get("/{spec_id}/nft")
async def get_nft_info(spec_id: UUID) -> dict:
    """Get NFT minting information"""
    spec = await Specification.get(spec_id)
    if not spec.nft_token_id:
        raise HTTPException(status_code=404, detail="Not minted as NFT")

    return {
        "specification_id": spec_id,
        "nft_token_id": spec.nft_token_id,
        "nft_contract_address": spec.nft_contract_address,
        "nft_chain_id": spec.nft_chain_id,
        "nft_minted_at": spec.nft_minted_at,
        "opensea_url": (
            f"https://opensea.io/assets/ethereum/"
            f"{spec.nft_contract_address}/{spec.nft_token_id}"
        )
    }
```

---

## Database Migrations

```python
# alembic/versions/029_add_specification_provenance.py

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add columns to specification table
    op.add_column('specification', sa.Column('ipfs_hash', sa.String()))
    op.add_column('specification', sa.Column('cid_version', sa.Integer(), default=1))
    op.add_column('specification', sa.Column('content_hash', sa.String()))
    op.add_column('specification', sa.Column('merkle_root', sa.String()))
    op.add_column('specification', sa.Column('did', sa.String(), unique=True))
    op.add_column('specification', sa.Column('nft_token_id', sa.BigInteger()))
    op.add_column('specification', sa.Column('nft_contract_address', sa.String()))
    op.add_column('specification', sa.Column('nft_chain_id', sa.Integer()))
    op.add_column('specification', sa.Column('nft_minted_at', sa.DateTime()))
    op.add_column('specification', sa.Column('content_locked', sa.Boolean(), default=False))

    # Add columns to item_spec table
    op.add_column('item_spec', sa.Column('requirement_hash', sa.String()))
    op.add_column('item_spec', sa.Column('merkle_index', sa.Integer()))
    op.add_column('item_spec', sa.Column('merkle_proof', sa.JSON()))

    # Create new tables
    op.create_table(
        'specification_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('specification_id', sa.UUID(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('actor', sa.String(), nullable=False),
        sa.Column('actor_role', sa.String()),
        sa.Column('transaction_hash', sa.String()),
        sa.Column('block_number', sa.BigInteger()),
        sa.Column('event_data', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['specification_id'], ['specification.id']),
        sa.Index('idx_spec_events_spec_id', 'specification_id'),
        sa.Index('idx_spec_events_type', 'event_type'),
        sa.Index('idx_spec_events_created', 'created_at')
    )

    op.create_table(
        'specification_provenance_nodes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('specification_id', sa.UUID(), nullable=False),
        sa.Column('node_index', sa.Integer()),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('actor', sa.String(), nullable=False),
        sa.Column('version', sa.String()),
        sa.Column('content_hash', sa.String()),
        sa.Column('merkle_root', sa.String()),
        sa.Column('previous_hash', sa.String()),
        sa.Column('current_hash', sa.String()),
        sa.Column('linked_to', sa.String()),
        sa.Column('signature', sa.String()),
        sa.Column('metadata', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['specification_id'], ['specification.id']),
        sa.Index('idx_prov_spec_id', 'specification_id')
    )

def downgrade():
    op.drop_table('specification_provenance_nodes')
    op.drop_table('specification_events')
    # Drop columns...
```

---

## Testing

```python
# tests/integration/test_specification_provenance.py

import pytest
from uuid import uuid4

@pytest.mark.asyncio
async def test_create_specification_with_provenance():
    """Test creating specification with full provenance"""
    spec_data = {
        "name": "Auth Requirements",
        "version": "1.0.0",
        "description": "Authentication system requirements",
        "requirements": [
            {
                "id": "REQ-001",
                "title": "OAuth2 Support",
                "acceptance_criteria": ["Must support auth code flow"]
            }
        ]
    }

    # Create
    spec = await create_specification(spec_data, current_user)

    # Verify IPFS storage
    assert spec.ipfs_hash is not None
    assert spec.ipfs_hash.startswith("bafy")

    # Verify Merkle root
    assert spec.merkle_root is not None

    # Verify DID
    assert spec.did is not None
    assert spec.did.startswith("did:web:")

    # Verify audit event
    events = await get_events(spec.id)
    assert len(events) >= 1
    assert events[0].event_type == "SpecCreated"

    # Verify provenance node
    nodes = await get_provenance_nodes(spec.id)
    assert len(nodes) >= 1
    assert nodes[0].action == "created"

@pytest.mark.asyncio
async def test_verify_requirement_in_baseline():
    """Test Merkle verification of requirement"""
    spec = await create_specification(...)
    req = spec.requirements[0]

    # Verify requirement
    result = await verify_requirement(
        spec.id,
        req.id,
        req.merkle_proof
    )

    assert result["verified"] is True
    assert result["merkle_root"] == spec.merkle_root

@pytest.mark.asyncio
async def test_modify_specification_creates_provenance_node():
    """Test that modifications create new provenance nodes"""
    spec = await create_specification(...)
    initial_nodes = await get_provenance_nodes(spec.id)

    # Modify
    await modify_specification(spec.id, {
        "version": "2.0.0",
        "description": "Updated"
    })

    # Verify new node
    new_nodes = await get_provenance_nodes(spec.id)
    assert len(new_nodes) == len(initial_nodes) + 1
    assert new_nodes[-1].action == "modified"
```

---

## Configuration

```python
# tracertm/config/provenance.py

from pydantic import BaseSettings

class ProvenanceSettings(BaseSettings):
    # IPFS
    ipfs_api_url: str = "http://localhost:5001"
    ipfs_gateway_url: str = "https://ipfs.io"
    pinata_api_key: str = None
    pinata_secret_key: str = None

    # Blockchain
    web3_provider_url: str = "https://eth-mainnet.g.alchemy.com/v2/..."
    specification_nft_address: str = "0x1234567890..."
    specification_nft_abi: str = "{}"  # Load from file
    private_key: str = None  # For minting
    chain_id: int = 1  # 1=mainnet, 137=polygon, 42161=arbitrum

    # DID
    did_domain: str = "specs.example.com"
    did_resolver_url: str = "https://example.com/.well-known/did.json"

    # Contracts
    use_layer2: bool = True
    layer2_name: str = "polygon"  # polygon, arbitrum, optimism

    class Config:
        env_prefix = "PROVENANCE_"

provenance_settings = ProvenanceSettings()
```

---

## Summary

### Quick Integration Path

1. **Week 1**: Add IPFS storage + event logging to existing models
2. **Week 2**: Add Merkle tree generation for requirements
3. **Week 3**: Deploy smart contracts + NFT minting
4. **Week 4**: Add DID registration + provenance chain tracking

### Minimal Viable Integration

Start with just:
1. Store specs on IPFS (adds immutability)
2. Generate Merkle roots (enables verification)
3. Create DIDs (adds decentralized identity)
4. Log events (adds audit trail)

Then upgrade to blockchain as needed.

### Key Files to Modify

- `tracertm/models/specification.py` - Add provenance columns
- `tracertm/models/item_spec.py` - Add Merkle verification
- `tracertm/services/` - Add new services for IPFS, Merkle, DID, NFT
- `tracertm/api/routers/` - Add provenance endpoints
- `alembic/versions/` - Add migration

### No Breaking Changes

All changes are additive. Existing code continues to work. New provenance features are opt-in.

---

## Resources for Your Team

1. Read: `BLOCKCHAIN_NFT_SPECIFICATION_PROVENANCE_RESEARCH.md`
2. Reference: `IMPLEMENTATION_PATTERNS_SPECIFICATION_PROVENANCE.md`
3. Quick Start: `SPECIFICATION_PROVENANCE_QUICK_START.md`
4. This document: Integration specifics for TracerTM

Good luck implementing specification provenance!
