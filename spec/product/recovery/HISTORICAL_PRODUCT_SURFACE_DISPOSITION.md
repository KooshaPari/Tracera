# Tracera Historical Product Surface Disposition

**Status:** accepted non-runtime product-intent disposition  
**Date:** 2026-10-01

This document decides the **product-intent destination** of recovered historical surfaces. It does not claim current runtime parity.

## Disposition vocabulary

- **PRESERVE** — mature product still needs the behavior substantially as recovered.
- **ADAPT** — mature product needs the outcome but not necessarily the historical UI/schema/mechanism.
- **SUPERSEDE** — a newer accepted product model replaces the historical surface.
- **OPTIONAL** — useful projection/integration, not universal core.
- **RETIRE** — no longer part of mature product intent.
- **EXECUTION-OWNED** — belongs to AgilePlus or another execution system; Tracera keeps references/evidence only.

## Pre-pivot spine

| Historical journey | Disposition | Mature intent |
|---|---|---|
| HJ-PRE-001 project/product open | ADAPT | Preserve stable product selection/open/recovery; UI route may change. |
| HJ-PRE-002 project item browsing | ADAPT | Preserve complete bounded inventory/navigation for selected product/configuration; no silent fallback to another product. |
| HJ-PRE-003 unified project graph | PRESERVE | Core product graph projection. |
| HJ-PRE-004 graph mode/perspective switching | PRESERVE | Multi-projection product model is central; projection must not mutate/truncate truth silently. |
| HJ-PRE-005 traceability matrix | ADAPT | Preserve matrix/tabular projection as a human inspection surface; canonical truth remains graph/model. |
| HJ-PRE-006 item detail | PRESERVE | Canonical entity detail and relationship/evidence inspection remains required. |
| HJ-PRE-007 global typed relationship management | ADAPT | Preserve relationship inspect/create/change capability; dedicated global page is not mandatory. |
| HJ-PRE-008 typed project projections | PRESERVE/ADAPT | Preserve applicable product/business/technical/UI/security/performance/etc projections; obsolete view names may be superseded. |

## d529 breadth

| Surface | Disposition | Mature intent |
|---|---|---|
| PageDecompositionView | PRESERVE | Product decomposition from site/page/layout/section/component/element is a first-class projection of UI/product structure. Historical component need not be the final entrypoint. |
| JourneyExplorer | PRESERVE | Journey modeling/exploration is first-class. Generic item table alone does not supersede journey semantics. |
| Problem model | ADAPT | Preserve product problem/dissatisfaction identity and relationships. Avoid duplicating work-ticket lifecycle owned by AgilePlus. |
| Process model | ADAPT | Preserve product/business/process structure when it describes the product/system; execution workflow state belongs elsewhere. |
| Multi-dimensional graph suite | PRESERVE as intent, SUPERSEDE weak oracle | Modes/filters/equivalence/journey overlays remain product intent; permissive tests are replaced by strict oracle contracts. |
| Items table virtualization | ADAPT | Performance mechanism only; mature obligation is scalable inventory without semantic loss. |
| Progressive edge loading | ADAPT | Allowed only with explicit partiality/continuation and no false absence. |
| Viewport culling / renderer optimization | ADAPT | Presentation optimization may not alter canonical graph truth. |
| Problem/user/account expansion bundled in d529 | ADAPT | Product semantics retained where applicable; auth/account mechanics follow current authority/security design. |
| Generated snapshots/test DBs/session dumps/backups | RETIRE as product intent | Historical forensic evidence only; never product capability. |

## Product/specification surfaces

- Requirements, obligations, capabilities and targets: **PRESERVE** as typed accepted intent.
- ADRs/decisions: **PRESERVE** as linked product/architecture decision artifacts, not necessarily authored exclusively in Tracera.
- BDD/scenarios/contracts/state machines: **ADAPT** as linked specifications/projections. AgilePlus may own work-local authoring; Tracera models accepted product truth and evidence.
- Test cases/suites/results: **ADAPT** as evidence/specification entities and external references; Tracera is not required to become a test runner.
- Coverage/QA/quality dashboards: **ADAPT** as projections of evidence and dissatisfaction; no independent truth store.
- Specifications dashboards/cards: **ADAPT**; presentation survives only where it exposes canonical entities.

## Integrations and execution

- GitHub/Jira/Linear/other ingestion: **OPTIONAL adapters**, with provenance/idempotency/conflict requirements.
- Agent sessions/runs, work dispatch, claims, review loops, execution service: **EXECUTION-OWNED by AgilePlus**. Tracera may reference attempts/candidates/evaluations/evidence.
- Chat/Codex/MCP assistant surfaces: **OPTIONAL interface/integration**; they do not own product truth.
- Temporal/workflow orchestration: **OPTIONAL/EXECUTION-OWNED** unless required for a Tracera-local maintenance task.
- Notifications/realtime/WebSocket: **OPTIONAL UX projection**, not canonical semantics.
- Blockchain-style proof UI: **RETIRE as universal requirement**; provenance/integrity requirements remain technology-neutral.

## Product lifecycle / configuration

Versions, releases, milestones, baselines, configurations, variants and effectivity: **PRESERVE/EXPAND**. Historical implementation may be incomplete, but mature Tracera must model applicability over time/configuration without truth leakage.

## Derived intelligence

Memory/distillation, requirement mining, duplicate/conflict detection, predictive/simulated-user dissatisfaction: **ADAPT/DEFERRED-MATURE**. Derived knowledge must retain provenance/confidence and cannot mutate accepted intent without explicit acceptance.

## Infrastructure

Neo4j/cache/R2/ClickHouse/Qdrant/pgvector/ML backends: **OPTIONAL adapters/implementation choices**. Core product identity, graph, observations and assessment must remain usable without them.

## Consequence

Historical source can now be mapped into the mature domain coverage map without asking whether every old route/service must return. Recovery means preserving accepted **outcomes and semantics**, not reconstructing every historical mechanism.
