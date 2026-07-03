/**
 * Tracera Desktop — preload script.
 *
 * Bridges the renderer (web UI) and the main process via a minimal,
 * explicit API surface. Context-isolation is on, sandbox is on, so the
 * renderer only sees what we explicitly expose here.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('tracera', {
  /**
   * Returns the URL the desktop shell is currently loading.
   * Useful for the renderer to show "Connected to: <url>" in a corner.
   */
  getTargetUrl: () => ipcRenderer.invoke('tracera:target-url'),

  /**
   * Returns the desktop shell version (matches package.json).
   */
  getVersion: () => ipcRenderer.invoke('tracera:version'),
});