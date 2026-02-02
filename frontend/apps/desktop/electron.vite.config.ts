import tailwindcss from "@tailwindcss/vite";
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
		plugins: [tailwindcss(), react()],
		root: "../web",
		resolve: {
			alias: {
				"@": path.resolve(__dirname, "../web/src"),
			},
		},
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
	},
});
