---
created: '2026-02-01T03:29:42.145103'
external_id: CACHE-005
id: b767daca-4496-45d2-9afa-724b8d0c82c8
links: []
owner: null
parent: null
priority: high
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.145103'
version: 1
---

# Auth Token Blacklist

## Description

Cache invalidated JWT tokens.

## Metadata

**key_pattern:** blacklist:{token_hash}

**ttl:** 24 hours

**eviction:** TTL

