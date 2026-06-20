---
created: '2026-02-01T03:29:42.180122'
external_id: CACHE-032
id: 551b332b-42b0-4ff6-98a9-311fc98285a2
links: []
owner: null
parent: null
priority: high
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.180122'
version: 1
---

# Geocode Cache

## Description

Cache address to lat/lng conversions.

## Metadata

**key_pattern:** geocode:{address_hash}

**ttl:** 7 days

**eviction:** LRU

