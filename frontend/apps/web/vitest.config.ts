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
		coverage: {
			exclude: ["src/**/*.{test,spec,stories}.{ts,tsx}", "src/test/**"],
			include: ["src/**/*.{ts,tsx}"],
			provider: "v8",
			reporter: ["text", "json", "html", "lcov"],
			thresholds: {
				branches: 70,
				functions: 70,
				lines: 70,
				statements: 70,
			},
		},
		environment: "jsdom",
		globals: true,
		include: ["src/**/*.{test,spec}.{ts,tsx}"],
		reporters: ["verbose"],
		setupFiles: ["./src/test/setup.ts"],
		ui: true,
	},
});
