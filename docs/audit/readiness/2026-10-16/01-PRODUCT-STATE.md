# Tracera: full product state and present usability

Review date: 2026-10-16 PDT / 2026-10-17 UTC. Independent read-only product/value review. Source pin: `ae68aea7febd772282606bf1e142d507316cfea0`, isolated checkout `/tmp/tracera-readiness-source-20261016-latest`. Repository is standalone (`fork=false`, `parent=null`, freshly resolved by engineering lane). This is completion of a project, not completion of an upstream fork.

## Executive judgement

**The operational kernel has a genuine isolated qualification receipt. The valuable product is not yet accepted.** There is substantial reusable code; a whole-project rewrite has not been justified. The highest-value remaining work is a coherent persistent explanatory product loop, not converting unavailable routes into superficially successful responses.

Q0 is a meaningful advance: exact-current-main Windows/SQLite build, readiness, invalid/missing/empty-input controls, a real supplied-issue Story write, identical Story after process restart, and cleanup of the owned candidate. The candidate is **stopped**. This review does not assert that a user can open that candidate now, that production was changed, or that the hosted frontend works. Q0 does not prove product observations, automatic discrepancy discovery, UI navigation, PostgreSQL, install/update or unfamiliar-user value. Receipt authority: `docs/audit/TRACERA-Q0-RUNTIME-QUALIFICATION.md` on PR #1132, head `723964216ccc6b21b5488a30e501543769808e16` at review start. No new build, product test suite, runtime probe, browser observation, screenshot or recording was performed by this lane.

## Intent and boundary

The controlling supplied dossier defines Tracera as a **persistent product/system model and dissatisfaction discovery** product. Its required witness is real product import, a genuine discrepancy with source evidence, bounded navigation and preserved identity through restart. Authority: external `CodeProjects/docs/docs-5/products/tracera/DOSSIER.md:5-24,55-93`; `AGENT-PROMPT.md:15-25,37-45`.

The repo README foregrounds agentic/LLM trace observability, memory and session history (`README.md:6,13-18`). Atlas is substantially ALM-oriented; the dossier explicitly says ALM must not redefine the product (`DOSSIER.md:28-30`). These are unresolved scope/intent tensions, not permission to silently discard work. Record each historical promise as retained required v1, supported later profile, superseded with evidence, or explicitly retired by the operator. A narrow CVP witnesses the product and preserves wider critical obligations (`DOSSIER.md:14`).

```text
real product at revision R
  -> accepted intent + source/interface + evidence
  -> genuine, correctly scoped discrepancy
  -> bounded explanation and affected-consumer navigation
  -> revision R+1 reconciliation
  -> restart with the same identities and provenance
  -> unfamiliar-user pilot across three owned products
```

## What the user can do now

There is a recipe and receipt for reproducing a narrow isolated backend exercise. A developer can build and run that profile and exercise its persisted Story path. The already-qualified candidate has been stopped; no currently served URL is certified here. No demonstrated user workflow yet imports a whole product, automatically identifies an evidence-backed discrepancy, navigates it in the real frontend, reconciles changed source and survives restart as one coherent job.

Historical receipts found 533 unique TRACERA items and zero CIVIS items; CIVIS zero does not establish successful CIVIS import. Historical navigation covered 56/59 direct routes, but only four global sidebar links were actually clicked while 40 project links were unavailable behind Project Not Found. Fourteen differently named views showed mixed records; detail-ID and redirects failed. These are historical findings, not current-main regressions: typed reads, journeys, search and snapshots have since improved. No fresh six-project completeness or hosted acceptance is inferred.

## All major goal families

The table covers the 15 product/engineering goal families identified from governing intent and existing audit baselines. It is a navigable family inventory, not a claim that every historic promise is accepted or every dynamic path is exhaustively understood. Source facts are not runtime acceptance.

| Goal family | Current source / receipt state | Usability and remaining finish criterion |
|---|---|---|
| 1. Reach and identify a project | API project reads exist; SQLite projects derive only from `problems` (`sqlite_store/projects.rs:17-23,74-80`) | Item-only project discovery can disagree with existing artifacts. Canonical runtime must open the real imported product with stable IDs and permission checks. |
| 2. Import real product/source | GitHub/Jira/AgilePlus issue/task ingest is mounted; Story/evidence/links are real separate writes (`ingest/persist.rs:24-112`) | Issue ingestion is not full product source import. Required source, accepted intent, revision anchors and evidence must import completely with explicit omissions. |
| 3. Canonical identities and authoring | Item, product, capability, baseline and graph foundations exist; many HTTP writes explicitly unavailable | Distinguish product/repository/project/session/work item. Preserve source-qualified IDs, real validation and durable authoring through selected interfaces. |
| 4. Correct artifact views | Persisted type-filtered specification and journey reads, pagination and missing-vs-empty distinctions exist | View X must show complete artifact X and selected details in the correct product; no mixed-table substitution. Actual frontend journey remains unaccepted. |
| 5. Specifications overview/verification | Stored statistics preserve unknown metrics; summary/verify/run/activity unavailable (`routes/specs.rs:272-284`) | Hub totals must reconcile with complete lists; compliance/pass rate must reference actual evidence, not zeros or invented defaults. |
| 6. Intent/source/test relationships | Product types and artifact links reusable; multiple model boundaries remain | One traceable accepted intent -> capability -> source/interface -> native result/evidence chain, with dangling and cross-product controls. |
| 7. Discrepancy detection/triage | Freshness, coverage and contradiction functions exist | Present identity/grouping defects require independent counterexamples; durable mounted discovery and evidence-backed resolution missing/unproven. |
| 8. Evidence/provenance/history | Evidence records, Store methods, source anchors and baseline types exist | Immutable observations must retain revision, producer, privacy and historical status; restart/source-change cannot silently overwrite proof. |
| 9. Search/bounded exploration | SQLite title substring search and suggestions now implemented | No semantic/symbol-index acceptance. A user must locate the known capability/finding and navigate relevant evidence with bounded effort and explicit unsupported edges. |
| 10. QA/execution/analytics/reporting | Definitions/read projections exist; many execution and analytics families unavailable | Test definition differs from execution/result. Ingest real native reports, execute retained workflows and derive reports with exact denominators. |
| 11. Integrations/collaboration | Many route families return truthful 501 | Every retained integration needs a real scoped roundtrip with pagination, retry, identity, conflict and privacy controls; historical breadth needs explicit disposition. |
| 12. Agent observability/memory | README promises trace/session/memory product; components exist | Real run -> source-linked timeline -> truthful durable memory contribution to product purpose remains unaccepted; this cannot replace the governed model without a decision. |
| 13. UI/API/MCP/CLI parity | Distinct interfaces/models and explicit demo mode exist | Required interfaces operate on the same persisted scoped identity and errors. A stack lifecycle CLI or in-memory demo is not full historical CRUD/product parity. |
| 14. Install/security/recovery | Q0 SQLite build/readiness/Story restart qualified in disposable Windows profile | Hosted ingress, frontend, project/user authorization, PostgreSQL, supported packaging/install/update/recovery and backup fidelity remain separate gates. |
| 15. Documentation/quality/status honesty | Existing baseline indexing and audit CSVs; improved 501 honesty; useful tests | Some UI labels overclaim implemented writes. Numeric test/coverage/negative-control gates and retained-promise acceptance need executed receipts. No completion percentage is defensible. |

Server-relative paths in this table are under `crates/tracera-server/src/` at the pinned SHA. Current implementation and engineering details are expanded in companion `02-ENGINEERING-STATE.md`.

## The immediate semantic risks

These were independently source-inspected at the fresh pin:

- Observation ingestion explicitly holds values and idempotency keys in memory, with persistent wiring deferred (`product/ingest.rs:3-9,75-87`). A database-backed Story surviving restart does not repair this semantic durability gap.
- Freshness labels its capability ID with the product ID (`product/detectors.rs:129-130`).
- Coverage compares an observation's product ID with a capability intent ID (`product/detectors.rs:179-193`), instead of preserving distinct identities.
- Contradiction groups by product and baseline, omitting capability and observation kind, then labels product as capability (`product/detectors.rs:237-265`). Unrelated pass/fail observations can appear contradictory.

These are source-demonstrable counterexamples, not fresh failing-test receipts. Correct detector behavior must be established before a user makes decisions from findings.

## What counts as unfinished, mocked or unknown

A truthful 501 is honest **unfinished functionality**, not feature completion. A legitimate test mock is not product deception. Explicitly selected MCP demo mode is not proof the configured production DB is mocked. Null/unknown metrics are correct when evidence is missing; fabricated successful empty envelopes are not. Source implementation, passing unit tests, isolated runtime proof, deployed acceptance and user value must remain separately labelled.

The engineering lane's reproducible census finds 216 unique literal route templates across 39 modules directly passed to `unavailable_routes(ROUTES)`. This excludes mixed/dynamic/other registrations and is only a lower bound, not 216 independent product capabilities. Historical 29 gap findings, 73 inventory rows, 284 API-reference methods and 652 indexed promise records have different denominators; none supplies a percentage complete.

## First useful user feedback

No unfamiliar-user three-product pilot is established. Seek intent/job feedback now: which question should Tracera answer, which source/evidence is authoritative, which promises remain required? Product usability/value feedback follows a functioning CVP. A developer manually feeding an already-written finding or coaching every click cannot establish discovery or independent usability.

Pilot: begin with one owned product to debug the protocol, then three representative owned products under versioned inputs and independent oracles. Cases include an unreachable capability, stale coverage evidence, dependency change, duplicated owner and legitimate exception (`DOSSIER.md:55-81`). An unfamiliar operator must explain current behavior, find the issue, identify affected consumers and propose a bounded repair; repeat after source change and restart. Retain time/actions, interventions, errors, false positives, abstentions and failed attempts. Pre-register quantitative success thresholds against a competent manual Git/search/spec workflow before observing results. No comparative winner is claimed.

## Evidence and publication boundary

This is a read-only assessment plus report files, not source repair or deployment. Source evidence is current to the pinned SHA. Q0 receipts are preserved prior executions matched to that SHA. Historical UI/data findings are dated, bounded evidence. The parent owns PDF/Markdown integration and publication. No secrets, screenshots, recordings or production captures were used. No memory files were used by this lane.
