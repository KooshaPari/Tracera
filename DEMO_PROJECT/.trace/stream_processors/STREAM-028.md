---
created: '2026-02-01T03:29:42.338158'
external_id: STREAM-028
id: 07ef9257-c7fa-45f1-90f1-e415c688f820
links: []
owner: null
parent: null
priority: critical
status: todo
type: stream_processor
updated: '2026-02-01T03:29:42.338158'
version: 1
---

# Velocity Fraud Detector

## Description

Detect abnormal transaction velocity.

## Metadata

**input:** payment.initiated stream

**output:** Velocity alerts

**window:** 1 minute sliding

