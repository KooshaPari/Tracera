---
created: '2026-02-01T03:29:41.847250'
external_id: DB_SCHEMA-034
id: 8375215d-5168-4f33-8930-fb76b2cb1637
links: []
owner: null
parent: null
priority: critical
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.847250'
version: 1
---

# payment_methods

## Description

User payment methods. Credit cards, debit, digital wallets.

## Metadata

**columns:**
- id
- user_id
- type
- provider
- last_four
- expiry_month
- expiry_year
- is_default
- created_at
**indexes:**
- user_id_idx
