// Temporarily disabled due to ESM regex parsing issue in @tanstack/router-plugin
// import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import commonjs from "@rollup/plugin-commonjs";
import path from "path";
import { fileURLToPath } from "url";
import { defineConfig } from "vite";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
	plugins: [commonjs(), react()], // TanStackRouterVite() temporarily disabled
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./src"),
		},
	},
	server: {
		port: 5173,
		proxy: {
			"/api": {
				target: "http://localhost:8080",
				changeOrigin: true,
			},
		},
	},
	optimizeDeps: {
		exclude: ["playwright-report"],
	},
	build: {
		outDir: "dist",
		sourcemap: true,
	},
});
