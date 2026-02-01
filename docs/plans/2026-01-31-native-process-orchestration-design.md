# Native Process Orchestration Design for TraceRTM

**Date:** 2026-01-31
**Status:** Approved
**Author:** AI Assistant with user collaboration

## Executive Summary

Migrate TraceRTM from Docker-based development to native process orchestration using Process Compose. This eliminates Docker daemon overhead while maintaining docker-compose-like orchestration capabilities across macOS, Linux, and Windows environments.

**Key Benefits:**
- 60-80% reduction in resource overhead (no Docker daemon)
- Native service management via Homebrew/system packages
- Cross-platform compatibility (macOS primary, Linux/Windows support)
- Familiar YAML-based configuration
- Enhanced developer experience with TUI dashboard

## Architecture Overview

### Service Stack

**Layer 1 - Infrastructure Services** (no dependencies):
- PostgreSQL 17 (port 5432) - Main relational database
- Redis 7 (port 6379) - Cache and session store
- Neo4j 5 (ports 7687, 7474) - Graph database
- NATS (ports 4222, 8222, 6222) - Message broker with JetStream

**Layer 2 - Workflow & Monitoring**:
- Temporal Server (depends on PostgreSQL) - Workflow orchestration
- Prometheus (standalone) - Metrics collection

**Layer 3 - Exporters**:
- postgres_exporter (port 9187) - PostgreSQL metrics
- redis_exporter (port 9121) - Redis metrics
- node_exporter (port 9100) - System metrics

**Layer 4 - Application Services**:
- Go Backend API (port 8080) - Main API server
- Python FastAPI (port 8000) - ML/AI services and CLI backend

**Layer 5 - Gateway & Visualization**:
- Caddy (port 4000) - Reverse proxy and API gateway
- Grafana (port 3000) - Monitoring dashboards

### Technology Choices

**Process Compose over alternatives:**
- Single Go binary (no dependencies)
- Docker-compose-compatible YAML syntax
- Built-in TUI for monitoring
- REST API for automation
- Health checks and dependency management
- Process scaling capabilities
- Cross-platform support (Win/Mac/Linux)

**Caddy over nginx:**
- Automatic HTTPS with Let's Encrypt
- Simpler configuration (Caddyfile vs nginx.conf)
- Better WebSocket support out-of-the-box
- Native JSON API for dynamic updates
- Already in toolchain

**Native binaries over containers:**
- Direct system access (no virtualization layer)
- Homebrew integration on macOS
- Standard package managers on Linux
- Consistent with "brew services" philosophy

## File Structure

```
/
├── process-compose.yaml              # Main config (macOS defaults)
├── process-compose.linux.yaml        # Linux path overrides
├── process-compose.windows.yaml      # Windows path overrides
├── Caddyfile.dev                     # Development reverse proxy
├── Brewfile.dev                      # Homebrew dependencies (macOS)
├── .env.example                      # Updated environment template
├── monitoring/
│   ├── prometheus.yml                # Prometheus config
│   ├── grafana.ini                   # Grafana settings
│   └── dashboards/                   # Pre-configured dashboards
├── scripts/
│   ├── setup-native-dev.sh           # Platform-aware installation
│   ├── install-exporters-linux.sh    # Linux exporter binaries
│   └── health-checks/                # Custom health check scripts
└── Makefile                          # Updated targets (no docker)
```

## Process Compose Configuration

### Main Configuration (`process-compose.yaml`)

```yaml
version: "0.5"

# Global settings
log_location: .process-compose/logs
log_level: info
shell:
  command: "/bin/bash"
  args: ["-c"]

environment:
  - "PYTHONUNBUFFERED=1"
  - "GO_ENV=development"
  - "LOG_FORMAT=json"

processes:
  #############################################################################
  # Layer 1: Infrastructure Services
  #############################################################################

  postgres:
    command: "postgres -D /opt/homebrew/var/postgresql@17"
    availability:
      restart: on_failure
      max_restarts: 5
      backoff_seconds: 2
    readiness_probe:
      exec:
        command: "pg_isready -h localhost -p 5432 -U tracertm"
      initial_delay_seconds: 2
      period_seconds: 5
      timeout_seconds: 3
      success_threshold: 1
      failure_threshold: 3
    environment:
      - "PGDATA=/opt/homebrew/var/postgresql@17"
      - "PGPORT=5432"

  redis:
    command: "redis-server /opt/homebrew/etc/redis.conf"
    availability:
      restart: on_failure
      max_restarts: 5
    readiness_probe:
      exec:
        command: "redis-cli -h localhost -p 6379 ping"
      initial_delay_seconds: 1
      period_seconds: 5
      timeout_seconds: 2

  neo4j:
    command: "neo4j console"
    availability:
      restart: on_failure
      max_restarts: 3
    readiness_probe:
      http_get:
        host: localhost
        port: 7474
        path: /
      initial_delay_seconds: 10
      period_seconds: 10
      timeout_seconds: 5
    environment:
      - "NEO4J_AUTH=neo4j/${NEO4J_PASSWORD:-password}"
      - "NEO4J_ACCEPT_LICENSE_AGREEMENT=yes"

  nats:
    command: "nats-server -js -m 8222 -p 4222 -D"
    availability:
      restart: on_failure
      max_restarts: 5
    readiness_probe:
      http_get:
        host: localhost
        port: 8222
        path: /healthz
      initial_delay_seconds: 2
      period_seconds: 5

  #############################################################################
  # Layer 2: Workflow & Monitoring
  #############################################################################

  temporal:
    command: "temporal server start-dev --db-filename .temporal/temporal.db"
    working_dir: "."
    depends_on:
      postgres:
        condition: process_healthy
    availability:
      restart: on_failure
      max_restarts: 3
    readiness_probe:
      http_get:
        host: localhost
        port: 7233
        path: /
      initial_delay_seconds: 5
      period_seconds: 10
      timeout_seconds: 5
    environment:
      - "TEMPORAL_CLI_ADDRESS=localhost:7233"

  prometheus:
    command: "prometheus --config.file=monitoring/prometheus.yml --storage.tsdb.path=.prometheus --web.console.libraries=/opt/homebrew/share/prometheus/console_libraries --web.console.templates=/opt/homebrew/share/prometheus/consoles --web.enable-lifecycle"
    availability:
      restart: on_failure
    readiness_probe:
      http_get:
        host: localhost
        port: 9090
        path: /-/ready
      initial_delay_seconds: 3
      period_seconds: 10

  #############################################################################
  # Layer 3: Exporters
  #############################################################################

  postgres-exporter:
    command: "postgres_exporter"
    depends_on:
      postgres:
        condition: process_healthy
    environment:
      - "DATA_SOURCE_NAME=postgresql://tracertm:${DB_PASSWORD:-tracertm_password}@localhost:5432/tracertm?sslmode=disable"
    readiness_probe:
      http_get:
        host: localhost
        port: 9187
        path: /metrics
      initial_delay_seconds: 2

  redis-exporter:
    command: "redis_exporter --redis.addr=redis://localhost:6379"
    depends_on:
      redis:
        condition: process_healthy
    readiness_probe:
      http_get:
        host: localhost
        port: 9121
        path: /metrics
      initial_delay_seconds: 2

  node-exporter:
    command: "node_exporter"
    readiness_probe:
      http_get:
        host: localhost
        port: 9100
        path: /metrics
      initial_delay_seconds: 1

  #############################################################################
  # Layer 4: Application Services
  #############################################################################

  go-backend:
    command: "air -c .air.toml"
    working_dir: "./backend"
    depends_on:
      postgres:
        condition: process_healthy
      redis:
        condition: process_healthy
      nats:
        condition: process_healthy
      temporal:
        condition: process_healthy
    availability:
      restart: on_failure
      max_restarts: 5
    readiness_probe:
      http_get:
        host: localhost
        port: 8080
        path: /health
      initial_delay_seconds: 5
      period_seconds: 10
      timeout_seconds: 3
    environment:
      - "DB_HOST=localhost"
      - "DB_PORT=5432"
      - "DB_USER=tracertm"
      - "DB_PASSWORD=${DB_PASSWORD:-tracertm_password}"
      - "DB_NAME=tracertm"
      - "REDIS_URL=redis://localhost:6379"
      - "NATS_URL=nats://localhost:4222"
      - "TEMPORAL_HOST=localhost:7233"
      - "PORT=8080"
      - "GIN_MODE=debug"
      - "PYTHON_BACKEND_URL=http://localhost:8000"

  python-backend:
    command: "uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
    working_dir: "."
    depends_on:
      postgres:
        condition: process_healthy
      redis:
        condition: process_healthy
      nats:
        condition: process_healthy
      temporal:
        condition: process_healthy
    availability:
      restart: on_failure
      max_restarts: 5
    readiness_probe:
      http_get:
        host: localhost
        port: 8000
        path: /health
      initial_delay_seconds: 5
      period_seconds: 10
    environment:
      - "DATABASE_URL=postgresql+asyncpg://tracertm:${DB_PASSWORD:-tracertm_password}@localhost:5432/tracertm"
      - "REDIS_URL=redis://localhost:6379"
      - "NATS_URL=nats://localhost:4222"
      - "TEMPORAL_HOST=localhost:7233"
      - "LOG_LEVEL=${LOG_LEVEL:-INFO}"
      - "GO_BACKEND_URL=http://localhost:8080"
      - "OPENAI_API_KEY=${OPENAI_API_KEY:-}"
      - "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}"

  #############################################################################
  # Layer 5: Gateway & Visualization
  #############################################################################

  caddy:
    command: "caddy run --config Caddyfile.dev --adapter caddyfile"
    depends_on:
      go-backend:
        condition: process_healthy
      python-backend:
        condition: process_healthy
    availability:
      restart: on_failure
    readiness_probe:
      http_get:
        host: localhost
        port: 4000
        path: /health
      initial_delay_seconds: 2
      period_seconds: 10

  grafana:
    command: "grafana-server --config monitoring/grafana.ini --homepath /opt/homebrew/share/grafana"
    depends_on:
      prometheus:
        condition: process_healthy
    availability:
      restart: on_failure
    readiness_probe:
      http_get:
        host: localhost
        port: 3000
        path: /api/health
      initial_delay_seconds: 3
      period_seconds: 10
    environment:
      - "GF_SERVER_HTTP_PORT=3000"
      - "GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}"
      - "GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}"
      - "GF_INSTALL_PLUGINS=redis-datasource"
```

### Platform Overrides

**Linux (`process-compose.linux.yaml`):**
```yaml
version: "0.5"

processes:
  postgres:
    command: "postgres -D /var/lib/postgresql/17/main"
    environment:
      - "PGDATA=/var/lib/postgresql/17/main"

  redis:
    command: "redis-server /etc/redis/redis.conf"

  neo4j:
    command: "/usr/share/neo4j/bin/neo4j console"

  prometheus:
    command: "prometheus --config.file=monitoring/prometheus.yml --storage.tsdb.path=.prometheus --web.console.libraries=/usr/share/prometheus/console_libraries --web.console.templates=/usr/share/prometheus/consoles --web.enable-lifecycle"

  grafana:
    command: "grafana-server --config monitoring/grafana.ini --homepath /usr/share/grafana"
```

**Windows (`process-compose.windows.yaml`):**
```yaml
version: "0.5"

shell:
  command: "powershell"
  args: ["-Command"]

processes:
  postgres:
    command: "pg_ctl -D C:\\Program Files\\PostgreSQL\\17\\data start"

  redis:
    command: "redis-server C:\\Program Files\\Redis\\redis.conf"

  # Neo4j, NATS, etc. with Windows paths
```

## Caddy Configuration

**`Caddyfile.dev`:**
```caddyfile
{
    auto_https off
    admin localhost:2019
}

:4000 {
    # Health check endpoint
    handle /health {
        respond "OK" 200
    }

    # Go Backend API
    handle /api/v1/* {
        reverse_proxy localhost:8080
    }

    # Python Backend API
    handle /api/py/* {
        reverse_proxy localhost:8000
    }

    # WebSocket support
    handle /ws/* {
        reverse_proxy localhost:8080 {
            header_up Upgrade {>Upgrade}
            header_up Connection {>Connection}
        }
    }

    # API Documentation
    handle /docs* {
        reverse_proxy localhost:8080
    }

    # Prometheus (admin only)
    handle /prometheus/* {
        reverse_proxy localhost:9090
    }

    # Grafana
    handle /grafana/* {
        reverse_proxy localhost:3000
    }

    # Default - could proxy to frontend in future
    handle {
        respond "TraceRTM API Gateway" 200
    }

    # Logging
    log {
        output file .process-compose/logs/caddy-access.log
        format json
    }
}
```

## Monitoring Configuration

**`monitoring/prometheus.yml`:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # PostgreSQL
  - job_name: 'postgresql'
    static_configs:
      - targets: ['localhost:9187']

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']

  # Node/System
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  # Go Backend
  - job_name: 'go-backend'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'

  # Python Backend
  - job_name: 'python-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  # Caddy
  - job_name: 'caddy'
    static_configs:
      - targets: ['localhost:2019']
    metrics_path: '/metrics'

  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

**`monitoring/grafana.ini`:**
```ini
[server]
http_port = 3000
root_url = http://localhost:4000/grafana/

[database]
type = sqlite3
path = .grafana/grafana.db

[security]
admin_user = admin
admin_password = admin

[auth.anonymous]
enabled = false

[dashboards]
default_home_dashboard_path = monitoring/dashboards/tracertm-overview.json

[provisioning]
datasources = monitoring/datasources
dashboards = monitoring/dashboards
```

## Installation Scripts

### `scripts/setup-native-dev.sh`

```bash
#!/bin/bash
set -euo pipefail

PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

echo "🚀 TraceRTM Native Development Setup"
echo "Platform: $PLATFORM ($ARCH)"
echo ""

# Detect package manager
detect_package_manager() {
  if command -v brew &> /dev/null; then
    echo "homebrew"
  elif command -v apt-get &> /dev/null; then
    echo "apt"
  elif command -v yum &> /dev/null; then
    echo "yum"
  elif command -v scoop &> /dev/null; then
    echo "scoop"
  else
    echo "unknown"
  fi
}

PKG_MGR=$(detect_package_manager)
echo "📦 Package Manager: $PKG_MGR"
echo ""

# Install Process Compose
install_process_compose() {
  echo "Installing Process Compose..."
  case $PKG_MGR in
    homebrew)
      brew install f1bonacc1/tap/process-compose
      ;;
    apt)
      wget -q https://github.com/F1bonacc1/process-compose/releases/latest/download/process-compose_linux_${ARCH}.tar.gz
      tar -xzf process-compose_linux_${ARCH}.tar.gz
      sudo mv process-compose /usr/local/bin/
      rm process-compose_linux_${ARCH}.tar.gz
      ;;
    scoop)
      scoop install process-compose
      ;;
    *)
      echo "❌ Unsupported package manager. Install Process Compose manually:"
      echo "   https://github.com/F1bonacc1/process-compose"
      exit 1
      ;;
  esac
}

# Install services via Homebrew (macOS/Linux)
install_homebrew_services() {
  echo "📦 Installing services via Homebrew..."

  cat > Brewfile.dev <<EOF
# Core databases
brew "postgresql@17"
brew "redis"
brew "neo4j"

# Message broker
brew "nats-server"

# Workflow engine
brew "temporal"

# Reverse proxy
brew "caddy"

# Monitoring stack
brew "prometheus"
brew "grafana"

# Exporters
brew "postgres_exporter"
brew "redis_exporter"
brew "node_exporter"

# Process orchestration
brew "f1bonacc1/tap/process-compose"

# Development tools
brew "air"  # Go hot reload
EOF

  brew bundle --file=Brewfile.dev

  echo "✅ Homebrew packages installed"
}

# Install services via APT (Ubuntu/Debian)
install_apt_services() {
  echo "📦 Installing services via APT..."

  sudo apt-get update
  sudo apt-get install -y \
    postgresql-17 \
    postgresql-client-17 \
    redis-server \
    prometheus \
    grafana

  # Neo4j (from official repo)
  wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
  echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
  sudo apt-get update
  sudo apt-get install -y neo4j

  # NATS (binary download)
  wget https://github.com/nats-io/nats-server/releases/latest/download/nats-server-linux-${ARCH}.tar.gz
  tar -xzf nats-server-linux-${ARCH}.tar.gz
  sudo mv nats-server-*/nats-server /usr/local/bin/
  rm -rf nats-server-*

  # Temporal (binary download)
  wget https://github.com/temporalio/cli/releases/latest/download/temporal_cli_linux_${ARCH}.tar.gz
  tar -xzf temporal_cli_linux_${ARCH}.tar.gz
  sudo mv temporal /usr/local/bin/
  rm temporal_cli_linux_${ARCH}.tar.gz

  # Caddy
  sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
  sudo apt update
  sudo apt install -y caddy

  # Exporters
  bash scripts/install-exporters-linux.sh

  echo "✅ APT packages installed"
}

# Platform-specific installation
case $PKG_MGR in
  homebrew)
    install_homebrew_services
    ;;
  apt)
    install_apt_services
    install_process_compose
    ;;
  scoop)
    echo "📦 Installing via Scoop..."
    scoop bucket add extras
    scoop install postgresql redis prometheus grafana caddy
    install_process_compose
    ;;
  *)
    echo "❌ Unsupported platform: $PLATFORM"
    exit 1
    ;;
esac

# Initialize PostgreSQL database
echo ""
echo "🗄️  Initializing PostgreSQL..."
case $PKG_MGR in
  homebrew)
    brew services start postgresql@17
    sleep 3
    createdb tracertm || echo "Database 'tracertm' already exists"
    createuser tracertm || echo "User 'tracertm' already exists"
    psql -d tracertm -c "ALTER USER tracertm WITH PASSWORD 'tracertm_password';" || true
    ;;
  apt)
    sudo systemctl start postgresql
    sudo -u postgres createdb tracertm || echo "Database 'tracertm' already exists"
    sudo -u postgres createuser tracertm || echo "User 'tracertm' already exists"
    sudo -u postgres psql -c "ALTER USER tracertm WITH PASSWORD 'tracertm_password';" || true
    ;;
esac

# Run database migrations
if [ -f "alembic.ini" ]; then
  echo ""
  echo "🔄 Running database migrations..."
  alembic upgrade head || echo "⚠️  Migrations failed - run manually with: alembic upgrade head"
fi

# Create necessary directories
echo ""
echo "📁 Creating working directories..."
mkdir -p .process-compose/logs
mkdir -p .prometheus
mkdir -p .grafana
mkdir -p .temporal

# Verify installation
echo ""
echo "✅ Verifying installation..."

MISSING=""
command -v process-compose >/dev/null || MISSING="$MISSING process-compose"
command -v postgres >/dev/null || MISSING="$MISSING postgres"
command -v redis-server >/dev/null || MISSING="$MISSING redis-server"
command -v caddy >/dev/null || MISSING="$MISSING caddy"
command -v prometheus >/dev/null || MISSING="$MISSING prometheus"
command -v grafana-server >/dev/null || MISSING="$MISSING grafana-server"

if [ -n "$MISSING" ]; then
  echo "❌ Missing tools:$MISSING"
  echo "Please install them manually."
  exit 1
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure"
echo "  2. Start services: make dev"
echo "  3. Access at: http://localhost:4000"
echo ""
```

### `scripts/install-exporters-linux.sh`

```bash
#!/bin/bash
set -euo pipefail

ARCH=$(uname -m)
BIN_DIR="/usr/local/bin"

echo "Installing Prometheus exporters for Linux..."

# Postgres Exporter
echo "- postgres_exporter"
wget -q https://github.com/prometheus-community/postgres_exporter/releases/latest/download/postgres_exporter-*linux-${ARCH}.tar.gz -O postgres_exporter.tar.gz
tar -xzf postgres_exporter.tar.gz
sudo mv postgres_exporter-*/postgres_exporter $BIN_DIR/
rm -rf postgres_exporter*

# Redis Exporter
echo "- redis_exporter"
wget -q https://github.com/oliver006/redis_exporter/releases/latest/download/redis_exporter-*linux-${ARCH}.tar.gz -O redis_exporter.tar.gz
tar -xzf redis_exporter.tar.gz
sudo mv redis_exporter-*/redis_exporter $BIN_DIR/
rm -rf redis_exporter*

# Node Exporter
echo "- node_exporter"
wget -q https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-*linux-${ARCH}.tar.gz -O node_exporter.tar.gz
tar -xzf node_exporter.tar.gz
sudo mv node_exporter-*/node_exporter $BIN_DIR/
rm -rf node_exporter*

echo "✅ Exporters installed to $BIN_DIR"
```

## Makefile Updates

**Complete replacement (no backward compatibility):**

```makefile
.PHONY: help dev dev-tui dev-down dev-logs dev-restart dev-status install-native

# Platform detection
PLATFORM := $(shell uname -s | tr '[:upper:]' '[:lower:]')
ARCH := $(shell uname -m)

# Process Compose config selection
ifeq ($(PLATFORM),linux)
    PC_CONFIG := -f process-compose.linux.yaml
else ifeq ($(findstring mingw,$(PLATFORM)),mingw)
    PC_CONFIG := -f process-compose.windows.yaml
else
    PC_CONFIG :=
endif

# Colors
GREEN  := \033[0;32m
YELLOW := \033[1;33m
NC     := \033[0m

help: ## Show this help
	@echo '$(GREEN)TraceRTM - Native Development$(NC)'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

#############################################################################
# Installation
#############################################################################

install-native: ## Install all native dependencies (one-time setup)
	@echo '$(GREEN)Installing native development dependencies...$(NC)'
	@bash scripts/setup-native-dev.sh

verify-install: ## Verify installation
	@echo '$(GREEN)Verifying installation...$(NC)'
	@command -v process-compose >/dev/null || { echo "❌ process-compose not found"; exit 1; }
	@command -v postgres >/dev/null || { echo "❌ postgres not found"; exit 1; }
	@command -v redis-server >/dev/null || { echo "❌ redis not found"; exit 1; }
	@command -v caddy >/dev/null || { echo "❌ caddy not found"; exit 1; }
	@command -v prometheus >/dev/null || { echo "❌ prometheus not found"; exit 1; }
	@echo '$(GREEN)✅ All tools installed$(NC)'

#############################################################################
# Development
#############################################################################

dev: ## Start all services (detached)
	@echo '$(GREEN)Starting TraceRTM development environment...$(NC)'
	@process-compose $(PC_CONFIG) up -d
	@echo ''
	@echo '$(GREEN)Services available at:$(NC)'
	@echo '  Gateway:    http://localhost:4000'
	@echo '  Go API:     http://localhost:8080'
	@echo '  Python API: http://localhost:8000'
	@echo '  Grafana:    http://localhost:3000'
	@echo '  Prometheus: http://localhost:9090'
	@echo '  Neo4j:      http://localhost:7474'
	@echo ''
	@echo 'View dashboard: make dev-tui'
	@echo 'View logs:      make dev-logs'

dev-tui: ## Start with interactive TUI dashboard
	@process-compose $(PC_CONFIG) up

dev-down: ## Stop all services
	@echo '$(GREEN)Stopping all services...$(NC)'
	@process-compose $(PC_CONFIG) down

dev-logs: ## Show logs for all services
	@process-compose $(PC_CONFIG) logs

dev-logs-follow: ## Follow logs (optionally for specific service)
	@if [ -z "$(SERVICE)" ]; then \
		process-compose $(PC_CONFIG) logs -f; \
	else \
		process-compose $(PC_CONFIG) logs -f $(SERVICE); \
	fi

dev-restart: ## Restart specific service (make dev-restart SERVICE=postgres)
	@if [ -z "$(SERVICE)" ]; then \
		echo "Usage: make dev-restart SERVICE=<service-name>"; \
		exit 1; \
	fi
	@process-compose $(PC_CONFIG) restart $(SERVICE)

dev-status: ## Show service status
	@process-compose $(PC_CONFIG) process list

dev-scale: ## Scale a service (make dev-scale SERVICE=worker REPLICAS=3)
	@if [ -z "$(SERVICE)" ] || [ -z "$(REPLICAS)" ]; then \
		echo "Usage: make dev-scale SERVICE=<name> REPLICAS=<count>"; \
		exit 1; \
	fi
	@process-compose $(PC_CONFIG) scale $(SERVICE)=$(REPLICAS)

#############################################################################
# Database
#############################################################################

db-migrate: ## Run database migrations
	@echo '$(GREEN)Running database migrations...$(NC)'
	@alembic upgrade head

db-rollback: ## Rollback last migration
	@alembic downgrade -1

db-reset: ## Reset database (destructive!)
	@echo '$(YELLOW)⚠️  This will destroy all data!$(NC)'
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		alembic downgrade base && alembic upgrade head; \
	fi

db-shell: ## Open PostgreSQL shell
	@psql -h localhost -U tracertm -d tracertm

#############################################################################
# Testing
#############################################################################

test: ## Run all tests
	@echo '$(GREEN)Running Python tests...$(NC)'
	@pytest tests/ -v
	@echo '$(GREEN)Running Go tests...$(NC)'
	@cd backend && go test -v ./...

test-python: ## Run Python tests with coverage
	@pytest tests/ -v --cov=src/tracertm --cov-report=html

test-go: ## Run Go tests with coverage
	@cd backend && go test -v -race -coverprofile=coverage.out ./...

test-integration: ## Run integration tests
	@pytest tests/ -v -m integration

#############################################################################
# Code Quality
#############################################################################

lint: ## Run linters
	@echo '$(GREEN)Linting Python...$(NC)'
	@ruff check src/ tests/
	@echo '$(GREEN)Linting Go...$(NC)'
	@cd backend && golangci-lint run

format: ## Format code
	@echo '$(GREEN)Formatting Python...$(NC)'
	@ruff format src/ tests/
	@echo '$(GREEN)Formatting Go...$(NC)'
	@cd backend && gofmt -s -w .

type-check: ## Type checking
	@mypy src/

#############################################################################
# Utilities
#############################################################################

clean: ## Clean build artifacts and logs
	@echo '$(GREEN)Cleaning build artifacts...$(NC)'
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .process-compose/logs/*
	@rm -rf htmlcov/
	@cd backend && go clean

logs-clean: ## Clean all service logs
	@rm -rf .process-compose/logs/*

data-clean: ## Clean all data directories (destructive!)
	@echo '$(YELLOW)⚠️  This will delete all local data!$(NC)'
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf .prometheus/* .grafana/* .temporal/*; \
	fi

#############################################################################
# Monitoring
#############################################################################

grafana-dashboard: ## Open Grafana in browser
	@open http://localhost:3000 || xdg-open http://localhost:3000 || echo "Open http://localhost:3000"

prometheus-ui: ## Open Prometheus in browser
	@open http://localhost:9090 || xdg-open http://localhost:9090 || echo "Open http://localhost:9090"

metrics: ## Show quick metrics summary
	@echo '$(GREEN)Service Metrics:$(NC)'
	@curl -s http://localhost:9090/api/v1/query?query=up | jq -r '.data.result[] | "\(.metric.job): \(.value[1])"' 2>/dev/null || echo "Prometheus not available"

.DEFAULT_GOAL := help
```

## Environment Variables

**`.env.example`:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://tracertm:tracertm_password@localhost:5432/tracertm
DB_USER=tracertm
DB_PASSWORD=tracertm_password
DB_NAME=tracertm

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password

# NATS
NATS_URL=nats://localhost:4222

# Temporal
TEMPORAL_HOST=localhost:7233

# Monitoring
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin

# Application
LOG_LEVEL=INFO
GO_ENV=development
GIN_MODE=debug

# AI Services (optional)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# WorkOS Auth (optional)
WORKOS_API_KEY=
WORKOS_CLIENT_ID=
```

## Migration Strategy

### Phase 1: Setup & Verification (Week 1)
1. Install Process Compose and native services
2. Create `process-compose.yaml` configuration
3. Set up Caddy reverse proxy
4. Configure monitoring stack
5. Verify all services start successfully

### Phase 2: Platform Testing (Week 1)
1. Test on macOS (primary platform)
2. Test on Linux (Ubuntu/Debian)
3. Test on Windows (if needed)
4. Document platform-specific issues

### Phase 3: Developer Onboarding (Week 2)
1. Update documentation (README, setup guides)
2. Run installation script with team member
3. Gather feedback on developer experience
4. Iterate on configuration

### Phase 4: Production Consideration (Future)
1. Document production deployment options
2. Consider systemd units for Linux servers
3. Evaluate Docker for production vs native
4. Plan migration strategy for existing deployments

## Success Criteria

- [ ] All services start via `make dev`
- [ ] Process Compose TUI shows all services healthy
- [ ] Caddy reverse proxy accessible at `:4000`
- [ ] Grafana dashboards show metrics from all services
- [ ] Hot reload works for Go and Python backends
- [ ] Cross-platform compatibility verified
- [ ] Installation script completes without errors
- [ ] Team members can onboard in < 15 minutes
- [ ] Resource usage < 30% of Docker-based setup
- [ ] No loss of functionality vs Docker setup

## Risk Mitigation

**Risk: Platform compatibility issues**
- Mitigation: Platform-specific config files, extensive testing

**Risk: Service dependency failures**
- Mitigation: Robust health checks, clear error messages

**Risk: Developer resistance to change**
- Mitigation: Keep setup simple, provide migration guide, show benefits

**Risk: Missing Docker features**
- Mitigation: Document any limitations upfront, provide workarounds

**Risk: Production deployment complexity**
- Mitigation: Keep Docker option for production, native for dev only

## Future Enhancements

1. **Process Compose v2 features** - Scheduled tasks, advanced scaling
2. **Custom health check scripts** - More sophisticated readiness checks
3. **Performance profiling** - Compare resource usage vs Docker
4. **Integration with IDEs** - VSCode/JetBrains task integration
5. **Cloud development** - Remote development server setup
6. **Multi-environment configs** - dev/staging/test configurations

## Conclusion

This design provides a comprehensive native process orchestration solution that eliminates Docker daemon overhead while maintaining the convenience of docker-compose-like configuration. The cross-platform approach ensures consistency across macOS, Linux, and Windows development environments while optimizing for the primary macOS platform.

The phased migration approach allows for iterative refinement and team feedback before full commitment, ensuring a smooth transition with minimal disruption to ongoing development work.
