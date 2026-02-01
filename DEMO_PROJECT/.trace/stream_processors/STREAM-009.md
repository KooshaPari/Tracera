---
created: '2026-02-01T03:29:42.324189'
external_id: STREAM-009
id: 476000df-2425-444a-8c40-e21ead71ac1e
links: []
owner: null
parent: null
priority: critical
status: todo
type: stream_processor
updated: '2026-02-01T03:29:42.324189'
version: 1
---

# Wait Time Monitor

## Description

Monitor rider wait times and trigger alerts for long waits.

## Metadata

**input:** ride.requested + ride.matched

**output:** Wait time alerts

**window:** Real-time

