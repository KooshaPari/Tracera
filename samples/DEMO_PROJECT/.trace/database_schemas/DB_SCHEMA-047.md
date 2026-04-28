---
created: '2026-02-01T03:29:41.873310'
external_id: DB_SCHEMA-047
id: e4f23eeb-1fb4-49f3-a849-415023b356fa
links: []
owner: null
parent: null
priority: medium
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.873310'
version: 1
---

# notifications

## Description

User notifications. In-app alerts, badges, deep links.

## Metadata

**columns:**
- id
- user_id
- type
- title
- message
- data
- read_at
- created_at
**indexes:**
- user_id_idx
- read_at_idx
