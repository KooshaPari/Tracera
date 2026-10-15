# Runtime receipts, 2026-10-14

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
identified a separate loopback gateway listening on 8091 and forwarding to
8080. When upstream content type is text/html for any `/api/` path, this
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
