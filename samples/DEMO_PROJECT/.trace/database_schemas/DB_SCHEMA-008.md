---
created: '2026-02-01T03:29:41.801537'
external_id: DB_SCHEMA-008
id: 9bc51e10-d390-4759-8c3d-f62a6123756e
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.801537'
version: 1
---

# password_resets

## Description

Password reset tokens. Time-limited recovery tokens.

## Metadata

**columns:**
- id
- user_id
- token_hash
- expires_at
- used_at
- created_at
**indexes:**
- user_id_idx
- token_hash_idx
