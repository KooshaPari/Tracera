---
created: '2026-02-01T03:29:41.822604'
external_id: DB_SCHEMA-015
id: 6fa20f5b-1d1f-4246-805c-74bcc4240f2e
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.822604'
version: 1
---

# driver_availability

## Description

Driver availability schedule. Online/offline status, shift times.

## Metadata

**columns:**
- id
- driver_id
- status
- available_from
- available_until
- updated_at
**indexes:**
- driver_id_idx
- status_idx
