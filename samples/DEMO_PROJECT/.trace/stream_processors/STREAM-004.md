---
created: '2026-02-01T03:29:42.321951'
external_id: STREAM-004
id: 4931a600-a3e6-4774-ac47-00c96fb3b30d
links: []
owner: null
parent: null
priority: critical
status: todo
type: stream_processor
updated: '2026-02-01T03:29:42.321951'
version: 1
---

# Surge Pricing Engine

## Description

Calculate dynamic surge multipliers based on supply/demand.

## Metadata

**input:** driver.online + ride.requested

**output:** surge.updated events

**window:** 1 minute sliding

