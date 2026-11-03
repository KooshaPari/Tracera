# Items list: recovery contract

Status: implementation in progress. Source baseline: `7558cf393a583ff2bcca634c3cb60cc81232f781`.

The user needs a truthful view of the project's persisted items and a working refresh action. The previous UI sent `include_specs`, which the Rust items endpoint rejects because its query decoder denies unknown fields, and treated failures as an empty list. A timer displayed a successful refresh without fetching anything.

## Contract

- `GET /api/v1/items` sends only supported filters (`project_id`, `view`, `status`, `limit`, and `offset`). The Rust handler currently does not support `parent_id`; a parent-filtered request must fail explicitly without silently presenting an unfiltered result. See `crates/tracera-server/src/routes/items.rs::Params`.
- A successful canonical response has an `items` array and a nonnegative integer `total` no smaller than the page length. Malformed responses fail visibly rather than becoming empty data. A page contains at most 50 items. This change does not implement snapshot isolation.
- Given an initial request failure, the list shows an error and no empty-state claim. Given a failed refresh after a previous success, the user is told the visible data is stale. A refresh must perform a new request and report failure or success according to the result, never a timer.
- Authentication and authorization failures (401/403) hide cached records and totals; transient failures can show the last successful data labeled stale. A short page inconsistent with `total`, `offset` and `limit` is an error, not an empty result.
- If the current table cannot faithfully represent an item's view, status, priority or version, it withholds the page and tells the user which fields are unsupported instead of displaying defaults. Paging remains available so a user can inspect later pages without displaying the unsupported page's rows or totals. Duplicate IDs fail the response. Other `useItems` consumers do not yet honor the `unsupportedFields` indicator and remain unqualified for such records.
- Given more than one page, the user can navigate next and previous by offset; changing project or view resets to the first page. The view states that search and filters cover only the displayed page, and cannot claim a consistent snapshot while records are changing concurrently.

## Evidence and limits

Focused hook and component tests exercise the response and user-visible contracts. They are not acceptance evidence for a running server or browser, project permissions, complete pagination, mutations, or legacy-backend compatibility. The canonical Rust item mutation routes remain unavailable at this baseline.
