---
created: '2026-02-01T03:29:41.886466'
external_id: DB_SCHEMA-060
id: 5822a0c9-f0a4-42f5-9ed4-81f6fb2a14d0
links: []
owner: null
parent: null
priority: medium
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.886466'
version: 1
---

# event_logs

## Description

Application event tracking. User actions, system events.

## Metadata

**columns:**
- id
- event_type
- user_id
- session_id
- properties
- created_at
**indexes:**
- event_type_idx
- user_id_idx
- created_at_idx
