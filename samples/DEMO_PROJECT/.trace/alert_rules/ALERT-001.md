---
id: ALERT-001
type: alert_rule
title: Payment Failures Exceed 5 Percent
status: active
created_at: 2026-01-31T20:29:13.233044
---

# Payment Failures Exceed 5 Percent

## Description
Payment failure rate exceeds 5%

## Metadata
```yaml
category: payment
condition: payment_failure_rate > 5
datapoints_to_alarm: 2
evaluation_period: 5m
notification_channels: 'PagerDuty + Slack #incidents'
severity: critical

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
