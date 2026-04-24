import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

// ---- Electron mock wiring ------------------------------------------------
// Main.ts registers side-effects at module scope (ipcMain.handle, app.on,
// App.whenReady).  We capture those callbacks through the mocks below so each
// Test can invoke them in isolation.

const whenReadyCallback: (() => void)[] = [];
const appOnCallbacks: Record<string, ((...a: unknown[]) => void)[]> = {};
const ipcHandlers: Record<string, (...a: unknown[]) => unknown> = {};

const mockLoadURL = vi.fn(() => Promise.resolve());
const mockLoadFile = vi.fn(() => Promise.resolve());
const mockOpenDevTools = vi.fn();
const mockWebContentsSend = vi.fn();
const mockOn = vi.fn();

function makeBrowserWindowInstance() {
  return {
    loadFile: mockLoadFile,
    loadURL: mockLoadURL,
    on: mockOn,
    webContents: {
      openDevTools: mockOpenDevTools,
      send: mockWebContentsSend,
    },
  };
}

const MockBrowserWindow = vi.fn(makeBrowserWindowInstance);

const mockSetApplicationMenu = vi.fn();
const mockBuildFromTemplate = vi.fn(
  (t: unknown) => `built-menu-from-template:${JSON.stringify(t).slice(0, 20)}`,
);

const mockOpenExternal = vi.fn(() => Promise.resolve());

const mockGetVersion = vi.fn(() => '1.2.3');

const mockCheckForUpdates = vi.fn();
const mockCheckForUpdatesAndNotify = vi.fn(() => Promise.resolve());

const whenReadyPromise = Promise.resolve();

vi.mock('electron', () => ({
  BrowserWindow: MockBrowserWindow,
  Menu: {
    buildFromTemplate: mockBuildFromTemplate,
    setApplicationMenu: mockSetApplicationMenu,
  },
  app: {
    getVersion: mockGetVersion,
    on: vi.fn((event: string, cb: (...a: unknown[]) => void) => {
      appOnCallbacks[event] ??= [];
      appOnCallbacks[event].push(cb);
    }),
    quit: vi.fn(),
    whenReady: vi.fn(() => {
      whenReadyCallback.push(() => undefined);
      return whenReadyPromise;
    }),
  },
  ipcMain: {
    handle: vi.fn((channel: string, handler: (...a: unknown[]) => unknown) => {
      ipcHandlers[channel] = handler;
    }),
  },
  shell: {
    openExternal: mockOpenExternal,
  },
}));

vi.mock('electron-updater', () => ({
  autoUpdater: {
    checkForUpdates: mockCheckForUpdates,
    checkForUpdatesAndNotify: mockCheckForUpdatesAndNotify,
  },
}));

// ---------------------------------------------------------------------------

describe('main process', () => {
  beforeEach(() => {
    vi.resetModules();
    // Clear captured state
    whenReadyCallback.length = 0;
    for (const key of Object.keys(appOnCallbacks)) {
      delete appOnCallbacks[key];
    }
    for (const key of Object.keys(ipcHandlers)) {
      delete ipcHandlers[key];
    }
    vi.clearAllMocks();
  });

  afterEach(() => {
    delete process.env.VITE_DEV_SERVER_URL;
  });

  async function importMain() {
    await import('../main/main.js');
    await Promise.resolve();
  }

  // ---- IPC handlers -------------------------------------------------------

  describe('IPC: app:version', () => {
    it('returns the app version from electron', async () => {
      await importMain();
      expect(ipcHandlers['app:version']).toBeDefined();
      const version = ipcHandlers['app:version']();
      expect(version).toBe('1.2.3');
      expect(mockGetVersion).toHaveBeenCalled();
    });
  });

  describe('IPC: app:check-updates', () => {
    it('returns updateInfo when updates are available', async () => {
      const fakeUpdateInfo = { version: '2.0.0', releaseDate: '2025-01-01' };
      mockCheckForUpdates.mockResolvedValueOnce({ updateInfo: fakeUpdateInfo });
      await importMain();

      const result = await ipcHandlers['app:check-updates']();
      expect(result).toEqual(fakeUpdateInfo);
    });

    it('returns null when checkForUpdates throws', async () => {
      mockCheckForUpdates.mockRejectedValueOnce(new Error('network error'));
      await importMain();

      const result = await ipcHandlers['app:check-updates']();
      expect(result).toBeNull();
    });

    it('returns undefined when checkForUpdates resolves with null', async () => {
      mockCheckForUpdates.mockResolvedValueOnce(null);
      await importMain();

      const result = await ipcHandlers['app:check-updates']();
      expect(result).toBeUndefined();
    });
  });

  // ---- createWindow (via whenReady) ---------------------------------------

  describe('createWindow', () => {
    it('creates a BrowserWindow with correct security options', async () => {
      await importMain();
      // Fire whenReady callback
      for (const cb of whenReadyCallback) {
        cb();
      }

      expect(MockBrowserWindow).toHaveBeenCalledOnce();
      const opts = MockBrowserWindow.mock.calls[0][0];

      expect(opts.width).toBe(1400);
      expect(opts.height).toBe(900);
      expect(opts.minWidth).toBe(800);
      expect(opts.minHeight).toBe(600);
      expect(opts.titleBarStyle).toBe('hiddenInset');
      expect(opts.webPreferences.contextIsolation).toBeTruthy();
      expect(opts.webPreferences.nodeIntegration).toBeFalsy();
      expect(opts.webPreferences.sandbox).toBeTruthy();
    });

    it('loads the dev server URL when VITE_DEV_SERVER_URL is set', async () => {
      process.env.VITE_DEV_SERVER_URL = 'http://localhost:5173';
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      expect(mockLoadURL).toHaveBeenCalledWith('http://localhost:5173');
      expect(mockOpenDevTools).toHaveBeenCalled();
      expect(mockLoadFile).not.toHaveBeenCalled();
    });

    it('loads the renderer index.html in production mode', async () => {
      delete process.env.VITE_DEV_SERVER_URL;
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      expect(mockLoadFile).toHaveBeenCalledOnce();
      const filePath: string = mockLoadFile.mock.calls[0][0];
      expect(filePath).toContain('renderer');
      expect(filePath).toContain('index.html');
      expect(mockLoadURL).not.toHaveBeenCalled();
      expect(mockOpenDevTools).not.toHaveBeenCalled();
    });

    it('sets mainWindow to null when the window is closed', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      // MockOn is called with ('closed', handler)
      const closedCall = mockOn.mock.calls.find((c: unknown[]) => c[0] === 'closed');
      expect(closedCall).toBeDefined();

      // Invoking the closed handler should not throw
      const closedHandler = closedCall![1] as () => void;
      expect(() => closedHandler()).not.toThrow();
    });
  });

  // ---- createMenu (via whenReady) -----------------------------------------

  describe('createMenu', () => {
    it('builds and sets the application menu', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      expect(mockBuildFromTemplate).toHaveBeenCalledOnce();
      expect(mockSetApplicationMenu).toHaveBeenCalledOnce();
    });

    it('menu template contains expected top-level labels', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      const template: { label: string }[] = mockBuildFromTemplate.mock.calls[0][0];
      const labels = template.map((item) => item.label);
      expect(labels).toContain('TraceRTM');
      expect(labels).toContain('File');
      expect(labels).toContain('Edit');
      expect(labels).toContain('View');
      expect(labels).toContain('Window');
      expect(labels).toContain('Help');
    });

    it('File > New Project sends menu:new-project via IPC', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      const template: {
        label: string;
        submenu?: Array<{ label?: string; click?: () => void }>;
      }[] = mockBuildFromTemplate.mock.calls[0][0];
      const fileMenu = template.find((m) => m.label === 'File')!;
      const newProject = fileMenu.submenu!.find((item) => item.label === 'New Project')!;

      newProject.click!();
      expect(mockWebContentsSend).toHaveBeenCalledWith('menu:new-project');
    });

    it('File > Open Project sends menu:open-project via IPC', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      const template: {
        label: string;
        submenu?: Array<{ label?: string; click?: () => void }>;
      }[] = mockBuildFromTemplate.mock.calls[0][0];
      const fileMenu = template.find((m) => m.label === 'File')!;
      const openProject = fileMenu.submenu!.find((item) => item.label === 'Open Project')!;

      openProject.click!();
      expect(mockWebContentsSend).toHaveBeenCalledWith('menu:open-project');
    });

    it('File > Import sends menu:import via IPC', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      const template: {
        label: string;
        submenu?: Array<{ label?: string; click?: () => void }>;
      }[] = mockBuildFromTemplate.mock.calls[0][0];
      const fileMenu = template.find((m) => m.label === 'File')!;
      const importItem = fileMenu.submenu!.find((item) => item.label === 'Import...')!;

      importItem.click!();
      expect(mockWebContentsSend).toHaveBeenCalledWith('menu:import');
    });

    it('File > Export sends menu:export via IPC', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      const template: {
        label: string;
        submenu?: Array<{ label?: string; click?: () => void }>;
      }[] = mockBuildFromTemplate.mock.calls[0][0];
      const fileMenu = template.find((m) => m.label === 'File')!;
      const exportItem = fileMenu.submenu!.find((item) => item.label === 'Export...')!;

      exportItem.click!();
      expect(mockWebContentsSend).toHaveBeenCalledWith('menu:export');
    });

    it('File menu click handlers are safe when mainWindow is null', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      // Simulate closing the window so mainWindow becomes null
      const closedCall = mockOn.mock.calls.find((c: unknown[]) => c[0] === 'closed');
      const closedHandler = closedCall![1] as () => void;
      closedHandler();

      const template: {
        label: string;
        submenu?: Array<{ label?: string; click?: () => void }>;
      }[] = mockBuildFromTemplate.mock.calls[0][0];
      const fileMenu = template.find((m) => m.label === 'File')!;
      const clickableItems = fileMenu.submenu!.filter((item) => typeof item.click === 'function');

      // All click handlers should not throw when mainWindow is null
      mockWebContentsSend.mockClear();
      for (const item of clickableItems) {
        expect(() => item.click!()).not.toThrow();
      }
      // WebContents.send should NOT have been called since mainWindow is null
      expect(mockWebContentsSend).not.toHaveBeenCalled();
    });

    it('Help > Documentation opens external docs URL', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      const template: {
        label: string;
        submenu?: Array<{ label?: string; click?: () => void }>;
      }[] = mockBuildFromTemplate.mock.calls[0][0];
      const helpMenu = template.find((m) => m.label === 'Help')!;
      const docsItem = helpMenu.submenu!.find((item) => item.label === 'Documentation')!;

      docsItem.click!();
      expect(mockOpenExternal).toHaveBeenCalledWith('https://tracertm.dev/docs');
    });

    it('Help > Report Issue opens external issues URL', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      const template: {
        label: string;
        submenu?: Array<{ label?: string; click?: () => void }>;
      }[] = mockBuildFromTemplate.mock.calls[0][0];
      const helpMenu = template.find((m) => m.label === 'Help')!;
      const reportItem = helpMenu.submenu!.find((item) => item.label === 'Report Issue')!;

      reportItem.click!();
      expect(mockOpenExternal).toHaveBeenCalledWith('https://github.com/tracertm/tracertm/issues');
    });
  });

  // ---- Auto-updater -------------------------------------------------------

  describe('autoUpdater', () => {
    it('calls checkForUpdatesAndNotify on whenReady', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }

      expect(mockCheckForUpdatesAndNotify).toHaveBeenCalledOnce();
    });
  });

  // ---- App lifecycle events -----------------------------------------------

  describe('app lifecycle', () => {
    it('quits the app on window-all-closed when not on macOS', async () => {
      const { app: mockApp } = await import('electron');
      const originalPlatform = process.platform;
      Object.defineProperty(process, 'platform', { value: 'win32' });

      await importMain();

      const allClosedCbs = appOnCallbacks['window-all-closed'];
      expect(allClosedCbs).toBeDefined();
      expect(allClosedCbs.length).toBeGreaterThan(0);
      allClosedCbs[0]();

      expect(mockApp.quit).toHaveBeenCalled();

      Object.defineProperty(process, 'platform', { value: originalPlatform });
    });

    it('does not quit on window-all-closed on macOS', async () => {
      const { app: mockApp } = await import('electron');
      const originalPlatform = process.platform;
      Object.defineProperty(process, 'platform', { value: 'darwin' });

      await importMain();

      const allClosedCbs = appOnCallbacks['window-all-closed'];
      expect(allClosedCbs).toBeDefined();
      allClosedCbs[0]();

      expect(mockApp.quit).not.toHaveBeenCalled();

      Object.defineProperty(process, 'platform', { value: originalPlatform });
    });

    it('does not re-create window on activate when mainWindow still exists', async () => {
      await importMain();
      for (const cb of whenReadyCallback) {
        cb();
      }
      expect(MockBrowserWindow).toHaveBeenCalledOnce();

      // Do NOT close the window; mainWindow is still set
      const activateCbs = appOnCallbacks['activate'];
      expect(activateCbs).toBeDefined();
      activateCbs[0]();

      // Should not create a second window
      expect(MockBrowserWindow).toHaveBeenCalledOnce();
    });

    it('re-creates window on activate when mainWindow is null', async () => {
      await importMain();
      // Fire whenReady to create the window once
      for (const cb of whenReadyCallback) {
        cb();
      }
      expect(MockBrowserWindow).toHaveBeenCalledOnce();

      // Simulate closing the window
      const closedCall = mockOn.mock.calls.find((c: unknown[]) => c[0] === 'closed');
      const closedHandler = closedCall![1] as () => void;
      closedHandler(); // Sets mainWindow = null

      // Now fire activate
      const activateCbs = appOnCallbacks['activate'];
      expect(activateCbs).toBeDefined();
      activateCbs[0]();

      expect(MockBrowserWindow).toHaveBeenCalledTimes(2);
    });
  });
});
