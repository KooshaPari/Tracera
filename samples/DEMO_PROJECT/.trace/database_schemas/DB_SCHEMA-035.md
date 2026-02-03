---
created: '2026-02-01T03:29:41.850169'
external_id: DB_SCHEMA-035
id: 326af823-b5bb-4e3c-9b57-abb05928a8e2
links: []
owner: null
parent: null
priority: critical
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.850169'
version: 1
---

# transactions

## Description

All payment transactions. Charges, refunds, payouts.

## Metadata

**columns:**
- id
- user_id
- ride_id
- amount
- currency
- status
- payment_method_id
- provider_transaction_id
- created_at
**indexes:**
- user_id_idx
- ride_id_idx
- status_idx
