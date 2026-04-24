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
  brew bundle --file=Brewfile.dev
  echo "✅ Homebrew packages installed"

  if ! command -v grafana-alloy >/dev/null 2>&1 && \
     ! { [ -x "$HOME/.local/bin/grafana-alloy" ] && "$HOME/.local/bin/grafana-alloy" run --help >/dev/null 2>&1; }; then
    echo "⚠️  Grafana Alloy is required for the local log and trace collector."
    echo "   Try: brew install grafana-alloy"
    echo "   If alloy-analyzer owns the alloy command, install the official release as:"
    echo "   $HOME/.local/bin/grafana-alloy"
  fi

  # Install exporters (not available in Homebrew)
  echo ""
  echo "📊 Installing Prometheus exporters..."
  bash scripts/install-exporters-macos.sh
}

# Install services via APT (Ubuntu/Debian)
install_apt_services() {
  echo "📦 Installing services via APT..."

  sudo apt-get update
  sudo apt-get install -y \
    postgresql-17 \
    postgresql-client-17 \
    prometheus \
    grafana

  if ! command -v dragonfly &> /dev/null; then
    echo "⚠️  Dragonfly is required for the default cache runtime."
    echo "   Install Dragonfly from https://www.dragonflydb.io/docs/getting-started or use Docker."
  fi

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
    scoop install postgresql dragonfly prometheus grafana caddy || {
      echo "⚠️  Dragonfly could not be installed via Scoop."
      echo "   Use Docker or the official Dragonfly release for the default cache runtime."
    }
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

# Run database migrations (source .env so DATABASE_URL is set; alembic/env.py also loads .env as fallback)
if [ -f "alembic.ini" ]; then
  echo ""
  echo "🔄 Running database migrations..."
  if [ -f ".env" ]; then
    set -a
    source .env
    set +a
  fi
  alembic upgrade head || echo "⚠️  Migrations failed - run manually with: source .env && alembic upgrade head"
fi

# Create necessary directories
echo ""
echo "📁 Creating working directories..."
mkdir -p .process-compose/logs
mkdir -p .prometheus
mkdir -p .grafana
mkdir -p .temporal
mkdir -p .alloy/data
mkdir -p .dragonfly

# Verify installation
echo ""
echo "✅ Verifying installation..."

MISSING=""
command -v process-compose >/dev/null || MISSING="$MISSING process-compose"
command -v postgres >/dev/null || MISSING="$MISSING postgres"
if ! command -v dragonfly >/dev/null 2>&1 && ! command -v docker >/dev/null 2>&1; then
  MISSING="$MISSING dragonfly-or-docker"
fi
if ! command -v grafana-alloy >/dev/null 2>&1 && \
   ! { [ -x "$HOME/.local/bin/grafana-alloy" ] && "$HOME/.local/bin/grafana-alloy" run --help >/dev/null 2>&1; }; then
  MISSING="$MISSING grafana-alloy"
fi
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
