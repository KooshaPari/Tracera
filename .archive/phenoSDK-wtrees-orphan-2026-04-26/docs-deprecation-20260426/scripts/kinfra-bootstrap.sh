#!/bin/bash
"""
KInfra Bootstrap Script: Environment Setup and Dependency Installation

This script sets up the development and production environment for KInfra,
installing all necessary dependencies and tools for Phase 5 features.

Usage:
    ./scripts/kinfra-bootstrap.sh [options]

Options:
    --dev              Set up development environment
    --prod             Set up production environment
    --tunnel-tools     Install tunnel tools (cloudflared, ngrok, localtunnel)
    --monitoring       Install monitoring tools (prometheus, grafana)
    --docker           Set up Docker environment
    --all              Set up complete environment (default)
    --force            Force reinstallation of existing tools
    --verbose          Verbose output
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEV_MODE=false
PROD_MODE=false
TUNNEL_TOOLS=false
MONITORING=false
DOCKER=false
ALL_MODE=true
FORCE=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEV_MODE=true
            ALL_MODE=false
            shift
            ;;
        --prod)
            PROD_MODE=true
            ALL_MODE=false
            shift
            ;;
        --tunnel-tools)
            TUNNEL_TOOLS=true
            ALL_MODE=false
            shift
            ;;
        --monitoring)
            MONITORING=true
            ALL_MODE=false
            shift
            ;;
        --docker)
            DOCKER=true
            ALL_MODE=false
            shift
            ;;
        --all)
            ALL_MODE=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "KInfra Bootstrap Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --dev              Set up development environment"
            echo "  --prod             Set up production environment"
            echo "  --tunnel-tools     Install tunnel tools (cloudflared, ngrok, localtunnel)"
            echo "  --monitoring       Install monitoring tools (prometheus, grafana)"
            echo "  --docker           Set up Docker environment"
            echo "  --all              Set up complete environment (default)"
            echo "  --force            Force reinstallation of existing tools"
            echo "  --verbose          Verbose output"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set verbose mode
if [ "$VERBOSE" = true ]; then
    set -x
fi

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if tool is installed
tool_installed() {
    if command_exists "$1"; then
        if [ "$FORCE" = true ]; then
            return 1
        else
            return 0
        fi
    else
        return 1
    fi
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."
    
    # Check if Python 3.11+ is available
    if ! command_exists python3; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [ "$(echo "$python_version < 3.11" | bc -l)" -eq 1 ]; then
        log_error "Python 3.11+ is required, found $python_version"
        exit 1
    fi
    
    # Install pip if not available
    if ! command_exists pip3; then
        log_info "Installing pip..."
        curl -sS https://bootstrap.pypa.io/get-pip.py | python3
    fi
    
    # Install basic dependencies
    log_info "Installing basic Python packages..."
    pip3 install --upgrade pip setuptools wheel
    
    # Install KInfra dependencies
    if [ -f "requirements.txt" ]; then
        log_info "Installing KInfra requirements..."
        pip3 install -r requirements.txt
    fi
    
    # Install development dependencies
    if [ "$DEV_MODE" = true ] || [ "$ALL_MODE" = true ]; then
        log_info "Installing development dependencies..."
        pip3 install pytest pytest-asyncio pytest-cov pytest-mock
        pip3 install black isort ruff mypy bandit
        pip3 install pre-commit
        pip3 install sphinx sphinx-rtd-theme
    fi
    
    log_success "Python dependencies installed"
}

# Install tunnel tools
install_tunnel_tools() {
    log_info "Installing tunnel tools..."
    
    # Install cloudflared
    if ! tool_installed cloudflared; then
        log_info "Installing cloudflared..."
        case "$(uname -s)" in
            Linux*)
                if command_exists apt-get; then
                    # Ubuntu/Debian
                    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
                    sudo dpkg -i cloudflared-linux-amd64.deb
                    rm cloudflared-linux-amd64.deb
                elif command_exists yum; then
                    # CentOS/RHEL
                    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.rpm
                    sudo rpm -i cloudflared-linux-amd64.rpm
                    rm cloudflared-linux-amd64.rpm
                else
                    log_warning "Unsupported Linux distribution, please install cloudflared manually"
                fi
                ;;
            Darwin*)
                if command_exists brew; then
                    brew install cloudflared
                else
                    log_warning "Homebrew not found, please install cloudflared manually"
                fi
                ;;
            *)
                log_warning "Unsupported operating system, please install cloudflared manually"
                ;;
        esac
    else
        log_info "cloudflared already installed"
    fi
    
    # Install ngrok
    if ! tool_installed ngrok; then
        log_info "Installing ngrok..."
        case "$(uname -s)" in
            Linux*)
                wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
                tar -xzf ngrok-v3-stable-linux-amd64.tgz
                sudo mv ngrok /usr/local/bin/
                rm ngrok-v3-stable-linux-amd64.tgz
                ;;
            Darwin*)
                if command_exists brew; then
                    brew install ngrok/ngrok/ngrok
                else
                    log_warning "Homebrew not found, please install ngrok manually"
                fi
                ;;
            *)
                log_warning "Unsupported operating system, please install ngrok manually"
                ;;
        esac
    else
        log_info "ngrok already installed"
    fi
    
    # Install localtunnel
    if ! tool_installed lt; then
        log_info "Installing localtunnel..."
        if command_exists npm; then
            npm install -g localtunnel
        else
            log_warning "npm not found, please install localtunnel manually"
        fi
    else
        log_info "localtunnel already installed"
    fi
    
    log_success "Tunnel tools installed"
}

# Install monitoring tools
install_monitoring_tools() {
    log_info "Installing monitoring tools..."
    
    # Install Prometheus
    if ! tool_installed prometheus; then
        log_info "Installing Prometheus..."
        case "$(uname -s)" in
            Linux*)
                wget -q https://github.com/prometheus/prometheus/releases/latest/download/prometheus-2.45.0.linux-amd64.tar.gz
                tar -xzf prometheus-2.45.0.linux-amd64.tar.gz
                sudo mv prometheus-2.45.0.linux-amd64/prometheus /usr/local/bin/
                sudo mv prometheus-2.45.0.linux-amd64/promtool /usr/local/bin/
                rm -rf prometheus-2.45.0.linux-amd64*
                ;;
            Darwin*)
                if command_exists brew; then
                    brew install prometheus
                else
                    log_warning "Homebrew not found, please install Prometheus manually"
                fi
                ;;
            *)
                log_warning "Unsupported operating system, please install Prometheus manually"
                ;;
        esac
    else
        log_info "Prometheus already installed"
    fi
    
    # Install Grafana
    if ! tool_installed grafana-server; then
        log_info "Installing Grafana..."
        case "$(uname -s)" in
            Linux*)
                if command_exists apt-get; then
                    # Ubuntu/Debian
                    wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
                    echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
                    sudo apt-get update
                    sudo apt-get install -y grafana
                elif command_exists yum; then
                    # CentOS/RHEL
                    sudo yum install -y https://dl.grafana.com/oss/release/grafana-10.0.0-1.x86_64.rpm
                else
                    log_warning "Unsupported Linux distribution, please install Grafana manually"
                fi
                ;;
            Darwin*)
                if command_exists brew; then
                    brew install grafana
                else
                    log_warning "Homebrew not found, please install Grafana manually"
                fi
                ;;
            *)
                log_warning "Unsupported operating system, please install Grafana manually"
                ;;
        esac
    else
        log_info "Grafana already installed"
    fi
    
    log_success "Monitoring tools installed"
}

# Set up Docker environment
setup_docker() {
    log_info "Setting up Docker environment..."
    
    # Check if Docker is installed
    if ! command_exists docker; then
        log_info "Installing Docker..."
        case "$(uname -s)" in
            Linux*)
                if command_exists apt-get; then
                    # Ubuntu/Debian
                    curl -fsSL https://get.docker.com -o get-docker.sh
                    sudo sh get-docker.sh
                    sudo usermod -aG docker $USER
                    rm get-docker.sh
                elif command_exists yum; then
                    # CentOS/RHEL
                    sudo yum install -y docker
                    sudo systemctl start docker
                    sudo systemctl enable docker
                    sudo usermod -aG docker $USER
                else
                    log_warning "Unsupported Linux distribution, please install Docker manually"
                fi
                ;;
            Darwin*)
                log_warning "Please install Docker Desktop for macOS from https://www.docker.com/products/docker-desktop"
                ;;
            *)
                log_warning "Unsupported operating system, please install Docker manually"
                ;;
        esac
    else
        log_info "Docker already installed"
    fi
    
    # Check if Docker Compose is installed
    if ! command_exists docker-compose; then
        log_info "Installing Docker Compose..."
        case "$(uname -s)" in
            Linux*)
                sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                sudo chmod +x /usr/local/bin/docker-compose
                ;;
            Darwin*)
                if command_exists brew; then
                    brew install docker-compose
                else
                    log_warning "Homebrew not found, please install Docker Compose manually"
                fi
                ;;
            *)
                log_warning "Unsupported operating system, please install Docker Compose manually"
                ;;
        esac
    else
        log_info "Docker Compose already installed"
    fi
    
    # Create Docker network for KInfra
    if ! docker network ls | grep -q kinfra; then
        log_info "Creating KInfra Docker network..."
        docker network create kinfra
    else
        log_info "KInfra Docker network already exists"
    fi
    
    log_success "Docker environment set up"
}

# Set up development environment
setup_dev_environment() {
    log_info "Setting up development environment..."
    
    # Install pre-commit hooks
    if command_exists pre-commit; then
        log_info "Installing pre-commit hooks..."
        pre-commit install
    else
        log_warning "pre-commit not found, skipping hook installation"
    fi
    
    # Create development configuration
    log_info "Creating development configuration..."
    mkdir -p ~/.kinfra/config
    cat > ~/.kinfra/config/kinfra.yaml << EOF
app_name: "kinfra-dev"
debug: true
log_level: "DEBUG"
environment: "development"

process_governance:
  enable_metadata_tracking: true
  max_process_age: 3600.0
  cleanup_interval: 300.0
  force_cleanup: false

tunnel_governance:
  default_lifecycle_policy: "smart"
  tunnel_reuse_threshold: 1800.0
  max_tunnel_age: 7200.0
  credential_scope: "project"

global_cleanup_policy:
  default_strategy: "conservative"
  max_concurrent_cleanups: 5
  cleanup_timeout: 300.0
  enabled: true

status_pages:
  auto_refresh_interval: 5
  include_service_details: true
  include_tunnel_details: true
  include_health_metrics: true
  theme: "default"
EOF
    
    # Create development scripts
    log_info "Creating development scripts..."
    mkdir -p scripts/dev
    
    cat > scripts/dev/start-dev.sh << 'EOF'
#!/bin/bash
# Start development environment

echo "Starting KInfra development environment..."

# Start Redis
if command -v redis-server >/dev/null 2>&1; then
    redis-server --daemonize yes --port 6379
    echo "Redis started on port 6379"
fi

# Start PostgreSQL
if command -v postgres >/dev/null 2>&1; then
    pg_ctl -D /usr/local/var/postgres start
    echo "PostgreSQL started"
fi

# Start NATS
if command -v nats-server >/dev/null 2>&1; then
    nats-server --port 4222 --daemon
    echo "NATS started on port 4222"
fi

echo "Development environment ready!"
EOF
    
    chmod +x scripts/dev/start-dev.sh
    
    cat > scripts/dev/stop-dev.sh << 'EOF'
#!/bin/bash
# Stop development environment

echo "Stopping KInfra development environment..."

# Stop Redis
if command -v redis-cli >/dev/null 2>&1; then
    redis-cli shutdown
    echo "Redis stopped"
fi

# Stop PostgreSQL
if command -v pg_ctl >/dev/null 2>&1; then
    pg_ctl -D /usr/local/var/postgres stop
    echo "PostgreSQL stopped"
fi

# Stop NATS
if command -v nats-server >/dev/null 2>&1; then
    pkill nats-server
    echo "NATS stopped"
fi

echo "Development environment stopped!"
EOF
    
    chmod +x scripts/dev/stop-dev.sh
    
    log_success "Development environment set up"
}

# Set up production environment
setup_prod_environment() {
    log_info "Setting up production environment..."
    
    # Create production configuration
    log_info "Creating production configuration..."
    mkdir -p ~/.kinfra/config
    cat > ~/.kinfra/config/kinfra.yaml << EOF
app_name: "kinfra-prod"
debug: false
log_level: "INFO"
environment: "production"

process_governance:
  enable_metadata_tracking: true
  max_process_age: 7200.0
  cleanup_interval: 600.0
  force_cleanup: false

tunnel_governance:
  default_lifecycle_policy: "reuse"
  tunnel_reuse_threshold: 3600.0
  max_tunnel_age: 14400.0
  credential_scope: "project"

global_cleanup_policy:
  default_strategy: "conservative"
  max_concurrent_cleanups: 10
  cleanup_timeout: 600.0
  enabled: true

status_pages:
  auto_refresh_interval: 10
  include_service_details: true
  include_tunnel_details: true
  include_health_metrics: true
  theme: "default"
EOF
    
    # Create production scripts
    log_info "Creating production scripts..."
    mkdir -p scripts/prod
    
    cat > scripts/prod/start-prod.sh << 'EOF'
#!/bin/bash
# Start production environment

echo "Starting KInfra production environment..."

# Start Redis with persistence
if command -v redis-server >/dev/null 2>&1; then
    redis-server --daemonize yes --port 6379 --appendonly yes
    echo "Redis started on port 6379 with persistence"
fi

# Start PostgreSQL
if command -v postgres >/dev/null 2>&1; then
    pg_ctl -D /usr/local/var/postgres start
    echo "PostgreSQL started"
fi

# Start NATS with clustering
if command -v nats-server >/dev/null 2>&1; then
    nats-server --port 4222 --daemon --cluster nats://localhost:6222
    echo "NATS started on port 4222 with clustering"
fi

echo "Production environment ready!"
EOF
    
    chmod +x scripts/prod/start-prod.sh
    
    cat > scripts/prod/stop-prod.sh << 'EOF'
#!/bin/bash
# Stop production environment

echo "Stopping KInfra production environment..."

# Stop Redis
if command -v redis-cli >/dev/null 2>&1; then
    redis-cli shutdown
    echo "Redis stopped"
fi

# Stop PostgreSQL
if command -v pg_ctl >/dev/null 2>&1; then
    pg_ctl -D /usr/local/var/postgres stop
    echo "PostgreSQL stopped"
fi

# Stop NATS
if command -v nats-server >/dev/null 2>&1; then
    pkill nats-server
    echo "NATS stopped"
fi

echo "Production environment stopped!"
EOF
    
    chmod +x scripts/prod/stop-prod.sh
    
    log_success "Production environment set up"
}

# Create systemd services
create_systemd_services() {
    log_info "Creating systemd services..."
    
    # Create KInfra service
    sudo tee /etc/systemd/system/kinfra.service > /dev/null << EOF
[Unit]
Description=KInfra Infrastructure Management
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 -m pheno.infra.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Create KInfra cleanup service
    sudo tee /etc/systemd/system/kinfra-cleanup.service > /dev/null << EOF
[Unit]
Description=KInfra Cleanup Service
After=kinfra.service

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 -m pheno.infra.cleanup
EOF
    
    # Create KInfra cleanup timer
    sudo tee /etc/systemd/system/kinfra-cleanup.timer > /dev/null << EOF
[Unit]
Description=Run KInfra cleanup every 5 minutes
Requires=kinfra-cleanup.service

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    log_success "Systemd services created"
}

# Main function
main() {
    log_info "Starting KInfra bootstrap..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        log_error "Please do not run this script as root"
        exit 1
    fi
    
    # Install Python dependencies
    install_python_deps
    
    # Install tunnel tools
    if [ "$TUNNEL_TOOLS" = true ] || [ "$ALL_MODE" = true ]; then
        install_tunnel_tools
    fi
    
    # Install monitoring tools
    if [ "$MONITORING" = true ] || [ "$ALL_MODE" = true ]; then
        install_monitoring_tools
    fi
    
    # Set up Docker
    if [ "$DOCKER" = true ] || [ "$ALL_MODE" = true ]; then
        setup_docker
    fi
    
    # Set up development environment
    if [ "$DEV_MODE" = true ] || [ "$ALL_MODE" = true ]; then
        setup_dev_environment
    fi
    
    # Set up production environment
    if [ "$PROD_MODE" = true ] || [ "$ALL_MODE" = true ]; then
        setup_prod_environment
    fi
    
    # Create systemd services (Linux only)
    if [ "$(uname -s)" = "Linux" ] && [ "$PROD_MODE" = true ]; then
        create_systemd_services
    fi
    
    log_success "KInfra bootstrap complete!"
    log_info "Next steps:"
    log_info "1. Configure your tunnel credentials: kinfra tunnel set-credentials"
    log_info "2. Start your first project: kinfra project start my-project"
    log_info "3. Check status: kinfra status show-global"
    
    if [ "$DEV_MODE" = true ] || [ "$ALL_MODE" = true ]; then
        log_info "4. Start development environment: ./scripts/dev/start-dev.sh"
    fi
    
    if [ "$PROD_MODE" = true ] || [ "$ALL_MODE" = true ]; then
        log_info "5. Start production environment: ./scripts/prod/start-prod.sh"
    fi
}

# Run main function
main "$@"