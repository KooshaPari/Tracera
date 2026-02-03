---
created: '2026-02-01T03:29:42.322878'
external_id: STREAM-006
id: 88e5f7df-f50d-441f-b83d-406962ef343e
links: []
owner: null
parent: null
priority: critical
status: todo
type: stream_processor
updated: '2026-02-01T03:29:42.322878'
version: 1
---

# Ride Completion Aggregator

## Description

Aggregate completed rides by region for capacity planning.

## Metadata

**input:** ride.completed stream

**output:** Regional capacity metrics

**window:** 5 minute tumbling

