# Tracera Remediation: Data Layer Hardening (I-Data)

## Scope

- Neo4j-backed traceability graph persistence (`tracertm/storage/*`)
- Migration/versioning strategy for graph schema and writer/adapter evolution

This repo currently uses:
- `src/tracertm/storage/neo4j_trace_link_writer.py` for write graph ops,
- `src/tracertm/storage/neo4j_graph_port.py` for GraphPort adapter boundaries.

## 1) Neo4j backup procedure

Run these commands from the Neo4j container or host with network access to Neo4j:

```bash
# Dump a full DB
docker exec -it tracera_neo4j neo4j-admin database dump neo4j \
  --to-path=/var/lib/neo4j/import \
  --overwrite-destination=true

# Copy dump artifact to host
docker cp tracera_neo4j:/var/lib/neo4j/import/neo4j.dump \
  ./backups/neo4j-$(date -u +%Y%m%d-%H%M%S).dump

# Stop writes before restore window
docker stop tracera-backend-go tracera-backend-python
```

## 2) Neo4j restore procedure

```bash
# Copy backup back into container
docker cp ./backups/<dump-file>.dump tracera_neo4j:/var/lib/neo4j/import/<dump-file>.dump

# Stop target DB cleanly
docker exec tracera_neo4j neo4j-admin database stop --database=neo4j

# Remove current DB files if approved
docker exec tracera_neo4j neo4j-admin database unload neo4j --force

# Restore from dump
docker exec tracera_neo4j neo4j-admin database load neo4j \
  --from-path=/var/lib/neo4j/import/<dump-file>.dump \
  --overwrite-destination=true

# Start DB and verify
docker exec tracera_neo4j neo4j-admin database start neo4j
```

Post-restore validation:

- run a smoke check against `/api/v1/traceability` read paths,
- compare counts for `Artifact`/`Requirement`/relationships before and after restore,
- run at least one traversal query using
  `query_forward_impact` and `query_reverse_impact`.

## 3) Migration/versioning approach

### Baseline now

- Graph schema is represented in code by typed values:
  - `TraceLinkType`
  - `ArtifactKind`
  - `RequirementStatus`
  - relationship projections in `src/tracertm/storage/neo4j_graph_port.py`.
- There is no explicit user-facing graph schema migration registry.

### Proposed versioning controls

1. Add explicit graph schema versions in `Neo4jGraphPort`:
   - `neo4j.setGraphDatabaseVersion("tracegraph", "vN")` via a single initialization routine
2. Maintain a migration index file:
   - `docs/remediation/neo4j-migrations.md`
   - columns: `version`, `date`, `scope`, `backward_compat`, `downgrade_plan`, `validation`.
3. For each breaking relation/label change:
   - add migration note,
   - add forward/backward compatibility window,
   - add runtime guard in `validate_node()` / `validate_edge()` boundaries.
4. Keep migration evidence in Git with changelog notes and rollout/rollback command block.

### Suggested sequencing for high-impact changes

1. Draft migration ticket and impact assessment.
2. Add Cypher migration in one migration runbook file.
3. Add adapter conversion test in a pre-commit smoke script.
4. Roll out with read-path fallback for one release window:
   - accept both old and new enum values,
   - normalize internally.
5. Remove fallback after deprecation window.

## 4) Operational safety checks

- Before backup/restore:
  - stop or drain `/api/v1/impact` endpoints,
  - take app-level lock if mutation endpoints are live.
- After restore:
  - run `GET /health` + `GET /ready`,
  - run impact traversal smoke,
  - verify `/api/v1/traceability` post count shape and deterministic response order.

