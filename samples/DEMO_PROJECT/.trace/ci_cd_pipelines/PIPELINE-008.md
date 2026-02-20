---
id: PIPELINE-008
type: ci_cd_pipeline
title: fraud-detection - Build
status: active
created_at: 2026-01-31T20:31:54.008933
---

# fraud-detection - Build

## Description
Build pipeline for fraud-detection microservice

## Metadata
```yaml
docker_registry: ECR
pipeline_type: build
runtime: GitHub Actions
service: fraud-detection
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
