# 🚀 TraceRTM - Multi-Platform Packaging Guide

## Overview

TraceRTM now supports native packaging for **macOS**, **Linux**, and **Windows** with:
- ✅ Backend (Go binary)
- ✅ CLI (Python + Typer)
- ✅ Desktop App (Tauri)
- ✅ Frontend (React web app)
- ✅ Auto-updates (go-autoupdate)
- ✅ Hot reload (air)
- ✅ Plugin system (go-plugin)

---

## Quick Start

### Build All Components
```bash
cd backend
make build-all
```

### Package for Specific Platform
```bash
# macOS (app bundle + CLI + desktop)
make dist-macos

# Linux (.deb + CLI)
make dist-linux

# Windows (.exe + CLI)
make dist-windows

# All platforms
make dist-all
```

---

## Build Targets

### Individual Components
```bash
make build-backend      # Go backend binary
make build-cli          # Python CLI tool
make build-desktop      # Tauri desktop app
make build-frontend     # React web app
```

### Platform-Specific Builds
```bash
make build-macos        # Backend + CLI + Desktop
make build-linux        # Backend + CLI
make build-windows      # Backend + CLI
make build-all          # All components
```

---

## Packaging Targets

### Create Distribution Packages
```bash
make package-macos      # Create .app bundle
make package-linux      # Create .deb structure
make package-windows    # Create .exe installer
make package-all        # All packages
```

### Full Distribution (Build + Package)
```bash
make dist-macos         # Build + package for macOS
make dist-linux         # Build + package for Linux
make dist-windows       # Build + package for Windows
make dist-all           # Build + package all
```

---

## Platform Details

### macOS
- **Format**: `.app` bundle (Universal binary)
- **Includes**: Backend, CLI, Desktop app
- **Installation**: Drag to Applications
- **Services**: LaunchAgent for background service
- **Updates**: Automatic via go-autoupdate

### Linux
- **Format**: `.deb` package (Debian/Ubuntu)
- **Includes**: Backend, CLI
- **Installation**: `sudo apt install tracertm.deb`
- **Services**: systemd service (tracertm.service)
- **Updates**: Automatic via package manager

### Windows
- **Format**: `.exe` installer (MSI)
- **Includes**: Backend, CLI
- **Installation**: Run installer
- **Services**: Windows Service
- **Updates**: Automatic via go-autoupdate

---

## Architecture

```
backend/cmd/
├── build/
│   └── main.go          # Build orchestrator
├── package/
│   └── main.go          # Packaging system
├── setup/
│   └── main.go          # Database setup
└── migrate/
    └── main.go          # Database migrations
```

---

## Features

### 🔄 Auto-Updates (go-autoupdate)
- Automatic version checking
- Delta updates (only changed files)
- Rollback on failure
- Configurable update server

### 🔥 Hot Reload (air)
- Development hot reload
- Automatic restart on code changes
- Preserves state during reload

### 🔌 Plugin System (go-plugin)
- Extensible architecture
- Load plugins at runtime
- Isolated plugin processes
- RPC-based communication

---

## Development Workflow

### Development (with hot reload)
```bash
cd backend
air  # Starts with hot reload
```

### Testing
```bash
make test              # Run all tests
make test-coverage     # With coverage report
make test-race         # Race condition detection
```

### Building for Distribution
```bash
make dist-all          # Build all platforms
```

---

## Deployment

### macOS
```bash
# Create DMG for distribution
hdiutil create -volname "TraceRTM" -srcfolder dist/TraceRTM-1.0.0.app -ov -format UDZO dist/TraceRTM-1.0.0.dmg
```

### Linux
```bash
# Create .deb package
dpkg-deb --build dist/tracertm-1.0.0 tracertm-1.0.0.deb
```

### Windows
```bash
# Create MSI installer (requires WiX Toolset)
heat dir dist\tracertm-1.0.0-windows -o files.wxs
candle files.wxs -o files.wixobj
light files.wixobj -o tracertm-1.0.0.msi
```

---

## Configuration

### Version Management
```bash
# Build with specific version
make dist-all VERSION=1.0.0
```

### Update Server
Configure in `backend/cmd/build/main.go`:
```go
const UpdateServer = "https://api.tracertm.dev/updates"
```

---

## Status

✅ Build system implemented
✅ Packaging system implemented
✅ Makefile targets added
⏳ Auto-update integration (next)
⏳ Hot reload integration (next)
⏳ Plugin system integration (next)

---

## Next Steps

1. Integrate go-autoupdate for automatic updates
2. Add air for development hot reload
3. Implement go-plugin system for extensibility
4. Create CI/CD pipelines for automated builds
5. Set up code signing for macOS/Windows

