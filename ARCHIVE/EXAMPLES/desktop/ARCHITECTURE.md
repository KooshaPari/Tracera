# TraceRTM Desktop Architecture

## Overview

TraceRTM Desktop is built using the Tauri framework, combining a Rust backend with a React frontend for a native, performant desktop application.

## Technology Stack

### Backend
- **Rust** - High-performance, memory-safe systems programming
- **Tauri 2.1** - Modern desktop application framework
- **SQLite (rusqlite)** - Embedded database for offline storage
- **Tokio** - Async runtime for concurrent operations
- **Reqwest** - HTTP client for API communication

### Frontend
- **React 18** - UI component library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **CSS3** - Modern styling with custom properties

## Architecture Layers

```
┌─────────────────────────────────────────┐
│           React Frontend                │
│  (TypeScript, React, CSS)               │
└─────────────────┬───────────────────────┘
                  │ Tauri Commands
                  ▼
┌─────────────────────────────────────────┐
│          Tauri Core Layer               │
│  (IPC, Window Management, Events)       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│          Rust Backend                   │
│  ┌───────────────────────────────────┐  │
│  │ Commands (commands.rs)            │  │
│  ├───────────────────────────────────┤  │
│  │ Sync Engine (sync.rs)             │  │
│  ├───────────────────────────────────┤  │
│  │ Database (db.rs)                  │  │
│  ├───────────────────────────────────┤  │
│  │ Menu System (menu.rs)             │  │
│  ├───────────────────────────────────┤  │
│  │ Shortcuts (shortcuts.rs)          │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
     ┌────────────┴────────────┐
     ▼                         ▼
┌──────────┐            ┌──────────────┐
│  SQLite  │            │  Remote API  │
│ Database │            │   (HTTP)     │
└──────────┘            └──────────────┘
```

## Core Components

### 1. Main Application (main.rs)

Entry point that:
- Initializes all Tauri plugins
- Sets up the database
- Creates native menus
- Registers keyboard shortcuts
- Starts background sync
- Handles deep links
- Manages auto-updates

### 2. Sync Engine (sync.rs)

Offline-first synchronization system:

**Features:**
- Background sync every 5 minutes
- Conflict resolution (last-write-wins)
- Network connectivity detection
- Pending changes queue
- Event emission for UI updates

**Sync Flow:**
```
1. Check network connectivity
2. Upload local changes
3. Download remote changes
4. Resolve conflicts
5. Update local database
6. Emit sync events
```

### 3. Database Layer (db.rs)

SQLite schema with tables:
- `requirements` - Requirements with metadata
- `tests` - Test cases
- `traces` - Traceability links
- `sync_queue` - Offline change queue
- `attachments` - File attachments

**Indices:**
- Status-based queries
- Timestamp-based queries
- Relationship lookups

### 4. Commands (commands.rs)

Tauri command handlers exposed to frontend:

```rust
sync_data()           // Manual sync trigger
get_sync_status()     // Current sync state
force_sync()          // Force immediate sync
get_local_data()      // Retrieve stored data
save_local_data()     // Save data locally
clear_cache()         // Clear local cache
get_app_info()        // App metadata
```

### 5. Menu System (menu.rs)

Native menu bars with:
- Application menu (About, Quit, etc.)
- File menu (New, Open, Save)
- Edit menu (Undo, Redo, Cut, Copy, Paste)
- View menu (Reload, DevTools, Fullscreen)
- Sync menu (Sync Now, Sync Status, Offline Mode)
- Window menu (Minimize, Maximize)
- Help menu (Docs, Issues, Updates)

### 6. Keyboard Shortcuts (shortcuts.rs)

Cross-platform shortcuts:
- File operations (Cmd/Ctrl+N, Cmd/Ctrl+S)
- Edit operations (Cmd/Ctrl+Z, Cmd/Ctrl+C)
- Navigation (Cmd/Ctrl+[, Cmd/Ctrl+])
- Sync (Cmd/Ctrl+Shift+S)
- Developer tools (Cmd/Ctrl+Alt+I)

## Frontend Architecture

### Component Hierarchy

```
App
├── DeepLinkHandler (invisible)
├── Header
│   ├── AppInfo
│   └── SyncIndicator
│       └── SyncDetails (dropdown)
├── Main
│   └── WelcomeScreen
│       ├── Features Grid
│       └── Actions
└── Footer
```

### State Management

Currently using React hooks for local state:
- `useState` - Component state
- `useEffect` - Side effects and event listeners

Future: Could integrate Redux or Zustand for complex state.

### Event System

Frontend listens to backend events:
- `sync-started` - Sync operation began
- `sync-completed` - Sync finished successfully
- `sync-error` - Sync failed
- `deep-link` - Deep link URL received
- `menu:*` - Menu item clicked

## Data Flow

### Offline-First Flow

```
User Action
    ↓
Frontend (React)
    ↓
Tauri Command
    ↓
Backend (Rust)
    ↓
SQLite (Local DB)
    ↓
Sync Queue
    ↓
Background Sync Task
    ↓
Remote API (when online)
```

### Sync Flow

```
Background Timer (5 min)
    ↓
Check Network
    ↓
[Online] → Upload Queue → Download Changes → Resolve Conflicts
    ↓
Update Local DB
    ↓
Emit Events
    ↓
Update UI
```

## Security

### Content Security Policy

Strict CSP configured in `tauri.conf.json`:
- Allows local resources only
- Permits API connections to configured endpoints
- Blocks inline scripts (except whitelisted)
- Prevents XSS attacks

### Data Storage

- All data encrypted at rest (OS-level)
- Credentials stored in OS keychain (future)
- No sensitive data in logs
- HTTPS for all API communications

## Build System

### Development

```bash
npm run tauri:dev
```

1. Vite starts dev server (port 1420)
2. Tauri watches Rust files
3. Hot reload for frontend
4. Incremental compilation for backend

### Production

```bash
npm run tauri:build
```

1. Vite builds optimized frontend
2. Cargo builds release binary
3. Tauri bundles application
4. Creates platform-specific installers

### Cross-Platform Builds

**macOS:**
- Universal binary (Intel + Apple Silicon)
- DMG installer
- Code signing support

**Windows:**
- MSI installer (WiX)
- NSIS installer
- Code signing support

**Linux:**
- DEB package (Debian/Ubuntu)
- AppImage (universal)

## Auto-Update System

1. Check endpoint on startup
2. Compare versions
3. Prompt user for update
4. Download update bundle
5. Install and restart

Update endpoint format:
```
https://api.tracertm.dev/updates/{target}/{current_version}
```

## Deep Linking

Protocol: `tracertm://`

Supported URLs:
```
tracertm://open-requirement?id=REQ-123
tracertm://open-test?id=TEST-456
tracertm://open-project?id=PROJECT-789
tracertm://sync
```

Implementation:
1. OS triggers app with URL
2. Tauri deep-link plugin captures
3. Event emitted to frontend
4. React router navigates

## Performance Considerations

### Backend Optimizations
- Async I/O with Tokio
- Connection pooling for SQLite
- Lazy loading for large datasets
- Indexed database queries

### Frontend Optimizations
- Code splitting with Vite
- Lazy component loading
- Virtual scrolling for long lists
- Debounced search/filter

### Memory Management
- Rust's ownership system prevents leaks
- React cleanup in useEffect
- Database connection management
- Event listener cleanup

## Testing Strategy

### Backend Tests
```rust
#[cfg(test)]
mod tests {
    // Unit tests for Rust code
}
```

### Frontend Tests
- Jest for unit tests
- React Testing Library for components
- Playwright for E2E tests

### Integration Tests
- Tauri command testing
- Full sync flow testing
- Deep link testing

## Future Enhancements

1. **Multi-window support** - Open multiple projects
2. **Plugin system** - Extensibility via plugins
3. **Theme system** - Dark/light/custom themes
4. **Advanced conflict resolution** - Three-way merge
5. **Real-time collaboration** - WebSocket sync
6. **Offline file handling** - Attachment sync
7. **Search indexing** - Full-text search
8. **Export/import** - Multiple formats

## Dependencies

See `package.json` and `Cargo.toml` for full dependency lists.

### Key Dependencies

**Frontend:**
- `@tauri-apps/api` - Tauri JavaScript API
- `react` - UI library
- `react-dom` - React renderer

**Backend:**
- `tauri` - Application framework
- `serde` - Serialization
- `tokio` - Async runtime
- `rusqlite` - SQLite bindings
- `reqwest` - HTTP client

## Development Guidelines

1. **Type Safety** - Use TypeScript for frontend, leverage Rust's type system
2. **Error Handling** - Proper error propagation, user-friendly messages
3. **Logging** - Use `log` crate for backend, `console` for frontend
4. **Code Style** - Follow Rust and TypeScript conventions
5. **Documentation** - Comment complex logic, update this doc
6. **Testing** - Write tests for critical paths
7. **Security** - Validate all inputs, sanitize outputs

## Resources

- [Tauri Documentation](https://tauri.app/v2/guides/)
- [Rust Book](https://doc.rust-lang.org/book/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
