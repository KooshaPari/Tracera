---
id: ALERT-010
type: alert_rule
title: Database Replica Lag
status: active
created_at: 2026-01-31T20:29:13.391828
---

# Database Replica Lag

## Description
Database replica lag >60 seconds

## Metadata
```yaml
category: infrastructure
condition: replica_lag_seconds > 60
evaluation_period: 2m
notification_channels: DBA Team
severity: critical

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
