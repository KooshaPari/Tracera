---
id: ALERT-014
type: alert_rule
title: High Latency Matching Service
status: active
created_at: 2026-01-31T20:29:13.400654
---

# High Latency Matching Service

## Description
Matching service latency >2s

## Metadata
```yaml
category: performance
condition: matching_service_latency > 2000
evaluation_period: 10m
notification_channels: 'Slack #performance'
severity: warning

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
