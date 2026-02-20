# Kubernetes Configuration for TraceRTM

This directory contains Kubernetes configurations for deploying TraceRTM with canary deployment capabilities.

## Directory Structure

```
k8s/
├── base/                          # Base Kubernetes resources
│   ├── deployment.yaml            # Stable deployments
│   ├── service.yaml               # Service definitions
│   ├── ingress.yaml               # NGINX ingress with canary support
│   ├── servicemonitor.yaml        # Prometheus monitoring
│   ├── prometheusrule.yaml        # Metrics and alerts
│   └── configmap.yaml             # Configuration
├── overlays/
│   ├── canary/                    # Canary deployment overlay
│   │   └── deployment-canary.yaml # Canary-specific configs
│   └── production/                # Production overlay (future)
└── README.md                      # This file
```

## Quick Start

### Deploy Base Resources

```bash
# Create namespace
kubectl create namespace tracertm

# Apply base resources
kubectl apply -f base/ -n tracertm

# Verify deployment
kubectl get all -n tracertm
```

### Deploy Canary

```bash
# Apply canary overlay
kubectl apply -f overlays/canary/ -n tracertm

# Check canary pods
kubectl get pods -n tracertm -l version=canary

# View traffic weight
kubectl get ingress tracertm-ingress-canary -n tracertm \
  -o jsonpath='{.metadata.annotations.nginx\.ingress\.kubernetes\.io/canary-weight}'
```

## Components

### Deployments

**Stable Deployments** (`base/deployment.yaml`):
- `tracertm-api` - Python FastAPI backend (3 replicas)
- `tracertm-backend` - Go backend service (3 replicas)

**Canary Deployments** (`overlays/canary/deployment-canary.yaml`):
- `tracertm-api-canary` - Canary version (1 replica)
- `tracertm-backend-canary` - Canary version (1 replica)

### Services

- `tracertm-api` - Main API service
- `tracertm-api-stable` - Stable version selector
- `tracertm-api-canary` - Canary version selector
- `tracertm-backend` - Main backend service
- `tracertm-backend-stable` - Stable version selector
- `tracertm-backend-canary` - Canary version selector

### Ingress

**Main Ingress** (`tracertm-ingress`):
- Routes traffic to stable deployments
- TLS termination
- Path-based routing

**Canary Ingress** (`tracertm-ingress-canary`):
- Progressive traffic splitting
- Weight-based routing (configurable)
- Header-based routing for testing

### Monitoring

**ServiceMonitor**:
- Automatic Prometheus scraping
- 30-second scrape interval
- Metrics from both stable and canary

**PrometheusRule**:
- Recording rules for canary metrics
- Alert rules for failures
- Comparison metrics (canary vs stable)

## Traffic Management

### Traffic Splitting Stages

```
Stage 1: 10% canary, 90% stable (5 minutes)
Stage 2: 50% canary, 50% stable (5 minutes)
Stage 3: 100% stable (promoted canary)
```

### Manual Traffic Control

Set canary traffic weight:
```bash
kubectl patch ingress tracertm-ingress-canary -n tracertm \
  --type=json \
  -p='[{"op": "replace", "path": "/metadata/annotations/nginx.ingress.kubernetes.io~1canary-weight", "value": "25"}]'
```

### Header-Based Testing

Test canary with header:
```bash
curl -H "X-Canary: always" https://your-domain.com/health
```

## Health Checks

All deployments include:

**Liveness Probe**:
- Path: `/health/liveness`
- Initial delay: 30s
- Period: 10s

**Readiness Probe**:
- Path: `/health/readiness`
- Initial delay: 10s
- Period: 5s

**Startup Probe**:
- Path: `/health`
- Failure threshold: 12
- Period: 5s

## Secrets

Required secrets in the namespace:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tracertm-secrets
type: Opaque
data:
  database-url: <base64-encoded>
  redis-url: <base64-encoded>
  nats-url: <base64-encoded>
  db-name: <base64-encoded>
  db-user: <base64-encoded>
  db-password: <base64-encoded>
```

Create secrets:
```bash
kubectl create secret generic tracertm-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=redis-url='redis://...' \
  --from-literal=nats-url='nats://...' \
  -n tracertm
```

## Monitoring

View metrics in Prometheus:
```bash
# Port forward to Prometheus
kubectl port-forward -n tracertm svc/prometheus 9090:9090

# Access: http://localhost:9090
```

Key metrics:
- `tracertm:canary:error_rate`
- `tracertm:canary:latency_p95`
- `tracertm:canary:success_rate`

## Scaling

### Manual Scaling

```bash
# Scale stable deployment
kubectl scale deployment tracertm-api -n tracertm --replicas=5

# Scale canary deployment
kubectl scale deployment tracertm-api-canary -n tracertm --replicas=2
```

### Auto-scaling

HPA example:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tracertm-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tracertm-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n tracertm
kubectl describe pod <pod-name> -n tracertm
kubectl logs <pod-name> -n tracertm
```

### Check Ingress
```bash
kubectl describe ingress -n tracertm
kubectl get ingress -n tracertm -o yaml
```

### Check Services
```bash
kubectl get svc -n tracertm
kubectl describe svc tracertm-api -n tracertm
```

### Check Metrics
```bash
# Check ServiceMonitor
kubectl get servicemonitor -n tracertm

# Check PrometheusRule
kubectl get prometheusrule -n tracertm
```

## Canary Deployment

For automated canary deployments, see:
- **Scripts**: `../scripts/canary/`
- **Workflow**: `../.github/workflows/canary-deploy.yml`
- **Documentation**: `../docs/guides/quick-start/canary-deployment-quickstart.md`

Quick deploy:
```bash
cd ../scripts/canary
export CANARY_IMAGE_TAG=v1.2.3
./canary-deploy.sh
```

## Best Practices

1. **Always test in staging first**
2. **Use readiness probes** for zero-downtime deployments
3. **Set resource limits** to prevent resource exhaustion
4. **Monitor metrics** during deployments
5. **Use secrets** for sensitive data
6. **Enable auto-scaling** for production
7. **Configure alerts** for critical issues

## Dependencies

Required in cluster:
- NGINX Ingress Controller
- Prometheus Operator (optional, for ServiceMonitor)
- cert-manager (for TLS)

## Support

- Full canary guide: `../scripts/canary/README.md`
- Architecture: `../docs/guides/canary-deployment-architecture.md`
- Completion report: `../docs/reports/task-109-canary-deployment-system-completion.md`
