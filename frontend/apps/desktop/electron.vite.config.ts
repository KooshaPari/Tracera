import react from "@vitejs/plugin-react";
import { defineConfig, externalizeDepsPlugin } from "electron-vite";
import path from "path";

export default defineConfig({
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
				"@": path.resolve(__dirname, "../web/src"),
			},
		},
		build: {
			outDir: path.resolve(__dirname, "dist/renderer"),
			rollupOptions: {
				input: path.resolve(__dirname, "../web/index.html"),
			},
		},
	},
});
