---
id: ALERT-006
type: alert_rule
title: Matching Service Down
status: active
created_at: 2026-01-31T20:29:13.370573
---

# Matching Service Down

## Description
Driver matching service unavailable

## Metadata
```yaml
category: matching
condition: matching_service_latency > 10000 OR errors > 50
evaluation_period: 3m
notification_channels: 'PagerDuty + Slack #oncall'
severity: critical

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
