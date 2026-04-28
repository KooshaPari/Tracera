---
created: '2026-02-01T03:29:41.800348'
external_id: DB_SCHEMA-007
id: 18a12b4c-4d40-4601-9e63-8f0bfbbf5311
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.800348'
version: 1
---

# user_roles

## Description

User role assignments. Supports rider, driver, admin roles.

## Metadata

**columns:**
- id
- user_id
- role
- granted_at
- granted_by
**indexes:**
- user_id_idx
- role_idx
