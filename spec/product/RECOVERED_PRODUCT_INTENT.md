# Recovered product intent — Tracera and AgilePlus

**Status:** controlling intent input for the current semantic specification passes.
**Captured:** 2026-09-29
**Nature:** user-authored clarification plus recovered prior-conversation terminology. This is product intent, not implementation evidence.

## Reciprocal product model

### AgilePlus

AgilePlus is the repository/checkout/project-level specification and execution environment for agents and humans.

Its design target is a synthesis rather than a clone:
- OpenSpec-like velocity, fluidity, brownfield fit, and intuitive change-oriented workflow;
- Spec Kit-like structured refinement, analysis, planning, tasking, convergence, and extensibility;
- BMAD-like depth, role/context discipline, adaptive process sizing, architecture/PRD rigor, and explicit decisions;
- established software/product engineering methods where they improve correctness;
- Tracera-native traceability, evidence, grading, and handoff semantics.

The intended experience is closer to a **school/ZyBooks assignment environment for software work** than a pile of Markdown:
- the assignment/spec tells the agent what outcome is required;
- requirements/scenarios/constraints are machine-addressable;
- work is decomposed into justified steps;
- agents can receive bounded context and work surfaces;
- an oracle/autograder can provide actionable feedback;
- retries/revisions preserve history rather than erase failed attempts;
- progress is derived from accepted criteria/evidence rather than self-report;
- spec, plan, implementation, review, and evidence evolve together without unnecessary waterfall ceremony.

AgilePlus owns ephemeral/local working change intent and execution: exploration, proposal/specification, research, design/architecture, plan/WBS/DAG, work packages, claims/checkouts/worktrees, agent execution, review/convergence, validation, receipts, and promotion of the work result.

### Tracera

Tracera moves the same traceability-first idea **outside one ephemeral checkout/device/project session** into the persistent global product scope: Jira/Linear-like in persistence and collaboration, but centered on a canonical product graph rather than tickets.

Older terminology recovered from prior discussions includes:
- feature graph;
- product graph;
- product-state graph;
- world model / product-evidence graph;
- live product-state control plane.

The defining object is not one tree. A product has multiple valid decompositions/projections over shared canonical entities and relations.

Examples:

#### Experience / UI decomposition

```text
Product
 -> application/surface
   -> route/page/screen
     -> region/section
       -> interaction/action/state
         -> observable behavior
```

The UI projection should feel inspectable/editable like a website builder: expand/collapse product structure, inspect a page or section, see what actions/states it supports, and navigate from that conceptual object to its implementation/evidence.

#### Functional/product decomposition

```text
Product
 -> pillar/domain
   -> capability/core feature
     -> feature
       -> sub-feature
         -> requirement/scenario/constraint
```

#### Architecture/runtime decomposition

System -> service/application -> package/module -> interface/API/event -> implementation artifact -> deployed artifact/runtime target.

#### Supply-chain decomposition

Product/release -> package/component -> dependency/SBOM item -> version/license/vulnerability/build provenance.

#### Verification decomposition

Requirement/quality property -> acceptance criterion -> oracle -> test/check/measurement -> execution -> result/evidence -> candidate/environment/verifier.

#### Documentation/intent decomposition

Product -> intent/baseline -> requirement/spec/ADR/design/doc -> revisions/provenance -> implementation/evidence relations.

These are **projections of one graph**, not disconnected inventories. The value comes from connecting them.

## Graph-as-product-editor

A graph edit can represent a proposed product edit.

Examples:
- add a page/interaction in the experience projection;
- add/change a capability or requirement in the functional projection;
- add an API/interface relation in architecture;
- change a dependency/SBOM item;
- alter an accepted quality target.

The proposed graph delta should expose downstream consequences before realization: affected specs, implementation surfaces, tests, docs, consumers, quality obligations, work needed, and evidence invalidated. Authorized work can then be delegated to AgilePlus/agents. Realized changes are reconciled back into Tracera from exact artifacts/evidence.

Tickets/work items are therefore derivative execution views, not the canonical product model.

## Transactional ledger / reconciliation semantics

Tracera should make controlled product mutation auditable:
1. current accepted graph;
2. proposed graph delta;
3. authorization/decision;
4. execution references;
5. exact implementation/artifact change;
6. verification evidence;
7. reconciliation into observed/accepted product state.

A controlled mutation is either reconciled or explicitly visible as a gap. Do not silently equate proposal, work completion, implementation presence, verification, and accepted product truth.

## Product verification is multidimensional

"Does the product do what it says?" includes more than functional existence.

The graph should support obligations/evidence for:
- correctness and negative/error behavior;
- performance/latency/throughput;
- reliability/recovery/degraded behavior;
- usability and interaction quality;
- accessibility;
- security/privacy/authority;
- compatibility/platform behavior;
- operability/deployment;
- maintainability/evolvability where objectively specified;
- documentation/interface truth;
- other product-specific quality properties.

These should be related to the exact feature/journey/candidate/environment they qualify. Quality dimensions are not copied into every FR merely to inflate requirement count.

## Bounded recursive decomposition

Every useful graph object may expose deeper views, but expansion must be bounded and purposeful. Users/agents should be able to collapse from code/test-level evidence back to product-level meaning and expand from product intent toward exact implementation/evidence without loading the whole universe.

## Persistent vs ephemeral

- AgilePlus can operate independently at repo/project scope and must remain useful without Tracera.
- Tracera persists product truth across repos, devices, sessions, releases, teams, agents, and external work systems.
- An AgilePlus work/spec graph can be linked/projected into Tracera where useful, but Tracera does not absorb AgilePlus's execution lifecycle.
- Tracera can represent products whose work is managed by humans, Jira, Linear, GitHub, AgilePlus, or another system.

## Implications for current specification work

1. Tracera source review must inventory UI/routes/actions, APIs/interfaces, SBOM/dependencies, architecture/runtime, tests/evidence, documentation/specs/intent, and product hierarchy as distinct graph projections and then define their cross-links.
2. A flat requirement list is insufficient; requirements must attach to graph entities, journeys, projections, quality properties, stages, and work/evidence surfaces.
3. AgilePlus must be evaluated as a spec-development/execution methodology and product, not merely a queue/agent dispatcher.
4. Both products need oracle/autograder semantics, but at different scopes:
   - AgilePlus grades a bounded change/work assignment and its execution.
   - Tracera grades persistent product obligations, product stages, and reconciled product state.
5. Existing code/docs are evidence and candidate behavior. They do not override this recovered intent merely because they are implemented.
