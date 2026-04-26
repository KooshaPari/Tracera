# Infrastructure Configs

Parameterized infrastructure configurations.

## Purpose
Standardized Docker, Kubernetes, and Terraform configurations.

## Structure
```
configs/infra/
├── docker/
│   ├── Dockerfile.base    # Base image
│   └── docker-compose.yml
├── kubernetes/
│   ├── deployment.yaml
│   └── service.yaml
└── terraform/
    └── modules/
```

## Docker Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `IMAGE_NAME` | Docker image name | `$PROJECT_NAME` |
| `BUILD_ARGS` | Build arguments | none |
| `PORTS` | Exposed ports | none |

## Kubernetes Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `NAMESPACE` | K8s namespace | `default` |
| `REPLICAS` | Pod replicas | `1` |
| `RESOURCES` | CPU/memory limits | none |

## Usage
```bash
# Build Docker image
docker build -f configs/infra/docker/Dockerfile.base .

# Apply K8s config
kubectl apply -f configs/infra/kubernetes/deployment.yaml
```

## Related
- [scripts/build/](../scripts/build/) - Build scripts
- [security/hardening/](../security/hardening/) - Container hardening
