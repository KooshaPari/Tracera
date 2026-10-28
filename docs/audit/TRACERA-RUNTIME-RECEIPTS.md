# Runtime receipts, 2026-10-14

## Actual navigation refresh, 2026-10-15 PDT

The local loopback SSH forward to Windows8091 again returned the six-project
list. Current project detail GET returned HTTP200 with named TRACERA and no
stub marker. Nevertheless, the project root DOM rendered Project Not Found,
omitting the project sidebar. The actual anchor-click lane recorded all44
baseline entries: four global command links clicked (Dashboard, Projects,
Items, Agents) and forty project links unavailable. These are actual clicks,
distinct from the earlier56 direct URL navigations. Artifact identity,
pagination and project isolation remain UNKNOWN; no missing link was invented.
See `TRACERA-SIDEBAR-CLICK-RECEIPTS.csv` and GAP-025.

Exact frontend collection GETs for contracts, features and scenarios in both
TRACERA and CIVIS each returned HTTP200 explicit stub:true, three generic empty
arrays and zero totals, without the expected typed collection key. They prove
neither true emptiness nor isolation. No verified contract/feature/scenario ID
was available for the three remaining detail routes; none was fabricated.
See `TRACERA-ENTITY-AVAILABILITY.csv`. A single existing cached-auth public
projects GET again returned403 text/plain from cloudflare; no login or Access
policy change was attempted. New receipts redact concrete project/entity IDs.

Compute placement: small DOM browser work local; existing Windows gateway
runtime read through loopback-only SSH. No heavy compute or public exposure.

Read-only GET/CLI observation only. No screenshots, source changes, merges,
mutation probes, Access policy changes, or credential output.

## Public access

Normal cloudflared Access login completed successfully, exit 0, with token
output discarded. A subsequent cached-cookie GET `/api/v1/projects` returned
HTTP 403, text/plain, server cloudflare, non-JSON. Login completion does not
establish data permission or public API/browser acceptance.

## Windows origin

SSH-scoped GET `http://127.0.0.1:8080/api/v1/projects` returned JSON with six
projects. TRACERA ID: `proj-64b13e21-67bc-4e97-b3ab-0e097a03e9db`.
CIVIS ID: `proj-cc8c08b8-ced6-4a75-9fc6-de409d1165bb`.

GET `/api/v1/projects/proj-64b13e21-67bc-4e97-b3ab-0e097a03e9db/specifications/summary`
returned HTTP 200, Content-Type text/html, and an HTML SPA shell. The listener
process identity and deployment revision were not established. This is an
origin response-shape observation, not proof of production or source drift.
Project-scoped item probes produced strings; current item counts are UNKNOWN.
PowerShell string Count must not be treated as an artifact count.

The preceding lane relayed public receipts: six projects; TRACERA 533/533
items (372 tests, 116 requirements, 17 components, 17 epics, 11 ADRs); CIVIS
0/0; summary explicit stub:true. Durable artifacts for those receipts were not
recovered in this refresh. Preserve them as historical provenance, distinct
from operator-reported 26 ADRs and the current origin HTML observation.

## Coverage

No rendered artifact identity or DOM click-through was verified. Historical
extraction covered 59 views and 284 API references; current canonical matrix
contains 44 Unknown view rows. These denominators are not interchangeable.
Complete pagination, X-renders-X, and public runtime acceptance remain UNKNOWN.
Mutation routes were NOT_PROBED. Local origin is not public Access acceptance.

## Gateway reconciliation, 2026-10-14 22:17 PDT

Process-scoped Windows listener inspection identified port 8080 PID 98924,
`tracera-live.exe`, executable `C:\Users\koosh\agents\tracera\tracera-live.exe`.
Read-only inspection of deployed `C:\Users\koosh\agents\tracera\front.js`
identified a separate loopback gateway listening on 8091 and forwarding to 8080. When upstream content type is text/html for any `/api/` path, this
gateway returns HTTP 200 JSON empty envelopes with `stub:true` for GET;
notifications/workflows/branches/versions/views root collections get `[]`.
Non-GET fallback is HTTP 501; those methods were not probed.

An independent safe GET to port 8091 using the listed TRACERA project ID
confirmed summary HTTP 200, application/json,
`x-tracera-stub: unimplemented-route`, and exactly
`{"items":[],"data":[],"results":[],"total":0,"count":0,"stub":true}`.
This reconciles the 8080 HTML and gateway stub observations; they are distinct
layers, not evidence of deployment drift. Public Access acceptance is still
unknown. The deployed script also references a canonical item service at
127.0.0.1:18000; its summary request failed and readiness was not established.

The deployed gateway file is outside the audited checkout. Its behavior must
not be attributed to a repository commit without a deployment/source mapping.
No capture-free DOM session was established; all rendered artifact and
pagination acceptance remains unverified.

## Read-only tunnel and method batch, 2026-10-14 23:55 to 2026-10-15 00:13 PDT

A loopback-only SSH forward from local 18991 to Windows 8091 worked. This
qualifies the authorized local gateway, not the public Cloudflare Access path.
The method table enumerates 284 references: 266 executable callsites and 18
definitions/references; 95 GET-only candidates, 172 mutation-containing routes
excluded, 17 unresolved. Mounted-view reachability remains unknown from source.

Of 95 GET candidates, 57 were probed with a valid TRACERA project ID where
required: 45 HTTP200 (43 explicit stub envelopes), 11 HTTP501 and one HTTP400.
Another 34 require actual entity IDs and four sensitive/action-semantic paths
were not probed. No mutation requests were made. See
`TRACERA-GET-METHOD-BATCH.csv`; this lists each response rather than extrapolating
the gateway fallback to every route. HTTP errors can reflect missing required
query parameters, not only missing functionality.

Flat `/api/v1/items?project_id=...&limit=100&offset=0` independently returned
533 TRACERA records, 533 unique IDs and total 533 in one gateway-aggregated
response: 11 ADRs, 17 components, 372 tests, 116 requirements and 17 epics.
CIVIS independently returned zero records and total zero, with no stub field.
Project-scoped item and summary routes for both projects instead returned
explicit stub envelopes. `limit=1000` is invalid pagination (HTTP400), not a
product gap. See `TRACERA-ITEM-PAGINATION-RECEIPTS.json` and
`TRACERA-SAFE-GET-RECEIPTS.csv`. These establish the returned item collection,
not the completeness of the upstream ingestion or rendered project artifacts.
