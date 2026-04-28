---
id: ALERT-012
type: alert_rule
title: Api Gateway 5Xx Errors
status: active
created_at: 2026-01-31T20:29:13.394340
---

# Api Gateway 5Xx Errors

## Description
API Gateway 5xx error rate >5%

## Metadata
```yaml
category: infrastructure
condition: api_5xx_error_rate > 5
evaluation_period: 2m
notification_channels: Platform + PagerDuty
severity: critical

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
