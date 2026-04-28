---
created: '2026-02-01T03:29:42.150694'
external_id: CACHE-007
id: 2c17eac5-e65a-4822-8a0e-33297385abd0
links: []
owner: null
parent: null
priority: high
status: todo
type: cache_strategy
updated: '2026-02-01T03:29:42.150694'
version: 1
---

# OTP Verification Cache

## Description

Cache OTP codes for phone verification.

## Metadata

**key_pattern:** otp:{phone}:{code}

**ttl:** 5 minutes

**eviction:** TTL

