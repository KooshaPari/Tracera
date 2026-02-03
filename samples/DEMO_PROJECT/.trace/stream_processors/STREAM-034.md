---
created: '2026-02-01T03:29:42.340933'
external_id: STREAM-034
id: f27fde2a-92a9-4a32-a649-74bbffbee005
links: []
owner: null
parent: null
priority: critical
status: todo
type: stream_processor
updated: '2026-02-01T03:29:42.340933'
version: 1
---

# Chargeback Predictor

## Description

Predict chargeback likelihood.

## Metadata

**input:** payment.* + user.* events

**output:** Chargeback risk scores

**window:** Real-time + ML

