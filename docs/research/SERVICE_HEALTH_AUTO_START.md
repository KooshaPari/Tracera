# Service Health Check & Auto-Start Research

**Research Date:** 2026-01-31
**Target Platform:** macOS (no Docker)
**Services:** PostgreSQL, Redis, Neo4j, NATS, Temporal

---

## Executive Summary

This document provides comprehensive research on auto-starting and health-checking services on macOS without Docker. The recommended approach combines **brew services** for service management with custom health check scripts using TCP/HTTP probes and intelligent retry logic.

**Key Recommendation:** Use launchd via `brew services` for auto-start, combined with Python/Bash health check scripts that verify service availability before application startup.

---

## 1. macOS Service Management

### 1.1 launchd (Native macOS)

[launchd](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) is macOS's native service management framework, similar to systemd on Linux. Services are configured using Property List (`.plist`) files.

**Key Concepts:**
- **LaunchDaemons** (`/Library/LaunchDaemons/`): System-wide services that run at boot
- **LaunchAgents** (`~/Library/LaunchAgents/`): User-level services
- **Automatic Start**: Services can be configured to start on boot or on-demand

**Example plist structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.postgresql.postgres</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/postgres</string>
        <string>-D</string>
        <string>/usr/local/var/postgres</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

**Manual launchd commands:**
```bash
# Load service (start and enable auto-start)
sudo launchctl load /Library/LaunchDaemons/com.postgresql.postgres.plist

# Unload service
sudo launchctl unload /Library/LaunchDaemons/com.postgresql.postgres.plist

# List loaded services
launchctl list | grep postgres
```

**Sources:**
- [PostgreSQL Auto-Start Configuration](https://gist.github.com/JaveedIshaq/afdc8ee9b579f10711acfee685a6aff0)
- [Disable/Enable PostgreSQL Autostart on Mac](https://gist.github.com/abhishekdev/1960888)

### 1.2 brew services (Recommended)

[Homebrew Services](https://www.dorokhovich.com/blog/homebrew-services) is a wrapper around launchd that simplifies service management for Homebrew-installed packages.

**Key Features:**
- Automatically creates and manages `.plist` files
- Integrates with launchd for system-level persistence
- Simple command-line interface
- Cross-platform consistency

**Core Commands:**
```bash
# List all services and their status
brew services list

# Start service now AND enable auto-start on boot
brew services start postgresql@16

# Start service now ONLY (no auto-start)
brew services run postgresql@16

# Stop service and disable auto-start
brew services stop postgresql@16

# Restart service
brew services restart postgresql@16

# Cleanup dead services
brew services cleanup
```

**How it works:**
1. Creates plist file: `~/Library/LaunchAgents/homebrew.mxcl.<service>.plist`
2. Registers with launchd: `launchctl load ~/Library/LaunchAgents/homebrew.mxcl.<service>.plist`
3. Starts the service immediately
4. Service persists across reboots

**Example output:**
```
Name              Status     User File
postgresql@16     started    user ~/Library/LaunchAgents/homebrew.mxcl.postgresql@16.plist
redis             started    user ~/Library/LaunchAgents/homebrew.mxcl.redis.plist
neo4j             error      user ~/Library/LaunchAgents/homebrew.mxcl.neo4j.plist
nats-server       none
temporal          none
```

**Sources:**
- [Homebrew Services Guide](https://www.dorokhovich.com/blog/homebrew-services)
- [Homebrew: Auto-Start on Boot](https://www.slingacademy.com/article/homebrew-how-to-make-service-auto-start-on-system-boot/)
- [Starting Background Services with Homebrew](https://thoughtbot.com/blog/starting-and-stopping-background-services-with-homebrew)

### 1.3 Service-Specific Setup

#### PostgreSQL
```bash
# Install and auto-start
brew install postgresql@16
brew services start postgresql@16

# Verify
psql -h localhost -U postgres -c "SELECT version();"
```

**Sources:**
- [How to Start PostgreSQL on macOS](https://www.w3resource.com/PostgreSQL/snippets/how-to-start-postgresql-server-on-macos-easily.php)
- [Native PostgreSQL with Homebrew](https://compositecode.blog/2025/12/10/a-complete-native-postgresql-with-homebrew/)

#### Redis
```bash
# Install and auto-start
brew install redis
brew services start redis

# Verify
redis-cli ping  # Should return "PONG"
```

**Sources:**
- [Redis Auto-Start OS X](https://gist.github.com/subfuzion/9631143)

#### Neo4j
```bash
# Install and configure
brew install neo4j
# Edit config: /usr/local/etc/neo4j/neo4j.conf
brew services start neo4j

# Verify
curl http://localhost:7474
```

**Sources:**
- [Neo4j macOS Installation](https://neo4j.com/docs/operations-manual/current/installation/osx/)

#### NATS
```bash
# Install
brew install nats-server

# Auto-start
brew services start nats-server

# Verify
curl http://localhost:8222/healthz  # Should return "OK"
```

**Sources:**
- [NATS Monitoring](https://docs.nats.io/running-a-nats-service/nats_admin/monitoring)
- [NATS Health Check](https://github.com/nats-io/nats-server/issues/1903)

#### Temporal
```bash
# Install Temporal CLI
brew install temporal

# Temporal requires manual server setup
# Download and run Temporal server:
temporal server start-dev

# Or use a custom launchd plist for auto-start
```

**Sources:**
- [Temporal CLI Reference](https://docs.temporal.io/cli)
- [Monitor Temporal Health](https://docs.temporal.io/cloud/high-availability/monitor)

---

## 2. Health Check Libraries & Patterns

### 2.1 Python Health Check Libraries

#### py-healthcheck
[py-healthcheck](https://pypi.org/project/py-healthcheck/) is a lightweight library for creating health check endpoints.

**Features:**
- Flask and Tornado integration
- In-memory caching (27s for success, 9s for failures)
- Customizable health check functions
- Environment info endpoints

**Installation:**
```bash
pip install py-healthcheck
```

**Example Usage:**
```python
from healthcheck import HealthCheck, EnvironmentDump

health = HealthCheck()

# Add check functions
def redis_available():
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379)
        client.ping()
        return True, "Redis is available"
    except Exception as e:
        return False, f"Redis unavailable: {str(e)}"

health.add_check(redis_available)

# Integrate with Flask
from flask import Flask
app = Flask(__name__)
app.add_url_rule("/health", "health", view_func=lambda: health.run())
```

**Sources:**
- [py-healthcheck PyPI](https://pypi.org/project/py-healthcheck/)
- [py-healthcheck Documentation](https://py-healthcheck.readthedocs.io/en/stable/)

#### django-health-check
For Django applications: [django-health-check](https://pypi.org/project/django-health-check/)

**Features:**
- Built-in checks for databases, caches, storage
- Supports Django 4.2, 5.2, 6.0
- Extensible with custom checks

**Sources:**
- [django-health-check PyPI](https://pypi.org/project/django-health-check/)

### 2.2 FastAPI Health Check Pattern

[FastAPI Health Check Example](https://www.index.dev/blog/how-to-implement-health-check-in-python)

```python
from fastapi import FastAPI, HTTPException
from typing import Dict
import socket
import redis

app = FastAPI()

def check_service(host: str, port: int, timeout: int = 3) -> bool:
    """Check if a TCP service is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return True
    except:
        return False

@app.get("/health")
async def health_check() -> Dict[str, str]:
    checks = {
        "postgresql": check_service("localhost", 5432),
        "redis": check_service("localhost", 6379),
        "neo4j": check_service("localhost", 7687),
        "nats": check_service("localhost", 4222),
    }

    if all(checks.values()):
        return {"status": "healthy", "services": checks}
    else:
        raise HTTPException(status_code=503, detail={"status": "unhealthy", "services": checks})
```

---

## 3. Service Discovery Solutions

### 3.1 Comparison Matrix

| Tool | Type | Complexity | macOS Support | Use Case |
|------|------|------------|---------------|----------|
| **etcd** | Key-value store | Low | ✅ (via brew) | Simple, Kubernetes-aligned |
| **Consul** | Service mesh | High | ✅ (via brew) | Multi-datacenter, complex networks |
| **Nacos** | Dynamic discovery | Medium | ✅ (Java-based) | Cloud-native apps |
| **ZooKeeper** | Coordination | Medium | ✅ (via brew) | Legacy, reliable |
| **File-based** | Simple | Very Low | ✅ Native | Single machine, dev environments |

**Sources:**
- [Service Discovery Tools Comparison](https://charleswan111.medium.com/comparing-service-discovery-and-coordination-tools-etcd-consul-eureka-nacos-polaris-157820eb1810)
- [Consul vs etcd](https://slickfinch.com/consul-vs-etcd-service-discovery-tools-comparison/)
- [Best Service Discovery Tools](https://devopscube.com/open-source-service-discovery/)

### 3.2 Recommended Approach for macOS Dev

**File-based discovery** is sufficient for local development:

```bash
# Service status file: ~/.tracertm/services.json
{
  "postgresql": {
    "status": "running",
    "host": "localhost",
    "port": 5432,
    "last_check": "2026-01-31T10:30:00Z"
  },
  "redis": {
    "status": "running",
    "host": "localhost",
    "port": 6379,
    "last_check": "2026-01-31T10:30:00Z"
  },
  "neo4j": {
    "status": "running",
    "host": "localhost",
    "port": 7687,
    "last_check": "2026-01-31T10:30:00Z"
  }
}
```

**For production or multi-service coordination:**
- Use **etcd** for simplicity and Kubernetes alignment
- Use **Consul** for complex service mesh requirements

---

## 4. Preflight Check Patterns

### 4.1 Python Implementation with Retry Logic

[Example from gist.github.com](https://gist.github.com/betrcode/0248f0fda894013382d7):

```python
#!/usr/bin/env python3
"""
Preflight check script - verifies all services are available before starting app
"""
import socket
import time
import subprocess
import sys
from typing import Dict, Tuple

# Configuration
SERVICES = {
    "postgresql": {"host": "localhost", "port": 5432},
    "redis": {"host": "localhost", "port": 6379},
    "neo4j": {"host": "localhost", "port": 7687},
    "nats": {"host": "localhost", "port": 4222},
    "temporal": {"host": "localhost", "port": 7233},
}

RETRY_COUNT = 5
RETRY_DELAY = 3  # seconds
CONNECTION_TIMEOUT = 3  # seconds

def check_tcp_port(host: str, port: int, timeout: int = CONNECTION_TIMEOUT) -> bool:
    """Check if a TCP port is open and accepting connections"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"  Error checking {host}:{port} - {e}")
        return False

def check_http_endpoint(url: str, timeout: int = CONNECTION_TIMEOUT) -> bool:
    """Check if an HTTP endpoint is responding"""
    try:
        import urllib.request
        req = urllib.request.Request(url)
        urllib.request.urlopen(req, timeout=timeout)
        return True
    except Exception:
        return False

def start_service_if_needed(service_name: str) -> bool:
    """Attempt to start a service using brew services"""
    print(f"  Attempting to start {service_name}...")
    try:
        # Map service names to brew formula names
        brew_names = {
            "postgresql": "postgresql@16",
            "redis": "redis",
            "neo4j": "neo4j",
            "nats": "nats-server",
            "temporal": None,  # Temporal requires manual setup
        }

        brew_name = brew_names.get(service_name)
        if not brew_name:
            print(f"  ⚠️  {service_name} cannot be auto-started via brew")
            return False

        # Start service
        subprocess.run(
            ["brew", "services", "start", brew_name],
            check=True,
            capture_output=True,
            text=True
        )

        # Wait a bit for service to initialize
        time.sleep(5)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to start {service_name}: {e.stderr}")
        return False

def check_service_with_retry(
    service_name: str,
    config: Dict[str, any],
    auto_start: bool = True
) -> Tuple[bool, str]:
    """
    Check if a service is available with retry logic
    Returns: (success, message)
    """
    host = config["host"]
    port = config["port"]

    for attempt in range(1, RETRY_COUNT + 1):
        if check_tcp_port(host, port):
            return True, f"✅ {service_name} is available at {host}:{port}"

        if attempt == 1 and auto_start:
            # First attempt failed, try to start the service
            if start_service_if_needed(service_name):
                continue  # Retry after starting

        if attempt < RETRY_COUNT:
            print(f"  Attempt {attempt}/{RETRY_COUNT} failed, retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)

    return False, f"❌ {service_name} is NOT available at {host}:{port} after {RETRY_COUNT} attempts"

def check_all_services(auto_start: bool = True, fail_fast: bool = False) -> bool:
    """
    Check all configured services

    Args:
        auto_start: Attempt to start services if they're down
        fail_fast: Stop checking at first failure

    Returns:
        True if all services are available
    """
    print("\n🔍 Checking service availability...\n")

    all_ok = True
    results = []

    for service_name, config in SERVICES.items():
        print(f"Checking {service_name}...")
        success, message = check_service_with_retry(service_name, config, auto_start)
        print(f"  {message}")
        results.append((service_name, success))

        if not success:
            all_ok = False
            if fail_fast:
                break

    print("\n" + "="*60)
    if all_ok:
        print("✅ All services are available!")
    else:
        print("❌ Some services are unavailable:")
        for name, success in results:
            if not success:
                print(f"  - {name}")
    print("="*60 + "\n")

    return all_ok

def graceful_degradation_mode():
    """
    Check which services are available and configure app accordingly
    Returns a dict of available services
    """
    available = {}
    for service_name, config in SERVICES.items():
        host = config["host"]
        port = config["port"]
        available[service_name] = check_tcp_port(host, port)
    return available

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Service health check and auto-start")
    parser.add_argument("--no-auto-start", action="store_true", help="Don't attempt to start services")
    parser.add_argument("--fail-fast", action="store_true", help="Stop at first failure")
    parser.add_argument("--degraded", action="store_true", help="Run in graceful degradation mode")

    args = parser.parse_args()

    if args.degraded:
        available = graceful_degradation_mode()
        print("Available services:", {k: v for k, v in available.items() if v})
        sys.exit(0)

    success = check_all_services(
        auto_start=not args.no_auto_start,
        fail_fast=args.fail_fast
    )

    sys.exit(0 if success else 1)
```

**Usage:**
```bash
# Check and auto-start services
python scripts/preflight_check.py

# Check only (don't auto-start)
python scripts/preflight_check.py --no-auto-start

# Fail fast mode (stop at first failure)
python scripts/preflight_check.py --fail-fast

# Graceful degradation (return available services)
python scripts/preflight_check.py --degraded
```

### 4.2 Bash Implementation

```bash
#!/bin/bash
# preflight_check.sh - Check and auto-start services

set -e

RETRY_COUNT=5
RETRY_DELAY=3
CONNECTION_TIMEOUT=3

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_port() {
    local host=$1
    local port=$2
    local timeout=${3:-$CONNECTION_TIMEOUT}

    if timeout $timeout bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

start_service() {
    local service_name=$1
    local brew_formula=$2

    echo "  Attempting to start $service_name via brew..."
    if brew services start "$brew_formula" 2>/dev/null; then
        sleep 5  # Wait for service to initialize
        return 0
    else
        return 1
    fi
}

check_service_with_retry() {
    local service_name=$1
    local host=$2
    local port=$3
    local brew_formula=$4
    local auto_start=${5:-true}

    echo "Checking $service_name..."

    for attempt in $(seq 1 $RETRY_COUNT); do
        if check_port "$host" "$port"; then
            echo -e "  ${GREEN}✅ $service_name is available at $host:$port${NC}"
            return 0
        fi

        if [ "$attempt" -eq 1 ] && [ "$auto_start" = true ] && [ -n "$brew_formula" ]; then
            start_service "$service_name" "$brew_formula"
            continue
        fi

        if [ "$attempt" -lt "$RETRY_COUNT" ]; then
            echo "  Attempt $attempt/$RETRY_COUNT failed, retrying in ${RETRY_DELAY}s..."
            sleep $RETRY_DELAY
        fi
    done

    echo -e "  ${RED}❌ $service_name is NOT available at $host:$port after $RETRY_COUNT attempts${NC}"
    return 1
}

main() {
    local auto_start=true
    local fail_fast=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-auto-start)
                auto_start=false
                shift
                ;;
            --fail-fast)
                fail_fast=true
                shift
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    echo ""
    echo "🔍 Checking service availability..."
    echo ""

    local all_ok=true

    # Check PostgreSQL
    if ! check_service_with_retry "PostgreSQL" "localhost" 5432 "postgresql@16" "$auto_start"; then
        all_ok=false
        [ "$fail_fast" = true ] && exit 1
    fi

    # Check Redis
    if ! check_service_with_retry "Redis" "localhost" 6379 "redis" "$auto_start"; then
        all_ok=false
        [ "$fail_fast" = true ] && exit 1
    fi

    # Check Neo4j
    if ! check_service_with_retry "Neo4j" "localhost" 7687 "neo4j" "$auto_start"; then
        all_ok=false
        [ "$fail_fast" = true ] && exit 1
    fi

    # Check NATS
    if ! check_service_with_retry "NATS" "localhost" 4222 "nats-server" "$auto_start"; then
        all_ok=false
        [ "$fail_fast" = true ] && exit 1
    fi

    # Check Temporal (no brew formula, manual start required)
    if ! check_service_with_retry "Temporal" "localhost" 7233 "" false; then
        echo -e "  ${YELLOW}⚠️  Temporal must be started manually: temporal server start-dev${NC}"
        all_ok=false
        [ "$fail_fast" = true ] && exit 1
    fi

    echo ""
    echo "============================================================"
    if [ "$all_ok" = true ]; then
        echo -e "${GREEN}✅ All services are available!${NC}"
    else
        echo -e "${RED}❌ Some services are unavailable${NC}"
    fi
    echo "============================================================"
    echo ""

    [ "$all_ok" = true ] && exit 0 || exit 1
}

main "$@"
```

**Usage:**
```bash
chmod +x scripts/preflight_check.sh

# Check and auto-start services
./scripts/preflight_check.sh

# Check only (don't auto-start)
./scripts/preflight_check.sh --no-auto-start

# Fail fast mode
./scripts/preflight_check.sh --fail-fast
```

**Sources:**
- [TCP Port Check Python Examples](https://gist.github.com/betrcode/0248f0fda894013382d7)
- [Python TCP Port Reachability](https://buildsoftwaresystems.com/post/python-remote-tcp-port-reachability-check/)

---

## 5. Process Supervision

### 5.1 Comparison Matrix

| Tool | Type | macOS Native | Language Support | Use Case |
|------|------|--------------|------------------|----------|
| **launchd** | System | ✅ Built-in | All | Native macOS, production |
| **supervisord** | Process manager | ⚠️ Via pip | All | Multi-process coordination |
| **PM2** | Process manager | ⚠️ Via npm | Node.js focus | Node apps, dev environment |
| **Monit** | Monitoring | ⚠️ Via brew | All | Production monitoring |

**Sources:**
- [Supervisord vs PM2](https://stackshare.io/stackups/pm2-vs-supervisord)
- [Supervisord Alternatives](https://stackshare.io/supervisord/alternatives)
- [PM2 Alternatives](https://stackshare.io/pm2/alternatives)

### 5.2 Recommendations

**For macOS Development:**
1. **Primary:** Use `launchd` via `brew services` (native, reliable, persists across reboots)
2. **Alternative:** Use `supervisord` for complex multi-process coordination

**supervisord example:**
```ini
; /usr/local/etc/supervisord.ini
[supervisord]
logfile=/usr/local/var/log/supervisord.log
pidfile=/usr/local/var/run/supervisord.pid

[program:temporal]
command=temporal server start-dev
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/usr/local/var/log/temporal.log

[program:python-backend]
command=/path/to/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
directory=/path/to/backend
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/usr/local/var/log/python-backend.log
```

**Start supervisord:**
```bash
brew install supervisor
brew services start supervisor
```

---

## 6. Service Dependency Management

### 6.1 Startup Order Coordination

Services should start in dependency order:

```
1. PostgreSQL  (database)
2. Redis       (cache)
3. Neo4j       (graph database)
4. NATS        (messaging)
5. Temporal    (workflow engine)
6. Application (depends on all above)
```

**Sources:**
- [systemd Service Dependencies](https://seb.jambor.dev/posts/systemd-by-example-part-2-dependencies/)
- [Docker Compose Startup Order](https://github.com/docker-archive-public/docker.docker.github.io-1/blob/master/compose/startup-order.md)

### 6.2 Implementation Strategy

#### Option A: Sequential Script
```bash
#!/bin/bash
# start_services.sh - Start services in dependency order

services=(
    "postgresql@16"
    "redis"
    "neo4j"
    "nats-server"
)

for service in "${services[@]}"; do
    echo "Starting $service..."
    brew services start "$service"
    sleep 2  # Allow service to initialize
done

# Temporal requires manual start
echo "Starting Temporal..."
temporal server start-dev &

echo "All services started!"
```

#### Option B: Parallel with Health Checks
```python
#!/usr/bin/env python3
# start_services_parallel.py

import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from preflight_check import check_tcp_port

def start_service(service_name: str, brew_formula: str, port: int):
    """Start a service and wait for it to be healthy"""
    print(f"Starting {service_name}...")
    subprocess.run(["brew", "services", "start", brew_formula], check=True)

    # Wait for service to be ready
    max_wait = 30
    for _ in range(max_wait):
        if check_tcp_port("localhost", port):
            print(f"✅ {service_name} is ready")
            return True
        time.sleep(1)

    print(f"⚠️ {service_name} took too long to start")
    return False

def main():
    # Start independent services in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(start_service, "PostgreSQL", "postgresql@16", 5432),
            executor.submit(start_service, "Redis", "redis", 6379),
            executor.submit(start_service, "Neo4j", "neo4j", 7687),
        ]

        # Wait for all to complete
        results = [f.result() for f in futures]

    # Start dependent services sequentially
    start_service("NATS", "nats-server", 4222)

    print("All services started!")

if __name__ == "__main__":
    main()
```

---

## 7. Service-Specific Health Checks

### 7.1 PostgreSQL
```python
def check_postgresql():
    """Check PostgreSQL with proper authentication"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="",
            database="postgres",
            connect_timeout=3
        )
        conn.close()
        return True, "PostgreSQL OK"
    except Exception as e:
        return False, f"PostgreSQL error: {e}"
```

**HTTP alternative:**
```bash
# PostgreSQL doesn't have HTTP endpoint by default
# Use TCP check or psql command
psql -h localhost -U postgres -c "SELECT 1" -t
```

### 7.2 Redis
```python
def check_redis():
    """Check Redis availability"""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, socket_connect_timeout=3)
        client.ping()
        return True, "Redis OK"
    except Exception as e:
        return False, f"Redis error: {e}"
```

**CLI alternative:**
```bash
redis-cli -h localhost -p 6379 ping
```

### 7.3 Neo4j
```python
def check_neo4j():
    """Check Neo4j availability via HTTP"""
    try:
        import requests
        response = requests.get("http://localhost:7474", timeout=3)
        return response.status_code == 200, "Neo4j OK"
    except Exception as e:
        return False, f"Neo4j error: {e}"
```

**CLI alternative:**
```bash
curl -s http://localhost:7474 | grep -q "neo4j" && echo "OK" || echo "FAIL"
```

### 7.4 NATS
```python
def check_nats():
    """Check NATS via health endpoint"""
    try:
        import requests
        response = requests.get("http://localhost:8222/healthz", timeout=3)
        return response.text == "OK", "NATS OK"
    except Exception as e:
        return False, f"NATS error: {e}"
```

**CLI alternative:**
```bash
curl -s http://localhost:8222/healthz
# Should return: OK
```

**Sources:**
- [NATS Monitoring Endpoints](https://docs.nats.io/running-a-nats-service/nats_admin/monitoring)
- [NATS Health Check Issue](https://github.com/nats-io/nats-server/issues/1903)

### 7.5 Temporal
```python
def check_temporal():
    """Check Temporal workflow service"""
    try:
        import requests
        # Temporal gRPC health check via HTTP gateway (if enabled)
        # Or use TCP check on gRPC port
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(("localhost", 7233))
        sock.close()
        return result == 0, "Temporal OK"
    except Exception as e:
        return False, f"Temporal error: {e}"
```

**CLI alternative:**
```bash
# Check if Temporal is responding
temporal operator namespace list 2>&1 | grep -q "default" && echo "OK" || echo "FAIL"
```

**Sources:**
- [Monitor Temporal Worker Health](https://docs.temporal.io/production-deployment/cloud/worker-health)
- [Temporal Metrics Reference](https://docs.temporal.io/references/cluster-metrics)

---

## 8. Retry Logic Best Practices

### 8.1 Exponential Backoff
```python
import time

def exponential_backoff_check(
    check_func,
    max_attempts: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0
):
    """
    Retry with exponential backoff

    Delays: 1s, 2s, 4s, 8s, 16s (capped at max_delay)
    """
    delay = initial_delay

    for attempt in range(1, max_attempts + 1):
        try:
            result = check_func()
            if result:
                return True
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

        if attempt < max_attempts:
            print(f"Retrying in {delay}s...")
            time.sleep(delay)
            delay = min(delay * backoff_factor, max_delay)

    return False
```

### 8.2 Circuit Breaker Pattern
```python
from datetime import datetime, timedelta

class CircuitBreaker:
    """
    Circuit breaker for service health checks
    - Prevents overwhelming a failing service
    - Automatically recovers when service is healthy
    """
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds before attempting recovery
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED (normal), OPEN (failing), HALF_OPEN (testing)

    def call(self, func):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func()
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    def on_success(self):
        """Reset circuit breaker on success"""
        self.failure_count = 0
        self.state = "CLOSED"

    def on_failure(self):
        """Record failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

# Usage
postgres_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

def check_postgres_with_breaker():
    return postgres_breaker.call(check_postgresql)
```

**Sources:**
- [FastAPI Health Check Best Practices](https://www.index.dev/blog/how-to-implement-health-check-in-python)
- [Docker Healthcheck Best Practices](https://www.furkanbaytekin.dev/blogs/software/writing-reliable-docker-healthchecks-that-actually-work)

---

## 9. Graceful Degradation

### 9.1 Strategy

Instead of failing completely when a service is unavailable, configure the application to work in degraded mode:

```python
# config.py
from preflight_check import graceful_degradation_mode

# Check available services at startup
AVAILABLE_SERVICES = graceful_degradation_mode()

# Configure features based on availability
FEATURES = {
    "graph_queries": AVAILABLE_SERVICES.get("neo4j", False),
    "caching": AVAILABLE_SERVICES.get("redis", False),
    "messaging": AVAILABLE_SERVICES.get("nats", False),
    "workflows": AVAILABLE_SERVICES.get("temporal", False),
}

# Application can still start with PostgreSQL only
assert AVAILABLE_SERVICES.get("postgresql"), "PostgreSQL is required"
```

### 9.2 Feature Flags

```python
# features.py
class FeatureFlags:
    def __init__(self, available_services):
        self.services = available_services

    @property
    def can_use_cache(self):
        return self.services.get("redis", False)

    @property
    def can_use_graph(self):
        return self.services.get("neo4j", False)

    def get_cache(self, key):
        if not self.can_use_cache:
            return None  # Fallback to no cache
        # ... actual cache logic

features = FeatureFlags(AVAILABLE_SERVICES)

# Usage in code
if features.can_use_cache:
    cached = features.get_cache(key)
else:
    # Fetch directly from database
    cached = db.query(...)
```

---

## 10. Recommended Implementation

### 10.1 Complete Startup Script

```python
#!/usr/bin/env python3
"""
TraceRTM Service Manager
- Checks service health
- Auto-starts services via brew
- Handles graceful degradation
- Provides detailed status reporting
"""

import sys
import time
import socket
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional

# Service configuration
SERVICES = {
    "postgresql": {
        "host": "localhost",
        "port": 5432,
        "brew_formula": "postgresql@16",
        "required": True,
        "health_check": "tcp",
    },
    "redis": {
        "host": "localhost",
        "port": 6379,
        "brew_formula": "redis",
        "required": False,
        "health_check": "tcp",
    },
    "neo4j": {
        "host": "localhost",
        "port": 7687,
        "brew_formula": "neo4j",
        "required": False,
        "health_check": "tcp",
    },
    "nats": {
        "host": "localhost",
        "port": 4222,
        "brew_formula": "nats-server",
        "required": False,
        "health_check": "tcp",
        "http_health": "http://localhost:8222/healthz",
    },
    "temporal": {
        "host": "localhost",
        "port": 7233,
        "brew_formula": None,
        "required": False,
        "health_check": "tcp",
        "manual_start": "temporal server start-dev",
    },
}

CONFIG_DIR = Path.home() / ".tracertm"
STATUS_FILE = CONFIG_DIR / "services.json"

class ServiceManager:
    def __init__(self, auto_start=True, retry_count=5, retry_delay=3):
        self.auto_start = auto_start
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.results = {}

    def check_tcp(self, host: str, port: int, timeout: int = 3) -> bool:
        """Check if TCP port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def start_service(self, name: str, brew_formula: str) -> bool:
        """Start service via brew services"""
        try:
            print(f"    Starting {name} via brew...")
            subprocess.run(
                ["brew", "services", "start", brew_formula],
                check=True,
                capture_output=True,
                text=True
            )
            time.sleep(5)  # Wait for initialization
            return True
        except subprocess.CalledProcessError as e:
            print(f"    Failed: {e.stderr}")
            return False

    def check_service(self, name: str, config: Dict) -> Tuple[bool, str]:
        """Check single service with retry logic"""
        for attempt in range(1, self.retry_count + 1):
            if self.check_tcp(config["host"], config["port"]):
                return True, f"Available at {config['host']}:{config['port']}"

            if attempt == 1 and self.auto_start and config.get("brew_formula"):
                if self.start_service(name, config["brew_formula"]):
                    continue

            if attempt < self.retry_count:
                time.sleep(self.retry_delay)

        msg = f"Unavailable at {config['host']}:{config['port']}"
        if config.get("manual_start"):
            msg += f" (Start with: {config['manual_start']})"
        return False, msg

    def check_all(self) -> bool:
        """Check all services and return overall status"""
        print("\n🔍 Checking services...\n")

        all_required_ok = True

        for name, config in SERVICES.items():
            print(f"Checking {name}...")
            success, message = self.check_service(name, config)

            status = "✅" if success else "❌"
            required = " (required)" if config.get("required") else " (optional)"
            print(f"  {status} {message}{required}")

            self.results[name] = {
                "available": success,
                "message": message,
                "required": config.get("required", False),
                "last_check": datetime.now().isoformat(),
            }

            if config.get("required") and not success:
                all_required_ok = False

        return all_required_ok

    def save_status(self):
        """Save service status to file"""
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(STATUS_FILE, 'w') as f:
            json.dump(self.results, f, indent=2)

    def print_summary(self, all_ok: bool):
        """Print summary report"""
        print("\n" + "="*60)
        if all_ok:
            print("✅ All required services are available!")
        else:
            print("❌ Some required services are unavailable")
            print("\nRequired services:")
            for name, result in self.results.items():
                if result["required"] and not result["available"]:
                    print(f"  ❌ {name}: {result['message']}")

        optional_down = [
            name for name, result in self.results.items()
            if not result["required"] and not result["available"]
        ]
        if optional_down:
            print("\nOptional services (degraded mode):")
            for name in optional_down:
                print(f"  ⚠️  {name}: {self.results[name]['message']}")

        print("="*60 + "\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TraceRTM Service Manager")
    parser.add_argument("--no-auto-start", action="store_true")
    parser.add_argument("--status-only", action="store_true", help="Show status from last check")

    args = parser.parse_args()

    if args.status_only:
        if STATUS_FILE.exists():
            with open(STATUS_FILE) as f:
                results = json.load(f)
            for name, status in results.items():
                available = "✅" if status["available"] else "❌"
                print(f"{available} {name}: {status['message']}")
        else:
            print("No status file found. Run without --status-only first.")
        sys.exit(0)

    manager = ServiceManager(auto_start=not args.no_auto_start)
    all_ok = manager.check_all()
    manager.save_status()
    manager.print_summary(all_ok)

    sys.exit(0 if all_ok else 1)
```

### 10.2 Integration with App Startup

**In your application's main entry point:**

```python
# main.py (backend)
import subprocess
import sys

def check_services():
    """Run preflight check before starting app"""
    result = subprocess.run(
        ["python", "scripts/service_manager.py"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print("⚠️  Not all required services are available")
        print("Continue anyway? (y/n): ", end="")
        response = input().lower()
        if response != 'y':
            sys.exit(1)

if __name__ == "__main__":
    check_services()

    # Start your application
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
```

---

## 11. Service Dependency Graph

```
┌─────────────────────────────────────────────────┐
│                  Application                    │
│            (Frontend + Backend)                 │
└─────────────┬───────────────────────────────────┘
              │
              │ Requires all services
              │
    ┌─────────┴─────────────┐
    │                       │
    ▼                       ▼
┌───────┐              ┌─────────┐
│ Core  │              │Optional │
│Services│             │Services │
└───┬───┘              └────┬────┘
    │                       │
    │                       │
    ▼                       ▼
┌──────────┐    ┌──────┐  ┌────────┐  ┌──────────┐
│PostgreSQL│    │Redis │  │ Neo4j  │  │Temporal  │
│(required)│    │(cache)  │(graph) │  │(workflow)│
└──────────┘    └──────┘  └────────┘  └──────────┘
                              │
                              │ Uses for messaging
                              ▼
                          ┌──────┐
                          │ NATS │
                          └──────┘

Legend:
  ─────  Dependency
  required: App won't start without it
  optional: App runs in degraded mode
```

---

## 12. Final Recommendations

### 12.1 For Development (macOS)

1. **Service Management**: Use `brew services` for all auto-startable services
   ```bash
   brew services start postgresql@16
   brew services start redis
   brew services start neo4j
   brew services start nats-server
   ```

2. **Health Checks**: Implement Python-based preflight script (Section 10.1)
   - TCP port checks for all services
   - Auto-start via brew when possible
   - Graceful degradation for optional services

3. **Service Discovery**: Use file-based status tracking (`~/.tracertm/services.json`)
   - Simple, sufficient for local dev
   - No additional dependencies

4. **Process Supervision**: Let launchd handle it (via brew services)
   - Native macOS integration
   - Survives reboots
   - System-level monitoring

### 12.2 For Production (Future)

1. **Service Management**: Use systemd (Linux) or proper container orchestration
2. **Health Checks**: Implement comprehensive HTTP health endpoints
3. **Service Discovery**: Consider etcd or Consul for multi-instance deployments
4. **Monitoring**: Add Prometheus + Grafana for metrics and alerting

### 12.3 Quick Start

```bash
# 1. Install services
brew install postgresql@16 redis neo4j nats-server temporal

# 2. Auto-start services
brew services start postgresql@16
brew services start redis
brew services start neo4j
brew services start nats-server

# 3. Manual start for Temporal (no brew service)
temporal server start-dev &

# 4. Verify all services
python scripts/service_manager.py

# 5. Start your application
cd backend && python main.py
```

---

## Sources

### macOS Service Management
- [Homebrew Services Guide](https://www.dorokhovich.com/blog/homebrew-services)
- [Homebrew: Auto-Start on Boot](https://www.slingacademy.com/article/homebrew-how-to-make-service-auto-start-on-system-boot/)
- [Starting Background Services with Homebrew](https://thoughtbot.com/blog/starting-and-stopping-background-services-with-homebrew)
- [PostgreSQL Auto-Start Configuration](https://gist.github.com/JaveedIshaq/afdc8ee9b579f10711acfee685a6aff0)
- [How to Start PostgreSQL on macOS](https://www.w3resource.com/PostgreSQL/snippets/how-to-start-postgresql-server-on-macos-easily.php)
- [Native PostgreSQL with Homebrew](https://compositecode.blog/2025/12/10/a-complete-native-postgresql-with-homebrew/)
- [Redis Auto-Start OS X](https://gist.github.com/subfuzion/9631143)
- [Neo4j macOS Installation](https://neo4j.com/docs/operations-manual/current/installation/osx/)

### Health Check Libraries
- [py-healthcheck PyPI](https://pypi.org/project/py-healthcheck/)
- [py-healthcheck Documentation](https://py-healthcheck.readthedocs.io/en/stable/)
- [django-health-check PyPI](https://pypi.org/project/django-health-check/)
- [FastAPI Health Check Example](https://www.index.dev/blog/how-to-implement-health-check-in-python)
- [TCP Port Check Examples](https://gist.github.com/betrcode/0248f0fda894013382d7)
- [Python TCP Port Reachability](https://buildsoftwaresystems.com/post/python-remote-tcp-port-reachability-check/)
- [Docker Healthcheck Best Practices](https://www.furkanbaytekin.dev/blogs/software/writing-reliable-docker-healthchecks-that-actually-work)

### Service Discovery
- [Service Discovery Tools Comparison](https://charleswan111.medium.com/comparing-service-discovery-and-coordination-tools-etcd-consul-eureka-nacos-polaris-157820eb1810)
- [Consul vs etcd](https://slickfinch.com/consul-vs-etcd-service-discovery-tools-comparison/)
- [Best Service Discovery Tools](https://devopscube.com/open-source-service-discovery/)

### Process Supervision
- [Supervisord vs PM2](https://stackshare.io/stackups/pm2-vs-supervisord)
- [Supervisord Alternatives](https://stackshare.io/supervisord/alternatives)
- [PM2 Alternatives](https://stackshare.io/pm2/alternatives)

### Service-Specific
- [NATS Monitoring](https://docs.nats.io/running-a-nats-service/nats_admin/monitoring)
- [NATS Health Check Issue](https://github.com/nats-io/nats-server/issues/1903)
- [Temporal CLI Reference](https://docs.temporal.io/cli)
- [Monitor Temporal Health](https://docs.temporal.io/cloud/high-availability/monitor)
- [Monitor Temporal Worker Health](https://docs.temporal.io/production-deployment/cloud/worker-health)
- [Temporal Metrics Reference](https://docs.temporal.io/references/cluster-metrics)

### Dependency Management
- [systemd Service Dependencies](https://seb.jambor.dev/posts/systemd-by-example-part-2-dependencies/)
- [Docker Compose Startup Order](https://github.com/docker-archive-public/docker.docker.github.io-1/blob/master/compose/startup-order.md)

---

**End of Research Document**
