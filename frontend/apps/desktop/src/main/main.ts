import { BrowserWindow, Menu, app, ipcMain, shell } from 'electron';
import { autoUpdater } from 'electron-updater';
import path from 'node:path';

let mainWindow: BrowserWindow | undefined = undefined;

function createWindow(): void {
  mainWindow = new BrowserWindow({
    height: 900,
    minHeight: 600,
    minWidth: 800,
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, '../preload/preload.js'),
      sandbox: true,
    },
    width: 1400,
  });

  // Load the web app
  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL).catch((error: unknown) => {
      console.error('Failed to load URL:', error);
    });
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html')).catch((error: unknown) => {
      console.error('Failed to load file:', error);
    });
  }

  mainWindow.on('closed', () => {
    mainWindow = undefined;
  });
}

function getMenuTemplate(): Electron.MenuItemConstructorOptions[] {
  return [
    {
      label: 'TraceRTM',
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' },
      ],
    },
    {
      label: 'File',
      submenu: [
        {
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow?.webContents.send('menu:new-project');
          },
          label: 'New Project',
        },
        {
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            mainWindow?.webContents.send('menu:open-project');
          },
          label: 'Open Project',
        },
        { type: 'separator' },
        {
          click: () => {
            mainWindow?.webContents.send('menu:import');
          },
          label: 'Import...',
        },
        {
          click: () => {
            mainWindow?.webContents.send('menu:export');
          },
          label: 'Export...',
        },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Window',
      submenu: [{ role: 'minimize' }, { role: 'zoom' }, { type: 'separator' }, { role: 'front' }],
    },
    {
      label: 'Help',
      submenu: [
        {
          click: () => {
            shell.openExternal('https://tracertm.dev/docs').catch((error: unknown) => {
              console.error('Failed to open external URL:', error);
            });
          },
          label: 'Documentation',
        },
        {
          click: () => {
            shell
              .openExternal('https://github.com/tracertm/tracertm/issues')
              .catch((error: unknown) => {
                console.error('Failed to open external URL:', error);
              });
          },
          label: 'Report Issue',
        },
      ],
    },
  ];
}

// Create application menu
function createMenu(): void {
  const template = getMenuTemplate();
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

function setupIpcHandlers(): void {
  ipcMain.handle('app:version', () => app.getVersion());
  ipcMain.handle('app:check-updates', async () => {
    try {
      const result = await autoUpdater.checkForUpdates();
      return result?.updateInfo;
    } catch {
      return null;
    }
  });
}

async function initApp(): Promise<void> {
  setupIpcHandlers();

  try {
    await app.whenReady();
    createWindow();
    createMenu();
    autoUpdater.checkForUpdatesAndNotify().catch((error: unknown) => {
      console.error('Failed to check for updates:', error);
    });
  } catch (error) {
    console.error('Failed to initialize app:', error);
  }

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });

  app.on('activate', () => {
    if (mainWindow === undefined) {
      createWindow();
    }
  });
}

initApp().catch((error: unknown) => {
  console.error('Unhandled error in initApp:', error);
});
