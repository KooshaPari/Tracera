---
created: '2026-02-01T03:29:41.880580'
external_id: DB_SCHEMA-052
id: 53346e01-c87a-47ac-99d0-04929a28bb21
links: []
owner: null
parent: null
priority: medium
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.880580'
version: 1
---

# promotion_redemptions

## Description

Promotion usage records. User redemption tracking.

## Metadata

**columns:**
- id
- promotion_id
- user_id
- ride_id
- discount_applied
- redeemed_at
**indexes:**
- promotion_id_idx
- user_id_idx
