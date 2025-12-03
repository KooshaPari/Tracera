# Quick Start Guide - TraceRTM Desktop

Get up and running with TraceRTM Desktop in under 5 minutes.

## Prerequisites Check

Run these commands to verify you have the required tools:

```bash
# Check Rust installation
rustc --version
# Should show: rustc 1.70.0 or higher

# Check Node.js installation
node --version
# Should show: v18.0.0 or higher

# Check npm installation
npm --version
# Should show: 8.0.0 or higher
```

If any are missing, install them:

- **Rust**: https://rustup.rs/
- **Node.js**: https://nodejs.org/

## Installation

### 1. Install Dependencies

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/desktop
npm install
```

This will install both JavaScript and Rust dependencies.

### 2. Start Development Server

```bash
npm run tauri:dev
```

This will:
- Start the Vite dev server
- Compile the Rust backend
- Launch the desktop application

**First launch may take 2-5 minutes** as Rust compiles all dependencies.

## Project Structure

```
desktop/
├── src/                    # React frontend
│   ├── App.tsx            # Main app component
│   ├── main.tsx           # Entry point
│   ├── components/        # React components
│   └── lib/               # Utilities
├── src-tauri/             # Rust backend
│   ├── src/
│   │   ├── main.rs        # App setup
│   │   ├── commands.rs    # Command handlers
│   │   ├── sync.rs        # Sync engine
│   │   ├── menu.rs        # Native menus
│   │   ├── shortcuts.rs   # Keyboard shortcuts
│   │   └── db.rs          # Database
│   ├── Cargo.toml         # Rust dependencies
│   └── tauri.conf.json    # Tauri config
├── package.json           # Node dependencies
└── vite.config.ts         # Vite config
```

## Common Commands

```bash
# Development
npm run dev              # Start Vite dev server only
npm run tauri:dev        # Start full Tauri app with hot reload

# Building
npm run build            # Build frontend only
npm run tauri:build      # Build complete desktop app

# Platform-specific builds
npm run tauri:build:mac      # macOS universal binary
npm run tauri:build:windows  # Windows MSI
npm run tauri:build:linux    # Linux DEB/AppImage
```

## Testing the App

Once the app launches, you should see:

1. **Header** with app name and version
2. **Sync Indicator** in top-right (will show "Offline" initially)
3. **Welcome Card** with features
4. **Action Buttons** for creating projects

## Keyboard Shortcuts

Try these shortcuts in the app:

- `Cmd/Ctrl+N` - New Requirement
- `Cmd/Ctrl+Shift+N` - New Test
- `Cmd/Ctrl+S` - Save
- `Cmd/Ctrl+R` - Reload
- `Cmd/Ctrl+Alt+I` - Open DevTools

## Configuration

### Backend API URL

Edit `src-tauri/src/sync.rs`:

```rust
const API_BASE_URL: &str = "http://localhost:8000/api";
```

### Sync Interval

Edit `src-tauri/src/sync.rs`:

```rust
const SYNC_INTERVAL_SECONDS: u64 = 300; // 5 minutes
```

## Troubleshooting

### Port 1420 is busy

```bash
# Kill process using port 1420
lsof -ti:1420 | xargs kill -9
```

### Rust compilation errors

```bash
# Update Rust
rustup update

# Clear cargo cache
cd src-tauri
cargo clean
```

### Frontend not loading

```bash
# Clear node modules and reinstall
rm -rf node_modules
npm install
```

### macOS: Command not found errors

```bash
# Install Xcode Command Line Tools
xcode-select --install
```

### Linux: Missing dependencies

```bash
# Install all required libraries
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

## Next Steps

1. **Read the Architecture**: See `ARCHITECTURE.md` for system design
2. **Check the README**: See `README.md` for detailed documentation
3. **Build for Production**: Run `npm run tauri:build` when ready
4. **Configure Auto-Updates**: Update the endpoint in `tauri.conf.json`

## Development Workflow

1. **Make Changes** to React or Rust code
2. **Hot Reload** automatically updates the app
3. **Test Changes** in the running application
4. **Build** when ready for distribution

## Getting Help

- **Tauri Discord**: https://discord.com/invite/tauri
- **GitHub Issues**: https://github.com/tracertm/tracertm/issues
- **Documentation**: https://tauri.app/v2/guides/

## Success Indicators

You've successfully set up TraceRTM Desktop when:

- [ ] App launches without errors
- [ ] You see the welcome screen
- [ ] Sync indicator shows status
- [ ] Menu bar is visible with all menus
- [ ] Keyboard shortcuts work
- [ ] Hot reload works when you edit files

Enjoy building with TraceRTM Desktop!
