---
created: '2026-02-01T03:29:42.186114'
external_id: CACHE-044
id: 30d3e823-f83a-4226-8a5b-38ebf808fe9b
links: []
owner: null
parent: null
priority: medium
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.186114'
version: 1
---

# Rate Limit Counter

## Description

Cache API rate limit counters per user.

## Metadata

**key_pattern:** ratelimit:{user_id}:{endpoint}

**ttl:** 1 minute

**eviction:** TTL

