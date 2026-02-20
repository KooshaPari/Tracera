---
created: '2026-02-01T03:29:41.796749'
external_id: DB_SCHEMA-003
id: 023ec395-034c-404e-949f-3fcd346ab183
links: []
owner: null
parent: null
priority: critical
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.796749'
version: 1
---

# user_sessions

## Description

Active user sessions. Tracks JWT tokens, device info, expiry times.

## Metadata

**columns:**
- id
- user_id
- token_hash
- device_id
- ip_address
- expires_at
- created_at
**indexes:**
- user_id_idx
- token_hash_idx
