---
id: DEPLOY_ENV-002
type: deployment_environment
title: Production - us-west-2
status: active
created_at: 2026-01-31T20:26:53.281911
---

# Production - us-west-2

## Description
Production environment in us-west-2 region with full HA setup

## Metadata
```yaml
auto_scaling: true
cache_clusters:
- redis-primary
- redis-replica
disaster_recovery: true
environment_type: production
ha_enabled: true
kubernetes_cluster: swiftride-prod-us-west-2
rds_instances:
- primary
- replica-1
- replica-2
region: us-west-2

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
