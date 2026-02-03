---
id: ALERT-003
type: alert_rule
title: Fraud Detection High Risk
status: active
created_at: 2026-01-31T20:29:13.240382
---

# Fraud Detection High Risk

## Description
High number of fraud attempts detected

## Metadata
```yaml
category: payment
condition: fraud_detection_rate > 10
datapoints_to_alarm: 2
evaluation_period: 5m
notification_channels: Security Team + PagerDuty
severity: critical

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
