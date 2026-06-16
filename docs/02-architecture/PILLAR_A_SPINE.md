# Pillar-A Spine — Canonical Graph Contract + ScorerPort (Phase 0)

**Status:** Scaffolding landed (contracts + tests). Migration of services pending.
**Epic:** `EPIC-TRC-A-SPINE`
**Requirements:** `FR-TRC-018`, `FR-TRC-019`, `NFR-TRC-010`, `NFR-TRC-011`
**Blueprint:** [`docs/TRACERA_PLATFORM_RND.md`](../TRACERA_PLATFORM_RND.md) §3.2–§3.3, §4 (Phase 0)

---

## 1. Why this is the first step

The platform blueprint (PR #493) makes Pillar A (deep traceability) the **spine**:
Pillars B/C/D all write into the *same* typed graph and are worthless if the schema
contract and scoring ports are not canonical first. Today the failure mode is **drift** —
node/edge kinds are invented ad-hoc across ~12 trace/impact services and the Neo4j
writer, and agreement scoring is heuristic and duplicated. This change introduces the
two contracts that stop the drift.

This is **one focused Phase-0 step**: the contracts + a dependency-free reference
implementation + tests. It does **not** migrate the existing services yet (that is the
follow-on tracked below).

## 2. What landed

| Artifact | Requirement | Purpose |
|---|---|---|
| `src/tracertm/ports/graph_contract.py` | `FR-TRC-018`, `NFR-TRC-010` | Canonical `NodeKind` / `EdgeType` enums (closed vocabulary), `GraphNode`/`GraphEdge` value objects, endpoint-validation (`validate_node`/`validate_edge`), and the `GraphPort` protocol — the *sole* graph-write contract. |
| `src/tracertm/ports/scorer.py` | `FR-TRC-019` | `ScorerPort` strategy protocol + `ScoreResult` (normalized `[0,1]` + rationale) + dependency-free `JaccardScorer` reference strategy. |
| `tests/unit/ports/test_graph_contract.py` | — | Vocabulary is closed; valid/invalid endpoints; `GraphPort` is satisfiable. |
| `tests/unit/ports/test_scorer.py` | — | Identical→1.0, disjoint→0.0, partial in-between, strategy is swappable at call site. |

### 2.1 Canonical vocabulary (the contract)

- **Node kinds:** `Requirement, Spec, ADR, Code, Test, PR, Commit, Release, Portfolio,
  OKR, Roadmap, Evidence, Journey, Keyframe, Repo, Team`.
- **Edge types:** `TRACES_TO, VERIFIES, IMPACTS, DEPENDS_ON, DUPLICATES, IMPLEMENTS,
  COVERS, EVIDENCES, BELONGS_TO, RELEASES`.
- **Endpoint rules:** structural edges (`IMPLEMENTS`, `COVERS`, `VERIFIES`, `EVIDENCES`,
  `RELEASES`) constrain their source/target kinds; semantic edges (`TRACES_TO`,
  `IMPACTS`, `DEPENDS_ON`, `DUPLICATES`, `BELONGS_TO`) are open-ended. Anything outside
  the vocabulary raises `SchemaContractError` — drift is impossible by construction.

### 2.2 ScorerPort strategy

`ScorerPort` is the single seam Pillars A and C both consume. The Jaccard strategy is
the zero-dependency baseline; embedding (`SentenceTransformer`, `SigLIP`) and VLM
blind-vs-intent strategies (`FR-TRC-020`, Phase 2) plug in behind the *same* port, so
callers never change.

## 3. Design choices

- **Stdlib-only contracts.** `ports/` has no graph-driver or ML dependency, so every
  pillar and the HexaKit Rust canonical ports can mirror it without heavy imports.
- **`runtime_checkable` Protocols, not ABCs.** Adapters (e.g. a Neo4j adapter wrapping
  the existing `storage/neo4j_trace_link_writer.py`) satisfy the port structurally —
  no inheritance coupling.
- **Validation at the write boundary.** `GraphPort` implementations MUST call
  `validate_node`/`validate_edge` before persisting; this is the enforcement point for
  `NFR-TRC-010`.

## 4. Follow-on (not in this step)

1. **Neo4j adapter** implementing `GraphPort` by wrapping
   `storage/neo4j_trace_link_writer.py`.
2. **Migrate the ~12 trace/impact services** to write *only* via `GraphPort`
   (`traceability_service`, `impact_analysis_service`, `blast_radius_service`, …).
3. **Refactor `traceability_score_service`** to consume `ScorerPort`; add the
   SentenceTransformer/SigLIP strategies (Phase 1).
4. **Graduate** `feat/cypher-impact-api`, `feat/trc013` (bulk ingest), `feat/trc015`
   (blast-radius scoring) onto the contract.
5. **Mirror** the vocabulary in HexaKit canonical ports (`NFR-TRC-011`).

## 5. Self-hosting

Per `NFR-TRC-012`, this change traces itself: `FR-TRC-018`/`FR-TRC-019` →
`src/tracertm/ports/*.py` → `tests/unit/ports/*` → this PR.
