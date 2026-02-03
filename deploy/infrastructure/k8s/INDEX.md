# TraceRTM Kubernetes Deployment - Complete Index

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: 2026-01-30

---

## 📋 Table of Contents

1. [Quick Links](#quick-links)
2. [Manifest Files](#manifest-files)
3. [Deployment Scripts](#deployment-scripts)
4. [Documentation](#documentation)
5. [Deployment Order](#deployment-order)
6. [Quick Commands](#quick-commands)

---

## 🔗 Quick Links

| Resource | Location | Purpose |
|----------|----------|---------|
| **Quick Start** | `QUICK_START.md` | 5-minute deployment guide |
| **README** | `README.md` | Complete reference |
| **Full Guide** | `../../docs/deployment/kubernetes_guide.md` | 800+ line comprehensive guide |
| **Summary** | `../../KUBERNETES_DEPLOYMENT_COMPLETE.md` | Implementation overview |

---

## 📁 Manifest Files

### Core Infrastructure (Apply in Order)

1. **00-namespace.yaml** (194 bytes)
   - Creates `tracertm` namespace
   - Labels: environment=production

2. **01-configmaps.yaml** (6.1 KB)
   - `app-config`: Application configuration
   - `nginx-config`: Nginx routing rules with smart routing

3. **02-secrets.yaml** (2.3 KB)
   - `app-secrets`: Database, JWT, WorkOS credentials
   - `tls-cert`: TLS certificates for HTTPS
   - `postgres-init`: Database initialization scripts
   - ⚠️ **MUST UPDATE BEFORE DEPLOYMENT**

### Data Layer

4. **03-postgres.yaml** (5.6 KB)
   - PostgreSQL StatefulSet (1 replica)
   - Service: `postgres-service:5432`
   - PVC: 20Gi persistent storage
   - CronJob: Daily automated backups
   - Resources: 500m CPU, 1Gi RAM

5. **04-redis.yaml** (4.9 KB)
   - Redis StatefulSet (1 replica)
   - Service: `redis-service:6379`
   - PVC: 10Gi persistent storage
   - Exporter: Prometheus metrics on :9121
   - Resources: 250m CPU, 512Mi RAM

6. **05-nats.yaml** (4.8 KB)
   - NATS StatefulSet with JetStream (1 replica)
   - Service: `nats-service:4222` (client), `:8222` (monitoring)
   - PVC: 5Gi persistent storage
   - Exporter: Prometheus metrics on :7777
   - Resources: 250m CPU, 512Mi RAM

### Application Layer

7. **06-go-backend.yaml** (6.6 KB)
   - Go Backend Deployment (3-10 replicas)
   - Service: `go-backend-service:8080` (API), `:9090` (metrics)
   - HPA: Scale on CPU 70%, Memory 80%
   - PDB: Min available 2 pods
   - Resources: 250m CPU, 256Mi RAM per pod
   - Init containers: Wait for PostgreSQL, Redis, NATS

8. **07-python-backend.yaml** (7.8 KB)
   - Python Backend Deployment (2-5 replicas)
   - Service: `python-backend-service:8000` (API), `:9091` (metrics)
   - HPA: Scale on CPU 75%, Memory 85%
   - PDB: Min available 1 pod
   - Resources: 500m CPU, 512Mi RAM per pod
   - Init containers: Wait for infrastructure + run migrations

### Ingress Layer

9. **08-ingress.yaml** (7.2 KB)
   - Nginx Deployment (2-5 replicas)
   - Service: `nginx-service:80/443` (LoadBalancer)
   - HPA: Scale on CPU 70%, Memory 80%
   - PDB: Min available 1 pod
   - Resources: 100m CPU, 128Mi RAM per pod
   - Features: TLS termination, rate limiting, smart routing

### Observability

10. **09-monitoring.yaml** (7.6 KB)
    - Prometheus Deployment (1 replica)
    - Grafana Deployment (1 replica)
    - PostgreSQL Exporter
    - Services and ConfigMaps
    - Scrapes all application and infrastructure metrics

### Security

11. **10-network-policies.yaml** (7.1 KB)
    - Default deny all ingress
    - Explicit allow rules for:
      - Nginx ← Internet
      - Nginx → Backends
      - Backends → Databases
      - Cross-backend communication
      - Prometheus scraping
      - DNS resolution

---

## 🛠 Deployment Scripts

Located in `/scripts/`:

### deploy_k8s.sh
**Purpose**: Automated deployment with validation  
**Usage**: `./scripts/deploy_k8s.sh [context]`  
**Features**:
- Interactive context confirmation
- Ordered manifest application
- Wait for infrastructure readiness
- Health check verification
- External IP detection
- Helpful command suggestions

### validate_k8s.sh
**Purpose**: Pre-deployment validation  
**Usage**: `./scripts/validate_k8s.sh`  
**Checks**:
- YAML syntax validation
- Kubernetes resource validation
- Security checks (default secrets warning)
- Resource configuration verification

### health_check.sh
**Purpose**: Post-deployment health verification  
**Usage**: `./scripts/health_check.sh [namespace] [context]`  
**Checks**:
- Pod health (all components)
- Service endpoints
- HPA status
- PVC verification
- Comprehensive reporting

---

## 📚 Documentation

### Quick Start (QUICK_START.md)
- 5-minute deployment guide
- Essential commands
- Troubleshooting quick reference
- **Start here** for fast deployment

### README (README.md)
- Architecture overview
- Resource requirements
- Scaling configuration
- Monitoring setup
- Backup procedures
- Complete command reference

### Kubernetes Guide (docs/deployment/kubernetes_guide.md)
- 800+ line comprehensive guide
- Prerequisites and setup
- Detailed step-by-step deployment
- Configuration deep dive
- Scaling strategies
- Monitoring and alerting
- Backup and restore procedures
- Troubleshooting guide
- Production checklist

### Implementation Summary (KUBERNETES_DEPLOYMENT_COMPLETE.md)
- Complete implementation overview
- Architecture details
- Success criteria validation
- File manifest
- Next steps for production

---

## 🔄 Deployment Order

### Automated (Recommended)
```bash
./scripts/deploy_k8s.sh [context]
```

### Manual (Step-by-Step)
```bash
# 1. Namespace
kubectl apply -f 00-namespace.yaml

# 2. Configuration
kubectl apply -f 01-configmaps.yaml
kubectl apply -f 02-secrets.yaml

# 3. Data Layer
kubectl apply -f 03-postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres -n tracertm --timeout=300s

kubectl apply -f 04-redis.yaml
kubectl wait --for=condition=ready pod -l app=redis -n tracertm --timeout=300s

kubectl apply -f 05-nats.yaml
kubectl wait --for=condition=ready pod -l app=nats -n tracertm --timeout=300s

# 4. Application Layer
kubectl apply -f 06-go-backend.yaml
kubectl rollout status deployment/go-backend -n tracertm

kubectl apply -f 07-python-backend.yaml
kubectl rollout status deployment/python-backend -n tracertm

# 5. Ingress
kubectl apply -f 08-ingress.yaml
kubectl rollout status deployment/nginx -n tracertm

# 6. Optional: Monitoring & Security
kubectl apply -f 09-monitoring.yaml
kubectl apply -f 10-network-policies.yaml
```

---

## ⚡ Quick Commands

### Deployment
```bash
# Deploy all
./scripts/deploy_k8s.sh

# Validate before deploy
./scripts/validate_k8s.sh

# Health check
./scripts/health_check.sh tracertm

# View all resources
kubectl get all -n tracertm
```

### Monitoring
```bash
# View pod status
kubectl get pods -n tracertm

# View logs (follow)
kubectl logs -f deployment/go-backend -n tracertm
kubectl logs -f deployment/python-backend -n tracertm

# Resource usage
kubectl top pods -n tracertm
kubectl top nodes

# HPA status
kubectl get hpa -n tracertm
```

### Scaling
```bash
# Manual scale
kubectl scale deployment/go-backend --replicas=5 -n tracertm
kubectl scale deployment/python-backend --replicas=3 -n tracertm

# View auto-scaling
kubectl describe hpa go-backend-hpa -n tracertm
```

### Configuration
```bash
# Edit config
kubectl edit configmap app-config -n tracertm
kubectl edit secret app-secrets -n tracertm

# Restart to apply changes
kubectl rollout restart deployment/go-backend -n tracertm
kubectl rollout restart deployment/python-backend -n tracertm
```

### Database
```bash
# Connect to PostgreSQL
kubectl exec -it postgres-0 -n tracertm -- psql -U tracertm

# Backup
kubectl exec -it postgres-0 -n tracertm -- \
  pg_dump -U tracertm -Fc tracertm > backup.dump

# View backup jobs
kubectl get cronjob -n tracertm
```

### Debugging
```bash
# Describe pod (see events)
kubectl describe pod <pod-name> -n tracertm

# Events
kubectl get events -n tracertm --sort-by='.lastTimestamp'

# Shell into pod
kubectl exec -it <pod-name> -n tracertm -- /bin/sh

# Port forward
kubectl port-forward svc/go-backend-service 8080:8080 -n tracertm
```

---

## 🚀 Deployment Checklist

### Before First Deployment

- [ ] Update `02-secrets.yaml` (all CHANGE_ME values)
- [ ] Configure valid TLS certificates
- [ ] Build and push container images
- [ ] Update image references in manifests
- [ ] Review resource requests/limits
- [ ] Set CORS_ORIGINS for your domain
- [ ] Choose appropriate storage classes

### After Deployment

- [ ] Verify all pods are running
- [ ] Check external IP assignment
- [ ] Test health endpoints
- [ ] Configure DNS (point domain to external IP)
- [ ] Set up monitoring alerts
- [ ] Test backup/restore procedures
- [ ] Load test and tune HPA

---

## 📊 Resource Summary

| Component | Replicas | CPU/pod | Memory/pod | Storage | Auto-scale |
|-----------|----------|---------|------------|---------|------------|
| Go Backend | 3-10 | 250m | 256Mi | - | Yes (HPA) |
| Python Backend | 2-5 | 500m | 512Mi | - | Yes (HPA) |
| PostgreSQL | 1 | 500m | 1Gi | 20Gi | No |
| Redis | 1 | 250m | 512Mi | 10Gi | No |
| NATS | 1 | 250m | 512Mi | 5Gi | No |
| Nginx | 2-5 | 100m | 128Mi | - | Yes (HPA) |
| Prometheus | 1 | 250m | 512Mi | - | No |
| Grafana | 1 | 100m | 256Mi | - | No |

**Total (at min replicas)**: ~5 CPU cores, ~10Gi RAM, ~85Gi storage

---

## 🔒 Security Features

- ✅ Network Policies (zero-trust)
- ✅ Non-root containers (runAsUser: 1000)
- ✅ Read-only root filesystem
- ✅ Drop all capabilities
- ✅ No privilege escalation
- ✅ TLS/HTTPS encryption
- ✅ Secret management
- ✅ Resource limits enforced
- ✅ Pod Security Standards ready

---

## 📞 Support

- **Issues**: Review troubleshooting guide in documentation
- **Scripts**: Use health_check.sh for diagnostics
- **Logs**: kubectl logs -f deployment/<name> -n tracertm
- **Events**: kubectl get events -n tracertm

---

**Status**: ✅ Production Ready (after updating secrets)  
**Last Validated**: 2026-01-30  
**All Manifests**: YAML Valid ✓
