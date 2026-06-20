import { contextBridge, ipcRenderer } from 'electron';

// Expose safe APIs to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getVersion: (): Promise<string> => ipcRenderer.invoke('app:version'),
  checkUpdates: (): Promise<unknown> => ipcRenderer.invoke('app:check-updates'),

  // File operations
  openFile: (): Promise<string | null> => ipcRenderer.invoke('dialog:openFile'),
  saveFile: (data: string): Promise<boolean> => ipcRenderer.invoke('dialog:saveFile', data),

  // Menu events
  onNewProject: (callback: () => void): void => {
    ipcRenderer.on('menu:new-project', callback);
  },
  onOpenProject: (callback: () => void): void => {
    ipcRenderer.on('menu:open-project', callback);
  },
  onImport: (callback: () => void): void => {
    ipcRenderer.on('menu:import', callback);
  },
  onExport: (callback: () => void): void => {
    ipcRenderer.on('menu:export', callback);
  },

  // Platform info
  platform: process.platform,
});

// TypeScript types for the exposed API
declare global {
  interface Window {
    electronAPI: {
      getVersion: () => Promise<string>;
      checkUpdates: () => Promise<unknown>;
      openFile: () => Promise<string | null>;
      saveFile: (data: string) => Promise<boolean>;
      onNewProject: (callback: () => void) => void;
      onOpenProject: (callback: () => void) => void;
      onImport: (callback: () => void) => void;
      onExport: (callback: () => void) => void;
      platform: NodeJS.Platform;
    };
  }
}
