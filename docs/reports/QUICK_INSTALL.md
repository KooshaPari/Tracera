# Quick Installation Guide

## The Issue

`postgres_exporter` and `redis_exporter` are NOT available via Homebrew.
They must be installed as binary downloads from GitHub.

## Solution

### Option 1: Use Our Automated Script (Recommended)

```bash
# Install everything (includes exporter binaries)
make install-native
```

This will:
1. Install Homebrew packages (Prometheus, Grafana, node_exporter, etc.)
2. Download postgres_exporter and redis_exporter binaries
3. Install them to /opt/homebrew/bin

### Option 2: Manual Installation (macOS)

```bash
# Install Homebrew packages
brew bundle --file=Brewfile.dev

# Install exporters manually
bash scripts/install-exporters-macos.sh
```

### Option 3: Skip Exporters (Minimal Setup)

If you don't need full monitoring, you can skip exporters:

```bash
# Just install core services
brew install postgresql@17 redis neo4j nats-server temporal caddy prometheus grafana node_exporter process-compose

# Start services without exporters
make dev-tui
```

The monitoring will work but postgres/redis metrics won't be available.

## Verification

```bash
# Check what's installed
which postgres_exporter redis_exporter node_exporter

# Or use our verification script
bash scripts/verify-native-setup.sh
```

## Current Command

You ran:
```bash
brew install prometheus grafana postgres_exporter redis_exporter node_exporter
```

✅ This installed: prometheus, grafana, node_exporter
❌ This failed: postgres_exporter, redis_exporter (not in Homebrew)

## Correct Command

```bash
# Install available tools
brew install prometheus grafana node_exporter

# Install missing exporters
bash scripts/install-exporters-macos.sh
```

Or just:
```bash
make install-native
```

