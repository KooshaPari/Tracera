#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

NAMESPACE="tracertm"
CONTEXT=${1:-""}
DRY_RUN=${DRY_RUN:-false}

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if kubectl is available
check_prerequisites() {
    print_info "Checking prerequisites..."

    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl could not be found. Please install kubectl first."
        exit 1
    fi

    if [ -z "$CONTEXT" ]; then
        CONTEXT=$(kubectl config current-context)
        print_warn "No context specified, using current context: $CONTEXT"
    fi

    print_info "Using Kubernetes context: $CONTEXT"

    # Confirm before proceeding
    read -p "Deploy to this context? (yes/no): " -n 3 -r
    echo
    if [[ ! $REPLY =~ ^yes$ ]]; then
        print_error "Deployment cancelled"
        exit 1
    fi
}

# Function to apply manifests
apply_manifest() {
    local manifest=$1
    local description=$2

    print_info "Applying $description..."

    if [ "$DRY_RUN" = "true" ]; then
        kubectl apply -f "$manifest" --dry-run=client --context="$CONTEXT"
    else
        kubectl apply -f "$manifest" --context="$CONTEXT"
    fi

    if [ $? -eq 0 ]; then
        print_info "$description applied successfully"
    else
        print_error "Failed to apply $description"
        exit 1
    fi
}

# Function to wait for resources
wait_for_pods() {
    local label=$1
    local description=$2
    local timeout=${3:-300}

    print_info "Waiting for $description to be ready (timeout: ${timeout}s)..."

    if kubectl wait --for=condition=ready pod -l "$label" -n "$NAMESPACE" --timeout="${timeout}s" --context="$CONTEXT"; then
        print_info "$description is ready"
    else
        print_error "$description failed to become ready within ${timeout}s"
        kubectl get pods -l "$label" -n "$NAMESPACE" --context="$CONTEXT"
        exit 1
    fi
}

# Function to wait for deployment
wait_for_deployment() {
    local deployment=$1
    local description=$2

    print_info "Waiting for $description deployment to complete..."

    if kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=300s --context="$CONTEXT"; then
        print_info "$description deployment completed"
    else
        print_error "$description deployment failed"
        kubectl get deployment "$deployment" -n "$NAMESPACE" --context="$CONTEXT"
        exit 1
    fi
}

# Main deployment function
main() {
    print_info "========================================="
    print_info "TraceRTM Kubernetes Deployment"
    print_info "========================================="

    check_prerequisites

    if [ "$DRY_RUN" = "true" ]; then
        print_warn "Running in DRY RUN mode - no changes will be applied"
    fi

    # Get the infrastructure directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    K8S_DIR="$SCRIPT_DIR/../infrastructure/k8s"

    if [ ! -d "$K8S_DIR" ]; then
        print_error "Kubernetes manifests directory not found: $K8S_DIR"
        exit 1
    fi

    print_info "Using manifests from: $K8S_DIR"

    # Step 1: Create namespace
    apply_manifest "$K8S_DIR/00-namespace.yaml" "Namespace"

    # Step 2: Apply ConfigMaps and Secrets
    apply_manifest "$K8S_DIR/01-configmaps.yaml" "ConfigMaps"
    apply_manifest "$K8S_DIR/02-secrets.yaml" "Secrets"

    if [ "$DRY_RUN" = "true" ]; then
        print_warn "Skipping resource wait in dry-run mode"
    else
        # Step 3: Deploy infrastructure (PostgreSQL, Redis, NATS)
        print_info "========================================="
        print_info "Deploying Infrastructure Services"
        print_info "========================================="

        apply_manifest "$K8S_DIR/03-postgres.yaml" "PostgreSQL"
        apply_manifest "$K8S_DIR/04-redis.yaml" "Redis"
        apply_manifest "$K8S_DIR/05-nats.yaml" "NATS"

        # Wait for infrastructure to be ready
        wait_for_pods "app=postgres" "PostgreSQL" 300
        wait_for_pods "app=redis" "Redis" 300
        wait_for_pods "app=nats" "NATS" 300

        print_info "Infrastructure services are ready"

        # Step 4: Deploy backends
        print_info "========================================="
        print_info "Deploying Backend Services"
        print_info "========================================="

        apply_manifest "$K8S_DIR/06-go-backend.yaml" "Go Backend"
        apply_manifest "$K8S_DIR/07-python-backend.yaml" "Python Backend"

        # Wait for backend deployments
        wait_for_deployment "go-backend" "Go Backend"
        wait_for_deployment "python-backend" "Python Backend"

        print_info "Backend services are ready"

        # Step 5: Deploy ingress
        print_info "========================================="
        print_info "Deploying Ingress"
        print_info "========================================="

        apply_manifest "$K8S_DIR/08-ingress.yaml" "Nginx Ingress"
        wait_for_deployment "nginx" "Nginx"

        # Optional: Apply monitoring and network policies if they exist
        if [ -f "$K8S_DIR/09-monitoring.yaml" ]; then
            apply_manifest "$K8S_DIR/09-monitoring.yaml" "Monitoring"
        fi

        if [ -f "$K8S_DIR/10-network-policies.yaml" ]; then
            apply_manifest "$K8S_DIR/10-network-policies.yaml" "Network Policies"
        fi
    fi

    # Display deployment status
    print_info "========================================="
    print_info "Deployment Status"
    print_info "========================================="

    kubectl get all -n "$NAMESPACE" --context="$CONTEXT"

    print_info ""
    print_info "========================================="
    print_info "Deployment Complete!"
    print_info "========================================="

    # Get external IP of nginx service
    print_info "Waiting for external IP assignment..."
    sleep 5
    EXTERNAL_IP=$(kubectl get svc nginx-service -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' --context="$CONTEXT" 2>/dev/null || echo "pending")

    if [ "$EXTERNAL_IP" != "pending" ] && [ -n "$EXTERNAL_IP" ]; then
        print_info "External IP: $EXTERNAL_IP"
        print_info "Access your application at: https://$EXTERNAL_IP"
    else
        print_warn "External IP not yet assigned. Check with:"
        echo "  kubectl get svc nginx-service -n $NAMESPACE --context=$CONTEXT"
    fi

    print_info ""
    print_info "Useful commands:"
    echo "  View pods:        kubectl get pods -n $NAMESPACE --context=$CONTEXT"
    echo "  View services:    kubectl get svc -n $NAMESPACE --context=$CONTEXT"
    echo "  View logs (Go):   kubectl logs -f deployment/go-backend -n $NAMESPACE --context=$CONTEXT"
    echo "  View logs (Py):   kubectl logs -f deployment/python-backend -n $NAMESPACE --context=$CONTEXT"
    echo "  Scale Go backend: kubectl scale deployment/go-backend --replicas=5 -n $NAMESPACE --context=$CONTEXT"
    echo "  Port forward:     kubectl port-forward svc/python-backend-service 8000:8000 -n $NAMESPACE --context=$CONTEXT"
}

# Run main function
main

exit 0
