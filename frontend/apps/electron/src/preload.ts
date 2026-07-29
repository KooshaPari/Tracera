import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("traceraDesktop", {
  gatewayUrl: (): Promise<string> => ipcRenderer.invoke("tracera:gateway"),
});
