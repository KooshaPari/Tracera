---
created: '2026-02-01T03:29:41.802944'
external_id: DB_SCHEMA-009
id: 83ddd61e-8333-4e19-8935-18acc7d6830c
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.802944'
version: 1
---

# oauth_connections

## Description

Third-party OAuth connections. Google, Apple, Facebook auth.

## Metadata

**columns:**
- id
- user_id
- provider
- provider_user_id
- access_token_hash
- refresh_token_hash
- connected_at
**indexes:**
- user_id_idx
- provider_idx
