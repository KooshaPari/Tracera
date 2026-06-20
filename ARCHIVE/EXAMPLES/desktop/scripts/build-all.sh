#!/bin/bash

# Build script for all platforms
# Usage: ./scripts/build-all.sh [mac|windows|linux|all]

set -e

PLATFORM=${1:-all}
BUILD_DIR="./target/release/bundle"

echo "================================================"
echo "TraceRTM Desktop - Cross-Platform Build Script"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

function log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Build for macOS
function build_mac() {
    log_info "Building for macOS (Universal)..."
    npm run tauri:build:mac
    log_info "macOS build completed: $BUILD_DIR/dmg/"
}

# Build for Windows
function build_windows() {
    log_info "Building for Windows..."
    npm run tauri:build:windows
    log_info "Windows build completed: $BUILD_DIR/msi/"
}

# Build for Linux
function build_linux() {
    log_info "Building for Linux..."
    npm run tauri:build:linux
    log_info "Linux build completed: $BUILD_DIR/deb/ and $BUILD_DIR/appimage/"
}

# Main build logic
case $PLATFORM in
    mac|macos)
        build_mac
        ;;
    windows|win)
        build_windows
        ;;
    linux)
        build_linux
        ;;
    all)
        log_info "Building for all platforms..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            build_mac
        else
            log_warn "Skipping macOS build (not on macOS)"
        fi

        if command -v cargo &> /dev/null; then
            if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
                build_windows
            else
                log_warn "Skipping Windows build (not on Windows)"
            fi

            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                build_linux
            else
                log_warn "Skipping Linux build (not on Linux)"
            fi
        else
            log_error "Rust/Cargo not found. Please install Rust."
            exit 1
        fi
        ;;
    *)
        log_error "Unknown platform: $PLATFORM"
        echo "Usage: $0 [mac|windows|linux|all]"
        exit 1
        ;;
esac

log_info "Build process completed!"
log_info "Artifacts available in: $BUILD_DIR"
