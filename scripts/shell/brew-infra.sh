#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

print_info() {
    echo "ℹ️  $1"
}

print_success() {
    echo "✅ $1"
}

print_warning() {
    echo "⚠️  $1"
}

print_error() {
    echo "❌ $1"
}

print_info "Installing and starting TraceRTM infra via Homebrew..."

if ! command -v brew &> /dev/null; then
    print_error "Homebrew required. Install from https://brew.sh"
    exit 1
fi

brew tap minio/minio 2>/dev/null || true

for pg in postgresql@17 postgresql@14 postgresql; do
    if brew list "$pg" &> /dev/null; then
        break
    fi
    print_info "Installing $pg (brew install $pg)..."
    brew install "$pg" 2>/dev/null && break || true
done

for formula in nats-server neo4j temporal minio; do
    if ! brew list "$formula" &> /dev/null; then
        print_info "Installing $formula (brew install $formula)..."
        brew install "$formula" || { print_warning "Install failed for $formula"; continue; }
    fi
done

print_info "Starting services (brew services start)..."
brew services start postgresql@17 2>/dev/null || brew services start postgresql@14 2>/dev/null || brew services start postgresql 2>/dev/null || true
brew services start nats-server 2>/dev/null || true
brew services start neo4j 2>/dev/null || true
brew services start temporal 2>/dev/null || true
brew services start minio 2>/dev/null || true

print_success "Homebrew services started. Waiting for ports..."
for i in $(seq 1 30); do
    sleep 0.5
    pg_ok=0; dragonfly_ok=0; nats_ok=0; neo4j_ok=0
    pg_isready -q 2>/dev/null && pg_ok=1
    redis-cli ping &> /dev/null && dragonfly_ok=1
    lsof -Pi :4222 -sTCP:LISTEN -t &> /dev/null && nats_ok=1
    lsof -Pi :7687 -sTCP:LISTEN -t &> /dev/null && neo4j_ok=1
    if [ "$pg_ok" = 1 ] && [ "$dragonfly_ok" = 1 ] && [ "$nats_ok" = 1 ] && [ "$neo4j_ok" = 1 ]; then
        print_success "PostgreSQL, Dragonfly, NATS, Neo4j are ready."
        break
    fi
done

echo ""
print_info "Ensure .env at repo root has: REDIS_URL=redis://localhost:6379, NATS_URL=nats://localhost:4222, NEO4J_URI=neo4j://localhost:7687, TEMPORAL_HOST=localhost:7233, TEMPORAL_NAMESPACE=default"
print_info "Then run: rtm dev start -q"

