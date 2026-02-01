---
created: '2026-02-01T03:29:41.856260'
external_id: DB_SCHEMA-038
id: 2feb96be-fb2e-4342-82f6-22f03704d2ef
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.856260'
version: 1
---

# wallet_transactions

## Description

Wallet transaction ledger. Debits, credits, descriptions.

## Metadata

**columns:**
- id
- user_id
- amount
- type
- description
- balance_after
- created_at
**indexes:**
- user_id_idx
- created_at_idx
