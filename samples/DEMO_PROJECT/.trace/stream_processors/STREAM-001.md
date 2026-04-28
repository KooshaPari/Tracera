---
created: '2026-02-01T03:29:42.320274'
external_id: STREAM-001
id: cc9ff915-26b1-4682-baca-3afd5fd55311
links: []
owner: null
parent: null
priority: critical
status: todo
type: stream_processor
updated: '2026-02-01T03:29:42.320274'
version: 1
---

# Real-time Ride Matcher

## Description

Match incoming ride requests with available drivers in real-time.

## Metadata

**input:** ride.requested stream

**output:** ride.matched events

**window:** 1 second

