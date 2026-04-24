#!/bin/bash
# ==============================================================================
# Environment Setup Script for Local Development
# ==============================================================================
# This script helps set up environment files for all services
# Run with: ./scripts/setup-env.sh
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔧 TracerTM Environment Setup"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

file_exists() {
    [ -f "$1" ]
}

# -----------------------------------------------------------------------------
# Check Prerequisites
# -----------------------------------------------------------------------------

echo "Checking prerequisites..."

# Check for required tools
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL not found. Install via: brew install postgresql"
fi

if ! command -v dragonfly &> /dev/null && ! command -v docker &> /dev/null; then
    print_warning "Dragonfly not found. Install Dragonfly or Docker for the default cache runtime"
fi

if ! command -v nats-server &> /dev/null; then
    print_warning "NATS not found. Install via: brew install nats-server"
fi

echo ""

# -----------------------------------------------------------------------------
# Go Backend Environment
# -----------------------------------------------------------------------------

echo "📦 Setting up Go Backend environment..."

GO_ENV_FILE="$ROOT_DIR/backend/.env"

if file_exists "$GO_ENV_FILE"; then
    print_warning "Go backend .env already exists. Backing up to .env.backup"
    cp "$GO_ENV_FILE" "$GO_ENV_FILE.backup"
fi

# Combine shared + Go-specific
cat "$ROOT_DIR/.env.shared" > "$GO_ENV_FILE"
echo "" >> "$GO_ENV_FILE"
echo "# --- Go Backend Specific ---" >> "$GO_ENV_FILE"
cat "$ROOT_DIR/.env.go-backend" >> "$GO_ENV_FILE"

# Fix DATABASE_URL format for Go (postgres:// not postgresql+asyncpg://)
sed -i.bak 's|postgresql+asyncpg://|postgres://|g' "$GO_ENV_FILE"
rm "$GO_ENV_FILE.bak"

print_success "Go backend .env created at: backend/.env"

# -----------------------------------------------------------------------------
# Python Backend Environment
# -----------------------------------------------------------------------------

echo "🐍 Setting up Python Backend environment..."

PY_ENV_FILE="$ROOT_DIR/.env"

if file_exists "$PY_ENV_FILE"; then
    print_warning "Python backend .env already exists. Backing up to .env.backup"
    cp "$PY_ENV_FILE" "$PY_ENV_FILE.backup"
fi

# Combine shared + Python-specific
cat "$ROOT_DIR/.env.shared" > "$PY_ENV_FILE"
echo "" >> "$PY_ENV_FILE"
echo "# --- Python Backend Specific ---" >> "$PY_ENV_FILE"
cat "$ROOT_DIR/.env.python-backend" >> "$PY_ENV_FILE"

print_success "Python backend .env created at: .env"

# -----------------------------------------------------------------------------
# Frontend Environment
# -----------------------------------------------------------------------------

echo "🎨 Setting up Frontend environment..."

FE_ENV_FILE="$ROOT_DIR/frontend/apps/web/.env.local"
FE_DIR="$ROOT_DIR/frontend/apps/web"

if [ ! -d "$FE_DIR" ]; then
    print_error "Frontend directory not found at: $FE_DIR"
else
    if file_exists "$FE_ENV_FILE"; then
        print_warning "Frontend .env.local already exists. Backing up to .env.local.backup"
        cp "$FE_ENV_FILE" "$FE_ENV_FILE.backup"
    fi

    cp "$ROOT_DIR/.env.frontend" "$FE_ENV_FILE"
    print_success "Frontend .env.local created at: frontend/apps/web/.env.local"
fi

# -----------------------------------------------------------------------------
# Database Setup
# -----------------------------------------------------------------------------

echo ""
echo "🗄️  Database Setup"
echo "=================="

if command -v createdb &> /dev/null; then
    if psql -lqt | cut -d \| -f 1 | grep -qw tracertm; then
        print_success "Database 'tracertm' already exists"
    else
        echo "Creating database 'tracertm'..."
        createdb tracertm && print_success "Database created" || print_error "Failed to create database"
    fi
else
    print_warning "PostgreSQL CLI tools not found. Create database manually:"
    echo "  createdb tracertm"
fi

# -----------------------------------------------------------------------------
# Summary and Next Steps
# -----------------------------------------------------------------------------

echo ""
echo "✨ Environment Setup Complete!"
echo "=============================="
echo ""
echo "📁 Environment files created:"
echo "  • backend/.env             (Go backend)"
echo "  • .env                     (Python backend)"
echo "  • frontend/apps/web/.env.local  (Frontend)"
echo ""
echo "🔐 IMPORTANT: Update these secrets in your .env files:"
echo "  • JWT_SECRET              (generate with: openssl rand -hex 32)"
echo "  • CSRF_SECRET             (generate with: openssl rand -hex 32)"
echo "  • WORKOS_CLIENT_ID        (from WorkOS dashboard)"
echo "  • WORKOS_API_KEY          (from WorkOS dashboard)"
echo "  • VOYAGE_API_KEY          (from VoyageAI or alternative)"
echo ""
echo "🚀 Start services individually:"
echo ""
echo "  Terminal 1 - PostgreSQL:"
echo "    pg_ctl -D /usr/local/var/postgres start"
echo "    (or it may already be running as a service)"
echo ""
echo "  Terminal 2 - Dragonfly:"
echo "    bash scripts/shell/redis-if-not-running.sh"
echo ""
echo "  Terminal 3 - NATS:"
echo "    nats-server -js"
echo ""
echo "  Terminal 4 - Go Backend:"
echo "    cd backend && air"
echo "    (or: go run main.go)"
echo ""
echo "  Terminal 5 - Python Backend:"
echo "    uvicorn tracertm.api.main:app --reload"
echo ""
echo "  Terminal 6 - Frontend:"
echo "    cd frontend/apps/web && bun run dev"
echo ""
echo "📖 For more details, see: docs/01-getting-started/README.md"
echo ""
