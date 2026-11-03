# Items Store routes

W1 introduces a canonical `items` table, separate from SWEE nodes and product
intent nodes. Neither graph records nor stories are relabelled as Items. Existing
rows in those tables are unchanged; there is no synthetic backfill.

`Store::create_item` persists the frontend Item contract for ingest callers. It is
a storage operation, not an HTTP create implementation. Core Item fields use
camelCase (`projectId`, `createdAt`, `updatedAt`); optional extension fields round
trip in the document. The SQL columns index the document's ID, project, status,
view and priority. Both backend implementations write these atomically.

| Method / route                            | Behavior                                                                           |
| ----------------------------------------- | ---------------------------------------------------------------------------------- |
| GET `/api/v1/items`                       | Persisted Items, optionally filtered by `project_id`, `status`, `view`, `priority` |
| GET `/api/v1/items/{id}`                  | Persisted Item or typed `item_not_found` 404                                       |
| GET `/api/v1/projects/{project_id}/items` | Same list restricted to the path project                                           |
| `/api/v1/items/{item_id}/pivot`           | Typed 501; equivalence navigation semantics absent                                 |
| `/api/v1/items/{item_id}/pivot-targets`   | Typed 501; available perspectives are not persisted                                |
| `/api/v1/pivot-targets`                   | Typed 501; no global target catalog semantics                                      |
| Item HTTP mutations, summary, bulk update | Typed 501                                                                          |

Lists return `items`, `total`, `limit`, `offset`, `has_more`, and `store: "items"`.
Limit defaults to 50 and accepts 1 through 100. Offset defaults to zero and must
be nonnegative. Results sort by opaque item ID ascending. Count and page are
read in one transaction; Postgres uses repeatable read. An offset above 100000
or a Store operation exceeding two seconds returns typed 503
`items_query_over_budget`. Other Store errors return sanitized typed 500
`items_store_error`. Unknown query options are rejected rather than ignored.

Project existence follows the current Store project model (persisted visible
problems), or persisted Items belonging to that project. A known project with
no matching Items returns a genuine empty page. An unknown project returns
`project_not_found` 404. A conflicting query `project_id` is rejected with 400.

The migrated SQLite production-router tests cover persisted fields and
extensions, exact filters including an SQL-injection negative control,
project scoping, pagination boundaries, missing records, invalid queries,
Store failures, a real exhausted pool timeout, valid empty pages, and typed 501
route labels. Postgres is compile-checked by the desk server test build; no live
Postgres runtime verification is claimed.

Legacy page/pageSize and cursor query options are not implemented by these routes;
callers must use the W4-style limit/offset contract. Unknown options return 400.

## Desk verification receipt (2026-10-16)

The required offline server command passed 72 tests, including nine Item route
tests and four graph route tests; no tests failed. Changed-file rustfmt passed
for 12 Rust files. Compute ran locally on the desk with two Cargo build jobs.

When several worktrees share a Cargo target, verify the output includes the
expected route test names and compiles this worktree's source. A stale shared
binary reported 57 passing tests without any Item or graph route tests; that
receipt was rejected. Refreshing this worktree's input timestamps forced a
source build, which produced the accepted 72-test result. No artifacts were
cleaned and no concurrent process was killed.
