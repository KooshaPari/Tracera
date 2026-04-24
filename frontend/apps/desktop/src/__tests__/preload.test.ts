import { beforeEach, describe, expect, it, vi } from 'vitest';

// ---- Electron mock wiring ------------------------------------------------

const mockInvoke = vi.fn();
const mockOnListener = vi.fn();
const mockExposeInMainWorld = vi.fn();

vi.mock('electron', () => ({
  contextBridge: {
    exposeInMainWorld: mockExposeInMainWorld,
  },
  ipcRenderer: {
    invoke: mockInvoke,
    on: mockOnListener,
  },
}));

// ---------------------------------------------------------------------------

/**
 * Preload.ts calls contextBridge.exposeInMainWorld at module scope.
 * We capture the exposed API object from the mock and exercise every method.
 */
function getExposedAPI(): Record<string, unknown> {
  const call = mockExposeInMainWorld.mock.calls.find((c: unknown[]) => c[0] === 'electronAPI');
  if (!call) {
    throw new Error('electronAPI was not exposed via contextBridge');
  }
  return call[1] as Record<string, unknown>;
}

describe('preload script', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
  });

  async function importPreload() {
    await import('../preload/preload.js');
  }

  it('exposes electronAPI on the main world', async () => {
    await importPreload();
    expect(mockExposeInMainWorld).toHaveBeenCalledOnce();
    expect(mockExposeInMainWorld).toHaveBeenCalledWith('electronAPI', expect.any(Object));
  });

  describe('app info APIs', () => {
    it('getVersion invokes app:version channel', async () => {
      mockInvoke.mockResolvedValueOnce('1.0.0');
      await importPreload();
      const api = getExposedAPI();

      const version = await (api.getVersion as () => Promise<string>)();
      expect(mockInvoke).toHaveBeenCalledWith('app:version');
      expect(version).toBe('1.0.0');
    });

    it('checkUpdates invokes app:check-updates channel', async () => {
      const updateData = { version: '2.0.0' };
      mockInvoke.mockResolvedValueOnce(updateData);
      await importPreload();
      const api = getExposedAPI();

      const result = await (api.checkUpdates as () => Promise<unknown>)();
      expect(mockInvoke).toHaveBeenCalledWith('app:check-updates');
      expect(result).toEqual(updateData);
    });
  });

  describe('file operation APIs', () => {
    it('openFile invokes dialog:openFile channel', async () => {
      mockInvoke.mockResolvedValueOnce('/path/to/file.json');
      await importPreload();
      const api = getExposedAPI();

      const result = await (api.openFile as () => Promise<string | null>)();
      expect(mockInvoke).toHaveBeenCalledWith('dialog:openFile');
      expect(result).toBe('/path/to/file.json');
    });

    it('saveFile invokes dialog:saveFile channel with data', async () => {
      mockInvoke.mockResolvedValueOnce(true);
      await importPreload();
      const api = getExposedAPI();

      const result = await (api.saveFile as (data: string) => Promise<boolean>)('{"key":"value"}');
      expect(mockInvoke).toHaveBeenCalledWith('dialog:saveFile', '{"key":"value"}');
      expect(result).toBeTruthy();
    });
  });

  describe('menu event listeners', () => {
    it('onNewProject registers listener on menu:new-project', async () => {
      await importPreload();
      const api = getExposedAPI();
      const callback = vi.fn();

      (api.onNewProject as (cb: () => void) => void)(callback);
      expect(mockOnListener).toHaveBeenCalledWith('menu:new-project', callback);
    });

    it('onOpenProject registers listener on menu:open-project', async () => {
      await importPreload();
      const api = getExposedAPI();
      const callback = vi.fn();

      (api.onOpenProject as (cb: () => void) => void)(callback);
      expect(mockOnListener).toHaveBeenCalledWith('menu:open-project', callback);
    });

    it('onImport registers listener on menu:import', async () => {
      await importPreload();
      const api = getExposedAPI();
      const callback = vi.fn();

      (api.onImport as (cb: () => void) => void)(callback);
      expect(mockOnListener).toHaveBeenCalledWith('menu:import', callback);
    });

    it('onExport registers listener on menu:export', async () => {
      await importPreload();
      const api = getExposedAPI();
      const callback = vi.fn();

      (api.onExport as (cb: () => void) => void)(callback);
      expect(mockOnListener).toHaveBeenCalledWith('menu:export', callback);
    });
  });

  describe('platform info', () => {
    it('exposes the current platform', async () => {
      await importPreload();
      const api = getExposedAPI();
      expect(api.platform).toBe(process.platform);
    });
  });

  describe('API shape completeness', () => {
    it('exposes exactly the expected keys', async () => {
      await importPreload();
      const api = getExposedAPI();
      const keys = Object.keys(api).toSorted();
      expect(keys).toEqual([
        'checkUpdates',
        'getVersion',
        'onExport',
        'onImport',
        'onNewProject',
        'onOpenProject',
        'openFile',
        'platform',
        'saveFile',
      ]);
    });
  });
});
