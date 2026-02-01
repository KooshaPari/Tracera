# TraceRTM Canonical Import/Export Format

This document defines the **standardized object notation** used for importing and exporting project data (project + items + links) across the API, CLI, web, and other clients.

## Overview

- **Export**: `GET /api/v1/projects/{project_id}/export?format=json` (items only) or `format=full` (project + items + links).
- **Import (into existing project)**: `POST /api/v1/projects/{project_id}/import` with items-only JSON or CSV.
- **Import (full, create project)**: `POST /api/v1/import` with canonical JSON (project + items + links).

The **canonical format** is a single JSON object with `project`, `items`, and `links`. It is round-trip compatible: export full → edit → import full.

## Schema (JSON)

```json
{
  "project": {
    "name": "string (required)",
    "description": "string (optional)",
    "metadata": "object (optional)"
  },
  "items": [
    {
      "id": "string (optional; logical id for link references; server assigns UUID on import)",
      "title": "string (required)",
      "view": "string (required)",
      "type": "string (required; same as view for trace views)",
      "status": "string (optional, default: todo)",
      "description": "string (optional)",
      "metadata": "object (optional)",
      "priority": "number or string (optional)"
    }
  ],
  "links": [
    {
      "source_id": "string (required; must match an item.id in this payload)",
      "target_id": "string (required; must match an item.id in this payload)",
      "type": "string (required; e.g. implements, tests, depends_on, relates_to)"
    }
  ]
}
```

## Export (full)

When you export with `format=full`:

- **project**: `id`, `name`, `description`, `created_at` (server-generated IDs and timestamps).
- **items**: each item includes `id` (UUID), `title`, `view`, `type`, `status`, `description`, `version`.
- **links**: each link includes `source_id`, `target_id`, `type` (UUIDs from the exported items).

You can re-import this JSON via `POST /api/v1/import`; the server will create a new project and assign new UUIDs, and link references are resolved from the `id` values in the same payload.

## Import (full)

- **Endpoint**: `POST /api/v1/import`
- **Body**: Raw JSON (content-type `application/json`) in the canonical form above.
- **Behavior**: Creates a new project (name/description from `project`), creates all items (assigning new UUIDs), maps old `id` → new UUID, then creates all links using the mapped IDs. The new project is associated with the authenticated account when applicable.
- **Response**: `{ "project_id": "<uuid>", "items_imported": N, "links_imported": M }`.

## Link types (examples)

Common values for `links[].type`: `implements`, `tests`, `depends_on`, `blocks`, `related_to`, `refines`, `decomposes`, `validates`, `exposes`, `uses`, `replaces`, `migrates_to`.

## Usage from clients

| Client | Export (full) | Import (full) |
|--------|----------------|---------------|
| **API** | `GET /api/v1/projects/{id}/export?format=full` | `POST /api/v1/import` with canonical JSON body |
| **Web** | Project Registry → Export → select project, format "Full (project + items + links)" | Project Registry → Import → mode "As new project (canonical JSON)", upload file |
| **CLI** | `rtm export --format full [-o file.json]` | `rtm import full file.json [--yes]` |
| **MCP** | `export_manage` with `action: "full"`, `payload: { project_id, output? }` | `import_manage` with `action: "full"`, `payload: { path }` or `{ content }` or `{ data }` |

## Validation

Use `ImportService.validate_import_data(json_str)` (or the API validation endpoint if exposed) to check canonical JSON before import. Validation requires: `project.name`, each item `title` and `view`, and each link `source_id`/`target_id` present in `items[].id`.

## Generating canonical JSON from mock SQL

The script `scripts/seed_swiftride_tracertm.py` builds canonical JSON from the SwiftRide mock SQL (most complete mock: 450+ items, 450+ links):

```bash
python scripts/seed_swiftride_tracertm.py --output swiftride_canonical.json
# Import via API:
# curl -X POST -H "Content-Type: application/json" -d @swiftride_canonical.json -H "Authorization: Bearer <token>" http://localhost:4000/api/v1/import
```
