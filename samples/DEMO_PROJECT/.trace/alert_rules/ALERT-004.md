---
id: ALERT-004
type: alert_rule
title: Refund Spike
status: active
created_at: 2026-01-31T20:29:13.330853
---

# Refund Spike

## Description
Abnormal spike in refund requests

## Metadata
```yaml
category: payment
condition: refund_rate > 20
datapoints_to_alarm: 2
evaluation_period: 5m
notification_channels: Finance Team + Slack
severity: critical

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
