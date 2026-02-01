---
created: '2026-02-01T03:29:42.167545'
external_id: CACHE-024
id: 1645b94e-41c6-4068-8785-30f269103881
links: []
owner: null
parent: null
priority: high
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.167545'
version: 1
---

# Scheduled Rides Cache

## Description

Cache upcoming scheduled rides.

## Metadata

**key_pattern:** scheduled:{rider_id}

**ttl:** 1 hour

**eviction:** LRU

