import path from "node:path";
import react from "@vitejs/plugin-react";
import type { PluginOption } from "vite";
import { defineConfig } from "vitest/config";

// Plugin to stub CSS imports - runs before Vite's built-in CSS processing
const cssStubPlugin = (): PluginOption => ({
	name: "css-stub",
	enforce: "pre",
	load(id) {
		if (
			id.endsWith(".css") ||
			id.endsWith(".scss") ||
			id.endsWith(".sass") ||
			id.endsWith(".less")
		) {
			return "export default {}";
		}
		return null;
	},
});

export default defineConfig({
	plugins: [cssStubPlugin(), react()] as PluginOption[],
	css: {
		postcss: {
			plugins: [], // Empty plugins array to bypass PostCSS processing
		},
	},
	test: {
		globals: true,
		environment: "jsdom",
		setupFiles: ["./src/__tests__/setup.ts"],
		testTimeout: 10000, // Increase timeout for coverage runs
		environmentOptions: {
			jsdom: {
				resources: "usable",
			},
		},
		poolOptions: {
			threads: {
				singleThread: false,
			},
		},
		css: false, // Disable CSS processing to avoid Tailwind v4 PostCSS issues in tests
		coverage: {
			provider: "v8",
			reporter: ["text", "json", "html", "lcov"],
			exclude: [
				"node_modules/",
				"src/__tests__/",
				"**/*.d.ts",
				"**/*.config.*",
				"**/mockData",
				"**/dist",
			],
			thresholds: {
				branches: 95,
				statements: 95,
				functions: 95,
				lines: 95,
			},
			all: true,
			sourceMap: true,
			transformMode: {
				web: [/\.[jt]sx?$/],
			},
		},
		include: ["src/__tests__/**/*.test.{ts,tsx}"],
		exclude: [
			"node_modules",
			"dist",
			".turbo",
		],
	},
	resolve: {
		alias: {
			"@/routeTree.gen": path.resolve(
				__dirname,
				"./src/__tests__/mocks/routeTree.mock.ts",
			),
			"@": path.resolve(__dirname, "./src"),
			"@tracertm/types": path.resolve(__dirname, "../../packages/types/src/index.ts"),
			"@repo/types": path.resolve(__dirname, "../../packages/types/src/index.ts"),
			// Mock elkjs to avoid worker issues in tests
			"elkjs/lib/elk.bundled.js": path.resolve(
				__dirname,
				"./src/__tests__/mocks/elk.mock.ts",
			),
			// Mock sigma.js to avoid WebGL issues in tests
			"sigma": path.resolve(
				__dirname,
				"./src/__tests__/mocks/sigma.mock.ts",
			),
		},
	},
});
