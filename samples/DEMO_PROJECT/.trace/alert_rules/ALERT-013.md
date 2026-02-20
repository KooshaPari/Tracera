---
id: ALERT-013
type: alert_rule
title: High Latency Api Gateway
status: active
created_at: 2026-01-31T20:29:13.399449
---

# High Latency Api Gateway

## Description
API Gateway latency >500ms

## Metadata
```yaml
category: performance
condition: api_gateway_latency > 500
evaluation_period: 10m
notification_channels: 'Slack #performance'
severity: warning

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
