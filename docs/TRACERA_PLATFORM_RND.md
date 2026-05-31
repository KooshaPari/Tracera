# Tracera Platform R&D Blueprint — 4-Pillar Superset Architecture

**Version:** 0.1 (R&D, not yet implemented)
**Date:** 2026-05-31
**Status:** Proposed — sets Tracera's R&D direction as the *robust superset*. AgilePlus is its narrow MVP, not parity.
**Owner:** Platform R&D
**Supersedes scope of:** `docs/FUNCTIONAL_REQUIREMENTS.md` (extends, does not replace)

---

## 0. Thesis

Tracera is **not** a requirements-traceability tool with bolt-ons. It is an **org-wide
engineering-intelligence platform** whose system-of-record is a typed graph that spans four
bounded contexts ("pillars") and the verifiable evidence that connects them:

> **Requirement → Code → Test → PR → Evidence**, across **every repo, team, and release in the org.**

AgilePlus (Rust PM/SDLC engine) is the MVP of **Pillar B only**. Tracera is the superset: it
embeds Pillar B, and adds deep traceability (A), an evidence/verification engine (C), and
multi-repo org intelligence (D) on top of one graph.

This document maps **current → target** per pillar, fixes the **reuse-over-handroll** decisions
(per the org quality charter), specifies a **hexagonal platform architecture**, and proposes a
**phased R&D roadmap** with new FR/NFR IDs registered against the existing
`FR-<CATEGORY>-NNN` scheme.

---

## 1. Current State Survey (as of 2026-05-31)

Surveyed from `E:/Dev/Tracera` working tree. **Correction to the framing brief:** the Tracera
core is **Python** (`src/tracertm/`, package `tracertm`), *not* Rust. There is no `agreement.rs`
or `vision.rs` in this repo. Agreement scoring / VLM verification exist as **services and
intent**, and the Rust assets live in sibling repos (AgilePlus, Authvault, HexaKit). The
blueprint treats the Rust crates as **reuse targets**, not as part of Tracera's core today.

**What exists today:**

| Area | Evidence in tree |
|---|---|
| Typed graph SSOT | `models/graph*.py`, `models/trace_link.py`, `models/{node_kind,edge_type,link_type}.py`; `storage/neo4j_trace_link_writer.py`; `services/graph_service.py`, `graph_analysis_service.py`, `graph_snapshot_service.py` |
| Traceability core (A) | `services/traceability_service.py`, `traceability_matrix_service.py`, `traceability_score_service.py`, `advanced_traceability_service.py`, `trace_service.py`, `auto_link_service.py`, `commit_linking_service.py`, `coverage_matrix_service.py` |
| Impact / blast radius (A) | `impact_analysis_service.py`, `blast_radius_service.py`, `critical_path_service.py`, `shortest_path_service.py`, `cycle_detection_service.py`, `feat/cypher-impact-api` branch |
| SDLC / PM (B) | `models/{item,feature,project,specification,adr,scenario,workflow,workflow_run,workflow_schedule}.py`; `services/{feature,item,specification,adr,status_workflow,progress_tracking}_service.py`; `adapters/agileplus_adapter.py` |
| Verification / evidence (C) | `services/verification_service.py`, `services/recording/{playwright_service,vhs_service,ffmpeg_pipeline,tape_generator}.py`, `services/requirement_quality_service.py`, `requirement_miner.py`; `docs/journeys/` (manifests stub) |
| Multi-repo intelligence (D) | `services/{dependency_analysis,dup_conflict_detector,github_import,github_project,jira_import,import,ingestion,external_integration}_service.py`; `models/{integration,external_link,github_app_installation,linear_app}.py` |
| Infra / ports | `database/{connection,async_connection}.py` (PG), `vault/` (secrets), `services/event_service.py` + `event_sourcing_service.py` (NATS-shaped), `storage/local_storage.py` + sync engine (MinIO-shaped), `mcp/` server, `grpc/` + `proto/`, `observability/` |
| Surfaces | `frontend/` Bun+Turbo monorepo (`apps/`, `packages/`); `tui/`; `feat/electrobun-desktop` branch (desktop app); MCP server |
| Requirements governance | `docs/FUNCTIONAL_REQUIREMENTS.md` — **142 FRs** across 9 categories (DISC/QUAL/APP/VERIF/RPT/COLLAB/AI/INFRA/MCP), each already wired to `Implemented in:` / `Tested in:` |

**Maturity:** Tracera is *far past MVP*. ~90 Python services, 50+ models, 201+ endpoints, an MCP
server, a TUI, and a desktop branch already exist. The R&D gap is **not "build features"** — it
is **coherence**: the four pillars exist as loosely-federated service piles without explicit
bounded-context seams, a unified graph schema contract, or a verification engine that closes the
loop from requirement to *visual* evidence.

### 1.1 Current → Target, per pillar

| Pillar | Today | Gap to target | Verdict |
|---|---|---|---|
| **A — Deep Requirements Traceability** | Neo4j writer + 10+ trace/impact services; matrix, blast-radius, agreement-scoring services present | No single typed-graph **schema contract** (node/edge kinds drift across services); agreement scoring is heuristic, not a pluggable scorer port (Jaccard / SentenceTransformer / SigLIP); reverse-impact API still on a feature branch | **80% — solidify into the platform spine** |
| **B — Full SDLC / Program Mgmt** | Items, features, specs, ADRs, workflows, status; `agileplus_adapter` | No portfolios/OKRs/roadmaps/releases as first-class graph nodes; AgilePlus (Rust) is a *sibling engine*, integration is one thin adapter, not a shared contract | **55% — extend, fold AgilePlus in as the PM engine via a contract port** |
| **C — Evidence & Verification Engine** | `verification_service`, Playwright/VHS/FFmpeg recording, journeys manifest stub | No **blind-vs-intent** keyframe verification loop; no VLM "code matches requirement" proof; evidence not stored as first-class graph artifacts in MinIO with TraceLinks; phenotype-journeys not wired | **35% — biggest build gap; wrap phenotype-journeys** |
| **D — Multi-Repo Org Intelligence** | Per-repo import (GitHub/Jira/Linear), dep analysis, dup/conflict detector | No org-wide **repo graph / ecosystem map** as a Tracera view; rationalization layer lives only in phenotype-registry docs; no cross-repo dependency or dup rollup surfaced in SPA | **30% — wrap phenotype-registry ecosystem-map/rationalization** |

---

## 2. Reuse / Wrap Decisions (wrap > handroll)

Per the quality charter and the "use existing ecosystem first" + "abstraction at 2 uses" memory.
Tracera **must not** re-implement what a sibling already ships.

| Need | Wrap this (do not handroll) | Location | Pillar | Integration seam |
|---|---|---|---|---|
| Auth / sessions / tokens | **Authvault** (Rust auth crate, has FRs/ + audit) — extends existing `workos_auth_service.py` | `C:/Users/koosh/Dev/Authvault` | INFRA | Auth port → Authvault behind HTTP/gRPC; replace ad-hoc auth |
| PM / SDLC engine (B) | **AgilePlus** (Rust Cargo workspace: crates/, agileplus-mcp, agents) | `C:/Users/koosh/Dev/AgilePlus` | B | Promote `agileplus_adapter.py` → a **PM contract port**; AgilePlus serves portfolios/OKRs/roadmaps/releases; Tracera projects them as graph nodes |
| Evidence / keyframe engine (C) | **phenotype-journeys** (blind-vs-intent keyframe + VLM verification) | sibling org repo (not cloned locally; toolchain-pinned — consumers override) | C | Evidence port → journeys runner; outputs keyframes + verdicts as MinIO artifacts + TraceLinks |
| Org ecosystem map + rationalization (D) | **phenotype-registry** (`ECOSYSTEM_MAP.md`, `RATIONALIZATION_PLAN.md`, `LIBRARY_RESEARCH_REGISTRY.md`, scaffold/) | `E:/Dev/phenotype-registry` | D | Registry port → ingest registry graph into Tracera's org-repo view |
| Shared hexagonal substrate | **HexaKit** `phenotype-*` crates: `port-traits`, `ports-canonical`, `contract(s)`, `event-bus`, `event-sourcing`, `mcp`, `project-registry`, `xdd-lib`, `bdd`, `compliance-scanner`, `policy-engine`, `telemetry`, `state-machine`, `validation` | `C:/Users/koosh/Dev/HexaKit-work` | all | Define canonical ports here; both Tracera (Py via gRPC/contract) and AgilePlus (Rust direct) consume the same contracts |
| Recording primitives (C) | Existing in-tree `recording/` (Playwright/VHS/FFmpeg) — already correct, keep | `src/tracertm/services/recording/` | C | Becomes the capture half of the Evidence port |

**Net build vs wrap:** Pillar A = mostly *refactor/solidify* (already built). Pillar B = *wrap
AgilePlus*. Pillar C = *wrap phenotype-journeys* + build the loop. Pillar D = *wrap
phenotype-registry*. Genuinely new code is concentrated in **the contract seams and the C loop**,
not in re-building features.

---

## 3. Platform Architecture (Hexagonal)

### 3.1 Bounded contexts = the 4 pillars

Each pillar is a **bounded context** with its own domain model, application services, and ports.
They share **one** thing: the typed graph SSOT (the integration contract). They never reach into
each other's services — only into the graph and via published domain events.

```
                         ┌────────────────────────────────────────────┐
                         │            SURFACES (driving adapters)        │
                         │  SPA (Bun/Turbo)  Desktop (Electrobun)  TUI   │
                         │  MCP server       gRPC/proto      REST v1     │
                         └───────────────┬──────────────────────────────┘
                                         │  (driving ports)
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                ▼                ▼                ▼
 ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐
 │  PILLAR A   │  │  PILLAR B   │  │  PILLAR C   │  │      PILLAR D        │
 │ Traceability│  │ SDLC / PM   │  │  Evidence & │  │  Multi-Repo Org      │
 │   Core      │  │ (AgilePlus) │  │ Verification│  │   Intelligence       │
 │ TraceLink   │  │ portfolios  │  │ journeys    │  │ repo graph, dep/dup, │
 │ graph,      │  │ OKRs,roadmap│  │ blind-vs-   │  │ rationalization      │
 │ impact,     │  │ releases,   │  │ intent VLM, │  │ (phenotype-registry) │
 │ scoring     │  │ compliance  │  │ evidence    │  │                      │
 └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘
        │                │                │                    │
        └────────────────┴───────┬────────┴────────────────────┘
                                  ▼  (driven ports — canonical, from HexaKit)
        ┌──────────────────────────────────────────────────────────────┐
        │  GRAPH (Neo4j)   RELATIONAL (PG)   EVENTS (NATS)               │
        │  OBJECT (MinIO)  SECRETS (Authvault/Vault)  SCORERS (VLM/ST)   │
        └──────────────────────────────────────────────────────────────┘
```

### 3.2 Driven ports (canonical, defined in HexaKit; Python protocols mirror them)

- `GraphPort` — typed node/edge upsert + Cypher impact queries (Neo4j). The **only** writer of graph truth.
- `RelationalPort` — projections, list/search, audit log (PG).
- `EventPort` — publish/subscribe domain events (NATS); already shaped by `event_sourcing_service`.
- `ObjectPort` — evidence artifacts: screenshots, recordings, keyframes (MinIO); already shaped by `storage/`.
- `AuthPort` — Authvault.
- `ScorerPort` — pluggable agreement scoring: `JaccardScorer`, `SentenceTransformerScorer`, `SigLIPScorer` (text), VLM blind-vs-intent (visual). Strategy pattern; pillar A + C consume it.
- `PmEnginePort` — AgilePlus (portfolios/OKRs/roadmaps/releases).
- `EvidenceRunnerPort` — phenotype-journeys.
- `RegistryPort` — phenotype-registry ecosystem/rationalization feed.

### 3.3 Data model

**Graph (Neo4j) — the SSOT.** One typed schema contract (the current gap is that node/edge kinds
drift). Canonical node kinds: `Requirement, Spec, ADR, Code, Test, PR, Commit, Release, Repo,
Team, Portfolio, OKR, Roadmap, Evidence, Journey, Keyframe`. Canonical edges:
`TRACES_TO, VERIFIES, IMPACTS, DEPENDS_ON, DUPLICATES, IMPLEMENTS, COVERS, EVIDENCES,
BELONGS_TO, RELEASES`. **All four pillars write only via `GraphPort` against this contract.**

**Relational (PG).** Read-model projections, fast list/search/filter, full audit/compliance
trail, user/account/RBAC, workflow run history. Derived from graph + events; never the source of
traceability truth.

**Object (MinIO).** Evidence blobs (screenshots, recordings, keyframes, VLM verdict cards),
addressed by content hash, linked from `Evidence`/`Keyframe` graph nodes.

**Events (NATS).** `requirement.changed`, `tracelink.created`, `evidence.verified`,
`release.cut`, etc. Drive projections, cross-pillar reactions, and the verification loop.

### 3.4 How the surfaces expose all 4

- **SPA** (Bun/Turbo `frontend/apps/`): one app, four pillar workspaces sharing a graph-explorer
  component + the read-model API. Pillar A = trace matrix + impact graph; B = portfolio/roadmap
  boards; C = evidence timeline w/ blind-vs-intent diff viewer; D = org repo/ecosystem map.
- **Desktop** (Electrobun branch): same SPA shell + local file-watcher ingestion (`storage/file_watcher`) for live code↔requirement linking.
- **MCP**: agent-facing tools per pillar (query trace, create link, run verification, query org graph) — the agent integration channel.
- **TUI / gRPC / REST v1**: programmatic + CI surfaces (e.g. CI posts evidence + TraceLinks).

---

## 4. Phased R&D Roadmap

**Pillar-1 priority = solidify Pillar A as the platform spine**, because B/C/D all write into the
same graph and are worthless if the schema contract and scoring ports aren't canonical first.

### Phase 0 — Contract foundation (spine)  *[FR-PLAT, NFR-PLAT]*
- Extract the **canonical graph schema contract** (node/edge kinds) into HexaKit; make `GraphPort` the sole graph writer; migrate the ~12 trace/impact services onto it.
- Define `ScorerPort` + the strategy implementations (Jaccard / SentenceTransformer / SigLIP / VLM).
- Land the reverse/forward impact API (graduate `feat/cypher-impact-api`).
- **Exit:** every existing trace service writes via one contract; impact API on main.

### Phase 1 — Pillar A hardening *[extends FR-QUAL, FR-DISC]*
- Pluggable agreement scoring behind `ScorerPort`; bulk TraceLink ingestion (graduate `feat/trc013`); blast-radius scoring (graduate `feat/trc015`).

### Phase 2 — Pillar C: the verification loop *[FR-VERIF-011..020]*
- Wrap **phenotype-journeys** behind `EvidenceRunnerPort`; store keyframes/recordings in MinIO as `Evidence` nodes with `VERIFIES` edges; implement **blind-vs-intent** VLM verdict ("does the running code match the requirement?"). This is the biggest net-new build.

### Phase 3 — Pillar B: fold in AgilePlus *[FR-APP-011..020]*
- Promote `agileplus_adapter` → `PmEnginePort`; project portfolios/OKRs/roadmaps/releases as graph nodes; compliance/audit trail on PG.

### Phase 4 — Pillar D: org intelligence *[FR-RPT-013..020 / new FR-ORG]*
- Wrap **phenotype-registry** behind `RegistryPort`; org repo-graph + dependency/dup rationalization surfaced as an SPA view.

### Phase 5 — Surface unification & polish
- Four pillar workspaces in one SPA; desktop parity; MCP tool coverage per pillar.

---

## 5. New Requirements (registered; extend existing scheme)

These are the **epics + headline FR/NFR IDs** this blueprint introduces. Full text and
`Implemented in:` / `Tested in:` to be backfilled as phases land (per traceability requirement).

**Epics**
- `EPIC-TRC-PLATFORM` — Tracera 4-pillar superset platform (this blueprint).
- `EPIC-TRC-A-SPINE` — Canonical graph contract + scorer ports (Phase 0–1).
- `EPIC-TRC-C-VERIFY` — Evidence & verification engine (Phase 2).
- `EPIC-TRC-B-PM` — AgilePlus PM engine integration (Phase 3).
- `EPIC-TRC-D-ORG` — Multi-repo org intelligence (Phase 4).

**FRs (new)**
- `FR-PLAT-001` Canonical typed-graph schema contract; `GraphPort` is the sole graph writer.
- `FR-PLAT-002` Pluggable `ScorerPort` (Jaccard / SentenceTransformer / SigLIP / VLM).
- `FR-VERIF-011` Blind-vs-intent VLM verification of running code against requirement.
- `FR-VERIF-012` Evidence artifacts (keyframes/recordings) stored in MinIO as graph `Evidence` nodes with `VERIFIES` edges, via phenotype-journeys.
- `FR-APP-011` Portfolios / OKRs / roadmaps / releases as first-class graph nodes via AgilePlus `PmEnginePort`.
- `FR-ORG-001` Org-wide repo/ecosystem graph + dependency/dup rationalization view via phenotype-registry `RegistryPort`.

**NFRs (new)**
- `NFR-PLAT-001` Graph writes go through exactly one contract (no service writes Neo4j directly).
- `NFR-PLAT-002` Wrap-over-handroll: Authvault/AgilePlus/journeys/registry/HexaKit are consumed via ports, not re-implemented.
- `NFR-PLAT-003` Every shipped capability traces Requirement→Code→Test→PR in the graph (self-hosting: Tracera traces itself).

---

## 6. Open Architecture Questions (for the user)

1. **Polyglot boundary.** Tracera core is **Python**; AgilePlus/Authvault/HexaKit ports are **Rust**. Do we (a) consume them as out-of-process services (gRPC/HTTP — clean but operational cost), or (b) pursue a Rust core for Tracera over time (the framing brief assumed Rust)? This is the single biggest decision.
2. **Graph vs relational source-of-truth.** Confirm Neo4j is the SSOT and PG is strictly a derived read-model + audit store (this blueprint assumes so). Any capability that needs strong transactional writes (PM/releases) may pressure that.
3. **AgilePlus relationship.** Is AgilePlus a *subordinate engine* Tracera wraps (this blueprint), or does it remain an independent product with Tracera merely federating it? Affects whether B's domain lives in AgilePlus or Tracera.
4. **VLM provider for blind-vs-intent.** Use the org Kimi K2.6 / Firepass stack, or a local vision model? Cost + determinism (memory says determinism is *not* required) tradeoff.
5. **Scope ceiling.** "And much much more" — should this blueprint reserve a Pillar E (e.g. cost/FinOps, or runtime observability via PhenoObservability) now, or defer?

---

## 7. Self-hosting principle

Tracera must trace **itself**: this blueprint's epics/FRs are registered in Tracera + AgilePlus,
and each future PR links Requirement→Code→Test→PR in the graph. Dogfooding is the acceptance test
for Pillar A.
