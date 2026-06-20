# Environment Configuration Audit & Consolidation Plan

## Current State Analysis

### Problem: 14 .env Files (Redundancy & Confusion)
```
.env                    # Main (174 lines)
.env.backup             # Backup copy
.env.example            # Template
.env.template           # Another template
.env.shared             # Shared vars
.env.local              # Local override
.env.integration        # Integration test
.env.neo4j.example      # Neo4j template
.env.python             # Python-specific
.env.python-backend     # Python backend
.env.go                 # Go-specific
.env.go-backend         # Go backend
.env.frontend           # Frontend
.env.gateway            # Gateway
```

**Issue**: Developers don't know which file to use. Secrets scattered across multiple files.

---

## Required Services (NO OPTIONALITY)

### 1. **Neo4j** (Graph Database)
- **Status**: Currently marked "Optional" in .env
- **Change**: Make REQUIRED for local development
- **Setup**: Homebrew + local instance
- **Config**:
  ```
  NEO4J_URI=neo4j://localhost:7687
  NEO4J_USER=neo4j
  NEO4J_PASSWORD=<local-dev-password>
  NEO4J_DATABASE=neo4j
  ```

### 2. **Hatchet** (Workflow Orchestration)
- **Status**: Currently commented out
- **Change**: Make REQUIRED
- **Setup**: Local Hatchet instance or cloud token
- **Config**:
  ```
  HATCHET_CLIENT_TOKEN=<token>
  HATCHET_API_URL=https://cloud.onhatchet.run
  ```

### 3. **Voyage AI** (Embeddings)
- **Status**: Partially configured
- **Change**: Make REQUIRED with fallback to sentence-transformers
- **Config**:
  ```
  EMBEDDING_PROVIDER=voyage
  VOYAGE_API_KEY=<api-key>
  VOYAGE_MODEL=voyage-3.5
  VOYAGE_DIMENSIONS=1024
  ```

### 4. **GitHub Integration**
- **Status**: Commented out
- **Change**: Make REQUIRED
- **Credentials Provided**:
  - Client ID: `Iv23liGR8KgbxkmtriYr`
  - Private Key: `/Users/kooshapari/Downloads/tracertm.2026-01-28.private-key.pem`
  - Webhook Secret: `e8b1050d0b3eeff2283e8d24a227821db3f8114b98235b6650768aa5853f6910`

---

## Consolidation Strategy

### Phase 1: Create Master .env
- Single source of truth
- All required services configured
- Clear sections for each service
- Comments explaining each variable

### Phase 2: Remove Redundant Files
- Keep only: `.env`, `.env.example`, `.env.local` (gitignored)
- Archive others to `ARCHIVE/env-configs/`

### Phase 3: Update Code
- Remove optional checks for Neo4j, Hatchet
- Treat as required services
- Add startup validation

### Phase 4: Documentation
- Setup guide for local development
- Service initialization scripts
- Troubleshooting guide

---

## Next Steps
1. ✅ Audit complete
2. ⏳ Create consolidated .env template
3. ⏳ Update backend code for required services
4. ⏳ Create setup scripts
5. ⏳ Document in README

