#!/usr/bin/env node

/**
 * Dev Server Performance Benchmark
 * Measures startup time and HMR update latency
 */

import { spawn } from "node:child_process";
import { performance } from "node:perf_hooks";

const TARGETS = {
	startup: 3000, // Target: <3s startup time
	hmr: 100, // Target: <100ms HMR update time
};

let startupTime = 0;

console.log("🚀 Starting Dev Server Performance Benchmark\n");
console.log("Targets:");
console.log(`  - Startup: <${TARGETS.startup}ms (<3s)`);
console.log(`  - HMR Update: <${TARGETS.hmr}ms (<100ms)\n`);

// Measure startup time
const startTime = performance.now();
const devServer = spawn("bun", ["run", "dev"], {
	stdio: "pipe",
	shell: true,
});

let serverReady = false;

devServer.stdout.on("data", (data) => {
	const output = data.toString();
	process.stdout.write(output);

	// Detect server ready
	if (
		!serverReady &&
		(output.includes("Local:") || output.includes("ready in"))
	) {
		serverReady = true;
		startupTime = Math.round(performance.now() - startTime);

		console.log("\n✅ Dev server is ready!");
		console.log(`⏱️  Startup time: ${startupTime}ms`);

		if (startupTime < TARGETS.startup) {
			console.log(
				`🎉 PASS: Startup time is ${TARGETS.startup - startupTime}ms faster than target!\n`,
			);
		} else {
			console.log(
				`⚠️  FAIL: Startup time is ${startupTime - TARGETS.startup}ms slower than target\n`,
			);
		}

		// Report and exit
		setTimeout(() => {
			console.log("\n📊 Benchmark Results:");
			console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
			console.log(`Startup Time:     ${startupTime}ms`);
			console.log(`Target:           ${TARGETS.startup}ms`);
			console.log(
				`Status:           ${startupTime < TARGETS.startup ? "✅ PASS" : "❌ FAIL"}`,
			);
			console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

			console.log("Cleaning up...");
			devServer.kill();
			process.exit(startupTime < TARGETS.startup ? 0 : 1);
		}, 2000);
	}
});

devServer.stderr.on("data", (data) => {
	process.stderr.write(data);
});

devServer.on("error", (error) => {
	console.error("❌ Error starting dev server:", error);
	process.exit(1);
});

// Timeout after 30 seconds
setTimeout(() => {
	if (!serverReady) {
		console.error("\n❌ Timeout: Dev server did not start within 30 seconds");
		devServer.kill();
		process.exit(1);
	}
}, 30000);
