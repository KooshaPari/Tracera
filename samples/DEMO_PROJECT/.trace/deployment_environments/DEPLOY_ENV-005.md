---
id: DEPLOY_ENV-005
type: deployment_environment
title: Production - ap-northeast-1
status: active
created_at: 2026-01-31T20:26:53.284904
---

# Production - ap-northeast-1

## Description
Production environment in ap-northeast-1 region with full HA setup

## Metadata
```yaml
auto_scaling: true
cache_clusters:
- redis-primary
- redis-replica
disaster_recovery: true
environment_type: production
ha_enabled: true
kubernetes_cluster: swiftride-prod-ap-northeast-1
rds_instances:
- primary
- replica-1
- replica-2
region: ap-northeast-1

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
