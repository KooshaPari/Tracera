---
created: '2026-02-01T03:29:41.799616'
external_id: DB_SCHEMA-006
id: 16e6ceb0-c5a5-4d22-bcdd-ef4e4ff3e7b8
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.799616'
version: 1
---

# user_verification

## Description

Identity verification records. KYC/background check status.

## Metadata

**columns:**
- id
- user_id
- verification_type
- status
- provider
- verified_at
- expires_at
**indexes:**
- user_id_idx
- status_idx
