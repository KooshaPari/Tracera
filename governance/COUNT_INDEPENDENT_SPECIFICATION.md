# Count-independent mature-product specification

**Controlling instruction: September 29, 2026. Applies to this repository and subsequent repo-by-repo passes.**

The user's conversational numbers are not targets, estimates to fit, minimums, maximums, quotas, or expected ranges. Requirement and hierarchy counts are outputs of analysis only. No fixed number governs when to start, stop, split, merge or accept a specification. Changing a quota to a larger quota is not a correction.

## Preserve the actual objective

Describe the most comprehensive presently knowable mature product first, then derive bounded viable-product stages and actionable work frontiers from it. The large, structured backlog is intentional. Do not replace this objective with a tiny MVP contract. Do not enlarge product scope merely to enlarge the catalogue. Mature-first describes the intended horizon; it does not license unsupported features or speculative architecture.

Tracera owns the persistent canonical product/system model, accepted product intent, product relations, evidence interpretation, dissatisfaction discovery and product-state assessment. AgilePlus owns execution and working-change state. Performing this specification manually is bootstrapping Tracera's intended function, not creating a competing permanent registry or product.

## Source and scope reconciliation

Inventory accepted user intent, product definitions, specifications, ADRs, public interfaces, domain models, UI/CLI/MCP journeys, supported components, configurations, integrations, failure paths, current tests and documented gaps. Follow relevant references and reconcile duplicates. Record exact source revision, location, reviewed extent, unresolved conflicts and ownership.

Use existing historical inventories as leads where useful; the separate deleted-repository restoration and exhaustive history-recovery effort remains deferred. An unread source is not reviewed. An inaccessible source is a coverage gap. Existing code describes present behavior, not automatically accepted desired behavior. New inferred obligations need a rationale and explicit proposal status. A source heading is not automatically an atomic requirement.

## Decompose semantics, not counts

For each accepted capability, identify independently observable obligations across its relevant actors, states, inputs, outputs, permissions, persistence, concurrency, failures and recovery. Apply only dimensions that materially affect that capability. Do not take a mechanical Cartesian product of dimensions or create a fixed number of children per parent.

Split a requirement when obligations can meaningfully differ in acceptance, implementation responsibility, stage applicability or failure outcome. Keep a cohesive behavior together when splitting only creates synonyms, grammatical fragments or test permutations. Test cases are not automatically additional FRs. Shared constraints and NFRs should be represented once with applicability links, not copied into every feature and counted as new functional scope.

Each candidate must explain the distinct behavior it adds and how it can be falsified. Generic text such as 'provide the accepted behavior for X' or 'handle invalid cases for X' is an unresolved prompt, not an executable specification. A template may enforce record structure; it may not invent the substance.

## Required semantic content

Every actionable FR needs: stable identity; authoritative origin or derivation rationale; product/component owner; pillar/feature/sub-feature links where meaningful; product role; actor and preconditions; trigger/input; observable outcome and postconditions; relevant prohibited/failure behavior; dependencies; stage-applicability rationale; likely source/work surfaces with mapping confidence; growth disposition with supporting evidence or an explicitly labelled estimate; and independently checkable acceptance intent.

Keep lifecycle/work state, observed behavior, trace completeness and product acceptance separate. An absent trace is not proof of a behavioral failure. A behavioral pass is not complete traceability. Evidence required to establish the pass itself cannot be absent.

## Stage selection and product shape

Define CVP/MVP/other applicable stages from useful closed journeys and their necessary capability/dependency closure. Do not choose 'the first N features', an arbitrary percentage, or a fixed allocation per pillar. Stages may branch or contain temporary obligations; nesting is not compulsory. Parent rollups deduplicate leaf contributions. Core versus auxiliary role does not follow array position or implementation difficulty.

A percentage must name its accepted horizon and evidence basis, and distinguish foundations, primitives, visible stubs, closed features, integration closure and real usable journeys. Unknown shape remains unknown. Stage achievement requires its explicit gates; a large catalogue or a high primitive count establishes neither a usable product nor external value.

## Stub-first continuity

Expose mature-shaped boundaries, implement a real usable spine, and stub only the breadth that is outside the selected journey. Grow chiefly by addition/enrichment. Temporary implementations require bounded replacement and migration costs. Do not assert universal mature compatibility or survivability without review. Forecast replacement estimates and measured outcomes must remain separate.

## Verification is designed now; test implementation remains deferred

Define concrete positive and relevant counterexample cases, expected results, fixtures, environment, reset/isolation, evidence binding and invalidation rules. Reserve test identities only after their case semantics are specified. A future test ID or generic 'wrong input must fail' sentence is insufficient. Do not claim test-generation readiness while material oracle decisions are left to the test writer.

## Completeness review and honest stopping

Review top-down intent and end-to-end journeys against bottom-up interfaces, components, data/state transitions and documented limitations. Classify every discovered material surface as covered, intentionally excluded with reason, deferred within mature scope, duplicate, or unresolved. Independently challenge the catalogue for missing behavior and padded/redundant records. Reconcile known contradictions and dangling links. Record review scope and remaining uncertainties.

Completion is a supported coverage conclusion about the reviewed product horizon, never a count threshold. If work stops with surfaces unreviewed, report a partial pass and the precise unfinished frontier; do not manufacture enough entries to declare it done. A decreasing count after deduplication is not scope loss when obligations and lineage are preserved.

## Invalidated first drafts

The initial uniform generated catalogue is rejected as a grading baseline. Preserve its Git history, but do not import its counts, generated stages, automatic compatibility assertions or generic test-readiness claims into the accepted product graph. Existing source-native requirements remain intact. Replacement candidates require source-backed semantic review; numbers are calculated only afterward.
