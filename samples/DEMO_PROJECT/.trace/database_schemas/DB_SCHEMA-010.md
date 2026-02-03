---
created: '2026-02-01T03:29:41.807359'
external_id: DB_SCHEMA-010
id: 3ee501fd-09e3-4aac-9982-8b48c32afe22
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.807359'
version: 1
---

# user_audit_log

## Description

User action audit trail. Tracks login, profile changes, security events.

## Metadata

**columns:**
- id
- user_id
- action
- ip_address
- user_agent
- metadata
- created_at
**indexes:**
- user_id_idx
- action_idx
- created_at_idx
