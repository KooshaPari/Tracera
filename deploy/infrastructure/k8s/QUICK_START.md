# TraceRTM Kubernetes - Quick Start

**5-Minute Deployment Guide**

## Prerequisites Checklist

- [ ] Kubernetes cluster running (v1.24+)
- [ ] kubectl configured and authenticated
- [ ] Container images built and pushed
- [ ] Secrets updated (see below)

## Deployment in 5 Steps

### 1. Update Secrets (REQUIRED)

```bash
vi infrastructure/k8s/02-secrets.yaml
```

**MUST CHANGE:**
- `DATABASE_PASSWORD` → Strong random password
- `JWT_SECRET` → Random 32+ character string
- `WORKOS_API_KEY` → Your actual WorkOS key
- `WORKOS_CLIENT_ID` → Your actual WorkOS client ID
- `tls.crt` and `tls.key` → Valid TLS certificates

### 2. Update Image References

```bash
# Replace with your registry
export REGISTRY="your-registry.io/tracertm"

sed -i "s|tracertm/go-backend:latest|$REGISTRY/go-backend:v1.0.0|g" \
  infrastructure/k8s/06-go-backend.yaml

sed -i "s|tracertm/python-backend:latest|$REGISTRY/python-backend:v1.0.0|g" \
  infrastructure/k8s/07-python-backend.yaml
```

### 3. Validate

```bash
./scripts/validate_k8s.sh
```

### 4. Deploy

```bash
./scripts/deploy_k8s.sh
# Or specify context:
./scripts/deploy_k8s.sh my-prod-cluster
```

### 5. Verify

```bash
./scripts/health_check.sh tracertm
kubectl get all -n tracertm
```

## Get External IP

```bash
kubectl get svc nginx-service -n tracertm
# Wait for EXTERNAL-IP to be assigned
```

## Access Services

```bash
# Prometheus
kubectl port-forward svc/prometheus-service 9090:9090 -n tracertm
# http://localhost:9090

# Grafana (admin/admin)
kubectl port-forward svc/grafana-service 3000:3000 -n tracertm
# http://localhost:3000

# Go Backend (direct)
kubectl port-forward svc/go-backend-service 8080:8080 -n tracertm
# http://localhost:8080/health

# Python Backend (direct)
kubectl port-forward svc/python-backend-service 8000:8000 -n tracertm
# http://localhost:8000/health
```

## Common Operations

### View Logs

```bash
# All Go backend pods
kubectl logs -f -l app=go-backend -n tracertm

# All Python backend pods
kubectl logs -f -l app=python-backend -n tracertm

# Specific pod
kubectl logs -f <pod-name> -n tracertm

# Migration logs
kubectl logs deployment/python-backend -c migrations -n tracertm
```

### Scale Services

```bash
# Scale Go backend to 5 replicas
kubectl scale deployment/go-backend --replicas=5 -n tracertm

# Scale Python backend to 3 replicas
kubectl scale deployment/python-backend --replicas=3 -n tracertm

# View auto-scaling status
kubectl get hpa -n tracertm
```

### Update Configuration

```bash
# Edit config
kubectl edit configmap app-config -n tracertm

# Restart to apply changes
kubectl rollout restart deployment/go-backend -n tracertm
kubectl rollout restart deployment/python-backend -n tracertm
```

### Database Operations

```bash
# Connect to PostgreSQL
kubectl exec -it postgres-0 -n tracertm -- psql -U tracertm

# Backup database
kubectl exec -it postgres-0 -n tracertm -- \
  pg_dump -U tracertm -Fc tracertm > backup.dump

# Restore database
cat backup.dump | \
  kubectl exec -i postgres-0 -n tracertm -- \
  pg_restore -U tracertm -d tracertm --clean

# View backup jobs
kubectl get cronjob -n tracertm
```

### Troubleshooting

```bash
# Pod status
kubectl get pods -n tracertm

# Describe pod (events)
kubectl describe pod <pod-name> -n tracertm

# All events
kubectl get events -n tracertm --sort-by='.lastTimestamp'

# Resource usage
kubectl top pods -n tracertm
kubectl top nodes

# Shell into pod
kubectl exec -it <pod-name> -n tracertm -- /bin/sh

# Network connectivity test
kubectl run -it --rm debug --image=busybox -n tracertm -- sh
# Then: wget -O- http://go-backend-service:8080/health
```

## Resource Requirements

### Minimum (Testing)
- 3 nodes × 4 CPU, 16GB RAM
- 50GB storage

### Production (Recommended)
- 5 nodes × 8 CPU, 32GB RAM
- 200GB SSD storage

## Default Scaling

| Service | Min | Max | Trigger |
|---------|-----|-----|---------|
| Go Backend | 3 | 10 | 70% CPU / 80% Mem |
| Python Backend | 2 | 5 | 75% CPU / 85% Mem |
| Nginx | 2 | 5 | 70% CPU / 80% Mem |

## Security Checklist

Before production:

- [ ] All secrets updated (no CHANGE_ME)
- [ ] Valid TLS certificates configured
- [ ] Private container registry used
- [ ] Network policies enabled
- [ ] RBAC configured
- [ ] Resource limits set
- [ ] Image scanning enabled
- [ ] Backup tested

## Need Help?

- **Full Guide**: `/docs/deployment/kubernetes_guide.md`
- **Detailed README**: `/infrastructure/k8s/README.md`
- **Complete Summary**: `/KUBERNETES_DEPLOYMENT_COMPLETE.md`
- **Scripts**: `/scripts/deploy_k8s.sh`, `validate_k8s.sh`, `health_check.sh`

## Quick Commands Cheat Sheet

```bash
# Deploy everything
./scripts/deploy_k8s.sh

# Check health
./scripts/health_check.sh tracertm

# View all resources
kubectl get all -n tracertm

# Watch pods
kubectl get pods -n tracertm -w

# Logs (follow)
kubectl logs -f deployment/go-backend -n tracertm

# Scale
kubectl scale deployment/go-backend --replicas=5 -n tracertm

# Restart
kubectl rollout restart deployment/go-backend -n tracertm

# Status
kubectl rollout status deployment/go-backend -n tracertm

# Delete everything (careful!)
kubectl delete namespace tracertm
```

---

**Ready to deploy?** Start with step 1 above!
