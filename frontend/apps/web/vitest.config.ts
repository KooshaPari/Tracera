import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
	plugins: [react()],
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./src"),
		},
	},
	test: {
		environment: "jsdom",
		globals: true,
		setupFiles: ["./src/test/setup.ts"],
		coverage: {
			provider: "v8",
			reporter: ["text", "json", "html", "lcov"],
			include: ["src/**/*.{ts,tsx}"],
			exclude: ["src/**/*.{test,spec,stories}.{ts,tsx}", "src/test/**"],
			thresholds: {
				lines: 70,
				functions: 70,
				branches: 70,
				statements: 70,
			},
		},
		include: ["src/**/*.{test,spec}.{ts,tsx}"],
		reporters: ["verbose"],
		ui: true,
	},
});
