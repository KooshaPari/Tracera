---
id: PIPELINE-003
type: ci_cd_pipeline
title: payment-service - Build
status: active
created_at: 2026-01-31T20:31:54.007081
---

# payment-service - Build

## Description
Build pipeline for payment-service microservice

## Metadata
```yaml
docker_registry: ECR
pipeline_type: build
runtime: GitHub Actions
service: payment-service
stages:
- checkout
- test
- build
- scan
- publish
triggers:
- push to main
- pull request

```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
