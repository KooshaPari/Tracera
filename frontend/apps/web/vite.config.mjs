import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/postcss";
import autoprefixer from "autoprefixer";
import path from "path";
import { fileURLToPath } from "url";
import { defineConfig, esmExternalRequirePlugin } from "vite";
import { ViteImageOptimizer } from "vite-plugin-image-optimizer";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Conditionally load React Compiler plugin (available for production builds)
const ReactCompilerConfig = {};

export default defineConfig({
	plugins: [
		// Handle React CJS → ESM interop for TanStack Router's ESM imports
		esmExternalRequirePlugin({
			external: [
				"react",
				"react-dom",
				"react/jsx-runtime",
				"react/jsx-dev-runtime",
			],
		}),
		// React with Babel - enables React Compiler for automatic memoization
		// React Compiler provides 30-60% fewer re-renders by auto-memoizing components
		react({
			babel: {
				plugins: [["babel-plugin-react-compiler", ReactCompilerConfig]],
			},
		}),
		// Image optimization - 50-80% smaller images in production builds
		ViteImageOptimizer({
			// Exclude SVG files due to css-what module compatibility issue with svgo
			exclude: /\.svg$/,
			png: {
				quality: 80,
			},
			jpeg: {
				quality: 80,
			},
			jpg: {
				quality: 80,
			},
			webp: {
				lossless: true,
			},
			avif: {
				lossless: true,
			},
		}),
	],
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./src"),
		},
		dedupe: [
			"react",
			"react-dom",
			"react/jsx-runtime",
			"react/jsx-dev-runtime",
		],
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
		// Exclude files that shouldn't be pre-bundled
		// These are either plugins, heavy libraries meant to be lazy-loaded, or test utilities
		exclude: [
			"playwright-report",
			// Heavy libraries - let them be code-split by Rollup
			"elkjs", // 200-300KB layout algorithm
			"monaco-editor", // 1-2MB code editor
			"@monaco-editor/react", // 1-2MB wrapper
			"swagger-ui-react", // 300KB+ API docs
			"redoc", // 300KB+ API docs
			"html2canvas", // 200KB+ canvas library
			"recharts", // Chart library with large bundle
			"@xyflow/react", // Heavy graph visualization
			"cytoscape", // Graph library
		],
		// Explicitly include core dependencies that should be pre-bundled
		// These are needed early and are not too large
		include: [
			"react",
			"react-dom",
			"react/jsx-runtime",
			"react/jsx-dev-runtime",
			"@tanstack/react-router",
			"@tanstack/react-query",
			"zustand",
			"sonner",
			"@radix-ui/react-dialog",
			"@radix-ui/react-dropdown-menu",
			"@radix-ui/react-select",
			"@radix-ui/react-tabs",
			"@radix-ui/react-toast",
			"@radix-ui/react-tooltip",
			"lucide-react",
			"framer-motion",
		],
	},
	build: {
		outDir: "dist",
		// Use 'hidden' sourcemaps in production for better build time
		// Maps are generated but not referenced in bundle
		// Set to true only if you need maps embedded (slows build by 2-3s)
		sourcemap: process.env.NODE_ENV === "development" ? true : "hidden",
		chunkSizeWarningLimit: 2500, // Lazy-loaded vendor chunks (graph, api-docs) are expected to be large
		// Minify JS and CSS - can be 'terser', 'esbuild', or false
		minify: "esbuild",
		rollupOptions: {
			onwarn(warning, warn) {
				if (warning.code === "SOURCEMAP_ERROR") return;
				warn(warning);
			},
			output: {
				// Optimize chunk file names
				entryFileNames: "assets/[name]-[hash].js",
				chunkFileNames: "assets/[name]-[hash].js",
				assetFileNames: "assets/[name]-[hash][extname]",
				manualChunks(id) {
					if (id.includes("node_modules")) {
						// Core React - should always be loaded first
						if (id.includes("/react-dom/") || id.includes("/react/")) {
							return "vendor-react";
						}
						// Router & state - needed early for navigation
						if (
							id.includes("@tanstack/react-router") ||
							id.includes("@tanstack/react-query") ||
							id.includes("/zustand/")
						) {
							return "vendor-router";
						}
						// Graph visualization (very heavy: ~400KB+)
						// elkjs alone is 200-300KB - make it lazy
						if (id.includes("/elkjs/")) {
							return "vendor-graph-elk";
						}
						// XyFlow and cytoscape are also heavy
						if (id.includes("@xyflow/") || id.includes("/cytoscape")) {
							return "vendor-graph-core";
						}
						// Charts (heavy: ~150KB)
						if (id.includes("/recharts/") || id.includes("/d3-")) {
							return "vendor-charts";
						}
						// Monaco editor (very heavy: 1-2MB!)
						// Should only load when user navigates to code view
						if (id.includes("monaco")) {
							return "vendor-monaco";
						}
						// API documentation (heavy: ~300KB)
						// Swagger UI and Redoc are large
						if (id.includes("swagger-ui") || id.includes("/redoc/")) {
							return "vendor-api-docs";
						}
						// HTML2Canvas and canvas-related (heavy)
						if (id.includes("html2canvas")) {
							return "vendor-canvas";
						}
						// Animation
						if (id.includes("framer-motion")) {
							return "vendor-motion";
						}
						// UI Framework
						if (id.includes("@radix-ui/")) {
							return "vendor-radix";
						}
						// Icons
						if (id.includes("lucide-react")) {
							return "vendor-icons";
						}
						// Forms & validation
						if (
							id.includes("react-hook-form") ||
							id.includes("@hookform/") ||
							id.includes("/zod/")
						) {
							return "vendor-forms";
						}
						// Tables & virtualization
						if (
							id.includes("@tanstack/react-table") ||
							id.includes("@tanstack/react-virtual")
						) {
							return "vendor-table";
						}
						// Drag & drop
						if (id.includes("@dnd-kit/")) {
							return "vendor-dnd";
						}
						// Notifications
						if (id.includes("/sonner/")) {
							return "vendor-notifications";
						}
						// Miscellaneous utilities
						if (
							id.includes("/date-fns/") ||
							id.includes("/dompurify/") ||
							id.includes("tailwind-merge") ||
							id.includes("class-variance-authority")
						) {
							return "vendor-utils";
						}
					}
				},
			},
		},
	},
	css: {
		postcss: {
			plugins: [tailwindcss({}), autoprefixer({})],
		},
	},
});
