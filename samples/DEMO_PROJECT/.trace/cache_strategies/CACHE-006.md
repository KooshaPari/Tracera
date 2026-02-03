---
created: '2026-02-01T03:29:42.146417'
external_id: CACHE-006
id: 37a34c06-b9db-4f47-adda-8d64171bf52b
links: []
owner: null
parent: null
priority: high
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.146417'
version: 1
---

# Password Reset Tokens

## Description

Cache password reset tokens with expiry.

## Metadata

**key_pattern:** reset:{token}

**ttl:** 15 minutes

**eviction:** TTL

