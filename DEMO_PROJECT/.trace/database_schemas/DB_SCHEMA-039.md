---
created: '2026-02-01T03:29:41.860272'
external_id: DB_SCHEMA-039
id: f7aefa6d-18d9-4503-aa2a-0af87decd7f2
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.860272'
version: 1
---

# payment_disputes

## Description

Payment dispute cases. Chargeback handling.

## Metadata

**columns:**
- id
- transaction_id
- reason
- status
- evidence_url
- resolved_at
- created_at
**indexes:**
- transaction_id_idx
- status_idx
