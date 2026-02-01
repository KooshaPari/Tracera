---
created: '2026-02-01T03:29:42.182735'
external_id: CACHE-037
id: 2f34e868-0728-43e5-a713-dcec7eaf24af
links: []
owner: null
parent: null
priority: high
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.182735'
version: 1
---

# Favorite Locations Cache

## Description

Cache user's saved favorite locations.

## Metadata

**key_pattern:** user:{user_id}:favorites

**ttl:** 30 minutes

**eviction:** LRU

