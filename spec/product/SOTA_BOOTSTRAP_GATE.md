# SOTA / Alternatives / Bootstrap Gate

**Status:** BLOCKING for specification completion.
**Captured:** 2026-09-29.
**Rule:** Tracera cannot reach 100% design/spec verification until this gate is complete. Post-build case studies do not substitute for pre-build architecture benchmarking.

## Questions this gate must answer

1. Which existing products, open-source projects, standards, methods, and research already solve each Tracera capability?
2. Which capabilities should be imported, integrated, adapted, or represented rather than hand-built?
3. Where does Tracera duplicate mature requirements/ALM, software-catalog, digital-thread/MBSE, knowledge-graph, product-management, observability, or traceability systems?
4. What remains genuinely differentiated after removing duplicated commodity functionality?
5. Are Tracera's ontology, storage, trace recovery, graph traversal, verification, product-edit, and agent-context designs technically competitive with current SOTA?
6. What is the explicit build-vs-bootstrap-vs-integrate decision for every major capability?
7. What alternative stack would be used if Tracera did not exist, and what measurable value must Tracera beat?

## Required comparison families

- requirements/ALM: Jama Connect, IBM DOORS Next, Siemens Polarion, Codebeamer and relevant open alternatives;
- product/work management: Jira Product Discovery/Jira, Linear and comparable systems;
- software catalogs/internal developer portals: Backstage, Cortex, Port, OpsLevel and comparable open systems;
- software engineering knowledge graphs / repository intelligence;
- requirements-to-code/test traceability and automated trace-link recovery research;
- digital thread / MBSE / SysML v2 concepts where transferable;
- SBOM/supply-chain/provenance standards and tooling;
- test/evidence/observability systems;
- graph databases/query engines and temporal/provenance models;
- agent-native codebase maps/context systems.

## Preliminary findings — not final decisions

- Live bidirectional requirements↔test/code traceability, baselines, impact analysis, approvals, and audit history already exist in mature ALM products. These are not sufficient differentiation.
- Software catalogs already provide entity/relation graphs, ownership, dependency/API mapping, lifecycle/search, and extensibility.
- Research actively covers trace-link recovery, heterogeneous software knowledge graphs, graph-backed repository context, and digital-twin/knowledge-graph closed loops.
- Candidate Tracera differentiation therefore needs to be tested around multi-projection product decomposition, graph-as-product-edit semantics, evidence-bound executable product state, agent-native context/verification, dissatisfaction discovery, and clean separation of product truth from work execution.

## Deliverables

- capability-by-capability comparison matrix with primary sources;
- architecture comparison and reusable primitives;
- standards/interchange map;
- build/buy/bootstrap/integrate decisions with rationale;
- differentiation ledger;
- explicit alternative-stack baseline;
- benchmark/case-study plan for post-build pilot;
- amendments to product requirements/architecture caused by findings.

No claim of optimal architecture is permitted before these deliverables are reviewed.
