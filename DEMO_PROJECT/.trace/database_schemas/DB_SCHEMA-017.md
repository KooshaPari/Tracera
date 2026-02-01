---
created: '2026-02-01T03:29:41.826362'
external_id: DB_SCHEMA-017
id: bc28096a-de3b-4079-a109-96f1efe67217
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.826362'
version: 1
---

# driver_payouts

## Description

Driver payout transactions. Weekly/daily payout batches.

## Metadata

**columns:**
- id
- driver_id
- period_start
- period_end
- total_amount
- fee
- net_amount
- status
- paid_at
**indexes:**
- driver_id_idx
- status_idx
