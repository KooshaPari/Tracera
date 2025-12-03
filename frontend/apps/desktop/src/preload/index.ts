import { contextBridge, ipcRenderer } from 'electron'

// Expose safe APIs to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getVersion: () => ipcRenderer.invoke('app:version'),
  checkUpdates: () => ipcRenderer.invoke('app:check-updates'),

  // File operations
  openFile: () => ipcRenderer.invoke('dialog:openFile'),
  saveFile: (data: string) => ipcRenderer.invoke('dialog:saveFile', data),

  // Menu events
  onNewProject: (callback: () => void) => ipcRenderer.on('menu:new-project', callback),
  onOpenProject: (callback: () => void) => ipcRenderer.on('menu:open-project', callback),
  onImport: (callback: () => void) => ipcRenderer.on('menu:import', callback),
  onExport: (callback: () => void) => ipcRenderer.on('menu:export', callback),

  // Platform info
  platform: process.platform,
})

// TypeScript types for the exposed API
declare global {
  interface Window {
    electronAPI: {
      getVersion: () => Promise<string>
      checkUpdates: () => Promise<unknown>
      openFile: () => Promise<string | null>
      saveFile: (data: string) => Promise<boolean>
      onNewProject: (callback: () => void) => void
      onOpenProject: (callback: () => void) => void
      onImport: (callback: () => void) => void
      onExport: (callback: () => void) => void
      platform: NodeJS.Platform
    }
  }
}
