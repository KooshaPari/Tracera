#!/usr/bin/env bash
#
# Toxiproxy Setup Script
#
# Downloads and starts Toxiproxy for chaos engineering tests.
# Toxiproxy acts as a TCP proxy that can inject network failures.

set -euo pipefail

TOXIPROXY_VERSION="${TOXIPROXY_VERSION:-2.9.0}"
TOXIPROXY_PORT="${TOXIPROXY_PORT:-8474}"
TOXIPROXY_DIR="${HOME}/.local/bin"
TOXIPROXY_BIN="${TOXIPROXY_DIR}/toxiproxy-server"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Detect OS and architecture
detect_platform() {
    local os
    local arch

    case "$(uname -s)" in
        Linux*)     os=linux;;
        Darwin*)    os=darwin;;
        *)          log_error "Unsupported OS: $(uname -s)"; exit 1;;
    esac

    case "$(uname -m)" in
        x86_64)     arch=amd64;;
        arm64|aarch64) arch=arm64;;
        *)          log_error "Unsupported architecture: $(uname -m)"; exit 1;;
    esac

    echo "${os}_${arch}"
}

# Download Toxiproxy
download_toxiproxy() {
    local platform
    platform=$(detect_platform)

    local download_url="https://github.com/Shopify/toxiproxy/releases/download/v${TOXIPROXY_VERSION}/toxiproxy-server-${platform}"

    log_info "Downloading Toxiproxy ${TOXIPROXY_VERSION} for ${platform}..."

    mkdir -p "${TOXIPROXY_DIR}"

    if command -v curl &> /dev/null; then
        curl -L -o "${TOXIPROXY_BIN}" "${download_url}"
    elif command -v wget &> /dev/null; then
        wget -O "${TOXIPROXY_BIN}" "${download_url}"
    else
        log_error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi

    chmod +x "${TOXIPROXY_BIN}"
    log_info "Toxiproxy downloaded to ${TOXIPROXY_BIN}"
}

# Check if Toxiproxy is installed
check_toxiproxy() {
    if [ -f "${TOXIPROXY_BIN}" ]; then
        log_info "Toxiproxy found at ${TOXIPROXY_BIN}"
        return 0
    elif command -v toxiproxy-server &> /dev/null; then
        TOXIPROXY_BIN=$(command -v toxiproxy-server)
        log_info "Toxiproxy found in PATH: ${TOXIPROXY_BIN}"
        return 0
    else
        log_warn "Toxiproxy not found"
        return 1
    fi
}

# Check if Toxiproxy is already running
is_toxiproxy_running() {
    if curl -sf "http://localhost:${TOXIPROXY_PORT}/version" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Start Toxiproxy
start_toxiproxy() {
    if is_toxiproxy_running; then
        log_info "Toxiproxy is already running on port ${TOXIPROXY_PORT}"
        return 0
    fi

    log_info "Starting Toxiproxy on port ${TOXIPROXY_PORT}..."

    # Start in background
    "${TOXIPROXY_BIN}" -host "0.0.0.0" -port "${TOXIPROXY_PORT}" &
    local toxiproxy_pid=$!

    # Wait for Toxiproxy to be ready
    local max_wait=10
    local waited=0

    while ! is_toxiproxy_running; do
        if [ $waited -ge $max_wait ]; then
            log_error "Toxiproxy failed to start within ${max_wait} seconds"
            kill "${toxiproxy_pid}" 2>/dev/null || true
            exit 1
        fi

        sleep 1
        waited=$((waited + 1))
    done

    log_info "Toxiproxy started successfully (PID: ${toxiproxy_pid})"
    echo "${toxiproxy_pid}" > /tmp/toxiproxy.pid
}

# Stop Toxiproxy
stop_toxiproxy() {
    if [ -f /tmp/toxiproxy.pid ]; then
        local pid
        pid=$(cat /tmp/toxiproxy.pid)

        if kill -0 "${pid}" 2>/dev/null; then
            log_info "Stopping Toxiproxy (PID: ${pid})..."
            kill "${pid}"
            rm /tmp/toxiproxy.pid
            log_info "Toxiproxy stopped"
        else
            log_warn "Toxiproxy PID file exists but process not running"
            rm /tmp/toxiproxy.pid
        fi
    else
        # Try to find and kill by port
        local pid
        pid=$(lsof -ti :${TOXIPROXY_PORT} 2>/dev/null || true)

        if [ -n "${pid}" ]; then
            log_info "Stopping Toxiproxy (PID: ${pid})..."
            kill "${pid}"
            log_info "Toxiproxy stopped"
        else
            log_warn "Toxiproxy not running"
        fi
    fi
}

# Status check
status_toxiproxy() {
    if is_toxiproxy_running; then
        local version
        version=$(curl -s "http://localhost:${TOXIPROXY_PORT}/version")
        log_info "Toxiproxy is running on port ${TOXIPROXY_PORT} (version: ${version})"

        # List proxies
        local proxies
        proxies=$(curl -s "http://localhost:${TOXIPROXY_PORT}/proxies" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 || echo "")

        if [ -n "${proxies}" ]; then
            log_info "Active proxies:"
            echo "${proxies}" | while read -r proxy; do
                echo "  - ${proxy}"
            done
        else
            log_info "No active proxies"
        fi
    else
        log_warn "Toxiproxy is not running"
        return 1
    fi
}

# Main command dispatcher
main() {
    local command="${1:-start}"

    case "${command}" in
        install)
            download_toxiproxy
            ;;
        start)
            if ! check_toxiproxy; then
                download_toxiproxy
            fi
            start_toxiproxy
            ;;
        stop)
            stop_toxiproxy
            ;;
        restart)
            stop_toxiproxy
            sleep 1
            start_toxiproxy
            ;;
        status)
            status_toxiproxy
            ;;
        *)
            echo "Usage: $0 {install|start|stop|restart|status}"
            echo ""
            echo "Commands:"
            echo "  install   Download Toxiproxy binary"
            echo "  start     Start Toxiproxy server"
            echo "  stop      Stop Toxiproxy server"
            echo "  restart   Restart Toxiproxy server"
            echo "  status    Check Toxiproxy status and list proxies"
            exit 1
            ;;
    esac
}

main "$@"
