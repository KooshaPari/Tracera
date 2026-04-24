#!/bin/bash
set -e

# TraceRTM Documentation Deployment Script
# Usage: ./deploy.sh [preview|production]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$DOCS_DIR/../../../backend"

ENVIRONMENT="${1:-preview}"
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

print_header() {
  echo -e "${BOLD}${BLUE}===================================================${NC}"
  echo -e "${BOLD}${BLUE}  TraceRTM Documentation Deployment${NC}"
  echo -e "${BOLD}${BLUE}===================================================${NC}\n"
}

print_step() {
  echo -e "${BOLD}${GREEN}▶${NC} ${BOLD}$1${NC}"
}

print_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1"
}

print_success() {
  echo -e "${GREEN}✓${NC} $1"
}

check_requirements() {
  print_step "Checking requirements..."

  # Check if bun is installed
  if ! command -v bun &> /dev/null; then
    print_error "bun is not installed. Please install it from https://bun.sh"
    exit 1
  fi
  print_success "bun is installed"

  # Check if vercel CLI is installed
  if ! command -v vercel &> /dev/null; then
    print_warning "Vercel CLI is not installed. Installing..."
    bun install --global vercel@latest
  fi
  print_success "Vercel CLI is available"

  # Check if Go is installed (for OpenAPI generation)
  if ! command -v go &> /dev/null; then
    print_warning "Go is not installed. Skipping OpenAPI spec generation."
    SKIP_OPENAPI=true
  else
    print_success "Go is installed"
  fi

  echo ""
}

generate_openapi() {
  if [ "$SKIP_OPENAPI" = true ]; then
    print_warning "Skipping OpenAPI spec generation (Go not installed)"
    return
  fi

  print_step "Generating OpenAPI specification..."

  # Check if swag is installed
  if ! command -v swag &> /dev/null; then
    print_info "Installing swag..."
    go install github.com/swaggo/swag/cmd/swag@latest
  fi

  # Generate OpenAPI spec from backend
  if [ -d "$BACKEND_DIR" ]; then
    cd "$BACKEND_DIR"
    print_info "Generating spec from Go backend..."

    swag init \
      --generalInfo main.go \
      --dir ./ \
      --output ./docs \
      --parseDependency \
      --parseInternal \
      --parseDepth 2 \
      --instanceName "tracertm"

    # Copy to docs public directory
    mkdir -p "$DOCS_DIR/public/api"
    cp docs/swagger.json "$DOCS_DIR/public/api/openapi.json"
    cp docs/swagger.yaml "$DOCS_DIR/public/api/openapi.yaml"

    print_success "OpenAPI spec generated and copied"
  else
    print_warning "Backend directory not found. Skipping OpenAPI generation."
  fi

  cd "$DOCS_DIR"
  echo ""
}

install_dependencies() {
  print_step "Installing dependencies..."
  cd "$DOCS_DIR/../.."
  bun install --frozen-lockfile
  print_success "Dependencies installed"
  cd "$DOCS_DIR"
  echo ""
}

build_site() {
  print_step "Building documentation site..."
  cd "$DOCS_DIR"

  bun run build

  print_success "Documentation site built"
  echo ""
}

deploy_to_vercel() {
  print_step "Deploying to Vercel ($ENVIRONMENT)..."
  cd "$DOCS_DIR"

  if [ "$ENVIRONMENT" = "production" ]; then
    print_warning "Deploying to PRODUCTION. Are you sure? (y/N)"
    read -r confirmation
    if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
      print_error "Deployment cancelled"
      exit 1
    fi

    # Pull production environment
    vercel pull --yes --environment=production

    # Build for production
    vercel build --prod

    # Deploy to production
    DEPLOYMENT_URL=$(vercel deploy --prebuilt --prod)
  else
    # Pull preview environment
    vercel pull --yes --environment=preview

    # Build for preview
    vercel build

    # Deploy to preview
    DEPLOYMENT_URL=$(vercel deploy --prebuilt)
  fi

  print_success "Deployment complete!"
  echo ""
  print_info "Deployment URL: ${DEPLOYMENT_URL}"
  echo ""
}

validate_deployment() {
  print_step "Validating deployment..."

  # Wait for deployment to propagate
  print_info "Waiting for deployment to propagate (10 seconds)..."
  sleep 10

  # Check if URL is accessible
  if curl -s -o /dev/null -w "%{http_code}" "$DEPLOYMENT_URL" | grep -q "200"; then
    print_success "Site is accessible"
  else
    print_warning "Site accessibility check failed. It may take a few moments to propagate."
  fi

  echo ""
}

print_summary() {
  echo -e "${BOLD}${GREEN}===================================================${NC}"
  echo -e "${BOLD}${GREEN}  Deployment Summary${NC}"
  echo -e "${BOLD}${GREEN}===================================================${NC}\n"
  echo -e "${BOLD}Environment:${NC} $ENVIRONMENT"
  echo -e "${BOLD}Deployment URL:${NC} $DEPLOYMENT_URL"
  echo ""
  if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "${BOLD}Production URL:${NC} https://docs.tracertm.com"
    echo ""
  fi
  echo -e "${GREEN}✓${NC} Deployment completed successfully!"
  echo ""
}

main() {
  print_header

  # Validate environment argument
  if [[ ! "$ENVIRONMENT" =~ ^(preview|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_info "Usage: ./deploy.sh [preview|production]"
    exit 1
  fi

  check_requirements
  generate_openapi
  install_dependencies
  build_site
  deploy_to_vercel
  validate_deployment
  print_summary
}

main
