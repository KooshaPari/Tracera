---
created: '2026-02-01T03:29:42.176024'
external_id: CACHE-029
id: e3cee319-60b1-4c48-8a92-b2b309a32c40
links: []
owner: null
parent: null
priority: high
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.176024'
version: 1
---

# Promotion Validation Cache

## Description

Cache valid promotion codes.

## Metadata

**key_pattern:** promo:{code}:valid

**ttl:** 10 minutes

**eviction:** LRU

