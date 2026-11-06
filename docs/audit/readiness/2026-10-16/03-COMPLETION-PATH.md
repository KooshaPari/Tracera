# Tracera: forward path to a valuable product and retained-scope completion

Planning pin: `ae68aea7febd772282606bf1e142d507316cfea0`, reviewed 2026-10-16 PDT / 2026-10-17 UTC. This is an evidence-qualified plan, not execution or a delivery promise. Q0 operational kernel is qualified in one stopped disposable Windows/SQLite candidate. Product CVP remains NOT READY.

## Finish the coherent job first

A valuable CVP/MVP has narrower breadth and complete behavior: import a real owned product, connect accepted intent and actual source/evidence, discover one genuine discrepancy without manually pre-authoring the finding, explain it with correct anchors, reconcile source change, and retain identities/provenance after restart. Requirements, ADRs and tests support this job. A page of 533 records, a green backend readiness route or many truthful 501s does not complete it.

The first real witness can use Tracera itself. Checked-in `tests/e2e/contract/ingest-github.e2e.yml:11-15` predicts 200 for an empty import; handler `handlers/ingest_api.rs:110-122` returns 422 when no live source is configured. Q0 observed the implementation response in isolation. The discrepancy is **stale/inconsistent contract evidence**, not proof that 200 is desired. The product must discover and explain that disagreement without conflating the contract's age with the correct behavior. The distinct-product/capability detector counterexamples are the stronger semantic correctness witness.

```text
Q0 operational receipt [DONE, candidate stopped]
                |
                v
A: freeze accepted core + canonical runtime + independent oracles
                |
                v
B: persistent products/capabilities/baselines/observations/findings
                |
                v
C: complete, namespaced, atomic/replay-safe source import
                |
                v
D: correct detectors -> explain discrepancy -> source-change reconcile
                |
                v
E: actual typed frontend, exact artifacts, bounded evidence navigation
                |
                v
F: failure/restart/isolation/deployment + unfamiliar-user pilot
                |
                v
retain-and-finish breadth / revise intent / explicit sunset
```

Pure detector counterexamples and UI inventory can proceed alongside schema planning, but shared schema/Store/router integration has one owner. Avoid a parallel fleet racing on shared traits. No production mutation, merge or rewrite is implied by this report.

## Concrete work packages and acceptance

| Package | Scope and concrete result | Dependencies | Effort, engineer-days | Primary uncertainty |
|---|---|---|---:|---|
| A. Boundary and artifact qualification | Record retained obligations, canonical runtime/profile and accepted job; freeze source manifest and independent positive/negative oracles; reuse Q0 | Owner intent and current receipts | 1-3 | Product meaning and which profiles must ship |
| B. Durable canonical product model | Products/capabilities/accepted baseline revisions, anchors, observations/findings and receipts persist through mounted Store adapters | A | 5-9 | Schema migration and distinct existing model ownership |
| C. Correct source import | Source-qualified external IDs; full paging; idempotency across retry/restart; same key/different bytes conflict; atomic batch or explicitly accepted resumable contract | B | 4-8 | Current separate writes, collision/replay semantics |
| D. Genuine semantic loop | Fix identity/comparability; real producer observations; explain mismatch, preserve unknowns; source R+1 updates historical/current findings correctly | B,C | 6-12 | Detector false positives and source-to-model bridge |
| E. Usable frontend | Item-only projects discoverable; artifact-X/view-X; complete pages/detail; evidence-backed summary and bounded explanation journey | B-D, partly parallel | 5-9 | Frontend/backend contract and real navigation |
| F. Reliability and pilot | Cross-product/private-evidence controls; crash/restart/restore; supported ingress/install; independent unfamiliar-user three-product tasks | C-E | 5-10 | Deployment and unanticipated user failures |

Ranges overlap; summing rows mechanically is not a schedule. Each includes focused implementation, meaningful tests, review and evidence. Uncertainty should shrink after A/B. Report estimate changes as old -> new with measured evidence and remaining dependencies.

## Time to useful and finished

No measured implementation velocity or committed staffing exists. Estimates below are planning judgement with low confidence, assuming reuse of Rust/React/Store foundations, one backend/integration owner plus one frontend/acceptance owner, actual owned sample products and access to the supported environment. Waiting on users/access is separate elapsed time. Agent concurrency is not linear engineer capacity.

| Cumulative milestone from current source | Optimistic | Base | Conservative | Acceptance meaning |
|---|---:|---:|---:|---|
| Valuable CVP | 14-24 engineer-days | 24-44 engineer-days | 44-74 engineer-days | One real discrepancy loop, selected real frontend and restart/negative controls |
| Unfamiliar-user pilot | 18-30 engineer-days | 28-50 engineer-days | 50-85 engineer-days | Three owned products, source change/restart, independent operator and value evidence |
| Broad retained v1 | 65-110 engineer-days | 95-215 engineer-days | 180-320+ engineer-days | Every explicitly retained obligation has correct implementation and accepted supported-profile evidence |

Illustration only: two experienced engineers achieving 1.2-1.5 effective engineer-days per working day imply base CVP roughly 4-8 working weeks, pilot roughly 4-9, broad v1 roughly 13-36. No actual capacity, start date or finish date is asserted. Q0's completion modestly reduces the old 25-45 CVP base to 24-44; it does not eliminate the semantic pipeline. Broad v1 has no defensible upper bound until historical retained scope and dynamic dependencies are decided. Estimates are not a reason to silently retire obligations.

## Finishing the whole retained project

After the first coherent job, disposition every baseline record without losing provenance. The seven indexed sources and 652 promise records are discovery material, not an accepted backlog of 652 equally sized tasks. Maintain a closure ledger with source promise, current contract, implementation owner, evidence profile, dependency, disposition and user impact. Suggested sequencing:

| Retained family | Finish requirement | Prioritization rationale |
|---|---|---|
| Product/identity/import/model | Correct complete durable semantic model and replay/reconciliation | Core dependency for every meaningful explanation |
| Source/evidence/graph/search | Qualified anchors, comparability, bounded navigation, affected consumers, explicit unsupported edges | Makes findings understandable and trustworthy |
| Artifact/specification UI | Exact type/product/data completeness, real detail/summary and verification evidence | Prevents misleading visible success |
| Authoring/work management | Real retained create/edit/link/workflow operations, validation and durable history | Finish promised breadth after model ownership settles |
| QA/execution/analytics/reporting | Actual run producers, result provenance, correct denominators and non-fabricated reporting | Records alone are not execution or compliance |
| Integrations/collaboration | Real scoped roundtrips, conflict/retry/privacy controls and failure contracts | Each integration adds external lifecycle cost |
| Agent traces/sessions/memory | Demonstrated durable contribution to accepted product purpose | Resolve observability vs product-model intent explicitly |
| UI/API/MCP/CLI profiles | Same canonical IDs, ownership, errors and outcome across required interfaces | Avoid separate demos masquerading as parity |
| Security/release/operations | Accepted authorization, backup/recovery, install/update and supported artifact matrix | Local build differs from released and installed acceptance |
| Documentation/quality/closure | Truthful capabilities, enforced numeric gates, independent negative controls, dated closure receipts | Completion is evidence, not route or task counts |

Do not spend the whole broad-v1 allowance converting stubs individually without grouping capabilities by user outcome. One route can support several jobs; several aliases can represent one capability. Explicit unavailability remains preferable to fabricated successful mocks while implementing real behavior.

## Rewrite decision

**Recommend retain and incrementally complete, with targeted replacement where qualified controls fail.** Existing storage adapters, migrations, typed projections, graph algorithms, persistence tests and honest error behavior are useful assets. Wholesale rewrite would re-create them while leaving product intent and acceptance unresolved.

Before replacing a subsystem, write a bounded retain/adopt/patch/wrap comparison: real consumer/job, current failure evidence, established local or external alternative, preserved identity/data/privacy, migration/rollback, maintenance burden and independent proof. Native indexing/search and native test/report formats are reuse directions in the dossier, not approval to invent a universal new engine. An adapter or narrower promise can be a successful product decision when explicitly accepted. Do not publish into other people's upstream repositories.

## Feedback, scaling, intent evolution and sunset

- **Feedback now:** validate intended question, authoritative evidence and retained scope. This is intent feedback, not product-fit acceptance.
- **Feedback after CVP:** independent user attempts, not a developer-led demo. First one-product protocol, then three-product pilot with seeded and retained-real gaps. Record failures/interventions and compare with competent manual workflow.
- **Scaling:** defer speculative throughput architecture until useful behavior is established and measured limits are real. Correct identity, privacy, durability and bounded behavior are immediate correctness requirements, not optional future scaling.
- **Intent evolution:** document accepted changes and migration for existing consumers; preserve superseded promises/evidence. ALM or observability cannot silently replace the governed product-model job.
- **Sunset:** a bounded pilot shows no useful advantage, an owned tool already fulfils the accepted job more simply, or operator explicitly chooses another direction. Retain/export necessary data and evidence, state which obligations move to which owner, stop owned services safely and leave a durable handoff. Sunset is an explicit product decision, not a convenient label for unfinished code.

## Immediate next bounded ownership

One owner should freeze the durable product-observation/import contract and mount the smallest real pipeline; an independent reviewer owns distinct-product/capability and contradiction controls. The next meaningful proof is not another static audit: imported real source expectation + independent observation -> persisted finding -> real UI explanation -> source change -> restart, without hand-authoring the finding. First execution slice and PR scope must remain isolated from existing checkouts and production, with no merge or force push.

No memory files were used by this lane. Current engineering details and exact source anchors are in companion `02-ENGINEERING-STATE.md`; governing authority is `DOSSIER.md:5-24,55-93` and `AGENT-PROMPT.md:15-25,37-45` in the external docs-5 Tracera dossier.
