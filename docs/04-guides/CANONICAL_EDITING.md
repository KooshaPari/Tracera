# Canonical project graph editing

The persisted canonical model supports interactive edits after import. Every
read or mutation is explicitly scoped to a canonical project; an item ID alone
never selects a project. These routes retain the existing canonical import,
export, paging, and traversal contracts.

| Route                                      | Request                                                                                | Result                                                 |
| ------------------------------------------ | -------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `POST /api/v1/items`                       | `project_id`, optional `id`, `title`, `view`, `type`, `status`, optional `description` | 201; canonical item and `project_id`                   |
| `PATCH /api/v1/items/{id}?project_id=...`  | Nonempty subset of `title`, `view`, `type`, `status`, `description`                    | 200; item detail; omitted fields retained              |
| `PUT /api/v1/items/{id}?project_id=...`    | Same partial update contract as PATCH                                                  | 200; item detail                                       |
| `DELETE /api/v1/items/{id}?project_id=...` | No body                                                                                | 204; incident links cascade only within this project   |
| `POST /api/v1/links`                       | `project_id`, `source_id`, `target_id`, `type`                                         | 201; canonical link, `project_id`, opaque `id`         |
| `PUT /api/v1/links/{id}?project_id=...`    | `source_id`, `target_id`, `type`                                                       | 200; atomically replaced link with its new opaque `id` |
| `DELETE /api/v1/links/{id}?project_id=...` | No body                                                                                | 204                                                    |

Link IDs returned by list/create/update encode the complete source/target/type
tuple with URL-safe base64. Clients must use the returned ID rather than build
one by joining strings with colons. Export keeps the existing link tuple format.

Each edit runs in one SQL transaction. The project row serializes edits before
an existing item is read, so changes to separate fields retain concurrent
updates. Composite foreign keys enforce endpoint existence within the same
project. A failed link replacement rolls back its deletion and project timestamp
update. Item deletion cascades its incident links. Missing objects return 404;
missing project scope or invalid editable values return 400; duplicate/conflicting
writes return 409. JSON create payloads reject unknown fields.

Interactive item updates cannot alter identity, source provenance, or imported
version evidence. Creating a new interactive item does not manufacture provider
provenance. Canonical storage does not model owner, priority, parent, arbitrary
spec fields, or link descriptions; payloads containing them are rejected rather
than reported as saved. Provider binding and import remain separate operations.

## Validation

`cargo test --locked -p tracera-server --test db_integration` includes a real
SQLite file close/reopen test covering edits, source evidence retention, same-ID
isolation, dangling rejection, atomic failed link replacement, delete and cascade.

The existing required PostgreSQL smoke job runs
`scripts/verify-postgres-canonical.py` with the actual server and database. It now
also exercises create/edit/link replacement/delete, two server restarts, rejected
provenance rewrites, rejected unscoped updates, duplicate items, dangling and
cross-project links, and delete cascade. The original 20-item/7-link fixture is
kept separate from interactive edit fixtures. Local SQLite HTTP parity uses
`--backend sqlite --database-url sqlite:///absolute/path.db?mode=rwc`.

These checks establish persistence behavior. Mounted frontend editing, a deployed
backend, human task success, and repeat use require separate acceptance receipts.
