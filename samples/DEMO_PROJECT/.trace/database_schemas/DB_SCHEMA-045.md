---
created: '2026-02-01T03:29:41.871625'
external_id: DB_SCHEMA-045
id: c0ce4b58-3bc1-4f2a-baae-976d7da1bce1
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.871625'
version: 1
---

# geocode_cache

## Description

Reverse geocode cache. Lat/lng to address lookups.

## Metadata

**columns:**
- lat_lng_hash
- address
- place_name
- cached_at
- expires_at
**indexes:**
- lat_lng_hash_idx
- expires_at_idx
