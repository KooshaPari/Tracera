---
created: '2026-02-01T03:29:42.320947'
external_id: STREAM-002
id: a9c919ff-6b3e-427f-a327-f13ada5471f3
links: []
owner: null
parent: null
priority: critical
status: todo
type: stream_processor
updated: '2026-02-01T03:29:42.320947'
version: 1
---

# ETA Calculator Stream

## Description

Calculate and update ETA continuously based on driver location.

## Metadata

**input:** driver.location_updated stream

**output:** ride.eta_updated events

**window:** 5 seconds

