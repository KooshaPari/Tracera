# Fresh engineering state and completion path

Observed 2026-10-16 PDT / 2026-10-17 UTC. Read-only engineering review; no source implementation, production actions, fresh builds or fresh test suites. Main was independently resolved through GitHub as `ae68aea7febd772282606bf1e142d507316cfea0`; an isolated clean detached clone is `/tmp/tracera-readiness-source-20261016-latest`. GitHub reports fork=false, parent=null. PR #1132 remains open at `723964216ccc6b21b5488a30e501543769808e16` at observation time. Publication may advance that docs branch after this review.

## Verdict and evidence boundary

**Operational kernel qualified in one isolated Windows/SQLite candidate; valuable product not yet qualified.** Q0's source matches current main exactly. Its evidence is stronger than the earlier unavailable-runtime observation and must supersede that observation for the isolated candidate only. The shared service and hosted frontend are not thereby qualified.

The Q0 report attests an explicit-target `cargo build --locked -p tracera-server` (exit 0, 2m36s), archive and binary hashes, readiness 200, invalid query 400, absent record 404, unconfigured empty ingest 422, supplied-issue ingestion, the identical Story after restart, and cleanup of only owned PIDs/listener. No unit suite was executed. The candidate stopped. Reference: `docs/audit/TRACERA-Q0-RUNTIME-QUALIFICATION.md` on PR #1132. These are preserved execution receipts, not a rerun in this review. A persisted Story does not establish canonical product/observation durability, automatic discrepancy discovery, frontend usability, PostgreSQL, or release acceptance.

The empty-input 422 versus stale YAML 200 is a documented contract discrepancy. It does not establish that the handler should return 200. No production IDs or secrets are needed to reproduce that distinction.

## Actual progress since the previous readiness review

| Main change | Established in source | Remaining boundary |
|---|---|---|
| #1149 persisted journeys/steps | Genuine Item reads, complete paged collection, project/type checks, explicit known-empty versus missing steps | Writes/run unavailable; frontend acceptance unproven |
| #1148 project JSON export/import | Canonical Items and internal artifact trace links round-trip; rejects incompatible shapes; partial writes reported truthfully | Not full product backup; no transaction; no durable retry/idempotency contract |
| #1147 auth ownership | Legacy login/logout/refresh return typed 501 and name upstream boundary | Upstream deployment protection remains unproven |
| #1146 SQLite title search | Bounded title substring search and suggestions, project filtering, stable order | No relevance/symbol/semantic index; ASCII case-folding; index APIs unavailable |
| #1141 specification reads | Persisted type-filtered list/detail/stats, incomplete fields remain null | Summary, verify/run/activities and mutations unfinished |

These are useful incremental completions. A typed 501 removes fabricated success but does not deliver the missing capability.

## Current engineering goal clusters

| Cluster | Source state and useful assets | Acceptance still required |
|---|---|---|
| Storage | Store abstractions; SQLite/PostgreSQL adapters and migrations; Q0 SQLite Story restart witness | Semantic observations, baselines, findings, retry identities and provenance survive restart and failure |
| Project identity | `sqlite_store/projects.rs:17-23,74-80` and PostgreSQL equivalent derive projects from nondeleted problems | First-class or consistently derived identity includes real Item-only products; no false Project Not Found |
| Source import | `ingest/persist.rs:39-111` persists Story/evidence/trace links | Namespaced external identity, replay/update semantics, atomicity or explicit resumable partial progress; cross-source collision controls |
| Product semantics | Product/intent/observation/baseline/assessment types, traversal and detector implementations exist | Mount durable product-aware import and query contracts; link actual source revisions to accepted intent |
| Observation ingestion | `product/ingest.rs:3-8,70-86` explicitly stores values and idempotency keys in memory | Persistent backend and mounted pipeline; idempotency across restart and partial batches |
| Detectors | Pure freshness/coverage/contradiction functions with tests | Correct product/capability scoping, comparable observations, persisted findings and execution through an actual user workflow |
| Typed artifacts | Item/spec/journey projections preserve canonical documents; unsupported metrics are null | Full artifact-X/view-X UI parity, complete pages, correct detail IDs, matching metrics and source evidence |
| Search | SQLite title substring and suggestions are real | Product-appropriate discovery and bounded evidence navigation; no claim of semantic/symbol search |
| Snapshots | Items and internal artifact links only, at most 1000 Items | Product models/observations/baselines/evidence semantics; consistent snapshot and atomic/replay restore |
| Graph/evidence | Graph algorithms, artifact links and evidence records reusable | Explain a discrepancy and affected consumers with revision-qualified anchors and retained uncertainty |
| Auth/isolation | Optional common bearer gate and upstream auth integrations | Deployment configuration, user/project authorization and cross-product access controls demonstrated |
| HTTP write/ALM breadth | Many route families explicitly unavailable | Retain or explicitly disposition each promised capability; never silently delete historical obligations |
| MCP/CLI | Separate Rust MCP node/edge tools and DB selection; explicit demo mode | Identity/contract parity with canonical product, durable failures, tool-driven core workflow, CLI acceptance |
| Deploy/recovery | Q0 build/readiness/restart/cleanup qualified in disposable candidate | Hosted ingress/frontend, supervised install/update, rollback/recovery, PostgreSQL and release proof |
| Quality | Useful failure, pagination, type, snapshot and unknown-data tests exist | Execute relevant suites and independent negative controls; enforce numeric coverage and local quality gates |

## Specific high-priority semantic defects

1. `product/detectors.rs:129-130` sets a freshness finding's capability ID to its product ID, despite `Observation.capability_id` existing (`observation.rs:93`). This conflates identities.
2. `product/detectors.rs:179-193` tests whether any observation's product ID equals a capability ID. A properly modelled observation for product P/capability C can therefore fail coverage association.
3. `product/detectors.rs:237-264` groups contradiction observations by product and baseline, omitting capability and observation kind. Unrelated passing and failing observations can become a false contradiction, again labelling product ID as capability ID. Add counterexamples before using this detector for user decisions.
4. Product observation ingestion and detector suite have no demonstrated mounting or durable Store wiring in current router/main/Store implementations. Tables in migration `009_product_model.sql` provide nodes/edges, not proof observations/findings run durably.
5. `ingest/persist.rs:39` uses `story-{external_id}`, without source/project namespace; separate Story/evidence/link writes can partially succeed. Collision and retry behavior need tests; production corruption was not observed or asserted.
6. `routes/export_import.rs:1-2,152-239` explicitly implements a narrow item snapshot with sequential writes and partial-write reporting. That honesty is valuable but cannot substitute for atomic semantic ingestion or complete backup.

## Unavailable surface: reproducible lower bound, not total feature count

Static census: **39 modules contain 216 unique literal path strings in ROUTES arrays directly passed to `unavailable_routes(ROUTES)`**. Method: read each `crates/tracera-server/src/routes/*.rs`, select that exact call, extract literal ROUTES array entries, deduplicate exact strings globally. Excludes mixed modules, dynamic routes, aliases, fallback-only unsupported methods, top-level router registrations and intentionally upstream-owned auth. It is a source-level lower bound of exact templates, not 216 independent business capabilities or a percentage of the product.

| Family group | Exact-template count within that census |
|---|---:|
| Item specification operations | 43 |
| Integrations | 23 |
| Executions + execution configuration | 11 |
| Test cases + test runs + test suites | 25 |
| Coverage + spec analytics + QA + quality | 21 |
| Storage | 9 |
| Projects + problems + processes | 19 |
| All other selected modules | 65 |
| Total deduplicated selected templates | 216 |

Other unavailable contracts include specification overview/stats, verifies, activities, scenario execution (`routes/specs.rs:272-284`), search indexing, canonical link operations and generic router operations. Historical 29 audit findings, 284 API references, 652 baseline records, and view counts describe different denominators. Do not add or divide them into a completion percentage.

Test mocks are legitimate test infrastructure. MCP `TRACERA_DEMO=1` is an explicitly selected in-memory demo path (`crates/tracera-mcp/src/bin/mcp-server.rs:82-87,122-139`); its existence is not evidence that configured DB-backed production is mocked. Conversely, unavailable mounted business operations are real unfinished scope even though their error contracts are tested.

## Quality qualification

Tests inspected, not rerun: specification list/detail/stats persistence, exact 501/no-write behavior, wrong-type/project/query/pagination controls and incomplete-metric preservation (`routes/specs_tests.rs:84-281`); journey pagination and malformed-vs-empty steps (`routes/journeys.rs:281-422`); JSON round-trip, invalid input no-write, partial-write disclosure and store failure (`routes/export_import.rs:324-478`). Q0 proves build and narrow HTTP behavior only.

`.github/workflows/coverage.yml:29-39` emits Rust coverage without a numeric fail-under. Frontend `vitest.config.ts:13-24` declares 90% thresholds, but thresholds require coverage mode and cannot establish a measured result. `lefthook.yml:59,143` masks Ruff-format and Python-collection failure with `|| true`. No current coverage percentage, hosted-green status or broad test acceptance is claimed.

## Dependency-ordered completion work

| Package | Concrete change/acceptance | Dependency | Effort range (engineer-days) |
|---|---|---|---:|
| A: accepted boundary/runtime | Preserve wider baseline; select canonical runtime/identity and acceptance oracles; Q0 already exists | Operator intent/dossier | 1-3 |
| B: canonical durable model | Durable products, capabilities, accepted baseline revisions, observations, source anchors, findings; mounted queries/import | A | 5-9 |
| C: correct ingestion | Source-qualified IDs; repeat/restart/partial-write semantics; import three owned products without cross-product collisions | B | 4-8 |
| D: genuine discrepancy loop | Correct detector identity/comparability; persisted explanation; source change/reassessment; positive and independent negative controls | B,C | 6-12 |
| E: usable complete artifact UI | Project identity, typed navigation/detail/pagination, source links and honest summary; actual unfamiliar-user tasks | B-D; partly parallel | 5-9 |
| F: recovery/isolation/pilot | Failure injection, restart, access control, supervised deploy and three-product unfamiliar-user pilot | C-E | 5-10 |

Ranges overlap and are not a naive additive schedule. The unchanged semantic blockers dominate. Completing Q0 reduces operational uncertainty but does not justify subtracting all prior qualification days or compressing the semantic implementation.

| Cumulative milestone from current source | Optimistic | Base | Conservative |
|---|---:|---:|---:|
| Valuable CVP | 14-24 engineer-days | 24-44 engineer-days | 44-74 engineer-days |
| Unfamiliar-user pilot | 18-30 engineer-days | 28-50 engineer-days | 50-85 engineer-days |
| Broad retained v1 including disposition of every obligation | 65-110 engineer-days | 95-215 engineer-days | 180-320+ engineer-days |

Planning estimates, low confidence, not measured velocity or commitments. A one-day shift of the old base is intentionally modest: Q0 is real but only part of qualification. Broad v1 is not bounded above until retained scope and dynamic dependencies are agreed. Illustrative two-engineer capacity of 1.2-1.5 effective engineer-days/day makes base CVP roughly 4-8 working weeks, pilot roughly 4-9, broad v1 roughly 13-36; no actual staffing or throughput guarantee.

## Rewrite, feedback and sunset

Retain storage/projections/tests and replace narrowly where controls expose failure. A wholesale rewrite does not solve the still-ambiguous retained product boundary and sacrifices usable persistence infrastructure. First ship a complete narrow product loop: import real intent/source, discover a genuine discrepancy, explain source evidence, reconcile source change, restart with the same model. A pile of 501-to-200 route changes is not that loop.

User intent feedback should happen now; usability/value feedback requires the functioning loop. No unfamiliar-user three-product pilot is established. Scaling work follows actual value and measured limits. Sunset only after an explicit bounded pilot/decision, retaining audit/baseline evidence; feedback/intent evolution must explicitly disposition old obligations, never silently erase them.

## Memory provenance

A lightweight prior-memory pass used `MEMORY.md:820-822` only to preserve the rule that incomplete tests are not green. Its old adapter run was not reused as current evidence. Rollout ID `019f6924-7ca3-72b3-b28b-ea1ed6829124`. All engineering conclusions above derive from current main and revision-matched Q0 documentation.
