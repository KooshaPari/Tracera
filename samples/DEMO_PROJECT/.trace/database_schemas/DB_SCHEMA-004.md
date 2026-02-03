---
created: '2026-02-01T03:29:41.797262'
external_id: DB_SCHEMA-004
id: 831ee182-3b5d-4b26-ace9-0fefbf9b95c2
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.797262'
version: 1
---

# user_devices

## Description

Registered user devices. Stores device tokens for push notifications.

## Metadata

**columns:**
- id
- user_id
- device_token
- platform
- app_version
- last_active
- created_at
**indexes:**
- user_id_idx
- device_token_idx
