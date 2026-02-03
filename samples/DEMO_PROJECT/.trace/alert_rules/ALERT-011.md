---
id: ALERT-011
type: alert_rule
title: Redis Cluster Down
status: active
created_at: 2026-01-31T20:29:13.393880
---

# Redis Cluster Down

## Description
Redis cluster unavailable

## Metadata
```yaml
category: infrastructure
condition: redis_available_nodes < 2
evaluation_period: 2m
notification_channels: Platform Team + PagerDuty
severity: critical

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
