---
created: '2026-02-01T03:29:41.790272'
external_id: DB_SCHEMA-001
id: 873ee80c-26e2-4d71-93be-84599dba3dbd
links: []
owner: null
parent: null
priority: critical
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.790272'
version: 1
---

# users

## Description

Core user account table. Stores authentication details, profile info, created timestamps.

## Metadata

**columns:**
- id
- email
- password_hash
- phone
- first_name
- last_name
- created_at
- updated_at
**indexes:**
- email_idx
- phone_idx
