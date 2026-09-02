const { app, BrowserWindow, Tray, Menu, nativeImage } = require('electron');
const path = require('path');

let mainWindow = null;
let tray = null;

const API_URL = process.env.TRACERA_API_URL || 'http://127.0.0.1:8080';
const DASHBOARD_URL = process.env.TRACERA_DASHBOARD_URL || 'https://tracera-kappa.vercel.app';

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: 'Tracera',
    webPreferences: { nodeIntegration: false, contextIsolation: true }
  });
  mainWindow.loadURL(DASHBOARD_URL);
  mainWindow.on('close', (e) => {
    if (!app.isQuitting) { e.preventDefault(); mainWindow.hide(); }
  });
}

function createTray() {
  tray = new Tray(nativeImage.createEmpty());
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Open Dashboard', click: () => { mainWindow.show(); mainWindow.loadURL(DASHBOARD_URL); } },
    { label: 'Open API Server', click: () => { mainWindow.show(); mainWindow.loadURL(API_URL + '/healthz'); } },
    { type: 'separator' },
    { label: 'Check Health', click: async () => {
      try {
        const resp = await fetch(API_URL + '/healthz');
        const data = await resp.json();
        mainWindow.show();
        mainWindow.webContents.executeJavaScript(`alert('Server: ' + JSON.stringify(${JSON.stringify(data)}))`);
      } catch(e) {
        mainWindow.show();
        mainWindow.webContents.executeJavaScript(`alert('Server unreachable')`);
      }
    }},
    { type: 'separator' },
    { label: 'Quit', click: () => { app.isQuitting = true; app.quit(); } }
  ]);
  tray.setToolTip('Tracera');
  tray.setContextMenu(contextMenu);
  tray.on('double-click', () => mainWindow.show());
}

app.whenReady().then(() => { createWindow(); createTray(); });
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
