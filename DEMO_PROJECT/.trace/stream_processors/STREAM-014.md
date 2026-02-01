---
created: '2026-02-01T03:29:42.326373'
external_id: STREAM-014
id: e623a925-c441-47e0-b92d-9ea96816b6be
links: []
owner: null
parent: null
priority: high
status: todo
type: stream_processor
updated: '2026-02-01T03:29:42.326373'
version: 1
---

# Driver Rating Aggregator

## Description

Calculate rolling average driver rating.

## Metadata

**input:** ride.rating_submitted stream

**output:** Current rating

**window:** 100 rides

