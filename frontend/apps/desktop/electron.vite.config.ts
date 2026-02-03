import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, externalizeDepsPlugin } from "electron-vite";
import path from "node:path";

export default defineConfig({
	main: {
		build: {
			outDir: "dist/main",
		},
		plugins: [externalizeDepsPlugin()],
	},
	preload: {
		build: {
			outDir: "dist/preload",
		},
		plugins: [externalizeDepsPlugin()],
	},
	renderer: {
		build: {
			outDir: path.resolve(__dirname, "dist/renderer"),
			cssMinify: "lightningcss",
			rollupOptions: {
				input: path.resolve(__dirname, "../web/index.html"),
			},
		},
		css: {
			transformer: "lightningcss",
			lightningcss: {},
		},
		plugins: [tailwindcss(), react()],
		resolve: {
			alias: {
				"@": path.resolve(__dirname, "../web/src"),
			},
		},
		root: "../web",
	},
});
