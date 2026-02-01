---
created: '2026-02-01T03:29:41.872700'
external_id: DB_SCHEMA-046
id: a0e616e9-6da1-4b1e-9f54-440ddc7bb76c
links: []
owner: null
parent: null
priority: high
status: todo
type: database_schema
updated: '2026-02-01T03:29:41.872700'
version: 1
---

# eta_cache

## Description

ETA calculation cache. Pre-calculated travel times.

## Metadata

**columns:**
- from_lat_lng_hash
- to_lat_lng_hash
- eta_seconds
- distance_meters
- cached_at
- expires_at
**indexes:**
- from_to_idx
- expires_at_idx
