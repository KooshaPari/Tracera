---
created: '2026-02-01T03:29:42.325077'
external_id: STREAM-011
id: ba6d63a4-0c56-4151-963e-c42af2a6e3f9
links: []
owner: null
parent: null
priority: high
status: todo
type: stream_processor
updated: '2026-02-01T03:29:42.325077'
version: 1
---

# Driver Acceptance Rate Calculator

## Description

Calculate rolling driver acceptance rate.

## Metadata

**input:** ride.matched + ride.accepted + ride.rejected

**output:** Acceptance rate metric

**window:** 1 hour sliding

