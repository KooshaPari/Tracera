# Traceability Matrix — Four Pillars

This document provides a living traceability skeleton across the four Tracera
platform pillars. Each row maps a high-level requirement to its source
document, test artifact, and current implementation status.

---

## Pillar A — Deep Traceability (Spine)

| Requirement | Source | Test | Status |
|---|---|---|---|
| `FR-TRC-018` — Canonical typed-graph schema contract (`GraphPort`) | `docs/02-architecture/PILLAR_A_SPINE.md` §2.1 | `tests/unit/ports/test_graph_contract.py` | ✅ Landed |
| `FR-TRC-019` — Pluggable agreement scorer (`ScorerPort`) | `docs/02-architecture/PILLAR_A_SPINE.md` §2.2 | `tests/unit/ports/test_scorer.py` | ✅ Landed |
| `NFR-TRC-010` — Closed vocabulary enforcement at write boundary | `docs/02-architecture/PILLAR_A_SPINE.md` §2.1 | `tests/unit/ports/test_graph_contract.py` | ✅ Landed |
| `NFR-TRC-011` — Zero-dependency reference implementations | `docs/02-architecture/PILLAR_A_SPINE.md` §3 | `tests/unit/ports/test_*.py` (stdlib only) | ✅ Landed |
| `FR-TRC-020` — VLM blind-vs-intent scoring (Phase 2) | `docs/TRACERA_PLATFORM_RND.md` §4 | *pending* | 🚧 Planned |

---

## Pillar B — SDLC / Program Management

| Requirement | Source | Test | Status |
|---|---|---|---|
| `FR-TRC-021` — Roadmap ↔ OKR bidirectional linking | `docs/TRACERA_PLATFORM_RND.md` §3.2 | *pending* | 🚧 Planned |
| `FR-TRC-022` — Portfolio-level release train tracking | `docs/TRACERA_PLATFORM_RND.md` §3.2 | *pending* | 🚧 Planned |
| `NFR-TRC-012` — Sub-100ms query latency for PM views | `docs/TRACERA_PLATFORM_RND.md` §4 | *pending* | 🚧 Planned |

---

## Pillar C — Evidence & Verification

| Requirement | Source | Test | Status |
|---|---|---|---|
| `FR-TRC-023` — Evidence node kind (`Evidence`, `Keyframe`) | `src/tracertm/ports/graph_contract.py` | `tests/unit/ports/test_graph_contract.py` | ✅ Landed |
| `FR-TRC-024` — SigLIP visual embedding scorer | `src/tracertm/ports/scorer.py` | *pending* | 🚧 Planned |
| `FR-TRC-025` — Journey trace link confidence scoring | `docs/evidence-contract.md` | *pending* | 🚧 Planned |

---

## Pillar D — Multi-Repo Org Intelligence

| Requirement | Source | Test | Status |
|---|---|---|---|
| `FR-TRC-026` — Repo-to-team ownership mapping (`BELONGS_TO`) | `src/tracertm/ports/graph_contract.py` | `tests/unit/ports/test_graph_contract.py` | ✅ Landed |
| `FR-TRC-027` — Cross-repository impact analysis | `docs/ARCHITECTURE.md` — Matrix Build Pipeline | `tests/` (integration) | 🚧 Planned |
| `FR-TRC-028` — Commit-to-release lineage (`RELEASES`) | `src/tracertm/ports/graph_contract.py` | `tests/unit/ports/test_graph_contract.py` | ✅ Landed |

---

## Legend

| Symbol | Meaning |
|---|---|
| ✅ | Contract / scaffolding landed |
| 🚧 | Planned or in-flight |
| ❌ | Blocked / not started |

---

*Last updated: integration/consolidate branch — auto-generated skeleton.*
