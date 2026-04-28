---
created: '2026-02-01T03:29:42.161406'
external_id: CACHE-021
id: c00ffe45-369e-408e-9626-9925e1d72c4e
links: []
owner: null
parent: null
priority: high
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.161406'
version: 1
---

# Route Cache

## Description

Cache calculated routes with polyline data.

## Metadata

**key_pattern:** route:{pickup_hash}:{dropoff_hash}

**ttl:** 1 hour

**eviction:** LRU

