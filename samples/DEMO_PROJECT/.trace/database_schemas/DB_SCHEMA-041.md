---
created: '2026-02-01T03:29:41.864842'
external_id: DB_SCHEMA-041
id: 77e4a7a2-223f-4cf3-8d1c-ba15525bd224
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.864842'
version: 1
---

# payout_accounts

## Description

Driver payout bank accounts. Bank details, verification status.

## Metadata

**columns:**
- id
- driver_id
- account_type
- account_number_hash
- routing_number_hash
- status
- verified_at
**indexes:**
- driver_id_idx
