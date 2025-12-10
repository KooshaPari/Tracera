# TraceRTM Desktop Application - Complete Guide

## Overview

TraceRTM Desktop is a cross-platform native application built with Tauri 2.0, Rust, and React. It provides offline-first requirements traceability management with automatic sync, native features, and cross-platform support.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [Development](#development)
5. [Building & Distribution](#building--distribution)
6. [Testing](#testing)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)

## Features

### Core Features

- **Offline-First Architecture**: Full functionality without internet
- **Real-time Sync**: Automatic sync every 5 minutes when online
- **Delta Sync**: Only changed items are synced
- **Conflict Resolution**: Last-write-wins with conflict queue
- **Native Menus**: Platform-native menu bars
- **System Tray**: Quick access and background operation
- **Deep Linking**: `tracertm://` URL scheme support
- **Auto-Updates**: Automatic update checking and installation
- **Native Notifications**: Desktop notifications for sync events
- **Keyboard Shortcuts**: Full keyboard navigation

### Export Capabilities

- **JSON Export**: Complete project export with metadata
- **CSV Export**: Tabular data export for spreadsheets
- **Markdown Export**: Documentation-friendly format
- **Traceability Matrix**: Complete relationship mapping

## Architecture

### Technology Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: Rust + Tauri 2.0
- **Database**: SQLite with full-text search
- **Sync**: Custom offline-first sync engine
- **IPC**: Tauri command system

### Database Schema

```sql
-- Projects table
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    synced_at TEXT,
    is_deleted INTEGER DEFAULT 0
);

-- Items table (unified for all types)
CREATE TABLE items (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    item_type TEXT NOT NULL,  -- feature, code, test, api, etc.
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL,
    priority TEXT,
    version INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    synced_at TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Links table (traceability)
CREATE TABLE links (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    link_type TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT NOT NULL,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (source_id) REFERENCES items(id),
    FOREIGN KEY (target_id) REFERENCES items(id)
);

-- Sync queue
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    operation TEXT NOT NULL,  -- create, update, delete
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    retry_count INTEGER DEFAULT 0
);

-- Conflicts
CREATE TABLE conflicts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    local_version TEXT NOT NULL,
    remote_version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    resolved INTEGER DEFAULT 0
);
```

### Sync Engine Flow

```
1. User makes changes → Add to sync_queue
2. Background worker (every 5 min):
   a. Check network connectivity
   b. Upload local changes from sync_queue
   c. Download remote changes since last_sync
   d. Resolve conflicts (last-write-wins)
   e. Update local database
   f. Clear processed sync_queue items
   g. Emit sync-completed event
3. UI updates via event listeners
```

## Getting Started

### Prerequisites

**Required:**
- Node.js 18+ and npm
- Rust 1.70+ and Cargo

**Platform-Specific:**

**macOS:**
```bash
xcode-select --install
```

**Windows:**
- Visual Studio Build Tools
- WebView2 Runtime

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install -y \
  libwebkit2gtk-4.0-dev \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev
```

### Installation

```bash
# Navigate to desktop directory
cd desktop

# Install dependencies
npm install

# Run development server
npm run tauri:dev
```

## Development

### Project Structure

```
desktop/
├── src/                          # React frontend
│   ├── components/
│   │   ├── SyncIndicator.tsx     # Sync status UI
│   │   └── DeepLinkHandler.tsx   # Deep link handler
│   ├── hooks/
│   │   ├── useProjects.ts        # Project CRUD hooks
│   │   ├── useItems.ts           # Item CRUD hooks
│   │   └── useSync.ts            # Sync status hooks
│   ├── lib/
│   │   ├── api.ts                # Tauri command wrappers
│   │   └── tauri.ts              # Tauri utilities
│   ├── App.tsx                   # Main component
│   └── main.tsx                  # Entry point
│
├── src-tauri/                    # Rust backend
│   ├── src/
│   │   ├── main.rs               # App initialization
│   │   ├── lib.rs                # Module exports
│   │   ├── models.rs             # Data models
│   │   ├── db.rs                 # Database setup
│   │   ├── db_ops.rs             # Database operations
│   │   ├── commands.rs           # Basic commands
│   │   ├── commands_extended.rs  # CRUD commands
│   │   ├── sync.rs               # Sync engine
│   │   ├── menu.rs               # Native menus
│   │   ├── tray.rs               # System tray
│   │   ├── notifications.rs      # Notifications
│   │   ├── export.rs             # Export functions
│   │   └── shortcuts.rs          # Keyboard shortcuts
│   ├── tests/
│   │   └── integration_test.rs   # Integration tests
│   ├── Cargo.toml                # Rust dependencies
│   └── tauri.conf.json           # Tauri config
│
├── scripts/
│   ├── build-all.sh              # Cross-platform build
│   └── test.sh                   # Test runner
│
└── package.json                  # Node dependencies
```

### Development Workflow

1. **Start dev server:**
   ```bash
   npm run tauri:dev
   ```

2. **Make changes** - Hot reload enabled for both Rust and React

3. **Run tests:**
   ```bash
   ./scripts/test.sh
   ```

4. **Build:**
   ```bash
   npm run tauri:build
   ```

### Adding New Features

**1. Add Rust Model (models.rs):**
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NewEntity {
    pub id: String,
    pub name: String,
    // ...
}
```

**2. Add Database Operations (db_ops.rs):**
```rust
impl Database {
    pub fn create_new_entity(&self, entity: &NewEntity) -> Result<()> {
        // Implementation
    }
}
```

**3. Add Tauri Command (commands_extended.rs):**
```rust
#[tauri::command]
pub async fn create_new_entity(
    app: AppHandle,
    name: String,
) -> Result<NewEntity, String> {
    // Implementation
}
```

**4. Register Command (main.rs):**
```rust
.invoke_handler(tauri::generate_handler![
    // ... existing commands
    commands_extended::create_new_entity,
])
```

**5. Add TypeScript API (lib/api.ts):**
```typescript
export const newEntityApi = {
  create: (name: string): Promise<NewEntity> =>
    invoke('create_new_entity', { name }),
};
```

**6. Create React Hook (hooks/useNewEntity.ts):**
```typescript
export function useNewEntities() {
  // Hook implementation
}
```

## Building & Distribution

### Build for Current Platform

```bash
npm run tauri:build
```

### Build for Specific Platforms

```bash
# macOS (Universal)
npm run tauri:build:mac

# Windows
npm run tauri:build:windows

# Linux
npm run tauri:build:linux
```

### Using Build Script

```bash
# Build all platforms (if available)
./scripts/build-all.sh all

# Build specific platform
./scripts/build-all.sh mac
./scripts/build-all.sh windows
./scripts/build-all.sh linux
```

### Build Artifacts

**macOS:**
- `target/release/bundle/dmg/TraceRTM_0.1.0_universal.dmg`
- `target/release/bundle/macos/TraceRTM.app`

**Windows:**
- `target/release/bundle/msi/TraceRTM_0.1.0_x64_en-US.msi`
- `target/release/bundle/nsis/TraceRTM_0.1.0_x64-setup.exe`

**Linux:**
- `target/release/bundle/deb/tracertm_0.1.0_amd64.deb`
- `target/release/bundle/appimage/tracertm_0.1.0_amd64.AppImage`

### Code Signing

**macOS:**
```json
// tauri.conf.json
{
  "bundle": {
    "macOS": {
      "signingIdentity": "Developer ID Application: Your Name (TEAM_ID)",
      "entitlements": "path/to/entitlements.plist"
    }
  }
}
```

**Windows:**
```json
{
  "bundle": {
    "windows": {
      "certificateThumbprint": "YOUR_CERTIFICATE_THUMBPRINT",
      "timestampUrl": "http://timestamp.digicert.com"
    }
  }
}
```

## Testing

### Run All Tests

```bash
./scripts/test.sh
```

### Rust Tests Only

```bash
cd src-tauri
cargo test
```

### Integration Tests

```bash
cd src-tauri
cargo test --test integration_test
```

### Test Coverage

```bash
cd src-tauri
cargo tarpaulin --out Html
```

## API Reference

### Project API

```typescript
import { projectApi } from './lib/api';

// Create project
const project = await projectApi.create('My Project', 'Description');

// Get project
const project = await projectApi.get('project-id');

// List projects
const projects = await projectApi.list();

// Update project
await projectApi.update(project);

// Delete project
await projectApi.delete('project-id');
```

### Item API

```typescript
import { itemApi } from './lib/api';

// Create item
const item = await itemApi.create(
  'project-id',
  'feature',
  'Item Title',
  'Item content...',
  'in-progress',
  'high'
);

// List items
const items = await itemApi.list('project-id', 'feature');

// Update item
await itemApi.update(item);

// Delete item
await itemApi.delete('item-id');
```

### Link API

```typescript
import { linkApi } from './lib/api';

// Create link
const link = await linkApi.create(
  'project-id',
  'source-id',
  'target-id',
  'implements'
);

// List links
const links = await linkApi.list('project-id');

// Delete link
await linkApi.delete('link-id');
```

### Sync API

```typescript
import { syncApi } from './lib/api';

// Trigger sync
await syncApi.forceSync();

// Get sync status
const status = await syncApi.getStatus();
// {
//   is_syncing: boolean,
//   last_sync: string | null,
//   sync_error: string | null,
//   pending_changes: number,
//   online: boolean
// }

// Get pending count
const count = await syncApi.getPendingCount();
```

### Export API

```typescript
import { exportApi } from './lib/api';
import { save } from '@tauri-apps/plugin-dialog';

// Export to JSON
const path = await save({ defaultPath: 'project.json' });
await exportApi.json('project-id', path);

// Export to CSV
const path = await save({ defaultPath: 'project.csv' });
await exportApi.csv('project-id', path);

// Export traceability matrix
const path = await save({ defaultPath: 'matrix.csv' });
await exportApi.traceabilityMatrix('project-id', path);

// Export to Markdown
const path = await save({ defaultPath: 'project.md' });
await exportApi.markdown('project-id', path);
```

### React Hooks

```typescript
import { useProjects, useItems, useSync } from './hooks';

function MyComponent() {
  // Projects hook
  const {
    projects,
    loading,
    error,
    createProject,
    updateProject,
    deleteProject,
  } = useProjects();

  // Items hook
  const {
    items,
    loading,
    error,
    createItem,
    updateItem,
    deleteItem,
  } = useItems('project-id', 'feature');

  // Sync hook
  const { status, error, sync } = useSync();

  // ...
}
```

## Troubleshooting

### Build Issues

**Error: `xcrun: error: unable to find utility "metal"`**
```bash
sudo xcode-select --switch /Library/Developer/CommandLineTools
```

**Error: `webkit2gtk not found`**
```bash
sudo apt-get install libwebkit2gtk-4.0-dev
```

**Error: `Visual Studio Build Tools not found`**
- Install Visual Studio Build Tools with C++ workload
- Or install Visual Studio Community with Desktop C++ workload

### Runtime Issues

**Database locked error:**
- Close all instances of the app
- Delete database file and restart
  - macOS: `~/Library/Application Support/com.tracertm.desktop/`
  - Windows: `%APPDATA%\com.tracertm.desktop\`
  - Linux: `~/.local/share/com.tracertm.desktop/`

**Sync not working:**
1. Check network connectivity
2. Verify API_BASE_URL in `src-tauri/src/sync.rs`
3. Check sync queue: Open DevTools and run:
   ```javascript
   await invoke('get_pending_sync_count')
   ```

**Deep links not working:**
- macOS: Reinstall the app
- Windows: Run as administrator once to register URL scheme
- Linux: Check `.desktop` file registration

### Performance Issues

**Slow startup:**
- Database might be large - check database size
- Try vacuuming database:
  ```sql
  VACUUM;
  ANALYZE;
  ```

**High memory usage:**
- Check for memory leaks in React components
- Ensure proper cleanup in useEffect hooks
- Monitor sync queue size

## Configuration

### Environment Variables

**Development:**
```bash
RUST_LOG=debug npm run tauri:dev
TAURI_DEBUG=1 npm run tauri:dev
```

**Production:**
```bash
API_BASE_URL=https://api.tracertm.dev npm run tauri:build
```

### Sync Configuration

Edit `src-tauri/src/sync.rs`:
```rust
const SYNC_INTERVAL_SECONDS: u64 = 300; // 5 minutes
const API_BASE_URL: &str = "http://localhost:8000/api";
```

### Auto-Update Configuration

Edit `src-tauri/tauri.conf.json`:
```json
{
  "plugins": {
    "updater": {
      "endpoints": [
        "https://api.tracertm.dev/updates/{{target}}/{{current_version}}"
      ]
    }
  }
}
```

## Best Practices

### Offline-First Development

1. **Always queue changes** - Never directly call API
2. **Handle offline state** - Show offline indicators
3. **Optimistic updates** - Update UI immediately
4. **Conflict resolution** - Handle sync conflicts gracefully

### Performance

1. **Lazy load data** - Don't load everything at startup
2. **Virtualize lists** - Use virtual scrolling for large lists
3. **Debounce sync** - Don't sync on every keystroke
4. **Index database** - Ensure proper SQLite indices

### Security

1. **Sanitize input** - Always validate user input
2. **Parameterized queries** - Use Rust params, not string interpolation
3. **Secure storage** - Use Tauri secure storage for sensitive data
4. **CSP headers** - Configure Content Security Policy

## Contributing

See main project CONTRIBUTING.md

## License

See LICENSE file

## Support

- Docs: https://tracertm.dev/docs
- Issues: https://github.com/tracertm/tracertm/issues
- Email: support@tracertm.dev
