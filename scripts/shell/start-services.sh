#!/bin/bash
# ==============================================================================
# Individual Service Startup Script
# ==============================================================================
# Run specific services individually for local development
# Usage: ./scripts/start-services.sh [service-name]
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# -----------------------------------------------------------------------------
# Service Functions
# -----------------------------------------------------------------------------

start_postgres() {
    print_info "Starting PostgreSQL..."

    # Check if already running
    if pg_isready -q 2>/dev/null; then
        print_success "PostgreSQL is already running"
        return 0
    fi

    # Try to start
    if command -v brew &> /dev/null; then
        brew services start postgresql@14 2>/dev/null || \
        brew services start postgresql 2>/dev/null || \
        pg_ctl -D /usr/local/var/postgres start
    else
        pg_ctl -D /usr/local/var/postgres start
    fi

    sleep 2

    if pg_isready -q 2>/dev/null; then
        print_success "PostgreSQL started"
    else
        print_error "Failed to start PostgreSQL"
        exit 1
    fi
}

start_nats() {
    print_info "Starting NATS..."

    # Check if already running on port 4222
    if lsof -Pi :4222 -sTCP:LISTEN -t &> /dev/null; then
        print_success "NATS is already running on port 4222"
        return 0
    fi

    # Start NATS with JetStream in background
    nats-server -js -D &
    NATS_PID=$!

    sleep 3

    # Check if NATS is listening on port 4222
    if lsof -Pi :4222 -sTCP:LISTEN -t &> /dev/null; then
        print_success "NATS started with JetStream (PID: $NATS_PID)"
    else
        print_error "Failed to start NATS"
        exit 1
    fi
}

start_neo4j() {
    print_info "Starting Neo4j..."

    # Check if already running on port 7687
    if lsof -Pi :7687 -sTCP:LISTEN -t &> /dev/null; then
        print_success "Neo4j is already running on port 7687"
        return 0
    fi

    NEO4J_CMD=""
    if command -v neo4j &> /dev/null; then
        NEO4J_CMD="neo4j"
    elif command -v brew &> /dev/null && [ -x "$(brew --prefix neo4j 2>/dev/null)/bin/neo4j" ]; then
        NEO4J_CMD="$(brew --prefix neo4j)/bin/neo4j"
    fi

    # Prefer neo4j start (CLI) over brew services to avoid launchctl hang/failure; see docs/reference/NEO4J_DEV_DEBUG.md
    if [ -n "$NEO4J_CMD" ]; then
        print_info "Starting Neo4j via CLI (neo4j start)..."
        $NEO4J_CMD start 2>/dev/null || true
        for i in $(seq 1 90); do
            sleep 0.5
            if lsof -Pi :7687 -sTCP:LISTEN -t &> /dev/null; then
                print_success "Neo4j started (port 7687)"
                return 0
            fi
        done
    fi

    # Fallback: brew services (can hang or fail with launchctl exit 5; run in background with bounded wait)
    if command -v brew &> /dev/null; then
        print_info "Trying brew services start neo4j (may not start under launchd)..."
        ( brew services start neo4j 2>/dev/null ) &
        BGPID=$!
        for i in $(seq 1 60); do
            sleep 0.5
            if lsof -Pi :7687 -sTCP:LISTEN -t &> /dev/null; then
                kill $BGPID 2>/dev/null || true
                wait $BGPID 2>/dev/null || true
                print_success "Neo4j started (port 7687)"
                return 0
            fi
        done
        kill $BGPID 2>/dev/null || true
        wait $BGPID 2>/dev/null || true
    else
        print_error "Homebrew required to start Neo4j. Install from https://brew.sh"
        exit 1
    fi

    print_error "Neo4j did not become ready in time."
    echo ""
    if [ -n "$NEO4J_CMD" ]; then
        echo "  Start manually:  $NEO4J_CMD start"
        echo "  To see startup errors:  $NEO4J_CMD console"
    else
        echo "  Start manually:  brew services start neo4j"
        echo "  Or run Neo4j from its install dir (see: brew --prefix neo4j)"
    fi
    echo "  Then run:  rtm dev start"
    echo "  See:  docs/reference/NEO4J_DEV_DEBUG.md"
    exit 1
}

start_minio() {
    print_info "Starting MinIO (S3-compatible object storage)..."

    if ! command -v brew &> /dev/null; then
        print_error "Homebrew required. Install from https://brew.sh"
        exit 1
    fi

    if ! command -v minio &> /dev/null; then
        print_info "Installing MinIO (brew install minio)..."
        brew install minio
    fi

    brew services start minio 2>/dev/null || true

    PORT="${MINIO_PORT:-9000}"
    for i in $(seq 1 30); do
        sleep 0.5
        if curl -sf -o /dev/null "http://127.0.0.1:$PORT/minio/health/live" 2>/dev/null || curl -sf -o /dev/null "http://127.0.0.1:$PORT" 2>/dev/null; then
            print_success "MinIO is up at http://127.0.0.1:$PORT"
            break
        fi
    done
    if ! curl -sf -o /dev/null "http://127.0.0.1:$PORT/minio/health/live" 2>/dev/null; then
        print_error "MinIO did not become ready. Check: brew services info minio"
        exit 1
    fi

    # Ensure root .env has S3 vars so Python/Go preflight passes
    ENV_FILE="$ROOT_DIR/.env"
    if [ -f "$ENV_FILE" ] && ! grep -q "^S3_ENDPOINT=" "$ENV_FILE" 2>/dev/null; then
        print_info "Adding S3 vars to .env..."
        cat >> "$ENV_FILE" << 'ENVBLOCK'

# MinIO (local) - added by start-services.sh minio
S3_ENDPOINT=http://127.0.0.1:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET=tracertm
S3_REGION=us-east-1
ENVBLOCK
        print_success "S3 vars appended to .env"
    fi

    # Create bucket via Go if backend exists (uses root .env S3_* or defaults)
    if [ -f "$ROOT_DIR/backend/cmd/create-minio-bucket/main.go" ]; then
        print_info "Creating bucket 'tracertm'..."
        (cd "$ROOT_DIR/backend" && set -a && [ -f "$ROOT_DIR/.env" ] && . "$ROOT_DIR/.env" 2>/dev/null; export S3_ENDPOINT="${S3_ENDPOINT:-http://127.0.0.1:9000}" S3_ACCESS_KEY_ID="${S3_ACCESS_KEY_ID:-minioadmin}" S3_SECRET_ACCESS_KEY="${S3_SECRET_ACCESS_KEY:-minioadmin}" S3_BUCKET="${S3_BUCKET:-tracertm}" S3_REGION="${S3_REGION:-us-east-1}"; set +a; go run ./cmd/create-minio-bucket/) 2>/dev/null && print_success "Bucket created" || print_warning "Bucket creation skipped (install Go or run from backend: go run ./cmd/create-minio-bucket/)"
    fi

    echo ""
    print_success "MinIO ready. API: http://127.0.0.1:$PORT  Console: http://127.0.0.1:${MINIO_CONSOLE_PORT:-9001} (minioadmin / minioadmin)"
}

start_temporal() {
    print_info "Starting Temporal (workflow server)..."

    if ! command -v brew &> /dev/null; then
        print_error "Homebrew required. Install from https://brew.sh"
        exit 1
    fi

    if ! command -v temporal &> /dev/null; then
        print_info "Installing Temporal CLI (brew install temporal)..."
        brew install temporal
    fi

    # Check if already running on port 7233
    if lsof -Pi :7233 -sTCP:LISTEN -t &> /dev/null; then
        print_success "Temporal is already running on port 7233"
        return 0
    fi

    TEMPORAL_DIR="$ROOT_DIR/.temporal"
    mkdir -p "$TEMPORAL_DIR"

    print_info "Starting Temporal server (dev mode, db: $TEMPORAL_DIR/dev.db)..."
    temporal server start-dev --db-filename "$TEMPORAL_DIR/dev.db" &
    TEMPORAL_PID=$!

    for i in $(seq 1 30); do
        sleep 0.5
        if lsof -Pi :7233 -sTCP:LISTEN -t &> /dev/null; then
            print_success "Temporal started (PID: $TEMPORAL_PID), gRPC: 127.0.0.1:7233"
            break
        fi
    done
    if ! lsof -Pi :7233 -sTCP:LISTEN -t &> /dev/null; then
        print_error "Temporal did not become ready. Check logs or: kill $TEMPORAL_PID"
        exit 1
    fi

    # Ensure root .env has Temporal vars so Python/Go preflight pass
    ENV_FILE="$ROOT_DIR/.env"
    if [ -f "$ENV_FILE" ] && ! grep -q "^TEMPORAL_HOST=" "$ENV_FILE" 2>/dev/null; then
        print_info "Adding TEMPORAL_HOST to .env..."
        echo "TEMPORAL_HOST=127.0.0.1:7233" >> "$ENV_FILE"
        print_success "TEMPORAL_HOST appended to .env"
    fi
    if [ -f "$ENV_FILE" ] && ! grep -q "^TEMPORAL_NAMESPACE=" "$ENV_FILE" 2>/dev/null; then
        print_info "Adding TEMPORAL_NAMESPACE to .env..."
        echo "TEMPORAL_NAMESPACE=default" >> "$ENV_FILE"
        print_success "TEMPORAL_NAMESPACE appended to .env"
    fi

    # Ensure Temporal namespace exists
    TEMPORAL_NAMESPACE="${TEMPORAL_NAMESPACE:-$(grep -E '^TEMPORAL_NAMESPACE=' "$ENV_FILE" 2>/dev/null | tail -1 | cut -d= -f2)}"
    TEMPORAL_NAMESPACE="${TEMPORAL_NAMESPACE:-default}"
    if ! temporal operator namespace describe --namespace "$TEMPORAL_NAMESPACE" &> /dev/null; then
        print_info "Creating Temporal namespace: $TEMPORAL_NAMESPACE"
        temporal operator namespace create --namespace "$TEMPORAL_NAMESPACE" --description "TraceRTM dev namespace" &> /dev/null \
            && print_success "Temporal namespace created" \
            || print_warning "Failed to create namespace (check temporal CLI permissions)"
    fi

    echo ""
    print_success "Temporal ready. gRPC: 127.0.0.1:7233  (temporal workflow list to verify)"
}

start_go_backend() {
    print_info "Starting Go Backend..."

    cd "$ROOT_DIR/backend"

    # Check if .env exists
    if [ ! -f ".env" ]; then
        print_error "Go backend .env not found. Run ./scripts/setup-env.sh first"
        exit 1
    fi

    print_info "Starting with air (hot reload)..."
    print_warning "Press Ctrl+C to stop"

    # Check if air is installed
    if ! command -v air &> /dev/null; then
        print_warning "air not found. Installing..."
        go install github.com/cosmtrek/air@latest
    fi

    air
}

start_python_backend() {
    print_info "Starting Python Backend..."

    cd "$ROOT_DIR"

    # Check if .env exists
    if [ ! -f ".env" ]; then
        print_error "Python backend .env not found. Run ./scripts/setup-env.sh first"
        exit 1
    fi

    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_warning "Virtual environment not found. Creating..."
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -e ".[dev]"
    else
        source .venv/bin/activate
    fi

    print_info "Starting with uvicorn (hot reload)..."
    print_warning "Press Ctrl+C to stop"

    uvicorn tracertm.api.main:app --reload --host 0.0.0.0 --port 8000
}

start_frontend() {
    print_info "Starting Frontend..."

    cd "$ROOT_DIR/frontend/apps/web"

    # Check if .env.local exists
    if [ ! -f ".env.local" ]; then
        print_error "Frontend .env.local not found. Run ./scripts/setup-env.sh first"
        exit 1
    fi

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "Dependencies not installed. Running bun install..."
        bun install
    fi

    print_info "Starting with Vite dev server (hot reload)..."
    print_warning "Press Ctrl+C to stop"

    bun run dev
}

start_all_deps() {
    print_info "Starting all dependencies (PostgreSQL, Dragonfly, NATS)..."
    start_postgres
    print_info "Starting Dragonfly cache runtime..."

    if redis-cli ping &> /dev/null; then
        print_success "Cache runtime is already running"
    else
        REDIS_COMPAT_PROVIDER=dragonfly bash "$SCRIPT_DIR/redis-if-not-running.sh" &
        DRAGONFLY_PID=$!
        sleep 3

        if redis-cli ping &> /dev/null; then
            print_success "Dragonfly started (PID: $DRAGONFLY_PID)"
        else
            print_error "Failed to start Dragonfly"
            exit 1
        fi
    fi
    start_nats
    print_success "All dependencies started"
    echo ""
    print_info "Now start backends and frontend in separate terminals:"
    echo "  Terminal 1: ./scripts/start-services.sh go-backend"
    echo "  Terminal 2: ./scripts/start-services.sh python-backend"
    echo "  Terminal 3: ./scripts/start-services.sh frontend"
}

stop_all() {
    print_info "Stopping all services..."

    # Stop cache runtime
    if redis-cli ping &> /dev/null; then
        redis-cli shutdown
        print_success "Cache runtime stopped"
    fi

    # Stop NATS
    if pgrep nats-server &> /dev/null; then
        pkill nats-server
        print_success "NATS stopped"
    fi

    # Note: PostgreSQL typically stays running as a service
    print_info "PostgreSQL left running (use 'brew services stop postgresql' to stop)"

    print_success "Services stopped"
}

# -----------------------------------------------------------------------------
# Main Script
# -----------------------------------------------------------------------------

show_usage() {
    echo "Usage: $0 [service]"
    echo ""
    echo "Services:"
    echo "  postgres          - Start PostgreSQL database"
    echo "  dragonfly         - Start Dragonfly cache runtime"
    echo "  nats              - Start NATS message broker"
    echo "  neo4j             - Start Neo4j graph DB (port 7687, Homebrew)"
    echo "  minio             - Start MinIO S3-compatible storage (port 9000, Homebrew)"
    echo "  temporal          - Start Temporal workflow server (port 7233, Homebrew)"
    echo "  brew-infra        - Install + start all infra via Homebrew"
    echo "  go-backend        - Start Go backend (port 8080)"
    echo "  python-backend   - Start Python backend (port 8000)"
    echo "  frontend         - Start frontend web app (port 3000)"
    echo "  deps              - Start all dependencies (PostgreSQL, Dragonfly, NATS)"
    echo "  stop              - Stop all services"
    echo ""
    echo "Examples:"
    echo "  $0 brew-infra              # Install and start all infra via Homebrew (then rtm dev start -q)"
    echo "  $0 deps                    # Start dependencies first"
    echo "  $0 go-backend              # Then start Go backend in terminal 1"
    echo "  $0 python-backend          # Then start Python backend in terminal 2"
    echo "  $0 frontend                # Then start frontend in terminal 3"
    echo ""
}

# Check arguments
if [ $# -eq 0 ]; then
    show_usage
    exit 0
fi

SERVICE=$1

case $SERVICE in
    postgres)
        start_postgres
        ;;
    dragonfly)
        print_info "Starting Dragonfly cache runtime..."
        if redis-cli ping &> /dev/null; then
            print_success "Cache runtime is already running"
        else
            REDIS_COMPAT_PROVIDER=dragonfly bash "$SCRIPT_DIR/redis-if-not-running.sh" &
            DRAGONFLY_PID=$!
            sleep 3
            if redis-cli ping &> /dev/null; then
                print_success "Dragonfly started (PID: $DRAGONFLY_PID)"
            else
                print_error "Failed to start Dragonfly"
                exit 1
            fi
        fi
        ;;
    nats)
        start_nats
        ;;
    neo4j)
        start_neo4j
        ;;
    brew-infra)
        bash "$SCRIPT_DIR/brew-infra.sh"
        ;;
    minio)
        start_minio
        ;;
    temporal)
        start_temporal
        ;;
    go-backend)
        start_go_backend
        ;;
    python-backend)
        start_python_backend
        ;;
    frontend)
        start_frontend
        ;;
    deps)
        start_all_deps
        ;;
    stop)
        stop_all
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown service: $SERVICE"
        echo ""
        show_usage
        exit 1
        ;;
esac
