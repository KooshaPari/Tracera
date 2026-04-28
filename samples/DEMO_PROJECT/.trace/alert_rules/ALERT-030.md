---
id: ALERT-030
type: alert_rule
title: Sla Latency Breach
status: active
created_at: 2026-01-31T20:29:13.413840
---

# Sla Latency Breach

## Description
P95 latency exceeds SLA

## Metadata
```yaml
category: sla
condition: p95_response_time > 1000
evaluation_period: 5m
notification_channels: Engineering + Product
severity: critical

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
