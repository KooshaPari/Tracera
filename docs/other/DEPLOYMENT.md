# TraceRTM Deployment Guide

This guide covers deploying TraceRTM in various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Compose](#docker-compose)
- [Kubernetes](#kubernetes)
- [Production Deployment](#production-deployment)
- [CI/CD](#cicd)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- **Docker** (v20.10+)
- **Docker Compose** (v2.0+)
- **kubectl** (v1.25+) - for Kubernetes deployments
- **Git**

### Optional Tools

- **Helm** - for Kubernetes package management
- **Terraform** - for infrastructure as code
- **uv** or **pip** - for Python development
- **Go** (v1.23+) - for Go backend development

## Local Development

### Using Docker Compose (Recommended)

1. **Clone the repository**

```bash
git clone https://github.com/your-org/tracertm.git
cd tracertm
```

2. **Start all services**

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

3. **Verify services are running**

```bash
docker-compose ps
```

4. **Access services**

- Python API: http://localhost:8000
- Go Backend: http://localhost:8080
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- NATS: localhost:4222
- Adminer (DB UI): http://localhost:8081
- Redis Commander: http://localhost:8082
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

5. **View logs**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f backend
```

6. **Stop services**

```bash
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v
```

### Manual Development Setup

#### Python API

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Set up database
export DATABASE_URL="postgresql+asyncpg://tracertm:tracertm_password@localhost:5432/tracertm"
alembic upgrade head

# Run the API
uvicorn tracertm.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Go Backend

```bash
cd backend

# Install dependencies
go mod download

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=tracertm
export DB_PASSWORD=tracertm_password
export DB_NAME=tracertm
export REDIS_URL=redis://localhost:6379
export NATS_URL=nats://localhost:4222

# Run the backend
go run main.go
```

## Docker Compose

### Production-like Setup

1. **Create environment file**

```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Build and start services**

```bash
docker-compose up -d --build
```

3. **Run database migrations**

```bash
docker-compose exec api alembic upgrade head
```

4. **Create admin user**

```bash
docker-compose exec api python -m tracertm.cli create-admin
```

### Development Setup with Hot Reload

```bash
# Use development compose file
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Backend and API will auto-reload on code changes
```

## Kubernetes

### Prerequisites

- Kubernetes cluster (v1.25+)
- kubectl configured
- Storage class configured
- (Optional) Ingress controller
- (Optional) cert-manager for TLS

### Quick Deploy

```bash
# Deploy everything
./scripts/deploy.sh all
```

### Step-by-Step Deploy

#### 1. Build and Push Images

```bash
# Build images
docker build -t tracertm-api:v1.0.0 .
docker build -t tracertm-backend:v1.0.0 backend/

# Tag for registry
docker tag tracertm-api:v1.0.0 your-registry.com/tracertm-api:v1.0.0
docker tag tracertm-backend:v1.0.0 your-registry.com/tracertm-backend:v1.0.0

# Push to registry
docker push your-registry.com/tracertm-api:v1.0.0
docker push your-registry.com/tracertm-backend:v1.0.0

# Or use the deploy script
DOCKER_REGISTRY=your-registry.com IMAGE_TAG=v1.0.0 ./scripts/deploy.sh push
```

#### 2. Update Secrets

Edit `k8s/secret.yaml` and update with your secrets:

```yaml
stringData:
  DB_PASSWORD: "your-secure-password"
  JWT_SECRET: "your-jwt-secret"
  # ... other secrets
```

Or create secrets from command line:

```bash
kubectl create secret generic tracertm-secrets \
  --from-literal=DB_PASSWORD=your-secure-password \
  --from-literal=JWT_SECRET=your-jwt-secret \
  -n tracertm
```

#### 3. Update ConfigMap

Edit `k8s/configmap.yaml` for your environment.

#### 4. Deploy Infrastructure

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/nats-deployment.yaml

# Wait for infrastructure to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n tracertm --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n tracertm --timeout=300s
kubectl wait --for=condition=ready pod -l app=nats -n tracertm --timeout=300s
```

#### 5. Deploy Application

```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/api-deployment.yaml

# Wait for application to be ready
kubectl wait --for=condition=ready pod -l app=tracertm-backend -n tracertm --timeout=300s
kubectl wait --for=condition=ready pod -l app=tracertm-api -n tracertm --timeout=300s
```

#### 6. Run Migrations

```bash
API_POD=$(kubectl get pod -n tracertm -l app=tracertm-api -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n tracertm $API_POD -- alembic upgrade head
```

#### 7. Deploy Ingress (Optional)

Update `k8s/ingress.yaml` with your domain names, then:

```bash
kubectl apply -f k8s/ingress.yaml
```

#### 8. Deploy Network Policies (Optional)

```bash
kubectl apply -f k8s/networkpolicy.yaml
```

### Verify Deployment

```bash
# Check all resources
kubectl get all -n tracertm

# Check pods
kubectl get pods -n tracertm

# Check services
kubectl get svc -n tracertm

# Check ingress
kubectl get ingress -n tracertm

# Check logs
kubectl logs -l app=tracertm-api -n tracertm --tail=100
kubectl logs -l app=tracertm-backend -n tracertm --tail=100
```

## Production Deployment

### Pre-deployment Checklist

- [ ] Update all secrets with strong, random values
- [ ] Configure TLS certificates (cert-manager or manual)
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy for database
- [ ] Set resource limits and requests appropriately
- [ ] Enable network policies
- [ ] Configure autoscaling
- [ ] Set up log aggregation
- [ ] Configure external DNS
- [ ] Review security policies

### Security Hardening

1. **Use strong secrets**

```bash
# Generate strong passwords
openssl rand -base64 32

# Generate JWT secret
openssl rand -hex 64
```

2. **Enable TLS**

Install cert-manager and configure TLS:

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create issuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

3. **Network Policies**

Ensure network policies are deployed and tested:

```bash
kubectl apply -f k8s/networkpolicy.yaml
```

4. **Pod Security**

Use Pod Security Standards:

```bash
kubectl label namespace tracertm pod-security.kubernetes.io/enforce=restricted
```

### Database Backup

Set up automated backups:

```bash
# Create backup CronJob
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: tracertm
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgres -U tracertm tracertm | gzip > /backup/tracertm-\$(date +%Y%m%d-%H%M%S).sql.gz
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: tracertm-secrets
                  key: DB_PASSWORD
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
EOF
```

## CI/CD

The project includes a GitHub Actions workflow for CI/CD. See `.github/workflows/ci.yml`.

### GitHub Secrets Required

Set these secrets in your GitHub repository:

- `KUBE_CONFIG_STAGING` - Base64 encoded kubeconfig for staging
- `KUBE_CONFIG_PRODUCTION` - Base64 encoded kubeconfig for production

```bash
# Encode kubeconfig
cat ~/.kube/config | base64 | pbcopy  # macOS
cat ~/.kube/config | base64 -w 0      # Linux
```

### Workflow Triggers

- **Push to main/develop** - Run tests and build images
- **Pull Request** - Run tests and security scans
- **Release** - Deploy to production

### Manual Deployment

You can trigger deployments manually from GitHub Actions.

## Monitoring

### Prometheus Metrics

Both services expose Prometheus metrics:

- API: `http://api:8000/metrics`
- Backend: `http://backend:8080/metrics`

### Grafana Dashboards

Access Grafana at http://localhost:3000 (or your ingress URL)

Default credentials:
- Username: admin
- Password: admin (change this!)

Import dashboards from `monitoring/grafana/dashboards/`

### Logs

```bash
# View logs from all pods
kubectl logs -l app=tracertm-api -n tracertm --tail=100 -f

# View logs from specific pod
kubectl logs <pod-name> -n tracertm -f

# Previous pod logs (if pod crashed)
kubectl logs <pod-name> -n tracertm --previous
```

## Troubleshooting

### Common Issues

#### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n tracertm

# Check events
kubectl get events -n tracertm --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n tracertm
```

#### Database Connection Failed

```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -- \
  psql -h postgres.tracertm.svc.cluster.local -U tracertm -d tracertm

# Check database pod
kubectl logs -l app=postgres -n tracertm
```

#### Services Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n tracertm

# Test service from within cluster
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
apk add curl
curl http://tracertm-api.tracertm.svc.cluster.local/health
```

#### Image Pull Errors

```bash
# Check if secret exists
kubectl get secret tracertm-registry-secret -n tracertm

# Create registry secret
kubectl create secret docker-registry tracertm-registry-secret \
  --docker-server=your-registry.com \
  --docker-username=username \
  --docker-password=password \
  --docker-email=email@example.com \
  -n tracertm
```

### Getting Help

- Check logs: `kubectl logs <pod-name> -n tracertm`
- Check events: `kubectl get events -n tracertm`
- Check pod status: `kubectl describe pod <pod-name> -n tracertm`
- Review deployment status: `./scripts/deploy.sh status`

For more help, see the [Kubernetes README](k8s/README.md).
