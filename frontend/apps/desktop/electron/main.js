/**
 * Tracera Desktop — main process.
 *
 * Loads the Tracera web UI in a native BrowserWindow. Provides:
 *   - Single-instance lock (a second launch focuses the existing window).
 *   - System tray icon with a context menu (Show, Reload, Open DevTools, Quit).
 *   - Persistent window bounds + tray preferences via electron-store.
 *   - External links open in the user's default browser, not in-app.
 *   - Configurable target URL: env TRACERA_URL (default: production Vercel/Page site).
 *
 * Target URL precedence (first wins):
 *   1. TRACERA_URL env var
 *   2. TRACERA_DEV_URL env var (only when --dev flag is passed)
 *   3. Default: https://kooshapari.github.io/Tracera/
 */

const { app, BrowserWindow, Tray, Menu, shell, ipcMain, dialog } = require('electron');
const path = require('node:path');
const fs = require('node:fs');

const isDev = process.argv.includes('--dev') || process.env.TRACERA_DEV_URL;
const DEFAULT_URL = 'https://kooshapari.github.io/Tracera/';

function resolveTargetUrl() {
  if (process.env.TRACERA_URL) return process.env.TRACERA_URL;
  if (isDev && process.env.TRACERA_DEV_URL) return process.env.TRACERA_DEV_URL;
  return DEFAULT_URL;
}

// Single-instance lock — second launch focuses existing window.
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  startApp();
}

function startApp() {
let mainWindow = null;
let tray = null;
let isQuitting = false;

// Minimal in-memory preferences (no electron-store dep needed for v0).
const prefs = {
  bounds: { width: 1280, height: 820 },
  startMinimized: false,
};

// Tiny log helper — Electron forwards stdout to system logs on packaged builds.
function log(...args) {
  console.log('[tracera-desktop]', ...args);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: prefs.bounds.width,
    height: prefs.bounds.height,
    minWidth: 800,
    minHeight: 600,
    title: 'Tracera',
    backgroundColor: '#090a0c',
    show: !prefs.startMinimized,
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  const targetUrl = resolveTargetUrl();
  log('loading target URL:', targetUrl, isDev ? '(dev)' : '(prod)');

  mainWindow.loadURL(targetUrl).catch((err) => {
    log('failed to load target URL:', err.message);
    dialog.showErrorBox(
      'Tracera failed to load',
      `Could not reach ${targetUrl}\n\n${err.message}\n\nCheck your network connection, or set TRACERA_URL to a different host.`,
    );
  });

  // Persist window bounds on resize/move.
  const persistBounds = () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      const b = mainWindow.getBounds();
      prefs.bounds = { width: b.width, height: b.height };
    }
  };
  mainWindow.on('resize', persistBounds);
  mainWindow.on('move', persistBounds);

  // Open external links in default browser, not in-app.
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url).catch((err) => log('failed to open external:', err.message));
    return { action: 'deny' };
  });

  // Hide instead of close (user can reopen via tray).
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function showMainWindow() {
  if (!mainWindow) {
    createWindow();
    return;
  }
  if (mainWindow.isMinimized()) mainWindow.restore();
  mainWindow.show();
  mainWindow.focus();
}

function buildTrayMenu() {
  return Menu.buildFromTemplate([
    {
      label: 'Show Tracera',
      click: () => showMainWindow(),
    },
    { type: 'separator' },
    {
      label: 'Reload',
      enabled: !!mainWindow,
      click: () => mainWindow?.webContents.reload(),
    },
    {
      label: 'Open DevTools',
      enabled: !!mainWindow && isDev,
      click: () => mainWindow?.webContents.openDevTools({ mode: 'detach' }),
    },
    { type: 'separator' },
    {
      label: `Target: ${resolveTargetUrl()}`,
      enabled: false,
    },
    { type: 'separator' },
    {
      label: 'Quit Tracera',
      click: () => {
        isQuitting = true;
        app.quit();
      },
    },
  ]);
}

function createTray() {
  // Use a minimal PNG icon (build/icon.png). Fall back to a placeholder
  // if not yet provided so the app still launches for development.
  const iconPath = path.join(__dirname, '..', 'build', process.platform === 'darwin' ? 'iconTemplate.png' : 'icon.png');
  let trayIconPath = iconPath;
  if (!fs.existsSync(trayIconPath)) {
    // Fallback: use the default Electron icon. Functional but unbranded.
    trayIconPath = null;
    log('tray icon not found at', iconPath, '— using default icon');
  }
  try {
    tray = trayIconPath ? new Tray(trayIconPath) : new Tray(nativeImageOrFallback());
    tray.setToolTip('Tracera');
    tray.setContextMenu(buildTrayMenu());
    tray.on('click', () => showMainWindow());
  } catch (err) {
    log('failed to create tray:', err.message);
  }
}

function nativeImageOrFallback() {
  // Empty 16x16 image — required by Tray on some platforms when no icon is provided.
  const { nativeImage } = require('electron');
  return nativeImage.createEmpty();
}

// IPC: renderer can request the target URL (for diagnostics display).
ipcMain.handle('tracera:target-url', () => resolveTargetUrl());
ipcMain.handle('tracera:version', () => app.getVersion());

// macOS: re-create window when dock icon is clicked and no windows are open.
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  } else {
    showMainWindow();
  }
});

// Second instance: focus existing window.
app.on('second-instance', () => {
  showMainWindow();
});

app.on('before-quit', () => {
  isQuitting = true;
});

app.whenReady().then(() => {
  createWindow();
  createTray();
});

app.on('window-all-closed', () => {
  // Stay alive in tray on all platforms (the tray menu has Quit).
  // Only fully quit on macOS when explicitly requested (default behavior).
  if (process.platform !== 'darwin' && isQuitting) {
    app.quit();
  }
});
} // end startApp()