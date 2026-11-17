# Tracera audit coverage and baseline register

Source revision: `4ec07444`. This is a documentation-only reconciliation of the
canonical inventory, not an authenticated production attestation.

## Evidence denominators

| Evidence set                                                      |                                 Count | Meaning                                                  |
| ----------------------------------------------------------------- | ------------------------------------: | -------------------------------------------------------- |
| Canonical `TRACERA-GAP-INVENTORY.csv` at source revision          |                               63 rows | 19 GAP records and 44 VIEW coverage records              |
| Canonical `TRACERA-GAP-ISSUES.md`                                 |                             19 issues | Static findings; operator observations remain attributed |
| Prior `/tmp/tracera-live-resume-20261014/docs/audit` artifacts    | 75 gaps, 59 views, 284 API references | Prior-pass provenance; not current verified counts       |
| Authenticated production views established by this reconciliation |                                     0 | All prior 59-view live checks remain Unknown             |
| Authenticated production API references established here          |                                     0 | All prior 284-reference live checks remain Unknown       |

The canonical issues describe an older static source snapshot
`9a4360e812eeee81ee7c0367b12a967cf7764440`; their source claims are not silently
requalified to deployed behavior by copying them into this register.
PR #1102 had an unsafe 2,239-file deletion diff and must not be used as the clean
handoff. The clean inventory PR #1103 was merged externally; this continuation
adds evidence on its descendant branch without merging or rewriting history.

## Pluggable expected-state baseline

| Selected source                                                                    | Interpretation / limitation                                                                                                      |
| ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `docs/FEATURE_INVENTORY.md`                                                        | Endpoint/capability migration oracle; opening warning says CURRENT labels describe historical Python, not the live Rust contract |
| `docs/governance/policy/endpoint_traceability_map.md`                              | FR -> endpoint -> test governance slice; 24 business routes plus two probes, not the whole current frontend surface              |
| `docs/traceability.md`                                                             | Declares route and FR linkage mapped, but explicitly calls test linkage partial and endpoints unmounted/untested                 |
| `docs/ops/TRACEABILITY.json`                                                       | Zero-byte tracked file at this revision; supplies no parseable traceability evidence                                             |
| `docs/sessions/20260726-frontend-convergence/02_PARITY_MATRIX.md`                  | Pending acceptance gates; does not certify per-view artifacts                                                                    |
| `docs/sessions/20260722-rich-dashboard-recovery/07_FRONTEND_CONVERGENCE_MATRIX.md` | Dated frontend convergence plan and route parity candidate                                                                       |
| `docs/04-guides/mcp-cli-api-matrix.md`                                             | Explicitly historical retired Python MCP/CLI reference                                                                           |

No hand-built CSV baseline has been supplied. If one is supplied, select it as
the expected-state input and retain these seven sources as provenance. Record
its path, source revision/date, selected project, expected artifact and fields in
each inventory row's evidence. Preserve the required CSV schema:
`id,area,view_or_route,expected,actual,severity,evidence,suggested_fix`.
Do not replace an Unknown actual result with a baseline assertion.

## Documentary gaps and existing coverage

GAP-017 already covers the historical/incomplete parity matrices. GAP-019 covers
unestablished artifact completeness. GAP-018 preserves the operator's CIVIS
zero-item observation; no live count or root cause is established here.

Additional verified documentary gap: `docs/ops/TRACEABILITY.json` is zero bytes
(`git cat-file -s 4ec07444:docs/ops/TRACEABILITY.json` returns `0`). It cannot serve
as the selected machine-readable traceability baseline. Suggested issue title:
**[Instinct] Restore a parseable traceability baseline with revision provenance**.
Generate a populated, validated projection from the authoritative mappings and
record its source revision. This is not a claim that runtime traceability fails.

The endpoint map marks `/api/v1/auth/me` unmounted, while canonical GAP-014 says
it is handled separately and is not a stub. This is a documented disagreement
requiring fresh active-mount tracing; neither statement is promoted to a current
live verdict here. The historical oracle warning and partial-test disclosure are
limitations, not independently demonstrated new runtime defects.

## Completion rule

A view named X must render artifact X for the selected project, with all required
fields and records. Verify artifact identity, project scope, permissions,
filters, every pagination page/cursor and aggregate counts. Distinguish genuinely
empty data from stub, failed, stale and partial data. Record DOM text and sanitized
request/response evidence without screenshots, recordings or secrets.

Read-only navigation and GET probes can establish live display evidence. Mutating
operations (create/update/delete/import/reindex/cache invalidation and similar)
remain unprobed; a static route finding does not establish successful mutation.
Until authenticated live evidence is recorded, the prior 59 views and 284 API
references remain Unknown and the inventory must not claim EVERY gap found.

## Refresh publication

Second refresh: GAP-021 independently confirms the deployed loopback gateway
converts missing GET routes into HTTP200 empty stub responses; 24 findings plus 44 view rows (33 severity Unknown) total 68. See runtime receipts for layered
8080/8091 evidence. No rendered page acceptance was added.

GAP-020 adds the verified zero-byte TRACEABILITY.json baseline defect; refreshed inventory contains 24 findings plus 44 view rows (33 severity Unknown) total 68. Historical 59-view extraction is preserved in TRACERA-HISTORICAL-VIEW-COVERAGE.csv, including all NOT_CLICKED statuses; it is provenance, not a current route attestation.

## API source reconciliation

TRACERA-API-SOURCE-RECONCILIATION.csv enumerates all 284 historical frontend references against source 4ec07444: 44 explicit Rust stubs, six mapped handlers, 234 unresolved Rust owners (not proof of runtime absence). The Vercel no-backend branch returns notFound for 246 references. Verbs were absent from the original extraction; method confirmation remains pending and mutation routes were NOT_PROBED. Conditional deployed fallback behavior is source-inspected; only the summary was directly probed at gateway8091.

## Latest runtime and method refresh

Current inventory: 24 gaps plus 44 view rows, 68 total. DOM receipts enumerate 59 baseline entries: 56 direct navigations (55 app DOM observations, one landing redirect) and three unresolved entity IDs. No sidebar click journey is claimed. Artifact completeness remains UNKNOWN. Fourteen entries show mixed 533-item tables; existing component detail shows Item Not Found and ADR detail redirects to list. Methods: 284 rows, 266 executable callsites, 18 definition/reference only; 95 GET-only, 172 mutation-containing, 17 unresolved. GET batch: 57 probed, 45 HTTP200 (43 explicit stubs), 11 HTTP501, one HTTP400; 38 not probed (34 unresolved IDs, four sensitive/action paths). Flat items independently return 533 unique TRACERA records, total533, and CIVIS0, total0 without stub. Local gateway evidence is not public Access acceptance.

## Sidebar and management refresh, 2026-10-15

Current inventory contains 25 findings and 44 view rows (33 Unknown, 10 High, one Medium), 69 total. Actual anchor-click receipts account for 44 baseline entries: four global links clicked, forty links unavailable because the known-project root renders Project Not Found. Six exact typed collection GETs across TRACERA/CIVIS return explicit stubs; detail IDs and isolation remain unknown. See new sidebar/entity receipts and GAP-025. Project-specific management heartbeat cadence and sunset limits are documented in TRACERA-AUDIT-HEARTBEAT.md.
