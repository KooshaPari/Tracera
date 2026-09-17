# Correction-aware evidence and action traces

Status: research dossier, proposed only. No runtime schema or existing ADR is changed.

Work tracking: [AgilePlus #1073](https://github.com/KooshaPari/AgilePlus/issues/1073). Canonical source/claim authority: [ResearchLedger Wave 3](https://github.com/KooshaPari/ResearchLedger/blob/8c271fd6765b01c6a6a6339d7273199a48e06334/docs/corpora/emergent-garden/research/WAVE-3-COMMENTS-AND-SYNTHESIS.md).

## Audited authority

Revision `b23469678da42d0d0ec8c303a7a97e5b1b19d293`: README, CLAUDE and accepted `docs/governance/ADR-ARCH-001-hexagonal-architecture.md` were read. The root AGENTS lookup returned not found. Tracera's documented role is trace, observability and audit for agentic workflows, with a supported Rust workspace and historical Python migration material.

The accepted ADR names trace ingestion, governance, evidence persistence, queue and external-issue boundaries. Its proposed directory layout is not treated as proof that every migration step is implemented. This proposal fits those boundaries and does not create a second research corpus or revive historical Python services.

## What the research requires us to distinguish

The comment corpus supplies real corrections and provenance hazards: a later activation correction, a tutorial configuration move, a historical absence of vision, and an audience paper lead that must not be mislabeled creator influence. The primary-source review distinguishes model reflections, spoken intentions, tool effects and independently evaluated outcomes.

The useful Tracera implication is typed evidence lineage, not a general claim that emergence or decentralized agents are superior.

## Proposed trace distinctions

Keep source, observation, assertion, inference, correction, evaluation and decision distinct. A statement that a tool succeeded is not the tool's observed outcome. A source's later correction should not erase the original event. An evaluator's verdict should identify what it measured and under which configuration.

Suggested record fields, subject to mapping onto existing domain types:

- source URI, source kind, source version/hash, locator, source publication/update time and capture time;
- evidence origin: creator statement, audience claim, primary research, code observation, agent inference, operator assertion or independent check;
- action and attempt IDs, observation revision, environment/tool/permission revision and candidate artifact hash;
- evaluator revision, result reference, acceptance scope and confidence rationale;
- supersedes, contradicts, qualifies, derived-from and affects-projection relations.

These names are conceptual requirements, not a new serialized API contract. Do not persist unneeded audience profiles or full research text in the trace store.

## Correction propagation example

1. A source proposes an activation advantage.
2. A later creator comment acknowledges an identity and questions that observation.
3. An independent mathematical check confirms equivalence under input scaling.
4. A controlled toy shows unmatched learning rates still yield different trajectories.
5. The downstream recommendation changes from an unsupported ranking to a parameterization-control requirement.

Store five different facts and their dependencies. Do not replace them with one confidence score or rewrite the original claim as though it had always been corrected. The exact numerical results belong to the canonical research evidence; Tracera should retain references and dependency state.

## Action-result example

A planner proposes a file change using observation revision A. Another worker changes the file to B. The adapter rejects the stale precondition, or executes and reports the actual base revision. A completion utterance cannot bypass that check. Retries require separate attempt IDs so duplicate delivery does not inflate successful-action counts.

For irreversible actions, record compensation or recovery limits explicitly. A repository rollback is not evidence that physical effects, emails or remote mutations were reversed.

## Negative controls

Test a missing source version, changed source text at the same URI, a corrected claim with dependent projections, an agent reflection presented as observation, duplicate event delivery, out-of-order action results, an evaluator mismatch, and a physically irreversible effect mislabeled rolled back.

Acceptance: historical records remain inspectable, current projections become stale when their inputs change, evidence classes remain distinguishable, duplicate delivery is idempotent, unknown outcomes remain unknown, and no unneeded source text or audience identity leaks into traces.

## Alternatives and implementation gate

The existing Evidence/TraceLink model may already support most fields; prefer reuse. A small adapter or validation layer may be sufficient. A global event schema migration is not authorized by this dossier. A source hash verifies bytes, not truth, authorship or completeness; count reconciliation is not an atomic snapshot.

Before implementation, inspect current Rust domain and port definitions, map fields, select compatibility behavior and add a bounded work package. The present change is documentation only. It claims no Rust test run, live ingestion migration, benchmark reproduction, merge or release.
