#!/bin/bash
# TracerTM DevContainer Post-Creation Script
# Runs after the devcontainer is created to set up the development environment

set -e

echo "========================================"
echo "TracerTM DevContainer Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to wait for service to be ready
wait_for_service() {
    local service=$1
    local host=$2
    local port=$3
    local max_attempts=30
    local attempt=0

    echo "Waiting for $service to be ready..."
    while [ $attempt -lt $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            print_status "$service is ready!"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    print_error "$service failed to start after $max_attempts attempts"
    return 1
}

# 1. Wait for essential services
echo ""
echo "Step 1: Waiting for services to be ready..."
wait_for_service "PostgreSQL" "postgres" 5432
wait_for_service "Redis" "redis" 6379
wait_for_service "NATS" "nats" 4222

# 2. Install Python dependencies
echo ""
echo "Step 2: Installing Python dependencies..."
if [ -f "pyproject.toml" ]; then
    print_status "Installing Python packages with uv..."
    uv sync
    print_status "Python dependencies installed"
else
    print_warning "pyproject.toml not found, skipping Python dependencies"
fi

# 3. Install Go dependencies
echo ""
echo "Step 3: Installing Go dependencies..."
if [ -d "backend" ] && [ -f "backend/go.mod" ]; then
    print_status "Downloading Go modules..."
    cd backend
    go mod download
    cd ..
    print_status "Go dependencies installed"
else
    print_warning "backend/go.mod not found, skipping Go dependencies"
fi

# 4. Install frontend dependencies
echo ""
echo "Step 4: Installing frontend dependencies..."
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    print_status "Installing frontend packages with Bun..."
    cd frontend
    bun install
    cd ..
    print_status "Frontend dependencies installed"
else
    print_warning "frontend/package.json not found, skipping frontend dependencies"
fi

# 5. Run database migrations
echo ""
echo "Step 5: Running database migrations..."
if [ -f "alembic.ini" ]; then
    print_status "Running Alembic migrations..."
    # Wait a bit more for PostgreSQL to be fully ready
    sleep 5

    # Run migrations with error handling
    if uv run alembic upgrade head; then
        print_status "Database migrations completed"
    else
        print_warning "Database migrations failed or already applied"
    fi
else
    print_warning "alembic.ini not found, skipping migrations"
fi

# 6. Set up Git hooks (optional)
echo ""
echo "Step 6: Setting up Git hooks..."
if [ -f ".pre-commit-config.yaml" ]; then
    print_status "Installing pre-commit hooks..."
    if uv run pre-commit install; then
        print_status "Git hooks installed"
    else
        print_warning "Failed to install pre-commit hooks"
    fi
else
    print_warning ".pre-commit-config.yaml not found, skipping Git hooks"
fi

# 7. Create necessary directories
echo ""
echo "Step 7: Creating necessary directories..."
mkdir -p .process-compose/logs
mkdir -p tmp
mkdir -p .prometheus
print_status "Directories created"

# 8. Set up environment file if not exists
echo ""
echo "Step 8: Checking environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_status "Creating .env from .env.example..."
        cp .env.example .env
        print_status ".env file created"
    else
        print_warning ".env.example not found, you may need to create .env manually"
    fi
else
    print_status ".env file already exists"
fi

# 9. Build Go backend (optional - for faster first run)
echo ""
echo "Step 9: Pre-building Go backend (optional)..."
if [ -d "backend" ]; then
    print_status "Building Go backend..."
    cd backend
    if go build -o /tmp/tracertm-api ./cmd/api; then
        print_status "Go backend built successfully"
        rm /tmp/tracertm-api
    else
        print_warning "Go backend build failed (will be built on first run)"
    fi
    cd ..
fi

# 10. Display helpful information
echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Start all services:"
echo "   make dev-tui        # Interactive dashboard"
echo "   make dev            # Background mode"
echo ""
echo "2. Access the application:"
echo "   Gateway:    http://localhost:4000"
echo "   Frontend:   http://localhost:5173"
echo "   Go API:     http://localhost:8080"
echo "   Python API: http://localhost:8000"
echo "   Grafana:    http://localhost:3000 (admin/admin)"
echo "   Prometheus: http://localhost:9090"
echo "   Neo4j:      http://localhost:7474 (neo4j/password)"
echo ""
echo "3. Run tests:"
echo "   make test           # All tests"
echo "   make test-go        # Go tests only"
echo "   make test-python    # Python tests only"
echo "   make test-frontend  # Frontend tests only"
echo ""
echo "4. View logs:"
echo "   tail -f .process-compose/logs/<service>.log"
echo ""
echo "📚 Documentation:"
echo "   README.md"
echo "   docs/guides/devcontainer-setup.md"
echo ""
print_status "DevContainer is ready for development!"
echo ""
