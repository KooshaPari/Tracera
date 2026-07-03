# PM Ideology Diff: Tracera vs AgilePlus

## Scope

This document compares the product-management ideology embedded in:

- Tracera planning/governance code in `src/tracertm/` and `crates/tracera-core/`
- AgilePlus domain/governance code in `C:/Users/koosh/Dev/AgilePlus/crates/agileplus-domain/`
- AgilePlus release-governance work packages in `C:/Users/koosh/Dev/AgilePlus/kitty-specs/`

The goal is to identify agreement, conflict, and the missing integration surface needed for a merged model.

## 1. Tracera PM Ideology

### Core shape

Tracera’s PM model is spec-first, traceability-heavy, and artifact-centric.

The active governance entrypoint is `src/tracertm/governance.py`, which defines:

- `GovernanceSpec` as the planning unit
- `GovernanceTrace` as the traceability edge from spec to downstream work
- `evaluate_spec_first_governance()` as the gate

The gate requires:

- approved specs
- acceptance criteria
- evidence links
- implementation trace
- test trace

It also rejects duplicate spec IDs and orphan traces.

### Process model

From the current Tracera code, the implicit process is:

1. Define a spec record.
2. Approve the spec before execution.
3. Attach acceptance criteria and evidence links.
4. Add trace records to implementation and test targets.
5. Run the governance gate.
6. Fail if any required trace or artifact is missing.

### Stages and gates

Tracera’s PM ideology is not a long lifecycle state machine. It is a narrow pre-execution gate:

- `draft` -> `approved` -> `implemented`
- gate criteria are boolean presence checks, not a multi-stage transition contract

The gate checks for:

- approval state
- acceptance criteria
- evidence
- implementation trace
- test trace

### Traceability model

Tracera’s traceability vocabulary is centered on the shared `traceability-core` model re-exported by `crates/tracera-core/src/lib.rs`:

- `Artifact`
- `Requirement`
- `TraceLink`
- `CoverageMatrix`
- `VerificationMethod`
- `RequirementStatus`

The Python side mirrors that vocabulary in:

- `src/tracertm/models/trace_link.py`
- `src/tracertm/matrix.py`
- `src/tracertm/storage/artifact_writer.py`

The model is intentionally evidence-driven:

- requirements carry acceptance criteria and verification methods
- links connect requirements to code, tests, evidence, and decisions
- coverage matrix summarizes requirement-to-artifact completeness

### Artifact model

`tracertm.models.trace_link` defines:

- `ArtifactKind` with requirement/design/code/test/evidence/risk/rationale
- `RequirementStatus` with lifecycle values from draft through verified/deprecated/rejected
- `TraceLinkType` with implements/verifies/satisfies/derives/conflicts/refines

`Requirement` is a specialized `Artifact` with:

- status
- priority
- rationale
- acceptance criteria
- verification method

`TraceLink` is the main connective tissue and is explicitly round-tripped through the shared core.

### Coverage and verification

`crates/tracera-core/src/matrix.rs` and `src/tracertm/matrix.py` emphasize coverage completion:

- requirement-to-artifact coverage matrix
- covered/partial/missing/stale/conflict summarization
- export and analysis helpers

In short, Tracera’s PM ideology is:

- spec-first
- trace-link driven
- evidence-linked
- coverage-measured
- gate checked before execution

## 2. AgilePlus PM Ideology

### Core shape

AgilePlus is a full delivery-governance system, not just a traceability gate.

The dominant runtime concepts in `crates/agileplus-domain` are:

- `Feature` as the primary planning aggregate
- `FeatureState` as the lifecycle state machine
- `GovernanceContract` as the immutable transition contract
- `PolicyRule` as a reusable policy primitive
- `IntentGraph` as the org-wide work ontology

### Feature lifecycle

`crates/agileplus-domain/src/domain/feature.rs` defines a strict lifecycle:

- `Created`
- `Specified`
- `Researched`
- `Planned`
- `Implementing`
- `Validated`
- `Shipped`
- `Retrospected`

This is not a simple approval gate. It is an enforced staged progression with exactly one valid forward step at each stage.

### Governance model

`crates/agileplus-domain/src/domain/governance.rs` adds the enforcement layer:

- `PolicyDomain` groups rules into security/quality/compliance/performance/custom
- `PolicyRule` stores a named rule with a check mode
- `GovernanceContract` binds rules to a feature and version
- `GovernanceRule` links transitions to required evidence and policy references
- `Evidence` links work packages to FR IDs and artifact paths

The result is a governance system where:

- state transitions are explicit
- evidence is typed
- policy references are reusable
- contracts are versioned and immutable

### Intent graph

`crates/agileplus-domain/src/intent_graph.rs` expands the model beyond features into a graph ontology:

- `NodeType` spans Intent, Plan, Feature, Story, Task, Spec, Commit, Test, PR, Bug, Artifact
- `DagStage` mirrors those stages
- `RelationshipType` encodes implements/tests/covers/traces-to/derives-from/resolves/blocks/depends-on
- `IntentGraph` validates DAG structure, root intent rules, and edge constraints

This is a broader planning graph than Tracera’s spec/trace gate. It is designed to support:

- hierarchical work decomposition
- dependency ordering
- graph validation
- provenance of work artifacts

### Claim engine and execution loop

AgilePlus also includes an operational claim model in `crates/agileplus-triage/src/claim.rs` and `crates/agileplus-factory/src/lib.rs`.

The claim engine introduces:

- `ClaimKind` for repo/branch/worktree/subproject ownership
- `ClaimState` with active/draining/expired
- `ClaimReason` as structured provenance for a claim
- TTL and heartbeat semantics

The factory loop turns governance into execution:

1. Poll issues.
2. Claim a worktree.
3. Create a claim-bound worktree.
4. Run the agent loop.
5. Open a PR.
6. Release the claim.

This is a runtime coordination model, not just a planning schema.

### kitty-specs governance

The `kitty-specs` work packages document the ideology in executable form.

Relevant patterns from the reviewed specs:

- strict state ordering for features
- audit/hash-chain governance
- versioned governance contracts
- evidence requirements tied to transitions
- policy evaluation as a gate engine
- risk-based promotion for release channels

That means AgilePlus’s PM ideology is:

- staged lifecycle first
- graph-shaped planning
- contract-based governance
- evidence-backed transition control
- operational claim/worker orchestration

## 3. Agreement

The systems agree on the core premise that work must be traceable and evidence-backed.

Shared ideas:

- planning artifacts should be explicit
- acceptance or gate criteria must exist before execution is trusted
- evidence should be linkable to work
- implementation and test activity must be traceable
- lifecycle state should constrain allowed work

Shared structural concepts:

- requirement-like planning units
- traceability links between intent and delivery
- governance checks before promotion or merge
- artifact/evidence records that can be audited later

## 4. Conflict

The models diverge in control granularity and scope.

### Conflict 1: gate style

Tracera uses a narrow pre-execution spec gate.

AgilePlus uses a staged lifecycle with transition contracts and policy enforcement at each step.

This means Tracera currently treats governance as a checklist, while AgilePlus treats it as a process machine.

### Conflict 2: primary aggregate

Tracera centers on `Requirement` / `Artifact` / `TraceLink`.

AgilePlus centers on `Feature` / `IntentGraph` / `GovernanceContract`.

The first is requirement- and traceability-led.
The second is feature- and delivery-flow-led.

### Conflict 3: process breadth

Tracera does not currently model:

- staged feature lifecycle
- claim ownership
- worktree orchestration
- policy rule registry
- immutable governance contracts
- graph-level planning DAG

AgilePlus does.

### Conflict 4: execution semantics

Tracera’s gate decides pass/fail for a spec record.

AgilePlus manages a workflow system where:

- work is claimed
- transitions are governed
- evidence is accumulated
- release channels can be gated

## 5. Gap

Current Tracera does not embed AgilePlus as a runtime dependency.

Evidence from the Tracera checkout:

- `rg -n "AgilePlus|agileplus" E:\Dev\Tracera -S` only finds docs and historical references
- active code in `crates/tracera-core` depends on `traceability-core`
- `src/tracertm/governance.py` is standalone Python governance logic
- there is no active import or crate dependency on AgilePlus code

So the current state is:

- Tracera is standalone
- AgilePlus is not embedded
- the two models are overlapping but isolated

That is the architectural gap relative to the directive that Tracera must be a superset embedding AgilePlus.

## 6. Required Re-Architecture

To satisfy the directive, Tracera should become a superset that depends on shared PM core, with AgilePlus as the PM substrate.

### Required target shape

- Tracera depends on `AgilePlus` or a shared `pm-core`
- AgilePlus remains optional standalone
- Tracera reuses AgilePlus feature lifecycle, governance contracts, policy rules, and claim semantics
- Tracera adds its own traceability/coverage/evidence runtime on top

### Concrete merge path

1. Extract shared PM primitives into a common core package.
2. Move lifecycle, governance contract, policy rule, and claim primitives into that shared core.
3. Make Tracera consume those primitives instead of duplicating a separate gate model.
4. Keep Tracera-specific traceability-core concepts as an extension layer, not a competing model.
5. Preserve AgilePlus standalone operation by making the shared PM core usable without Tracera.

### Integration contract

The merged architecture should enforce:

- AgilePlus defines the process model
- Tracera consumes and extends it
- Tracera cannot run without the shared PM substrate
- AgilePlus can still run on its own

## 7. Unified Superset Ideology

The best merged model is a superset:

- AgilePlus provides process, lifecycle, claim, contract, and policy governance
- Tracera provides traceability, coverage, artifact linkage, and evidence instrumentation

Recommended ideology:

1. Feature is the top-level delivery aggregate.
2. Spec/Requirement is the contract surface attached to a Feature.
3. GovernanceContract defines transition-specific evidence and policy requirements.
4. PolicyRule is reusable enforcement logic.
5. IntentGraph captures planning/dependency structure.
6. Claim engine coordinates ownership and execution.
7. TraceLink and CoverageMatrix provide observable proof of execution and verification.

## 8. ADR-Style Merge Decisions

### Decision 1: Feature over requirement as the top-level work aggregate

**Status**: Adopt

**Rationale**: AgilePlus has a richer lifecycle and governance contract model. Tracera’s requirement model is too narrow to carry execution-phase control. The merged stack should use Feature as the process root and Requirement/Artifact as attached traceability surfaces.

### Decision 2: Governance contracts as first-class, immutable transition bindings

**Status**: Adopt

**Rationale**: Tracera currently checks presence of evidence and traces, but not lifecycle-bound evidence contracts. AgilePlus’s contract model provides a stronger and more scalable mechanism for stage-gated governance.

### Decision 3: Keep traceability-core as the evidence/coverage layer

**Status**: Adopt

**Rationale**: Tracera’s strongest differentiator is its traceability model. That should remain the explicit evidence layer on top of the lifecycle and contract substrate.

### Decision 4: Use IntentGraph as the shared planning DAG

**Status**: Adopt

**Rationale**: AgilePlus already models multi-node planning, dependency ordering, and DAG validation. Tracera should not invent a parallel planning graph.

### Decision 5: Use claim semantics for execution ownership

**Status**: Adopt

**Rationale**: The claim engine is the missing operational layer between planning and execution. It prevents ambiguity over who owns work and when a resource is safe to mutate.

### Decision 6: Preserve standalone AgilePlus operation

**Status**: Adopt

**Rationale**: The directive requires AgilePlus to remain optional standalone. Shared PM core must therefore be consumable without Tracera runtime dependencies.

## 9. Bottom Line

Tracera and AgilePlus agree on traceability and evidence, but they currently encode the idea at different layers.

- Tracera: spec gate + requirement traceability + coverage
- AgilePlus: lifecycle machine + contract governance + claim orchestration + graph planning

Current state:

- **standalone Tracera**
- **AgilePlus not embedded**

Required end state:

- **Tracera embeds shared PM core / AgilePlus substrate**
- **AgilePlus remains optional standalone**
- **Tracera becomes the superset**

## 10. Sync Note

This document is intentionally limited to the current source snapshots and the observed repository wiring in this checkout.
