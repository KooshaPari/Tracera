---
id: ALERT-002
type: alert_rule
title: Payment Gateway Down
status: active
created_at: 2026-01-31T20:29:13.236960
---

# Payment Gateway Down

## Description
Payment gateway unreachable

## Metadata
```yaml
category: payment
condition: payment_gateway_latency > 30000 OR payment_gateway_errors > 10
datapoints_to_alarm: 2
evaluation_period: 5m
notification_channels: PagerDuty + SMS
severity: critical

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
