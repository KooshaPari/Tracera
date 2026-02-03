import path from "node:path";
import { fileURLToPath } from "node:url";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { checker } from "vite-plugin-checker";
import { ViteImageOptimizer } from "vite-plugin-image-optimizer";
import { sentryVitePlugin } from "@sentry/vite-plugin";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Conditionally load React Compiler plugin (available for production builds)
const ReactCompilerConfig = {};

/** @type {Array<[(id: string) => boolean, string]>} */
const VENDOR_CHUNK_RULES = [
	[
		(id) => id.includes("/react-dom/") || id.includes("/react/"),
		"vendor-react",
	],
	[
		(id) =>
			id.includes("@tanstack/react-router") ||
			id.includes("@tanstack/react-query") ||
			id.includes("/zustand/"),
		"vendor-router",
	],
	[(id) => id.includes("/elkjs/"), "vendor-graph-elk"],
	[
		(id) => id.includes("@xyflow/") || id.includes("/cytoscape"),
		"vendor-graph-core",
	],
	[(id) => id.includes("/recharts/") || id.includes("/d3-"), "vendor-charts"],
	[(id) => id.includes("monaco"), "vendor-monaco"],
	[
		(id) => id.includes("swagger-ui") || id.includes("/redoc/"),
		"vendor-api-docs",
	],
	[(id) => id.includes("html2canvas"), "vendor-canvas"],
	[(id) => id.includes("framer-motion"), "vendor-motion"],
	[(id) => id.includes("@radix-ui/"), "vendor-radix"],
	[(id) => id.includes("lucide-react"), "vendor-icons"],
	[
		(id) =>
			id.includes("react-hook-form") ||
			id.includes("@hookform/") ||
			id.includes("/zod/"),
		"vendor-forms",
	],
	[
		(id) =>
			id.includes("@tanstack/react-table") ||
			id.includes("@tanstack/react-virtual"),
		"vendor-table",
	],
	[(id) => id.includes("@dnd-kit/"), "vendor-dnd"],
	[(id) => id.includes("/sonner/"), "vendor-notifications"],
	[
		(id) =>
			id.includes("/date-fns/") ||
			id.includes("/dompurify/") ||
			id.includes("tailwind-merge") ||
			id.includes("class-variance-authority"),
		"vendor-utils",
	],
];

function getManualChunkName(id) {
	if (!id.includes("node_modules")) return;
	for (const [test, name] of VENDOR_CHUNK_RULES) {
		if (test(id)) return name;
	}
	return;
}

export default defineConfig({
	build: {
		outDir: "dist",
		// Use 'hidden' sourcemaps in production for better build time
		// Maps are generated but not referenced in bundle
		// Set to true only if you need maps embedded (slows build by 2-3s)
		sourcemap: process.env.NODE_ENV === "development" ? true : "hidden",
		chunkSizeWarningLimit: 2500, // Lazy-loaded vendor chunks (graph, api-docs) are expected to be large
		// Minify JS and CSS - can be 'terser', 'esbuild', or false
		minify: "esbuild",
		// Lightning CSS for faster CSS minification (Vite Performance Guide)
		cssMinify: "lightningcss",
		// Target modern browsers for better minification and tree-shaking
		target: "esnext",
		// Disable CSS code splitting for better caching
		cssCodeSplit: true,
		// Enable build optimizations
		reportCompressedSize: false, // Disable gzip size reporting to speed up build
		// Optimize chunk size
		assetsInlineLimit: 4096, // Inline assets smaller than 4KB
		// Drop logger.debug and logger.info calls in production for security
		// Only keep logger.warn and logger.error for production monitoring
		esbuild: {
			drop: process.env.NODE_ENV === "production" ? ["debugger"] : [],
			pure:
				process.env.NODE_ENV === "production"
					? ["logger.debug", "logger.info", "logger.table"]
					: [],
		},
		rollupOptions: {
			// Optimize tree-shaking
			treeshake: {
				moduleSideEffects: "no-external",
				propertyReadSideEffects: false,
				tryCatchDeoptimization: false,
			},
			onwarn(warning, warn) {
				if (warning.code === "SOURCEMAP_ERROR") return;
				warn(warning);
			},
			output: {
				// Optimize chunk file names
				entryFileNames: "assets/[name]-[hash].js",
				chunkFileNames: "assets/[name]-[hash].js",
				assetFileNames: "assets/[name]-[hash][extname]",
				// Optimize output options for better compression
				compact: true,
				// Improve module format
				format: "es",
				manualChunks(id) {
					return getManualChunkName(id);
				},
			},
		},
	},
	css: {
		// Lightning CSS for transform (nesting, autoprefix) and minify; replaces PostCSS (Vite Performance Guide)
		transformer: "lightningcss",
		lightningcss: {
			// Targets derived from build.target "esnext" by default; override here if needed
		},
	},
	optimizeDeps: {
		// Exclude files that shouldn't be pre-bundled
		// These are either plugins, heavy libraries meant to be lazy-loaded, or test utilities
		exclude: [
			"playwright-report",
			// Heavy libraries - let them be code-split by Rollup
			// Note: elkjs moved to include due to CJS/ESM interop issues
			"monaco-editor", // 1-2MB code editor
			"@monaco-editor/react", // 1-2MB wrapper
			"swagger-ui-react", // 300KB+ API docs
			"redoc", // 300KB+ API docs
			"html2canvas", // 200KB+ canvas library
			"@xyflow/react", // Heavy graph visualization
			"cytoscape", // Graph library
		],
		// Exclude test/report directories from dependency scanning
		entries: [
			"index.html",
			"!playwright-report/**",
			"!coverage/**",
			"!.trace/**",
		],
		// Explicitly include core dependencies that should be pre-bundled
		// These are needed early and are not too large
		include: [
			"react",
			"react-dom",
			"react/jsx-runtime",
			"react/jsx-dev-runtime",
			// Pre-bundle use-sync-external-store to convert CJS to ESM
			// This fixes "does not provide an export named 'default'" error
			"use-sync-external-store/shim",
			"use-sync-external-store/shim/with-selector",
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
			"eventemitter3", // Required for recharts compatibility
			"recharts", // Chart library needs pre-bundling for decimal.js-light compatibility
			"recharts-scale", // Chart library scale utilities
			"decimal.js-light", // Decimal library for recharts
			// Pre-bundle elkjs to handle CJS/ESM interop
			"elkjs/lib/elk.bundled.js",
		],
		// Vite 8 uses Rolldown for deps optimization (rolldownOptions accepts input options; format is not valid here)
		rolldownOptions: {},
	},
	plugins: [
		// Tailwind v4 via Vite plugin (uses Lightning CSS in production; no PostCSS)
		tailwindcss(),
		// Run oxlint (type-aware) in worker thread; show errors in overlay and terminal
		checker({
			oxlint: {
				lintCommand: "oxlint --type-aware",
				cwd: ".",
				dev: { logLevel: ["error", "warning"] },
			},
			overlay: true,
			terminal: true,
		}),
		// eslint-disable-next-line @typescript-eslint/no-deprecated -- Router plugin API; migrate when TanStack provides replacement
		TanStackRouterVite({
			routesDirectory: "./src/routes",
			generatedRouteTree: "./src/routeTree.gen.ts",
			quoteStyle: "single",
		}),
		// React with optional Babel - enables React Compiler for automatic memoization when available
		// React Compiler provides 30-60% fewer re-renders by auto-memoizing components
		react({
			// Enable Fast Refresh for instant updates in development
			fastRefresh: true,
			// Optimize JSX runtime imports
			jsxRuntime: "automatic",
			// Configure Babel for React Compiler (production only for stability)
			babel:
				process.env.NODE_ENV === "production" &&
				process.env.ENABLE_REACT_COMPILER === "true"
					? {
							plugins: [["babel-plugin-react-compiler", ReactCompilerConfig]],
						}
					: undefined,
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
		// Sentry plugin for source maps and release tracking (production only)
		...(process.env.NODE_ENV === "production" &&
		process.env.VITE_SENTRY_AUTH_TOKEN != null &&
		process.env.VITE_SENTRY_AUTH_TOKEN !== ""
			? [
					sentryVitePlugin({
						org: process.env.VITE_SENTRY_ORG,
						project: process.env.VITE_SENTRY_PROJECT,
						authToken: process.env.VITE_SENTRY_AUTH_TOKEN,
						sourcemaps: {
							assets: "./dist/assets/**",
						},
						telemetry: false,
						// Automatically inject release information
						release: {
							name: process.env.VITE_APP_VERSION ?? "unknown",
							dist: process.env.VITE_BUILD_ID ?? "local",
						},
					}),
				]
			: []),
	],
	resolve: {
		// Fewer extensions = fewer filesystem checks (Vite Performance Guide)
		extensions: [".mjs", ".js", ".mts", ".ts", ".jsx", ".tsx", ".json"],
		alias: [
			{ find: "@", replacement: path.resolve(__dirname, "./src") },
			{
				find: "@atoms/types",
				replacement: path.resolve(
					__dirname,
					"../../packages/types/src/index.ts",
				),
			},
			{
				find: "@tracertm/types",
				replacement: path.resolve(
					__dirname,
					"../../packages/types/src/index.ts",
				),
			},
			{
				find: "@tracertm/ui",
				replacement: path.resolve(__dirname, "../../packages/ui/src/index.ts"),
			},
			{
				find: /^react-is$/,
				replacement: path.resolve(__dirname, "./src/lib/react-is-shim.ts"),
			},
			{
				find: /^prop-types$/,
				replacement: path.resolve(__dirname, "./src/lib/prop-types-shim.ts"),
			},
			// Internal: shim imports the real package via this alias to avoid circular dependency
			{
				find: "use-sync-external-store-with-selector-real",
				replacement: path.resolve(
					__dirname,
					"../../node_modules/use-sync-external-store/shim/with-selector.js",
				),
			},
			// CJS use-sync-external-store/shim/with-selector has no ESM default; zustand needs default import
			{
				find: "use-sync-external-store/shim/with-selector",
				replacement: path.resolve(
					__dirname,
					"./src/lib/use-sync-external-store-with-selector-shim.ts",
				),
			},
			{
				find: "use-sync-external-store/shim/with-selector.js",
				replacement: path.resolve(
					__dirname,
					"./src/lib/use-sync-external-store-with-selector-shim.ts",
				),
			},
			// Keep lodash/fp/* as lodash (for swagger-ui-react); must be before general lodash -> lodash-es
			{ find: /^lodash\/fp\/(.*)$/, replacement: "lodash/fp/$1" },
			{ find: /^lodash\/get$/, replacement: "lodash-es/get" },
			{ find: /^lodash\/isNil$/, replacement: "lodash-es/isNil" },
			{ find: /^lodash\/isString$/, replacement: "lodash-es/isString" },
			{ find: /^lodash\/isObject$/, replacement: "lodash-es/isObject" },
			{ find: /^lodash\/max$/, replacement: "lodash-es/max" },
			{ find: /^lodash\/min$/, replacement: "lodash-es/min" },
			{ find: /^lodash\/(.*)$/, replacement: "lodash-es/$1" },
			{ find: "lodash", replacement: "lodash-es" },
			// swagger-ui-react requests lodash-es/fp/* but lodash-es has no fp; resolve to lodash/fp
			{ find: "lodash-es/fp/assocPath", replacement: "lodash/fp/assocPath" },
			{ find: "lodash-es/fp/set", replacement: "lodash/fp/set" },
			{ find: /^lodash-es\/fp\/(.*)$/, replacement: "lodash/fp/$1" },
		],
		dedupe: [
			"react",
			"react-dom",
			"react/jsx-runtime",
			"react/jsx-dev-runtime",
			"use-sync-external-store",
		],
	},
	server: {
		port: 5173,
		// Bind to loopback only; Caddy (4000) is the single dev entrypoint. Do not open 5173 in the browser.
		host: "127.0.0.1",
		// open: true or use vite --open to warm up entry and improve first load (Vite Performance Guide)
		// Optimize HMR for faster updates; client connects via gateway so HMR works when using http://localhost:4000
		hmr: {
			overlay: true,
			clientPort: 4000,
		},
		// Optimize watch settings
		watch: {
			// Exclude directories that don't need watching (avoids "too many open files")
			ignored: [
				"**/node_modules/**",
				"**/dist/**",
				"**/.git/**",
				"**/coverage/**",
				"**/playwright-report/**",
				"**/.trace/**",
				"**/.session/**",
				"**/docs/**",
				"**/*.md",
				"**/ARCHIVE/**",
				"**/CONFIG/**",
			],
			// Use native file system events (faster on macOS)
			usePolling: false,
		},
		proxy: {
			"/api": {
				target: "http://localhost:8080",
				changeOrigin: true,
			},
		},
		// Warm up frequently used files
		warmup: {
			clientFiles: [
				"./src/routes/__root.tsx",
				"./src/routes/index.tsx",
				"./src/routes/projects.index.tsx",
				"./src/components/layout/Layout.tsx",
				"./src/lib/lazy-loading.tsx",
			],
		},
	},
	ssr: {
		// Prevent SSR/pre-bundling issues with use-sync-external-store
		noExternal: ["use-sync-external-store"],
	},
});
