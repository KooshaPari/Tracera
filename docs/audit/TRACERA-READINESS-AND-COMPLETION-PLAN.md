# Tracera readiness and completion plan

Review timestamp: 2026-10-16 16:51 PDT. Read-only audit and planning; no product implementation, tests, builds, service changes, screenshots or recordings were performed by these review lanes. Documentation publication does not deliver any product feature.

## Exact source, runtime and authority boundary

Three independent review lanes inspected main at `9977063f990e3ba172f51b603209674ed12114f7` in a fresh isolated `/tmp/tracera-readiness-main-20261016` source view. GitHub repository metadata independently returned `fork=false`, `parent=null`, default branch `main`: this is completion of an owned project, not a full-fork migration. Metadata is not proof of all historical authorship/license obligations.

PR #1132 audit evidence is based on older revisions. Its 29 gaps, 73 inventory rows, 284 frontend references and 652 baseline promise records are distinct denominators, not current-main unfinished-feature counts or a percentage complete. The 2026-10-16 15:50 PDT acceptance receipt found Windows localhost 8080/8091 refused connections; public Access previously redirected/denied requests. Current source improvements are not proof of deployment or present user usability. Earlier 56/59 navigations prove historical route reachability, not completed user jobs; 533 TRACERA items and zero CIVIS items are historical data observations.

Governing external product authority: `/Users/kooshapari/CodeProjects/docs/docs-5/products/tracera/DOSSIER.md:5-24,55-93`, `STATE.md:15-25`, `NEXT-ACTIONS.md:5-31`, `AGENT-PROMPT.md:15-25,37-45`. These require a real product model, evidence-backed discrepancy, bounded navigation and survival through source change/restart. The dossier is a proposed work program, not runtime certification. Its older capture requirements are superseded by the operator's absolute no-screenshot/no-recording policy.

There are THREE intent inputs to reconcile, not silently replace: (1) the user's explicit parity/artifact baseline and completeness expectation, (2) governing product-model outcome, (3) current repository trace/observability/memory/session-viewer claims. README.md:13-18 and docs/ARCHITECTURE.md:3-17 establish the third; they do not authorize deleting the other two. FEATURE_INVENTORY.md:1-10 now explicitly labels its Python entries historical migration safety material; historical promises still need retained/deferred/retired disposition with evidence. No master PRD or current accepted scope hierarchy was established by these bounded reviews. A new product rewrite or a narrowed finish contract requires a recorded operator intent decision.

## Actual architecture and competing surfaces

`Cargo.toml:1-10` is the current build-root authority: nine members (server, two MCP surfaces, edge, CLI, events, WorkOS, Atlas, mock AgCord). Canonical component map `docs/ARCHITECTURE.md:39-61` describes server Axum/Store/SQLite/Postgres, edge Worker, CLI stack management and optional queue wiring. Extra GraphQL/ML/Neo4j/Go-CLI/Python-SDK trees are explicitly not workspace members (`:51-54`): preserve them as separate/historical or optional obligations, not automatically production capabilities. Broad local 27-service platform (`:19-26,81-85`) is not evidence all 27 are required for the valuable slice.

Two MCP channels have different ownership routes: `tracertm-mcp/src/main.rs:1-10` proxies to HTTP API; `tracera-mcp/src/bin/mcp-server.rs:3-17,56-92` constructs Store directly using a database URL, with an explicit in-memory demo mode. Do not call this duplication proven waste without consumer evidence; do require one semantic contract and authentication/data-owner explanation so clients cannot see different worlds. Demo mode is an explicit dev option, not automatically a production defect.

Atlas is literally an ALM engine for delegation, accountable changes, signoff and CI (`tracera-atlas/src/lib.rs:1-22,68-81`), not the source-index explanatory product model described by the dossier. Retain useful code while keeping external engine work state distinct.

Web is React/TanStack SPA, Electrobun is a shell loading an external gateway, and a Tauri tree is also present (`docs/ARCHITECTURE.md:63-79`; desktop README:13-23,55-70). Shell existence is not proof of installed usability. Self-host instructions explicitly say WorkOS AuthKit is not wired and the checked-in forward-auth placeholder does not protect public traffic (`deploy/selfhost/README.md:24-37,54-65`); security gates fail closed, so this is an unfinished integration, not permission to disable protection.

Migration oracle now explicitly marks Python CURRENT entries historical and points to API_REFERENCE (`docs/FEATURE_INVENTORY.md:1-10`). Preserve historical capability commitments but resolve current contract from mounted Rust handlers/current frontend consumers. Blanketing all legacy inventory promises as required immediate features would recreate discarded scope without an intent decision.

## Current engineering state

| Area                   | Evidence at exact source pin                                                                       | Assessment / required acceptance                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ---------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Canonical Items        | `crates/tracera-server/src/item.rs:7-21`; `pg_store/items.rs:29-57`; `sqlite_store/items.rs:29-52` | Real persisted documents, preserved extension fields, parameter-bound filtering, deterministic ID ordering. PG count/page use repeatable-read transaction. Reuse. Prove migration/roundtrip against actual source corpus, both supported databases.                                                                                                                                                                                                                                                                 |
| Item HTTP reads        | `routes/items.rs:29-105`                                                                           | Bounded two-second queries, explicit pagination, store errors distinct from empty success; project list has item-based existence fallback. Reuse; verify frontend consumer schema and full page traversal.                                                                                                                                                                                                                                                                                                          |
| Specification reads    | `routes/specs.rs:75-123,149-181,194-248`                                                           | ADR/contract/feature/scenario lists/details/stats project/type-filter canonical items and preserve document fields. Missing observations remain null. Reuse. Summary, execution, verification/activity remain unavailable at `specs.rs:272-284`.                                                                                                                                                                                                                                                                    |
| Original Gap #1        | `routes/specs.rs:281-284`                                                                          | Source now returns honest 501 for specifications summary; expected dashboard aggregate/health contract still unfinished. Must define health denominators, unavailable-data semantics, provenance, then implement and test against persisted values.                                                                                                                                                                                                                                                                 |
| Broad missing surface  | `routes/w9.rs:108-160`; route family files; `router.rs:181-356`                                    | Static tally 240 W9 unavailable templates across 42 family files, 60 direct main-router `any(not_implemented)` registrations, ten specs unavailable templates. These are registration counts, NOT unique-method endpoint counts and NOT additive with 284 frontend references. Search, project mutations/import/export, equivalences, journeys, component library/tokens, AI/docs, executions/tests, notifications/settings and others need prioritization or explicit sunset.                                      |
| Projects / identity    | `pg_store/projects.rs:12-21,49-78`; `store.rs:145-150`                                             | Project catalog/get derive only from nondeleted problems, whereas Items have independent project_id. An item-only project can appear through Items and fail project lookup. Source-design inconsistency, runtime not re-proved. Need canonical project ownership and migration preserving IDs; empty CIVIS must be legitimate empty, not missing.                                                                                                                                                                   |
| Graph                  | `routes/graph.rs:1-7,54-86,121-281`; unsupported at 283-288                                        | Real SWEE graph reads validate dangling edges and implement reachability/path/cycles/topological/orphans. IDs are SWEE IDs, explicitly not artifact IDs. Reuse algorithmic infrastructure, but do not equate graph presence with source/intent traceability acceptance; bind artifact identity and provenance. Impact/traverse/exhaustive paths unavailable.                                                                                                                                                        |
| Ingest                 | `ingest/persist.rs:39-107`; `handlers/ingest_api.rs:20-29,77-101`                                  | Real Story/Evidence/TraceLink persistence. Story ID is `story-{external_id}` without source/project namespace; writes occur separately and errors accumulate. Candidate correctness risks: source/repo collisions, retries, partial results and no per-artifact atomicity. No observed production corruption claimed. Requirement counter increments on Story creation (`persist.rs:54,112`), not canonical requirement creation. Define/project namespace and transactional/idempotent import before claiming CVP. |
| Auth / scope           | `main.rs:67-88`; `auth.rs:15-49`; `router.rs:91-115`                                               | Nonloopback bind requires explicit mode plus token. Shared bearer authorizes application routes; WorkOS integration config-gated. No per-project/tenant authorization seen in this path. Suitable only if explicitly qualified as trusted single-operator deployment; multiuser access needs principal-to-project authorization and cross-project negative controls. Not a claim of unauthenticated public exploit.                                                                                                 |
| Persistence / recovery | `db.rs:9-42`; `main.rs:195-230`; `health.rs:44-75`                                                 | PG/SQLite pools, migrations, WAL/busy timeout, real readiness Store probe exist. Reuse. Restore rehearsal, actual deployment provenance and original-data reconciliation unproved by this read-only review.                                                                                                                                                                                                                                                                                                         |
| Problem lifecycle      | `store.rs:190-198`                                                                                 | Rust port explicitly describes a minimum column subset and follow-up full model: workaround/permanent-fix/KED/soft-delete/optimistic-locking semantics not complete. Include only if retained in v1 intent; do not silently label all ITIL finished.                                                                                                                                                                                                                                                                |
| MCP / CLI              | `crates/tracera-mcp/src/bin/mcp-server.rs:121-138,145-167,268-269`; `Cargo.toml:2`                 | MCP demo store is explicitly opt-in TRACERA_DEMO=1 and errors on Item persistence, so not blanket production fake-data defect. Legacy demo reads empty/readiness OK are intentional demo behavior requiring unmistakable demo mode. Two MCP packages plus CLI require consumer-level parity testing; mere tools/list is insufficient.                                                                                                                                                                               |
| Release/runtime        | Main source differs from historical deployed `tracera-live.exe`/front.js evidence                  | Need source SHA -> executable hash -> startup config -> database -> public domain attestation. Parent's current runtime unavailable finding means historic 43/57 stub probe results cannot certify current deployment behavior. No live acceptance in this lane.                                                                                                                                                                                                                                                    |

## Tests and gates: useful evidence, material limits

- `routes/items_tests.rs:70,88,126,150,183,227,241,249,262`: meaningful persisted reads, exact filters, page boundaries, missing/invalid queries, store failure and timeout, true empty vs failure. These are source-inspected tests, NOT freshly passed tests.
- `routes/specs_tests.rs:7-55,84-139,216-299`: SQLite fixture includes 115 records, unrelated types, another project; checks persisted identity/type, pagination and missing/wrong-type controls, unavailable operations not mutating records, unknown observations not invented. Good starting negative controls.
- `routes/w9_tests.rs:34-75`: integrated router tests >200 unavailable templates across GET/POST/PUT/PATCH/DELETE; catches registration/precedence bugs. `:79-91` retains unknown-route 404. This proves unavailability contract if passing; does NOT prove those operations work.
- `not_implemented.rs:69-101` creates isolated per-template routers for main direct stub tests. Narrower than whole-stack proof. Do not market 'zero 200 stubs' as 'zero unfinished features'.
- `.github/workflows/coverage.yml:29-41`: generates/uploads Rust coverage but no numeric fail-under floor configured in this workflow. `frontend/apps/web/vitest.config.ts:13-23` defines 90% thresholds, while package test is plain vitest without `--coverage` (`package.json:32`); routine test command alone does not demonstrate thresholds executed or met.
- `lefthook.yml:55-59` masks Ruff result with `|| true`; `:88-92` permits missing secret scanner; `:139-143` collects Python tests and ignores failure, does not execute tests. Pre-push has cargo check and frontend build, not Rust behavior tests. Therefore local hooks are not yet a complete replacement for unavailable hosted CI. `:108-125` can start stack and mutate formatting during push, undesirable as a deterministic verify-only gate.
- Existing hosted CI contains Rust/Python/Go/TS execution and aggregator jobs, but this lane did not inspect live CI statuses, test results or coverage artifacts. No 85%/90% certification is made.

## Goal and first-user usability matrix

| Goal / user job                            | Current-main evidence                                                                                                                                                  | User usability verdict                                                                                 | Minimum observable acceptance                                                                                                                               |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reach an owned project safely              | router.rs:128-155 probes/ingest; quickstart.md:36-45 requires ingress boundary; project GET router.rs:163-171                                                          | Source routes exist; present deployment unqualified                                                    | Authenticated user opens real project; forbidden user denied; no direct exposed unauthenticated backend; exact artifact/source/config recorded              |
| Import an actual product/source            | ingest/github.rs:26-43 fetches open issues, page size 100; router.rs:154-156 mounts GitHub/Jira/AgilePlus                                                              | Issue import is narrower than whole-product source model; complete source discovery unknown            | Version-pinned owned repo imports required source/interface/requirement/evidence records; all pages counted; replay idempotent; omissions explicit          |
| Create/edit project and canonical items    | handlers/projects.rs:1-5 unavailable mutations; router.rs:180-197 read-only items                                                                                      | Cannot call general-purpose authoring usable from these HTTP paths                                     | Create/import, edit and inspect selected canonical artifacts; validation failures retain data; restart keeps IDs/content                                    |
| Correct typed project views                | specs.rs:40-53,76-120,146-194 canonical typed projections, pagination/failures                                                                                         | Source improvement; browser end-to-end unqualified                                                     | ADR view contains ADRs only; correct project/type; all pages; selected item shows complete source/metadata, not mixed rows                                  |
| Specifications overview and verification   | specs.rs:196-252 derives only stored metrics, unknown values null; :272-284 summary/verify/run/activity 501                                                            | Lists potentially useful; hub and verification not complete                                            | Hub totals match typed lists; unknown compliance/pass rate shown unknown; verification references actual run/evidence                                       |
| Link intent -> code -> tests -> evidence   | routes/links.rs:1-17 says item-link storage absent; distinct artifact links; router.rs:149-161 trace APIs                                                              | Central explanatory job remains incomplete across models                                               | One canonical identity mapping; create/navigate valid links; reject dangling/cross-project edges; trace provenance and source revision visible              |
| Explain impact and gaps                    | handlers/governance.rs:9-45 compute uses supplied links; routes/graph.rs:1-9 SWEE graph distinct from artifacts, no project/depth filters                              | Useful primitives; not yet proof of product-bound explanation                                          | Seed real known gap; query persisted owned model; source anchors justify result; independent oracle checks false positives/missing edges                    |
| Evidence and audit trail                   | handlers/evidence.rs:58-110 delegates list/create to Store; root /evidence router.rs:152                                                                               | Source implemented, complete immutable decision history not proven                                     | Attach real evidence with source/run/time; retrieve after restart; stale evidence marked; claimed result reproducible                                       |
| Search and bounded exploration             | router.rs:233-239 search 501; routes/graph.rs:23-42 pagination, :8 cycles capped at 500 nodes                                                                          | Graph query building blocks; full explainable search unavailable                                       | Locate known symbol/capability, expand bounded neighbors, explicit unsupported dynamic edge, no fabricated relationships                                    |
| QA/test execution, analytics and reporting | routes/item_specs.rs:5-48, spec_analytics.rs:5-13 unavailable; specs.rs:239-252 null execution metrics                                                                 | Test records do not constitute execution/pass evidence                                                 | Ingest actual native reports, distinguish test definition/run/result, exact denominators, durable exportable explanation                                    |
| External integrations and collaboration    | routes/w9.rs:5-94 enumerates unimplemented integration/sync/accounts/notifications/etc families                                                                        | Broad promise remains unavailable; do not infer every integration missing from this file alone         | For each accepted integration: real authorized roundtrip, provenance, pagination/retry/idempotency/conflict handling, consistent identity                   |
| Agent session observability and memory     | README.md:13-18, ARCHITECTURE.md:41-48; memory/distillation/distiller.rs:12-26 stores Vec/Instant in-process; router.rs:320-339 Codex/docs/AI endpoints 501            | Components and promise exist; persistent full user flow unknown                                        | Real run/session ingestion -> source-linked timeline -> truthful memory output; restart retains accepted state; private evidence stays private              |
| MCP and CLI parity                         | tracera-mcp tools.rs:33-99 SWEE typed read/write arguments; bin/mcp-server.rs:79-92 DB required unless explicit demo; tracera-cli commands.rs:39-59 lifecycle commands | Current CLI is stack manager, NOT historic full CRUD CLI; MCP graph subset is not whole product parity | Same scoped model and IDs through required UI/API/MCP/CLI operations; unsupported capability declared; no demo mode for acceptance                          |
| Install/update/durability                  | desktop README.md:13-23 external local gateway wrapper, :65-70 shell features; db_integration.rs:1-25 in-memory SQLite direct Store tests                              | Packaging/source tests do not prove installed product, upgrade or restart                              | Install supported profile, exercise real flow, restart process + persistent DB, update/rollback preserving ownership and IDs, recover backup                |
| Honest product documentation               | ApiView.tsx:45-65 labels project POST/PATCH implemented; :89-93 labels item POST implemented, contrary to router.rs/handlers/projects.rs                               | Current misleading UI content remains even after server honesty                                        | Generate status from versioned capability contract; examples are marked examples; advertised action corresponds to real route/method and acceptance receipt |

Paths without leading slash above are relative to the pinned checkout; server paths
are under `crates/tracera-server/src/`, except tests under `crates/tracera-server/tests/`.
Frontend ApiView is `frontend/apps/web/src/pages/projects/views/ApiView.tsx`.
The three historic missing detail IDs and 40 sidebar links gated by ProjectNotFound
are historical receipt facts, not proof current-main repairs have failed.

## Valuable CVP: narrow breadth, complete correctness

Recommended first useful promise:
"Import one actual owned product and answer one real question about its intended
capability, implementing source and verification evidence, exposing a genuine
mismatch with an explanation another engineer can check; keep that model through
source update and restart."

This directly satisfies the dossier, while requirements/tests/ADRs support the
explanation. A generic table of 533 records alone does not. A hosted shell alone
also does not. CVP/MVP is a scope boundary, not permission for mocked outcomes.

First operator journey:

    owned repo at revision R
      -> import real source + capability/requirement/evidence anchors
      -> inspect project and correctly typed artifact
      -> navigate intent -> implementation -> test/run/evidence
      -> explain one known genuine discrepancy and affected consumer
      -> export/share a source-anchored explanation
      -> ingest revision R+1; mark old evidence stale, preserve IDs
      -> restart and reopen the same model and explanation

For this slice, finish import completeness/idempotency, canonical identity and link
semantics, typed rendering/detail, meaningful gap oracle, durable evidence, restart,
and ingress. Other menus must say unavailable or be excluded from the chosen profile;
the wider backlog remains recorded. Do not present zeros as healthy metrics.

## Completion packages and effort

All ranges are **engineering effort days**, not autonomous wall time or a calendar promise. One day means roughly six productive hours of implementation/review/verification by a qualified engineer assisted by agents. Team throughput, CI availability, deployment access and source authority remain unknown. Parallelism limited by shared schema/identity and integrator review. Planning confidence LOW overall; moderate confidence in existence of named source gaps. Size after qualification, not from route count.

| Package | Scope and acceptance gate                                                                                                                      | Optimistic / base / conservative effort days |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| Q0      | Pin intended CVP, canonical backend/source/deploy/db, reproduce source update discrepancy on actual corpus, dedup route family ownership       | 1-2 / 2-4 / 4-7                              |
| Q1      | Canonical project/artifact/source IDs; migration/reconciliation; CIVIS honest emptiness; cross-source retry/idempotency and atomic writes      | 3-5 / 5-9 / 9-15                             |
| Q2      | Import -> explainable source/intent relation -> genuine discrepancy -> source update/restart semantics; provenance and stale relation behavior | 5-8 / 8-14 / 14-24                           |
| Q3      | Chosen CVP UI views exact artifact rendering, detail navigation, complete pagination and meaningful summary; unsupported affordances explicit  | 3-5 / 5-9 / 9-15                             |
| Q4      | Negative controls against actual stores; no false-success failures; restart/restore; trusted deployment/auth path and version attestation      | 3-5 / 5-9 / 9-15                             |
| Q5      | Unfamiliar user across three real products; documented setup, observe full loop and repair first feedback issues                               | 2-4 / 4-7 / 7-12                             |

Cumulative CVP engineering estimate from these dependencies: optimistic 15-25 days, base 25-45 days, conservative 45-75 days. A 17-35-day estimate from another lane is plausible only under reuse-heavy, clean-deployment and already-implemented intent-engine assumptions; Q0 must resolve that. CVP excludes broad workflow/AI/component/test-run/admin surfaces but includes real semantic value. Pilot incorporating unfamiliar-user feedback: cumulative ~25-50 base engineering days, ~45-85 conservative. User participation delay is additional unknown calendar time.

Broad retained v1 completion (all intentionally retained current advertised families, not future scaling): provisional **95-215 cumulative engineering days**, LOW confidence, not a ceiling. This is compatible with another lane's sizing only if scope freezes and existing adapters prove reusable. Work beyond CVP groups into (a) Item/project CRUD, version history/import/export and conflict semantics ~10-20 additional days; (b) search/equivalence/journeys and trace analysis ~15-35; (c) execution/test/quality/reporting semantics ~15-35; (d) provider/AI/docs/components/integrations and retained collaboration/admin surfaces ~20-45; (e) multiuser authorization, dual-store parity, recovery/deployment release qualification and docs/test-oracle repair ~15-35. Shared work means these rough ranges are NOT additive with CVP or each other without a concrete DAG. Scope expansion or discovery of a missing intent engine can exceed the band. Sunset removed goals by explicit intent decision rather than fake completion.

```text
Q0 source + intent qualification
  -> Q1 identity / import / persistence
    -> Q2 discrepancy + source-update semantics
      -> Q3 exact views + summary
        -> Q4 fault/restart/auth acceptance
          -> Q5 unfamiliar-user pilot
            -> feedback decision: retain / revise / sunset
Retained broad families run in parallel only after Q1 schema/contracts freeze;
integration and acceptance remain serialized gates.
```

## Estimate reconciliation, staffing and finish authority

The independent usability lane's 17-35 engineer-day CVP band assumes reuse-heavy source indexing and a clean running profile; engineering's 25-45 base band includes explicit identity, semantic reconciliation and negative-control qualification. Use **25-45 cumulative engineer-days base, 45-75 conservative** for a valuable CVP until Q0 proves the shorter assumptions. Pilot-ready estimate is **25-50 cumulative base, 45-85 conservative**. Conditional broad retained v1 is **95-215 cumulative engineer-days**, very low confidence and not a ceiling. These bands describe different maturity boundaries; they are not additive and do not certify all historic promises.

Calendar illustration only: with two available senior owners plus bounded agents, shared-schema dependencies and review may yield 1.2-1.5 effective engineer-days per working day. Then CVP base is roughly 4-8 working weeks, pilot 4-9, broad retained v1 13-36. With one effective engineer, divide the effort by five for approximate working weeks. None is a staffing commitment or release date; Access, deployment, user scheduling, new defects and scope decisions add unknown elapsed time. Re-estimate after Q0 and first real import loop with old -> new range and measured reason. All-652-historic-promise completion remains unbounded until scope is classified.

## Ordered decision and action path

1. Preserve the current audit, classify historical versus superseded findings against exact main and deployed SHA, and bind the canonical service/database/profile owner. Restart only through the owning authorized lane; this docs audit grants no service-action authority.
2. Record the primary persona/job and disposition each expected baseline promise: required CVP, required broad v1, supported later profile, historical, or explicitly retired. Keep unanswered intent conflicts UNKNOWN; operator decides retirement. A real artifact view cannot substitute another artifact to claim coverage.
3. Execute Q0-Q4 in an implementation-authorized branch with one owner for shared schema and integration, then independent acceptance. Keep this read-only audit separate from implementation authorization. Do not count honest 501 conversion as feature completion.
4. Run the first unfamiliar-user job, then the three-product pilot. Preserve negative outcomes and feedback. Decide continue/refine, bounded subsystem replacement, or sunset on evidence.
5. Close only the accepted finish contract: every retained promise has real behavior and consumer proof, measured gates, durable deployed artifact and recovery evidence. Scaling beyond proven demand, later user feedback and new intent are separately owned future work; they cannot excuse current retained stubs.

## Required evidence and publication limitations

Every retained promise needs source/profile, canonical persisted owner, mounted consumer and correct artifact schema, complete data/pagination, meaningful errors, independent negative controls, and an acceptance receipt. All project gates remain separate: source implemented, tests passed, integrated, deployed, installed and user-validated. No 85% or 90% coverage result is claimed. Governing floors apply independently to required families, critical behavior must pass completely, and checker qualification must show failures on deliberately wrong cases. Fixture presence, tools/list, honest unavailability or quiet CI is insufficient.

Scheduler ownership: the earlier 10-minute heartbeat remains sunset; this bounded review does not re-enable it. Finish/sunset decisions require a durable owner and wakeup condition. External Access failure does not by itself mean product sunset.

Historical memory used only as an evidence caution: MEMORY.md:822 records earlier Tracera focused tests did not complete, so formatting alone did not make that work green. No historical implementation fact is presented as current. Review source citations above are pinned to main SHA, while runtime/historical observations are explicitly attributed to the existing audit receipt.

## User feedback and value decision

There is no supplied proof of real unfamiliar-user validation. Do not claim fit.
Pilot plan derives from DOSSIER.md:55-81: three representative owned products, seeded
and retained-real cases (unreachable capability, stale coverage evidence, dependency
change, duplicated owner, legitimate exception); compare with competent manual
Git/search/spec workflow under matched inputs. First run one product to debug the
protocol; then all three. Preserve failures and human interventions.

Proposed practical session: 45-60 minutes per unfamiliar operator on the first
product, plus a 20-30 minute source-change/restart revisit. This is a feedback-session
timebox, not delivery ETA or a fabricated observed result. Jobs: explain a capability,
locate real mismatch, identify affected consumer, justify bounded repair. Observe
whether operator can complete each without developer coaching, time/actions, wrong
claims, missing evidence, confidence, and whether they would reuse the result.

Hard pass conditions: no invented/stale-as-current claims, no entity duplication on
replay, preserved ownership/IDs through restart, no private evidence leakage, genuine
negative-control detection and legitimate exception not misreported. Pre-register
quantitative time/error criteria against the manual baseline before running; do not
invent a favorable threshold after seeing data. If the tool is correct but not useful,
change the interaction or target job with operator intent; more menu breadth is not
a substitute for feedback.

## Finish, continue, rewrite or sunset

- Finish the chosen CVP when the actual product loop passes independent evidence,
  not when every menu is reachable. Keep broad v1 obligations visible.
- Finish bounded v1 when every retained promise has owner/profile/acceptance evidence,
  all required negative controls pass, install/restart/update are qualified, and
  operational/user docs describe the same shipped artifact. Scaling beyond measured
  demand and new user-requested features are explicitly separate future work.
- Continue learning if users get real value but need workflow changes; change scope
  with recorded intent and retain provenance of superseded obligations.
- Consider a scoped subsystem replacement only if repeated measured attempts show
  incompatible model contracts or maintenance cost beyond reuse; prefer known index,
  search/database and native report formats (DOSSIER.md:46-53). Whole-project rewrite
  currently has no evidential justification and would discard working primitives.
- Consider product sunset if an idiomatic reused tool/adapter meets the same accepted
  job at materially lower cost, users do not value the result after bounded pilots,
  or operator withdraws the intent. Preserve data/export/receipts/ownership handoff.
  This report recommends decision gates; it does not execute a sunset.
