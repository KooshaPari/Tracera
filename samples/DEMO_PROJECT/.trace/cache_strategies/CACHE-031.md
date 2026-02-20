---
created: '2026-02-01T03:29:42.178484'
external_id: CACHE-031
id: dd0e477f-73e3-4379-8a4b-fa78a6291d11
links: []
owner: null
parent: null
priority: high
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.178484'
version: 1
---

# Refund Status Cache

## Description

Cache refund processing status.

## Metadata

**key_pattern:** refund:{refund_id}

**ttl:** 10 minutes

**eviction:** LRU

