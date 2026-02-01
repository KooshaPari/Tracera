---
created: '2026-02-01T03:29:42.332798'
external_id: STREAM-021
id: e6205990-4c51-44dd-84c7-8af256877ab7
links: []
owner: null
parent: null
priority: medium
status: todo
type: stream_processor
updated: '2026-02-01T03:29:42.332798'
version: 1
---

# User Churn Predictor

## Description

Predict user churn based on activity patterns.

## Metadata

**input:** user.* + ride.* events

**output:** Churn risk scores

**window:** 30 day sliding

