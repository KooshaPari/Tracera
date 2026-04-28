# TraceRTM Kubernetes Deployment

This directory contains Kubernetes manifests for deploying TraceRTM to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster (v1.25+)
- kubectl configured to access your cluster
- Docker registry (optional, for custom images)
- Storage class configured for PersistentVolumeClaims
- (Optional) Ingress controller (e.g., nginx-ingress)
- (Optional) cert-manager for TLS certificates

## Quick Start

### Deploy Everything

```bash
# From the root of the repository
./scripts/deploy.sh all
```

### Deploy Step by Step

```bash
# 1. Build and push images (optional)
DOCKER_REGISTRY=your-registry.com IMAGE_TAG=v1.0.0 ./scripts/deploy.sh push

# 2. Deploy infrastructure
./scripts/deploy.sh infra

# 3. Deploy application
./scripts/deploy.sh app

# 4. Deploy network policies
./scripts/deploy.sh network

# 5. Deploy ingress
./scripts/deploy.sh ingress

# 6. Run database migrations
./scripts/deploy.sh migrate

# 7. Check status
./scripts/deploy.sh status
```

## Directory Structure

```
k8s/
├── README.md                    # This file
├── namespace.yaml              # Namespace definition
├── configmap.yaml              # Application configuration
├── secret.yaml                 # Secrets (credentials, tokens)
├── postgres-deployment.yaml    # PostgreSQL database
├── redis-deployment.yaml       # Redis cache
├── nats-deployment.yaml        # NATS message broker
├── backend-deployment.yaml     # Go backend service
├── api-deployment.yaml         # Python API service
├── ingress.yaml                # Ingress configuration
└── networkpolicy.yaml          # Network policies
```

## Configuration

### Secrets

Before deploying, update the secrets in `k8s/secret.yaml`:

```yaml
# Database credentials
DB_PASSWORD: "your-secure-password"
POSTGRES_PASSWORD: "your-secure-password"

# JWT secret
JWT_SECRET: "your-jwt-secret-key"

# Admin credentials
ADMIN_PASSWORD: "your-admin-password"
```

**IMPORTANT**: Never commit real secrets to Git. Use environment-specific secret management.

### ConfigMap

Update the ConfigMap in `k8s/configmap.yaml` for your environment:

```yaml
# Application configuration
LOG_LEVEL: "INFO"  # DEBUG, INFO, WARNING, ERROR
GIN_MODE: "release"  # debug, release, test
```

### Ingress

Update the ingress hosts in `k8s/ingress.yaml`:

```yaml
spec:
  tls:
  - hosts:
    - api.tracertm.example.com      # Replace with your domain
    - backend.tracertm.example.com  # Replace with your domain
```

## Deployment Options

### Local Development (Minikube/Kind)

```bash
# Use local images without pushing to registry
./scripts/deploy.sh all
```

### Staging Environment

```bash
# Deploy to staging namespace with specific image tag
NAMESPACE=tracertm-staging \
IMAGE_TAG=develop-abc123 \
DOCKER_REGISTRY=registry.example.com \
./scripts/deploy.sh all
```

### Production Environment

```bash
# Deploy to production with specific context
KUBE_CONTEXT=production-cluster \
NAMESPACE=tracertm \
IMAGE_TAG=v1.0.0 \
DOCKER_REGISTRY=registry.example.com \
./scripts/deploy.sh all
```

## Scaling

### Manual Scaling

```bash
# Scale API pods
kubectl scale deployment tracertm-api -n tracertm --replicas=5

# Scale backend pods
kubectl scale deployment tracertm-backend -n tracertm --replicas=5
```

### Auto-scaling

The deployment includes HorizontalPodAutoscaler (HPA) that automatically scales based on CPU and memory usage:

- Min replicas: 3
- Max replicas: 10
- CPU threshold: 70%
- Memory threshold: 80%

View HPA status:

```bash
kubectl get hpa -n tracertm
```

## Monitoring

### Pod Status

```bash
# Get all pods
kubectl get pods -n tracertm

# Get pod details
kubectl describe pod <pod-name> -n tracertm

# View pod logs
kubectl logs <pod-name> -n tracertm

# Follow pod logs
kubectl logs -f <pod-name> -n tracertm
```

### Service Status

```bash
# Get all services
kubectl get svc -n tracertm

# Get service details
kubectl describe svc tracertm-api -n tracertm
```

### Ingress Status

```bash
# Get ingress
kubectl get ingress -n tracertm

# Get ingress details
kubectl describe ingress tracertm-ingress -n tracertm
```

## Database Management

### Run Migrations

```bash
# Run migrations using the deploy script
./scripts/deploy.sh migrate

# Or manually
API_POD=$(kubectl get pod -n tracertm -l app=tracertm-api -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n tracertm $API_POD -- alembic upgrade head
```

### Access Database

```bash
# Port-forward to PostgreSQL
kubectl port-forward -n tracertm svc/postgres 5432:5432

# Connect using psql
psql -h localhost -p 5432 -U tracertm -d tracertm
```

### Backup Database

```bash
# Create a backup
POSTGRES_POD=$(kubectl get pod -n tracertm -l app=postgres -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n tracertm $POSTGRES_POD -- pg_dump -U tracertm tracertm > backup.sql

# Restore from backup
cat backup.sql | kubectl exec -i -n tracertm $POSTGRES_POD -- psql -U tracertm tracertm
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n tracertm

# Check pod logs
kubectl logs <pod-name> -n tracertm

# Check init container logs
kubectl logs <pod-name> -n tracertm -c <init-container-name>
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
POSTGRES_POD=$(kubectl get pod -n tracertm -l app=postgres -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POSTGRES_POD -n tracertm

# Test database connectivity
kubectl exec -n tracertm $POSTGRES_POD -- pg_isready -U tracertm
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n tracertm

# Test service from within cluster
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
# Inside the pod:
apk add curl
curl http://tracertm-api.tracertm.svc.cluster.local/health
```

### Network Policy Issues

```bash
# Temporarily remove network policies for testing
kubectl delete networkpolicy --all -n tracertm

# Re-apply after testing
kubectl apply -f k8s/networkpolicy.yaml
```

## Clean Up

### Delete Everything

```bash
# Delete namespace (removes all resources)
kubectl delete namespace tracertm

# Delete persistent volumes (if needed)
kubectl delete pvc --all -n tracertm
```

### Delete Specific Components

```bash
# Delete application only
kubectl delete -f k8s/api-deployment.yaml
kubectl delete -f k8s/backend-deployment.yaml

# Delete infrastructure
kubectl delete -f k8s/postgres-deployment.yaml
kubectl delete -f k8s/redis-deployment.yaml
kubectl delete -f k8s/nats-deployment.yaml
```

## Security Considerations

1. **Secrets Management**: Use a secret management solution like HashiCorp Vault or AWS Secrets Manager
2. **Network Policies**: Review and customize network policies for your security requirements
3. **RBAC**: Implement Role-Based Access Control for API access
4. **Image Scanning**: Scan container images for vulnerabilities before deployment
5. **TLS**: Use cert-manager to automatically manage TLS certificates
6. **Pod Security**: Review pod security contexts and implement PodSecurityPolicies/PodSecurityStandards

## Performance Tuning

### Resource Limits

Adjust resource requests and limits based on your workload:

```yaml
resources:
  requests:
    cpu: 500m      # Guaranteed CPU
    memory: 512Mi  # Guaranteed memory
  limits:
    cpu: 2000m     # Maximum CPU
    memory: 2Gi    # Maximum memory
```

### Database Performance

```bash
# Increase PostgreSQL shared_buffers
# Edit postgres-deployment.yaml and add:
command:
  - postgres
  - -c
  - shared_buffers=256MB
  - -c
  - max_connections=200
```

### Redis Performance

```bash
# Configure Redis maxmemory
# Edit redis-deployment.yaml and add:
command:
  - redis-server
  - --maxmemory
  - 512mb
  - --maxmemory-policy
  - allkeys-lru
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/tracertm/issues
- Documentation: https://docs.tracertm.example.com
