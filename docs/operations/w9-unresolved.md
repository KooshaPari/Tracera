# Remaining route decisions

W9 inventories literal `/api/v1` references in production frontend TypeScript
and the checked-in public OpenAPI paths. Query strings are excluded, parameter
names are normalized for comparison, and existing registrations (including
the formatted specification routes) are excluded. The resulting cohort is
264 distinct templates in 47 families, rather than an assumed 234 references.
This includes legacy paths outside `/api/v1`. Counts are templates, not HTTP
operations or call sites.

Four already registered operations are also corrected: POST projects changes
from 201 to 501, PUT project from 200 to 501, DELETE project from 204 to 501,
and GET `/org-intel/metrics` from hard-coded coverage/gaps with 200 to 501.
The CSV therefore has 268 decision rows: 264 new templates and four existing
operations. Implemented project reads remain available.

`w9-route-decisions.csv` records every added template, family, decision, and
before/after status. `THIS_PR` denotes the PR containing that file; the PR body
includes the same CSV with its actual PR URL. Regenerate with
`python scripts/w9_inventory.py --generate`, then `cargo fmt`.

Every added operation is deliberately 501. None has an existing handler and
Store contract implementing the complete referenced frontend operation. There
are no in-memory success stand-ins, new database drivers, or schema changes.

| Families | Decision rationale |
| --- | --- |
| Integrations, notifications, webhooks | No connector, sync queue, delivery, notification, or webhook repository operations in Store. Registration does not read credentials or configure providers. |
| Test cases, test runs, test suites, QA, coverage | No lifecycle/result/activities/coverage metrics repository. Canonical item records alone do not establish execution, coverage, approval, or trend semantics. |
| Problems | Existing `/problems` SQLite handlers expose `items/count` and a narrower filter/create contract. The referenced `/api/v1/problems` client expects `problems/total`, additional fields, lifecycle transitions, RCA, and activity semantics. These new aliases stay unavailable rather than silently dropping filters or fields. The existing SQLite handlers remain available. |
| Processes, executions, workflows, distributed operations | No persisted process versions, execution lifecycle, artifact store, participant coordination, or schedule contract. |
| Item specifications, quality, specification analytics | Generic persisted items do not implement the specialized analysis, verification, prioritization, baseline, defect, or test-run contracts. Existing specification projections retain their existing registrations. |
| Concepts, equivalence(s), journeys, libraries, tokens | No corresponding concept/projection, confirmation, journey step, component-library, or design-token repository contracts. |
| Branches, versions, graph(s), matrix, search | Snapshot/branch/viewport/matrix/export/search contracts are absent. Existing persisted graph and item reads remain registered. |
| AI, chat, docs, Codex, agent(s), MCP, mutations | No provider execution, generation, chat, session, tool execution, or operation persistence contract. |
| Accounts, auth, settings, sync, metrics, events, reports, storage, WS | No implementation for these referenced operations in this router. Existing identity middleware, auth configuration, credentials, health checks, and implemented domain handlers are unchanged. |

The shared unavailable response is exactly
`{"error":"not_implemented","route":"<matched template>"}` with HTTP 501.
IDs and query values are excluded. The gateway resolves known templates too;
unknown gateway paths use `/api/{*path}` instead of echoing arbitrary input.
Backend unknown paths remain 404. Normal authentication and CSRF checks still
run before protected operations: a rejected request can return 401/403 before
the 501 handler is reached.

The UI boundary replaces unavailable resource views with “Not implemented yet”
before mounting their demo/zero metric content. Implemented item/specification
views remain accessible. The chat panel is labeled unavailable, and notification
errors no longer become a successful empty list or zero unread count.
Project create/edit/delete dialogs also display that label without mounting
write controls or reporting a successful mutation.

The Rust contract test uses the integrated router and a migrated in-memory
SQLite fixture. It exercises GET, POST, PUT, PATCH, and DELETE for every W9
template, with concrete IDs and a query value that must not reach the response.
It also requires unknown routes to remain 404. The gateway test independently
checks exact expected templates and payloads from the CSV; UI tests check that
unavailable views do not mount their children and implemented views still do.

Limitations: this inventory is a static reference audit, not live deployment
proof. Entirely runtime-generated routes may require further enumeration.
UI boundaries intentionally disable incomplete surfaces rather than asserting
their data is complete. The local docs-3 product dossier was unavailable.
The verification receipt and PR distinguish executed checks from blocked gates.
