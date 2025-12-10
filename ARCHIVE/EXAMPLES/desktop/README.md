# TraceRTM Desktop Application

Modern, offline-first requirements traceability management tool built with Tauri and React.

## Features

- **Offline-First Architecture**: Work without internet connection, sync when available
- **Native Performance**: Built with Rust and Tauri for maximum speed and efficiency
- **Cross-Platform**: Supports macOS, Windows, and Linux
- **Auto-Updates**: Automatic update checks and installation
- **Deep Linking**: Support for `tracertm://` protocol URLs
- **Native Menus**: Platform-native menu bars with keyboard shortcuts
- **SQLite Storage**: Local database for offline data persistence
- **Background Sync**: Automatic synchronization every 5 minutes

## Architecture

### Backend (Rust/Tauri)
- `src-tauri/src/main.rs` - Application entry point and setup
- `src-tauri/src/commands.rs` - Tauri command handlers for frontend-backend communication
- `src-tauri/src/sync.rs` - Offline-first synchronization engine
- `src-tauri/src/menu.rs` - Native menu bar implementation
- `src-tauri/src/shortcuts.rs` - Keyboard shortcuts management
- `src-tauri/src/db.rs` - SQLite database initialization and schema

### Frontend (React/TypeScript)
- `src/App.tsx` - Main application component
- `src/components/SyncIndicator.tsx` - Real-time sync status display
- `src/components/DeepLinkHandler.tsx` - Deep link URL handling

## Prerequisites

- [Rust](https://www.rust-lang.org/tools/install) 1.70+
- [Node.js](https://nodejs.org/) 18+
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)

### Platform-Specific Requirements

**macOS:**
- Xcode Command Line Tools: `xcode-select --install`

**Linux:**
```bash
sudo apt-get update
sudo apt-get install -y \
  libwebkit2gtk-4.0-dev \
  build-essential \
  curl \
  wget \
  libssl-dev \
  libgtk-3-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev
```

**Windows:**
- [Microsoft Visual Studio C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- [WebView2](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)

## Development

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run tauri:dev
```

This will:
1. Start the Vite development server on port 1420
2. Launch the Tauri application
3. Enable hot-reload for both frontend and backend

### Build for Production

```bash
npm run tauri:build
```

### Platform-Specific Builds

```bash
# macOS Universal Binary (Intel + Apple Silicon)
npm run tauri:build:mac

# Windows x64
npm run tauri:build:windows

# Linux x64
npm run tauri:build:linux
```

## Deep Linking

The application supports the `tracertm://` protocol for deep linking:

```
tracertm://open-requirement?id=REQ-123
tracertm://open-test?id=TEST-456
tracertm://open-project?id=PROJECT-789
tracertm://sync
```

## Keyboard Shortcuts

### File Operations
- `Cmd/Ctrl+N` - New Requirement
- `Cmd/Ctrl+Shift+N` - New Test
- `Cmd/Ctrl+O` - Open Project
- `Cmd/Ctrl+S` - Save

### Edit Operations
- `Cmd/Ctrl+Z` - Undo
- `Cmd/Ctrl+Shift+Z` - Redo
- `Cmd/Ctrl+X` - Cut
- `Cmd/Ctrl+C` - Copy
- `Cmd/Ctrl+V` - Paste
- `Cmd/Ctrl+A` - Select All

### View
- `Cmd/Ctrl+R` - Reload
- `Cmd/Ctrl+Alt+I` - Toggle Developer Tools

### Sync
- `Cmd/Ctrl+Shift+S` - Sync Now

## Configuration

### API Endpoint

Edit `src-tauri/src/sync.rs` to configure the backend API URL:

```rust
const API_BASE_URL: &str = "http://localhost:8000/api";
```

### Sync Interval

Adjust the sync interval in `src-tauri/src/sync.rs`:

```rust
const SYNC_INTERVAL_SECONDS: u64 = 300; // 5 minutes
```

## Auto-Updates

The application checks for updates on startup in production builds. Update configuration is in `src-tauri/tauri.conf.json`:

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

## Database Schema

Local SQLite database includes tables for:
- `requirements` - Requirements with status and metadata
- `tests` - Test cases linked to requirements
- `traces` - Many-to-many traceability relationships
- `sync_queue` - Pending changes for offline sync
- `attachments` - File attachments

## Troubleshooting

### Build Fails on macOS

Ensure Xcode Command Line Tools are installed:
```bash
xcode-select --install
```

### Build Fails on Linux

Install all required dependencies:
```bash
sudo apt-get install -y libwebkit2gtk-4.0-dev build-essential curl wget libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

### Port 1420 Already in Use

The development server requires port 1420. If it's in use:
```bash
# Find and kill the process using port 1420
lsof -ti:1420 | xargs kill -9
```

### Rust Compilation Errors

Update Rust to the latest version:
```bash
rustup update
```

## License

Copyright (c) 2024 TraceRTM Team

## Contributing

See the main project README for contribution guidelines.
