---
id: ALERT-042
type: alert_rule
title: Aws Cost Spike
status: active
created_at: 2026-01-31T20:29:13.436437
---

# Aws Cost Spike

## Description
Daily AWS cost increased >30%

## Metadata
```yaml
category: cost
condition: aws_daily_cost_change > 30
evaluation_period: 1h
notification_channels: Finance + Engineering
severity: warning

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
