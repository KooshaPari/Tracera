# Source baseline closure, 2026-10-15

Pinned source: `5a9f45fb81f5337ef8e07ed531f1ef63a0913a7c`.
This bounded pass changes documentation only. No runtime, authentication,
mutation, test-suite or production acceptance checks were repeated.

## Pluggable promise index

`TRACERA-BASELINE-PROMISES.csv` indexes all top-level Markdown table data rows
and list starters in the seven selected baseline files, plus an empty-file
sentinel. It is a discovery index, not an assertion that all indexed prose is an
endpoint promise. Continuation paragraphs, code blocks and nested context must
be read at the cited source line. It preserves historical/pending semantics.
A future operator CSV can replace the selected expected-state source; retain
this index as provenance and record replacement revision and selection rules.
The required canonical gap-inventory columns remain unchanged.

| Source                       | Indexed records | Interpretation                                                                     |
| ---------------------------- | --------------: | ---------------------------------------------------------------------------------- |
| FEATURE_INVENTORY.md         |             501 | All capability/document list rows; API subsection has 215 capability rows          |
| endpoint_traceability_map.md |              30 | 26 endpoint rows plus four rule/list entries                                       |
| traceability.md              |               7 | Three baseline references and four status assertions                               |
| TRACEABILITY.json            |               1 | Empty-file sentinel, existing GAP-020                                              |
| 20260726 parity matrix       |               8 | Eight acceptance gates, seven pending plus regression required                     |
| 20260722 convergence matrix  |              19 | Five implementation rows, six semantic rows, five improvements, three reject rules |
| MCP/CLI/API matrix           |              86 | Historical tool, command, storage, capability and flow entries                     |
| Total                        |             652 | Indexed records, not 652 accepted features                                         |

The API subsection contains 199 single-method rows, one combined CRUD row,
13 router descriptors and two handler paths. Its historical sections contain
17 mounted Python, 11 CURRENT/unmounted Python, 174 deleted and 13 Go rows.
The CURRENT disclaimer prevents treating historical Python statuses as live
Rust failures. The Go On main YES claims need explicit historical qualification
(GAP-029). Neither parity matrix enumerates every current view's artifact schema;
that pre-existing limitation remains GAP-017 and GAP-019. The MCP matrix explicitly
labels the retired Python stack historical; its historical capabilities are
migration expectations, not proof the current runtime supports them.

## New documentary findings

GAP-026 corrects the governance map's auth/me mount contradiction against the
active Rust router. GAP-027 records three broken test-file links. GAP-028 records
five missing links to existing method/path contract-test definitions. Definitions
prove neither test execution nor passing coverage. GAP-029 records 13 Go oracle
claims that cite an absent source file. All four are Medium documentary gaps.

The empty TRACEABILITY.json is already GAP-020; it was not duplicated. The
traceability overview's partial-test warning is candid disclosure, not a new
runtime defect. Its generic mapped assertions do not establish exhaustive
route or requirement coverage.

## Remaining acceptance boundary

The endpoint baseline has not received an exhaustive 215-row migration mapping
or execution audit. The 44 sidebar-view rows retain 33 Unknown severities;
37 Unknown rows remain across the canonical inventory. Public Access acceptance,
three detail IDs, sidebar journeys and artifact completeness remain unresolved.
A missing Rust owner alone does not prove deployed absence because a gateway
may implement it. No source inference in this pass changes runtime receipts.

## Method and source-reference correction

The earlier prose denominator of 17 unresolved methods was narrower than the
actual CSV: 20 method cells contained UNKNOWN. This pass classifies 19 of those
20 cells from callsites, URL prefixes or returned-URL semantics. One remains
UNKNOWN: artifact-download URL construction has no proven rendered consumer.
The storage URL reference proves no additional GET; DELETE remains established.
The desktop `/updates` value is a prefix; its actual GET appends `/manifest`.
SSE and WebSocket GET handshakes are explicitly not ordinary JSON GET probes.

The 284 records now comprise 276 executable/handshake callsite references,
seven definition/reference-only entries, and one URL prefix. Executable does
not mean mounted production reachability. Six definition-only catalog entries
remain documentary; the seventh is the unresolved artifact-download URL.
Streaming examples and ExportWizard still lack a proven production mount.
Items/links have a concrete GraphView route mount; no runtime verdict follows.
All method source corrections are pinned to 5a9f45fb and appended to existing
callsite evidence. No requests were sent to verify these classifications.

## Final URL classification and bounded linkage extension, 2026-10-15

At `0ccf98c8`, the final unresolved method row constructs an artifact-download
URL; it does not execute an HTTP request. `api/executions.ts:191` returns that
string and exports it at line 301, with no `downloadArtifact` callers under
`frontend/apps/web/src`. The fallback in `useQAEnhancedNodeData.ts:88` is in a
hook with no import/call consumers in that tree. Generic artifact media
renderers (`components/graph/QAEnhancedNode.tsx:370,401,407` and
`components/graph/nodes/NodeExpandPopup.tsx:113`) do not prove this producer
feeds a mounted view. Classify the row as NOT_APPLICABLE_UNCONSUMED_URL;
production reachability remains UNKNOWN. No download request was made.
The preceding one-UNKNOWN-method count is superseded: zero unresolved method
cells, seven reference-only entries, 276 executable/handshake references,
and one URL prefix. This is source classification, not runtime acceptance.

A finite five-row follow-up of the governance baseline checked GET org metrics,
GET teams, GET sprints, GET stories, and POST sprints against exact contract
YAML endpoint/method definitions. All five omit existing test linkage; extend
GAP-028 from five to ten rows, without creating a duplicate gap. Their active
router declarations are at `crates/tracera-server/src/router.rs:154-155,172-173`.
No contract tests were executed. The 652-record promise index remains a
discovery index; this five-row pass is not exhaustive baseline acceptance.
