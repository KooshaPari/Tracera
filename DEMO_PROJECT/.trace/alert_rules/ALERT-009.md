---
id: ALERT-009
type: alert_rule
title: Database Primary Down
status: active
created_at: 2026-01-31T20:29:13.387766
---

# Database Primary Down

## Description
Primary database unreachable

## Metadata
```yaml
category: infrastructure
condition: database_connections == 0
evaluation_period: 2m
notification_channels: DBA Team + PagerDuty
severity: critical

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
