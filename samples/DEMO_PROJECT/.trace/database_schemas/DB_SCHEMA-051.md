---
created: '2026-02-01T03:29:41.875373'
external_id: DB_SCHEMA-051
id: 558d4dca-15a0-4dbc-9673-f1312b388a1d
links: []
owner: null
parent: null
priority: medium
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.875373'
version: 1
---

# promotions

## Description

Marketing promotions. Discount codes, referral programs.

## Metadata

**columns:**
- id
- code
- type
- discount_amount
- discount_percent
- max_uses
- uses_count
- valid_from
- valid_until
**indexes:**
- code_idx
- valid_from_idx
