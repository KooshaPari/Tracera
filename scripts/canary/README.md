# Canary Deployment Scripts

Automated canary deployment system with progressive traffic shifting and automatic rollback.

## Overview

The canary deployment system progressively shifts traffic from stable to canary deployments:
- **Stage 1**: 10% traffic for 5 minutes
- **Stage 2**: 50% traffic for 5 minutes
- **Stage 3**: 100% traffic (promotion)

At each stage, automated health checks monitor:
- Error rate (<1%)
- P95 latency (<500ms)
- P99 latency (<1000ms)
- Success rate (>99%)
- Pod health and restarts

If any check fails, automatic rollback is triggered.

## Scripts

### canary-deploy.sh

Main deployment script that orchestrates the entire canary deployment process.

**Usage:**
```bash
export NAMESPACE=tracertm
export CANARY_IMAGE_TAG=v1.2.3
export PROMETHEUS_URL=http://prometheus:9090

./scripts/canary/canary-deploy.sh
```

**Environment Variables:**
- `NAMESPACE` - Kubernetes namespace (default: tracertm)
- `CANARY_IMAGE_TAG` - Image tag to deploy as canary (required)
- `PROMETHEUS_URL` - Prometheus URL for metrics (default: http://prometheus:9090)
- `CHECK_INTERVAL` - Seconds between health checks (default: 60)
- `PROMOTION_THRESHOLD_DURATION` - Duration at each stage (default: 300)

**Features:**
- Progressive traffic shifting (10% → 50% → 100%)
- Automated health monitoring at each stage
- Automatic rollback on failure
- Pod health verification
- Prometheus metrics validation

### canary-metrics.sh

Real-time metrics analysis comparing canary vs stable versions.

**Usage:**
```bash
export NAMESPACE=tracertm
export PROMETHEUS_URL=http://prometheus:9090
export LOOKBACK=5m

./scripts/canary/canary-metrics.sh
```

**Output:**
- Error rate comparison
- Latency comparison (P95, P99)
- Request rate
- Success rate
- Active alerts
- Pod status

### canary-rollback.sh

Emergency rollback script for immediate canary termination.

**Usage:**
```bash
export NAMESPACE=tracertm

./scripts/canary/canary-rollback.sh
```

**Actions:**
- Sets canary traffic weight to 0
- Scales canary deployments to 0 replicas
- Verifies stable deployment health
- Ensures all traffic routes to stable

## GitHub Actions Workflow

The canary deployment can be triggered via GitHub Actions:

```yaml
# Manual trigger
gh workflow run canary-deploy.yml \
  -f image_tag=v1.2.3 \
  -f auto_promote=true
```

**Workflow Stages:**
1. **Validate** - Verify image tag and cluster access
2. **Deploy Canary** - Deploy canary version
3. **Stage 1 (10%)** - Monitor with 10% traffic
4. **Stage 2 (50%)** - Monitor with 50% traffic
5. **Promote** - Promote to stable (if auto_promote=true)
6. **Rollback** - Automatic rollback on any failure

## Success Metrics

Canary must meet these thresholds at each stage:

| Metric | Threshold | Description |
|--------|-----------|-------------|
| Error Rate | <1% | 5xx errors / total requests |
| P95 Latency | <500ms | 95th percentile response time |
| P99 Latency | <1000ms | 99th percentile response time |
| Success Rate | >99% | Non-5xx responses / total |
| Pod Restarts | ≤2 | Container restart count |
| Pod Ready Ratio | 100% | Ready pods / total pods |

## Monitoring

Prometheus metrics tracked:
- `tracertm:canary:error_rate`
- `tracertm:canary:latency_p95`
- `tracertm:canary:latency_p99`
- `tracertm:canary:success_rate`
- `tracertm:canary:request_rate`

Alerts:
- `CanaryHighErrorRate` - Error rate >1% for 2m
- `CanaryHighLatency` - P95 latency >500ms for 2m
- `CanaryPodCrashing` - >2 restarts in 5m
- `CanaryPodNotReady` - Not all pods ready for 2m

## Manual Operations

### Check canary status
```bash
kubectl get pods -n tracertm -l version=canary
kubectl get ingress -n tracertm tracertm-ingress-canary
```

### View canary traffic weight
```bash
kubectl get ingress tracertm-ingress-canary -n tracertm \
  -o jsonpath='{.metadata.annotations.nginx\.ingress\.kubernetes\.io/canary-weight}'
```

### Manually adjust traffic weight
```bash
# Set to 25%
kubectl patch ingress tracertm-ingress-canary -n tracertm \
  --type=json \
  -p='[{"op": "replace", "path": "/metadata/annotations/nginx.ingress.kubernetes.io~1canary-weight", "value": "25"}]'
```

### Force rollback
```bash
./scripts/canary/canary-rollback.sh
```

### Test canary with header
```bash
# Force traffic to canary
curl -H "X-Canary: always" https://tracertm.example.com/health
```

## Deployment Timeline

Typical canary deployment timeline:

```
0:00  - Deploy canary pods
0:02  - Canary pods ready
0:02  - Set traffic to 10%
0:02  - Monitor (5 minutes)
0:07  - Set traffic to 50%
0:07  - Monitor (5 minutes)
0:12  - Promote to stable
0:12  - Stable rollout begins
0:22  - Stable rollout complete
0:22  - Scale down canary
```

**Total Time: ~10 minutes** (excluding stable rollout)

## Troubleshooting

### Canary pods not starting
```bash
kubectl describe pod -n tracertm -l version=canary
kubectl logs -n tracertm -l version=canary
```

### Metrics not available
```bash
# Check Prometheus
kubectl port-forward -n tracertm svc/prometheus 9090:9090
# Visit http://localhost:9090

# Check ServiceMonitor
kubectl get servicemonitor -n tracertm
```

### Traffic not routing to canary
```bash
# Check ingress configuration
kubectl describe ingress tracertm-ingress-canary -n tracertm

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

### Rollback not working
```bash
# Manual cleanup
kubectl scale deployment tracertm-api-canary -n tracertm --replicas=0
kubectl scale deployment tracertm-backend-canary -n tracertm --replicas=0
kubectl patch ingress tracertm-ingress-canary -n tracertm \
  --type=json \
  -p='[{"op": "replace", "path": "/metadata/annotations/nginx.ingress.kubernetes.io~1canary-weight", "value": "0"}]'
```

## Best Practices

1. **Always test in staging first** - Validate canary deployment in staging environment
2. **Monitor actively** - Watch metrics during deployment
3. **Have rollback ready** - Keep rollback script accessible
4. **Gradual rollout** - Don't skip stages
5. **Document changes** - Track what's being deployed
6. **Alert on failures** - Configure Prometheus alerts
7. **Test with headers** - Use `X-Canary: always` header for manual testing

## Architecture

```
                                    ┌─────────────┐
                                    │   Ingress   │
                                    │  Controller │
                                    └──────┬──────┘
                                           │
                                    ┌──────┴──────┐
                                    │   Canary    │
                                    │   Weight    │
                                    └──────┬──────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        │                                      │
                  10% Traffic                            90% Traffic
                        │                                      │
                ┌───────▼────────┐                    ┌────────▼───────┐
                │     Canary     │                    │     Stable     │
                │  Deployments   │                    │  Deployments   │
                └────────────────┘                    └────────────────┘
                        │                                      │
                ┌───────┴────────┐                    ┌────────┴───────┐
                │   API v1.2.3   │                    │   API v1.2.2   │
                │ Backend v1.2.3 │                    │ Backend v1.2.2 │
                └────────────────┘                    └────────────────┘
```

## Health Check Endpoints

Enhanced health endpoints for canary deployments:

- `/health` - Standard health check
- `/health/canary` - Enhanced health with deployment info and metrics
- `/health/readiness` - Kubernetes readiness probe
- `/health/liveness` - Kubernetes liveness probe

## Metrics Collection

Canary-specific metrics are collected via:
- Prometheus ServiceMonitor
- Custom PrometheusRule for canary metrics
- Pod annotations for scraping

See `k8s/base/servicemonitor.yaml` and `k8s/base/prometheusrule.yaml`.
