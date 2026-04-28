#!/bin/bash
set -euo pipefail

# TraceRTM Deployment Script
ENVIRONMENT="${1:-staging}"
VERSION="${2:-latest}"
NAMESPACE="tracertm-${ENVIRONMENT}"

echo "Deploying TraceRTM ${VERSION} to ${ENVIRONMENT}"

# Check prerequisites
command -v kubectl >/dev/null 2>&1 || { echo "kubectl required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "docker required"; exit 1; }

# Build images
docker build -t tracertm/backend:${VERSION} ./backend
docker build -t tracertm/frontend:${VERSION} ./frontend 2>/dev/null || true

# Create namespace
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Deploy components
kubectl apply -f k8s/configmap.yaml -n ${NAMESPACE}
kubectl apply -f k8s/secret.yaml -n ${NAMESPACE}
kubectl apply -f k8s/postgres-deployment.yaml -n ${NAMESPACE}
kubectl apply -f k8s/redis-deployment.yaml -n ${NAMESPACE}
kubectl apply -f k8s/nats-deployment.yaml -n ${NAMESPACE}
kubectl apply -f k8s/backend-deployment.yaml -n ${NAMESPACE}
kubectl apply -f k8s/api-deployment.yaml -n ${NAMESPACE}
kubectl apply -f k8s/ingress.yaml -n ${NAMESPACE}
kubectl apply -f k8s/hpa.yaml -n ${NAMESPACE}
kubectl apply -f k8s/monitoring.yaml -n ${NAMESPACE}

echo "Deployment complete!"
