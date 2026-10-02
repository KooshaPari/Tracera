# Tracera Architecture Amendment Candidates from Research

**Status:** proposed; blocking semantic review required before acceptance.
**Date:** 2026-09-29.

These amendments are not feature requests generated from novelty. They are concrete changes suggested by internal archaeology + SOTA/PLM/ALM/SPL research.

## A-01 — Replace static product graph assumption with overloaded + resolved projections

Maintain one canonical overloaded structure containing common and conditional entities/relations. Resolve a context-specific product graph for a target configuration/effectivity context.

Software contexts can include:
- product/edition/variant;
- version/revision;
- OS/architecture/device;
- environment;
- tenant/customer class;
- geography/regulation;
- feature flags/evaluation context;
- rollout cohort;
- dependency/API version;
- time.

Avoid cloning independent product graphs for every configuration.

## A-02 — Add explicit applicability/effectivity to relations and obligations

A relation/claim may exist canonically but apply only under a predicate/context. Static edge existence is not enough.

Need:
- effectivity variables;
- scopes;
- expressions/constraints;
- full and partial resolution;
- explanation of inclusion/exclusion.

Evaluate UVL as the software variability interchange/constraint language.

## A-03 — Separate identity, revision, artifact version, configuration and baseline

Do not overload BaselineRevision.

Candidate:
- ProductEntityId — stable identity;
- EntityRevision — accepted definition evolution;
- ArtifactVersion/Digest — concrete realization;
- Configuration — compatible resolved selection/context;
- Baseline — frozen named snapshot/contract;
- Release — promoted product configuration.

## A-04 — Introduce suspect relation/evidence state

A link can remain present but become semantically suspect after source/target change.

Need invalidation propagation based on:
- endpoint revision;
- configuration/applicability;
- validator revision;
- evidence dependencies;
- graph delta.

Do not delete historical links/evidence when they become suspect.

## A-05 — Generalize product state into multiple simultaneous lifecycle projections

Represent accepted, designed, implemented, built, released, deployed and observed states separately.

Dissatisfaction includes disagreement between these projections.

## A-06 — ProductChange / GraphDelta as first-class object

Product changes carry:
- motivation/finding;
- proposed graph delta;
- impacted configurations;
- impact analysis;
- authorization;
- realization references;
- rollout/migration;
- verification obligations;
- invalidated evidence;
- effective context/time;
- reconciliation result.

AgilePlus executes work; Tracera owns product-change semantics.

## A-07 — Standards-backed evidence adapters

Prefer adapters/mappings for:
- CycloneDX/SPDX;
- in-toto/SLSA;
- OpenTelemetry;
- SARIF;
- JUnit/coverage;
- OpenAPI/AsyncAPI/GraphQL;
- Git/OCI;
- ReqIF;
- OSLC;
- SysML v2.

Do not create proprietary substitutes without a demonstrated gap.

## A-08 — Explicit authority lattice

Separate authority from confidence.

Candidate authority:
- accepted product fact;
- deterministic source-system fact;
- verified observation;
- authorized decision;
- inferred candidate;
- imported unverified claim;
- historical/superseded.

A high-confidence inference is not an accepted fact.

## A-09 — Discovery pipeline uses deterministic extraction before LLM inference

Brownfield model construction order:
1. deterministic source inventory/parsers;
2. native standard/source-system imports;
3. inferred candidate relations;
4. confidence/provenance;
5. contradiction/gap analysis;
6. bounded authorization;
7. continuous reconciliation.

## A-10 — Code graph is an adapter/substrate, not the product kernel

Evaluate agentforge-graph, ContextGraph, CodeGraphAgent, SCIP/LSP/tree-sitter and similar tooling before maintaining custom multi-language parsing.

## A-11 — Variability reasoning bootstraps from SPL research

Evaluate UVL + FeatureIDE/flamapy concepts for:
- optional/mandatory features;
- alternatives;
- cross-tree constraints;
- valid configurations;
- configuration derivation;
- feature-model evolution;
- family-level/lifted analysis.

## A-12 — Logical graph API before storage commitment

Tracera product semantics must not depend directly on Neo4j-specific behavior.

Benchmark:
- SQLite/Postgres relational graph;
- LadybugDB/embedded property graph;
- Neo4j;
- other credible embedded/server options.

Query corpus must include bounded traversal, reverse trace, impact, effectivity resolution, historical/configuration query, provenance and MACE aggregation.

## A-13 — MACE evaluator is versioned evidence-producing computation

A grader/oracle has:
- identity/version;
- criterion;
- applicability;
- exact candidate/environment;
- execution;
- result vector;
- evidence;
- failure classification;
- dependencies/invalidation.

Do not reduce grader identity to a test path.

## A-14 — Registry and source systems remain federated authorities

PhenoRegistry is ecosystem index/projection. Git owns source revisions. External ALM/PLM owns its native records. Tracera maps/reconciles rather than duplicating every state machine.

## Acceptance gate

Each amendment must be:
- mapped to internal intent;
- supported by SOTA evidence;
- checked against current implementation cost;
- assigned accept/adapt/reject/defer;
- reflected in requirements/ontology if accepted;
- covered by an architecture experiment where risk remains high.
