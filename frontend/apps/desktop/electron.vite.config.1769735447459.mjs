// Electron.vite.config.ts
import react from '@vitejs/plugin-react';
import { defineConfig, externalizeDepsPlugin } from 'electron-vite';
import path from 'node:path';

const __electron_vite_injected_dirname =
  '/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/desktop';
const electron_vite_config_default = defineConfig({
  main: {
    build: {
      outDir: 'dist/main',
    },
    plugins: [externalizeDepsPlugin()],
  },
  preload: {
    build: {
      outDir: 'dist/preload',
    },
    plugins: [externalizeDepsPlugin()],
  },
  renderer: {
    build: {
      outDir: path.resolve(__electron_vite_injected_dirname, 'dist/renderer'),
      rollupOptions: {
        input: path.resolve(__electron_vite_injected_dirname, '../web/index.html'),
      },
    },
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__electron_vite_injected_dirname, '../web/src'),
      },
    },
    root: '../web',
  },
});
export { electron_vite_config_default as default };
