---
created: '2026-02-01T03:29:41.815413'
external_id: DB_SCHEMA-011
id: a02f3071-d693-4fa8-a243-0369342472c5
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.815413'
version: 1
---

# drivers

## Description

Driver profiles. Stores license info, vehicle details, earnings account.

## Metadata

**columns:**
- id
- user_id
- license_number
- license_expiry
- status
- approval_date
- rating
- total_trips
**indexes:**
- user_id_idx
- status_idx
