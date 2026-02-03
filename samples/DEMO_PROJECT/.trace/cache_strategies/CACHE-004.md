---
created: '2026-02-01T03:29:42.142871'
external_id: CACHE-004
id: 8e9ca562-bf4e-453c-a1aa-e8fdfbdf6f8d
links: []
owner: null
parent: null
priority: high
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.142871'
version: 1
---

# User Roles Cache

## Description

Cache user role assignments.

## Metadata

**key_pattern:** user:{user_id}:roles

**ttl:** 30 minutes

**eviction:** LRU

