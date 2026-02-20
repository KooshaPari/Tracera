---
created: '2026-02-01T03:29:41.850726'
external_id: DB_SCHEMA-036
id: 82fdda8b-439c-4300-b38a-8e307768dc8a
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.850726'
version: 1
---

# refunds

## Description

Refund records. Full/partial refunds, reason, status.

## Metadata

**columns:**
- id
- transaction_id
- amount
- reason
- status
- processed_at
- created_at
**indexes:**
- transaction_id_idx
- status_idx
