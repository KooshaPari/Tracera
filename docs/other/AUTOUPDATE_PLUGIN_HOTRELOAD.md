# 🚀 TraceRTM - Auto-Update, Plugin System & Hot Reload

## Overview

TraceRTM now includes three powerful development and deployment features:

1. **🔄 Auto-Update** - Automatic version checking and installation
2. **🔌 Plugin System** - Extensible architecture with runtime plugins
3. **🔥 Hot Reload** - Development hot reload with air

---

## 1. Auto-Update System

### Features
- ✅ Automatic version checking
- ✅ Delta updates (only changed files)
- ✅ Rollback on failure
- ✅ Configurable update server
- ✅ Cross-platform support

### Usage

#### Enable Auto-Updates
```go
import "tracertm/internal/autoupdate"

config := autoupdate.UpdateConfig{
    UpdateServer: "https://api.tracertm.dev/updates",
    CurrentVersion: "1.0.0",
    CheckInterval: 24 * time.Hour,
    Enabled: true,
}

checker := autoupdate.NewUpdateChecker(config)
go checker.Start(ctx)
```

#### Check for Updates Manually
```go
if err := checker.CheckNow(); err != nil {
    log.Printf("Update check failed: %v", err)
}
```

#### Get Current Version
```go
version := checker.GetCurrentVersion()
fmt.Printf("Current version: %s\n", version)
```

### Update Server API

```
GET /latest?os=darwin&arch=arm64
Response: 1.0.1

GET /download/1.0.1?os=darwin&arch=arm64
Response: Binary file
```

---

## 2. Plugin System

### Features
- ✅ Runtime plugin loading
- ✅ Isolated plugin processes
- ✅ RPC-based communication
- ✅ Plugin discovery
- ✅ Hot plugin loading/unloading

### Creating a Plugin

```go
package main

import "tracertm/internal/plugin"

type MyPlugin struct{}

func (p *MyPlugin) Name() string {
    return "my-plugin"
}

func (p *MyPlugin) Version() string {
    return "1.0.0"
}

func (p *MyPlugin) Execute(args map[string]interface{}) (interface{}, error) {
    // Plugin logic here
    return "result", nil
}

func New() plugin.PluginInterface {
    return &MyPlugin{}
}
```

### Building a Plugin

```bash
go build -buildmode=plugin -o plugins/my-plugin.so ./plugins/my-plugin
```

### Using Plugins

```go
import "tracertm/internal/plugin"

pm := plugin.NewPluginManager("./plugins")

// Load all plugins
pm.LoadAllPlugins()

// Execute a plugin
result, err := pm.ExecutePlugin("my-plugin", map[string]interface{}{
    "key": "value",
})

// List loaded plugins
plugins := pm.ListPlugins()
```

---

## 3. Hot Reload (air)

### Features
- ✅ Automatic restart on code changes
- ✅ Preserves state during reload
- ✅ Fast rebuild
- ✅ Development-only

### Installation

```bash
go install github.com/cosmtrek/air@latest
```

### Usage

```bash
cd backend
air
```

### Configuration

Edit `.air.toml`:
```toml
[build]
  cmd = "go build -o ./tmp/main ."
  bin = "./tmp/main"
  delay = 1000
  exclude_dir = ["assets", "tmp", "vendor"]
```

---

## Integration Example

```go
package main

import (
    "context"
    "time"
    "tracertm/internal/autoupdate"
    "tracertm/internal/plugin"
)

func main() {
    ctx := context.Background()

    // Setup auto-update
    updateConfig := autoupdate.UpdateConfig{
        UpdateServer: "https://api.tracertm.dev/updates",
        CurrentVersion: "1.0.0",
        CheckInterval: 24 * time.Hour,
        Enabled: true,
    }
    checker := autoupdate.NewUpdateChecker(updateConfig)
    go checker.Start(ctx)

    // Setup plugin system
    pm := plugin.NewPluginManager("./plugins")
    pm.LoadAllPlugins()

    // Start your application
    // ...
}
```

---

## Makefile Commands

```bash
# Development with hot reload
make dev              # Runs with air

# Build for distribution
make build-all        # Build all components
make dist-all         # Build + package all

# Plugin management
make build-plugin     # Build a plugin
make load-plugins     # Load all plugins
```

---

## Status

✅ Auto-update system implemented
✅ Plugin system implemented
✅ Hot reload configuration created
⏳ Integration tests (next)
⏳ CI/CD pipelines (next)

---

## Next Steps

1. Add integration tests for auto-update
2. Create example plugins
3. Set up CI/CD for automated builds
4. Implement update server
5. Add plugin marketplace

