# Pass 06: technical bootstrap decisions and acceptance experiments

Date: 2026-09-29. Status: PROPOSED / NOT SPECIFICATION-COMPLETE.
Inspected Tracera revision: `3c289c78a76b292826f019c233f2ce1f7200c197`.
Research commit: `KooshaPari/PhenoRegistry@f36565172c2b9640273dc4ad6a30516c769225b0`.

The [source and claim register](https://github.com/KooshaPari/PhenoRegistry/blob/f36565172c2b9640273dc4ad6a30516c769225b0/docs/governance/atlas/products/Tracera/research/PASS-06-EVIDENCE.json), [technical analysis](https://github.com/KooshaPari/PhenoRegistry/blob/f36565172c2b9640273dc4ad6a30516c769225b0/docs/governance/atlas/products/Tracera/research/PASS-06-TECHNICAL-CONFORMANCE.md) and [paper appraisal](https://github.com/KooshaPari/PhenoRegistry/blob/f36565172c2b9640273dc4ad6a30516c769225b0/docs/governance/atlas/products/Tracera/research/PASS-06-PAPER-APPRAISAL.md) record primary sources, inspected extent, proposals and limitations. Existing source-native specifications and invalidated-catalog safeguards remain unchanged.

## Three separate lifetimes

1. Worker attempt: process, model/tool configuration, sandbox, lease and attempt-specific provenance.
2. Durable development effort: accepted working change, specification revisions, work packages, review history and receipts. AgilePlus owns this state; it must outlive a checkout or agent.
3. Persistent product: accepted intent, product configurations, realized artifacts, deployments, evidence interpretation and dissatisfaction. Tracera owns this state independently of who does the work.

Attempt identity, development/change identity and product-configuration identity must not be conflated. Human, agent and deterministic workers are replaceable. Work completion is not product acceptance. Replacing a worker must not destroy valid evidence; it also must not transfer expired authority automatically.

## Decisions proposed from the inspected code

| Surface | Evidence | Proposed decision | Still required |
|---|---|---|---|
| `frontend/apps/web/package.json` | React Flow, Sigma/Graphology, Cytoscape and ELK already declared [I1] | Qualify current consumers; bounded authoring and broad exploration may use different renderers over shared canonical IDs | Entry-point reachability, persistence, keyboard/accessibility, rejected mutation and performance witnesses |
| `crates/tracera-server/src/store.rs` | SQLite/Postgres boundary already exists; TraceLink lacks explicit endpoint revision/configuration/authority fields [I2] | Keep as low-rewrite baseline while defining richer relation assertions; no engine replacement by metaphor | Equivalent semantic and recovery workloads, migration cost, query/load results |
| `crates/tracera-server/src/product/queries.rs` | `query_intents` ignores query.product_id; invalid kind/status becomes no filter; baseline is a lower bound [I3] | Specify caller isolation or explicit validation; distinguish exact snapshot query from history filtering | Real helper and mounted-API witness; this static finding is not a demonstrated cross-tenant exploit |
| Code inventory | SCIP and tree-sitter have different roles [E4,E6] | Compiler/indexer-backed symbols, syntax fallback and native build metadata as separate adapters | Coverage on Rust/TS/Python targets, generated sources, target/configuration identity |
| Alternative stores | Kuzu archived; Ladybug has a documented read-write Database-object constraint [E1-E3] | Ladybug is a benchmark candidate only; inspect ownership/concurrency topology first | Actual process model, supported version, recovery and license/security review |

No renderer state, inferred link or imported display label becomes accepted product truth merely because a tool produced it.

## Grade identity versus progress comparison

Each evaluation binds its **own** candidate, product/configuration, contract/criterion revisions, evaluator version and evidence cut. For progress across candidates, hold the comparison basis constant: applicable requirements, weighting, target configuration, evaluator, workload and freshness policy. The candidate is intentionally the variable being improved, not a field that must be identical across a progress series.

Changing scope, targets, evaluator or workload must be shown separately or both candidates must be re-evaluated on the common basis. Evidence age remains visible. Historical-best score, current-candidate status and user-facing display state are different values. Two points can show an observed delta; they do not establish an asymptote or a reliable future convergence rate.

This clarifies the comparison-basis terminology in the registry report. It does not authorize a scalar score to hide a failed critical obligation.

## Executed research experiment, not product proof

`TRC-EXP-EVIDENCE-BINDING-01` is a standalone Python/SQLite reference model in the registry, not imported into the application. It completed **30 checks** and detected **seven deliberately removed binding guards**. The cases cover wrong product/baseline/candidate/configuration/expectation/evaluation/producer, non-green statuses, worker substitution, restart, replay conflicts, append-only evidence and rollback.

[Source](https://github.com/KooshaPari/PhenoRegistry/blob/f36565172c2b9640273dc4ad6a30516c769225b0/docs/governance/atlas/products/Tracera/research/pass06/reference_oracle.py) and [raw results](https://github.com/KooshaPari/PhenoRegistry/blob/f36565172c2b9640273dc4ad6a30516c769225b0/docs/governance/atlas/products/Tracera/research/pass06/reference-results.json) are retained with the source digest and environment.

Limits: no Tracera Rust execution, no cryptographic admission, no distributed writer/graph benchmark, no safe evidence-subsumption proof. Experimental status precedence is not a final accepted product policy. Mass product-test generation remains deferred.

## Next bounded work and completion gate

Run the actual product-scoping witness first; inspect callers before changing behavior. Then specify and compare safe evidence reuse, current relational versus embedded graph semantics, and the reachable UI mutation path. Existing native suites should be reused where they can supply valid evidence; the research example is not a substitute.

Keep both product passes and registry PRs open/draft until whole-source reconciliation, concrete acceptance design, meaningful stage/journey mappings, selected dependency qualification, architecture-risk experiments and independent semantic review close. Neither this document nor its source count awards product progress or specification completeness. No third repository is authorized.
