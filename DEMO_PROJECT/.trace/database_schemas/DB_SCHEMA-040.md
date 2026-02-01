---
created: '2026-02-01T03:29:41.864226'
external_id: DB_SCHEMA-040
id: a8bc6e80-e4ee-4982-81c2-64c9dcf5087a
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.864226'
version: 1
---

# payment_holds

## Description

Pre-authorization holds. Temporary card authorizations.

## Metadata

**columns:**
- id
- user_id
- ride_id
- amount
- payment_method_id
- captured_at
- released_at
- created_at
**indexes:**
- ride_id_idx
- user_id_idx
