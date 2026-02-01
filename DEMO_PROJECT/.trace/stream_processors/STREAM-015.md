---
created: '2026-02-01T03:29:42.327694'
external_id: STREAM-015
id: 6d127b12-da4b-4f38-af2a-4cdd4b0d5a86
links: []
owner: null
parent: null
priority: high
status: todo
type: stream_processor
updated: '2026-02-01T03:29:42.327694'
version: 1
---

# Driver Utilization Calculator

## Description

Calculate driver utilization rate (active vs. available).

## Metadata

**input:** ride.started + ride.completed + driver.online

**output:** Utilization rate

**window:** 1 hour tumbling

