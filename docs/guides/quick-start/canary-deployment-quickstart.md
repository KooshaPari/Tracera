# Canary Deployment Quick Start Guide

Get started with automated canary deployments in 5 minutes.

## Prerequisites

- Kubernetes cluster with kubectl access
- NGINX Ingress Controller installed
- Prometheus for metrics monitoring
- `jq` and `curl` command-line tools

## Quick Deploy

### 1. Validate Environment

```bash
export NAMESPACE=tracertm
export IMAGE_TAG=v1.2.3

./scripts/canary/validate-canary.sh
```

### 2. Deploy via Script

```bash
export CANARY_IMAGE_TAG=v1.2.3
export PROMETHEUS_URL=http://prometheus:9090

./scripts/canary/canary-deploy.sh
```

### 3. Deploy via GitHub Actions

```bash
gh workflow run canary-deploy.yml \
  -f image_tag=v1.2.3 \
  -f auto_promote=true
```

## What Happens

1. **Deploy** (2 min) - Canary pods start with new version
2. **Stage 1** (5 min) - 10% traffic, health monitoring
3. **Stage 2** (5 min) - 50% traffic, continued monitoring
4. **Promote** (3 min) - Update stable, cleanup canary

**Total Time**: ~10 minutes

## Monitor Progress

### Check Canary Status
```bash
kubectl get pods -n tracertm -l version=canary
```

### View Metrics
```bash
./scripts/canary/canary-metrics.sh
```

### Check Traffic Weight
```bash
kubectl get ingress tracertm-ingress-canary -n tracertm \
  -o jsonpath='{.metadata.annotations.nginx\.ingress\.kubernetes\.io/canary-weight}'
```

## Manual Testing

Test canary version before promotion:

```bash
# Route request to canary
curl -H "X-Canary: always" https://your-domain.com/health

# Check canary health
curl -H "X-Canary: always" https://your-domain.com/health/canary
```

## Emergency Rollback

If issues are detected:

```bash
./scripts/canary/canary-rollback.sh
```

Rollback completes in <60 seconds.

## Success Criteria

Canary must meet these thresholds:

- Error rate: <1%
- P95 latency: <500ms
- P99 latency: <1000ms
- Success rate: >99%
- No pod crashes

If any metric fails, automatic rollback occurs.

## Common Commands

```bash
# Apply base resources
kubectl apply -f k8s/base/ -n tracertm

# Apply canary deployment
kubectl apply -f k8s/overlays/canary/ -n tracertm

# Update canary image
kubectl set image deployment/tracertm-api-canary \
  api=tracertm-api:v1.2.3 -n tracertm

# Set traffic weight manually
kubectl patch ingress tracertm-ingress-canary -n tracertm \
  --type=json \
  -p='[{"op": "replace", "path": "/metadata/annotations/nginx.ingress.kubernetes.io~1canary-weight", "value": "25"}]'

# Scale canary down
kubectl scale deployment tracertm-api-canary -n tracertm --replicas=0
```

## Troubleshooting

### Canary pods not starting
```bash
kubectl describe pod -n tracertm -l version=canary
kubectl logs -n tracertm -l version=canary --tail=50
```

### No traffic reaching canary
```bash
kubectl describe ingress tracertm-ingress-canary -n tracertm
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller --tail=50
```

### Metrics not available
```bash
kubectl get servicemonitor -n tracertm
kubectl port-forward -n tracertm svc/prometheus 9090:9090
# Visit http://localhost:9090
```

## Next Steps

- Review full documentation: `scripts/canary/README.md`
- Customize thresholds: `k8s/base/configmap.yaml`
- Set up alerts: `k8s/base/prometheusrule.yaml`
- Configure CI/CD: `.github/workflows/canary-deploy.yml`

## Architecture

```
Ingress → Traffic Split (10%/50%/100%)
  ├─ Canary Pods (new version)
  └─ Stable Pods (current version)
       ↓
  Prometheus monitors both
       ↓
  Auto-promote or rollback
```

## Best Practices

1. **Test in staging first** - Always validate canary in non-production
2. **Monitor actively** - Watch metrics during deployment
3. **Document changes** - Track what's being deployed
4. **Use headers for testing** - Test canary manually before promotion
5. **Keep rollback ready** - Have emergency rollback accessible

## Support

- Full docs: `scripts/canary/README.md`
- Completion report: `docs/reports/task-109-canary-deployment-system-completion.md`
- Health endpoints: `/health`, `/health/canary`, `/health/readiness`
