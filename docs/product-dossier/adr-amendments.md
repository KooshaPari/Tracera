# Proposed ADR amendments for owner reconciliation

Status: proposals only. These do not overwrite accepted contracts or accept ADR-VIZ-001. Reconcile with [WP-07](../WP-07-product-graph-design.md), [existing governance](../governance/ADR-GOV-001-agileplus-governance-source.md), spatial design #1104 and execution registration in AgilePlus issue #1124. The supplied reference to AgilePlus ADR-0019 has not been independently resolved here; verify its path/status before proposing changes there.

## Persistent graph authority and typed projections

Context: ledger-first prose and generic view rows narrow the owner intent. Proposed decision: persistent typed product state with independent projections and additive domain adapters; audit/evidence remains supporting state. Separate per-view truth stores duplicate authority; a universal untyped item row lacks domain semantics. An immediate storage rewrite is unjustified by bounded source inspection. Consequences: versioned profiles, loss-accounted migrations and cross-view identity oracles. SQL versus graph-engine selection requires measured workloads.

## Product applicability versus work acceptance

Context: editing a product graph can require deterministic, human or agent work. Proposed decision: retain AgilePlus work acceptance and separate Tracera product applicability, linked through versioned receipts. Duplicating a work graph, promoting worker self-report or forcing Tracera on standalone AgilePlus conflicts with existing boundaries. Consequences: stale baseline handling, retries, idempotency and recovery without conflating Done with satisfied obligations.

## Simulation with bounded validity

Context: a convincing world depiction can conceal unmodeled behavior. Proposed decision: canonical scene/model identity, explicit fidelity/assumptions, replayable solver inputs, uncertainty, calibration and independent reality checks. Reuse spatial geometry truth classes. Renderer-as-truth, animation-as-proof and universal full physics are unsuitable defaults. Consequences: assumption registry, calibration evidence and change-impact invalidation. Renderer/solver choices remain benchmarked proposals.

## Product-aware UX and independent provenance

Context: product investigation requires semantic views and task-grounded design. Proposed decision: derive interactions independently from user tasks, record alternatives, original assets, licensed code/asset sources and usability evidence. Incumbent cloning, recoloring and universal generic tables are insufficient rationale. Consequences: design review remains separate from runtime/product acceptance. No employment history or legal determination is included.
