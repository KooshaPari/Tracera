---
created: '2026-02-01T03:29:42.180712'
external_id: CACHE-033
id: 369156dc-8440-45b1-b6e9-a6efc15937a1
links: []
owner: null
parent: null
priority: high
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.180712'
version: 1
---

# Reverse Geocode Cache

## Description

Cache lat/lng to address conversions.

## Metadata

**key_pattern:** reverse_geocode:{lat}:{lng}

**ttl:** 7 days

**eviction:** LRU

