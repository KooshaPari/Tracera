// electron.vite.config.ts
import react from "@vitejs/plugin-react";
import { defineConfig, externalizeDepsPlugin } from "electron-vite";
import path from "path";

var __electron_vite_injected_dirname =
	"/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/desktop";
var electron_vite_config_default = defineConfig({
	main: {
		plugins: [externalizeDepsPlugin()],
		build: {
			outDir: "dist/main",
		},
	},
	preload: {
		plugins: [externalizeDepsPlugin()],
		build: {
			outDir: "dist/preload",
		},
	},
	renderer: {
		plugins: [react()],
		root: "../web",
		resolve: {
			alias: {
				"@": path.resolve(__electron_vite_injected_dirname, "../web/src"),
			},
		},
		build: {
			outDir: path.resolve(__electron_vite_injected_dirname, "dist/renderer"),
			rollupOptions: {
				input: path.resolve(
					__electron_vite_injected_dirname,
					"../web/index.html",
				),
			},
		},
	},
});
export { electron_vite_config_default as default };
