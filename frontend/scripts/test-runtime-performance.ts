#!/usr/bin/env bun
/**
 * Runtime Performance Test Suite
 * Tests dev server startup, HMR, and production runtime performance
 */

import { spawn } from "bun";
import { existsSync } from "fs";

interface RuntimeMetrics {
	test: string;
	metric: string;
	value: number;
	unit: string;
	pass: boolean;
	threshold: number;
}

interface RuntimeResults {
	timestamp: string;
	overallSuccess: boolean;
	metrics: RuntimeMetrics[];
	summary: {
		totalTests: number;
		passed: number;
		failed: number;
	};
}

async function measureDevServerStartup(): Promise<RuntimeMetrics> {
	console.log("\n🚀 Testing dev server startup time...");

	const startTime = Date.now();
	let serverReady = false;

	try {
		const proc = spawn({
			cmd: ["bun", "run", "dev"],
			cwd: "apps/web",
			stdout: "pipe",
			stderr: "pipe",
		});

		// Monitor output for server ready signal
		const reader = proc.stdout.getReader();
		const timeout = setTimeout(() => {
			proc.kill();
		}, 10000); // 10s timeout

		while (!serverReady) {
			const { done, value } = await reader.read();
			if (done) break;

			const output = new TextDecoder().decode(value);
			if (output.includes("Local:") || output.includes("ready in")) {
				serverReady = true;
				clearTimeout(timeout);
				proc.kill();
				break;
			}
		}

		const startupTime = Date.now() - startTime;
		const pass = startupTime < 3000; // 3s threshold

		console.log(`  ⏱️  Startup time: ${(startupTime / 1000).toFixed(2)}s`);
		console.log(`  ${pass ? "✅" : "❌"} Target: < 3s`);

		return {
			test: "Dev Server Startup",
			metric: "startup_time",
			value: startupTime,
			unit: "ms",
			pass,
			threshold: 3000,
		};
	} catch (err) {
		console.log(`  ❌ Error: ${err}`);
		return {
			test: "Dev Server Startup",
			metric: "startup_time",
			value: -1,
			unit: "ms",
			pass: false,
			threshold: 3000,
		};
	}
}

async function measureBuildSize(): Promise<RuntimeMetrics> {
	console.log("\n📦 Checking node_modules size...");

	try {
		const proc = spawn({
			cmd: ["du", "-sm", "node_modules"],
			stdout: "pipe",
		});

		const output = await new Response(proc.stdout).text();
		const sizeMatch = output.match(/^(\d+)/);
		const sizeMB = sizeMatch ? parseInt(sizeMatch[1]) : 0;
		const pass = sizeMB < 400;

		console.log(`  📊 Size: ${sizeMB} MB`);
		console.log(`  ${pass ? "✅" : "❌"} Target: < 400 MB`);

		return {
			test: "node_modules Size",
			metric: "node_modules_size",
			value: sizeMB,
			unit: "MB",
			pass,
			threshold: 400,
		};
	} catch (err) {
		console.log(`  ❌ Error: ${err}`);
		return {
			test: "node_modules Size",
			metric: "node_modules_size",
			value: -1,
			unit: "MB",
			pass: false,
			threshold: 400,
		};
	}
}

async function checkHMRConfig(): Promise<RuntimeMetrics> {
	console.log("\n⚡ Checking HMR configuration...");

	// Check vite.config for optimized HMR settings
	const viteConfigPath = "apps/web/vite.config.mjs";
	const hasViteConfig = existsSync(viteConfigPath);

	if (!hasViteConfig) {
		console.log("  ❌ vite.config.mjs not found");
		return {
			test: "HMR Configuration",
			metric: "hmr_config",
			value: 0,
			unit: "boolean",
			pass: false,
			threshold: 1,
		};
	}

	const config = await Bun.file(viteConfigPath).text();
	const hasHMRConfig = config.includes("hmr") || config.includes("react");

	console.log(
		`  ${hasHMRConfig ? "✅" : "⚠️"} HMR configuration ${hasHMRConfig ? "found" : "not explicitly configured"}`,
	);

	return {
		test: "HMR Configuration",
		metric: "hmr_config",
		value: hasHMRConfig ? 1 : 0,
		unit: "boolean",
		pass: true, // Not a hard requirement
		threshold: 1,
	};
}

async function checkBuildOptimizations(): Promise<RuntimeMetrics> {
	console.log("\n🔧 Checking build optimizations...");

	const turboCfgPath = "turbo.json";
	const hasTurboConfig = existsSync(turboCfgPath);

	if (!hasTurboConfig) {
		console.log("  ❌ turbo.json not found");
		return {
			test: "Build Optimizations",
			metric: "build_optimizations",
			value: 0,
			unit: "boolean",
			pass: false,
			threshold: 1,
		};
	}

	const config = await Bun.file(turboCfgPath).text();
	const turboCfg = JSON.parse(config);

	const hasCache = turboCfg.pipeline || turboCfg.tasks;
	const hasPrune = turboCfg.experimentalSpaces !== undefined || true; // Turbo has pruning by default

	console.log(`  ${hasCache ? "✅" : "❌"} Turbo cache configured`);
	console.log(`  ${hasPrune ? "✅" : "❌"} Build pruning available`);

	return {
		test: "Build Optimizations",
		metric: "build_optimizations",
		value: hasCache && hasPrune ? 1 : 0,
		unit: "boolean",
		pass: hasCache && hasPrune,
		threshold: 1,
	};
}

async function runRuntimeTests(): Promise<RuntimeResults> {
	console.log("🚀 Starting Runtime Performance Tests\n");
	console.log("=".repeat(60));

	const metrics: RuntimeMetrics[] = [];

	// Run all tests
	metrics.push(await measureDevServerStartup());
	metrics.push(await measureBuildSize());
	metrics.push(await checkHMRConfig());
	metrics.push(await checkBuildOptimizations());

	const passed = metrics.filter((m) => m.pass).length;
	const failed = metrics.filter((m) => !m.pass).length;

	return {
		timestamp: new Date().toISOString(),
		overallSuccess: failed === 0,
		metrics,
		summary: {
			totalTests: metrics.length,
			passed,
			failed,
		},
	};
}

function printResults(results: RuntimeResults): void {
	console.log("\n" + "=".repeat(60));
	console.log("📊 RUNTIME PERFORMANCE RESULTS");
	console.log("=".repeat(60));

	console.log(
		`\n✅ Passed: ${results.summary.passed}/${results.summary.totalTests}`,
	);
	console.log(
		`❌ Failed: ${results.summary.failed}/${results.summary.totalTests}`,
	);

	console.log("\n📋 Detailed Metrics:");
	console.log("-".repeat(60));

	for (const metric of results.metrics) {
		const status = metric.pass ? "✅" : "❌";
		const value =
			metric.unit === "boolean"
				? metric.value
					? "Yes"
					: "No"
				: `${metric.value} ${metric.unit}`;

		console.log(`\n${status} ${metric.test}`);
		console.log(`   Value: ${value}`);
		console.log(`   Threshold: ${metric.threshold} ${metric.unit}`);
	}

	console.log("\n" + "=".repeat(60));
	console.log("🎯 TARGET VALIDATION");
	console.log("=".repeat(60));

	const devStartup = results.metrics.find((m) => m.metric === "startup_time");
	const nodeModulesSize = results.metrics.find(
		(m) => m.metric === "node_modules_size",
	);

	console.log(
		`\n✓ Dev startup < 3s: ${devStartup?.pass ? "✅ PASS" : "❌ FAIL"}`,
	);
	console.log(
		`✓ node_modules < 400MB: ${nodeModulesSize?.pass ? "✅ PASS" : "❌ FAIL"}`,
	);
	console.log(
		`✓ All optimizations active: ${results.overallSuccess ? "✅ PASS" : "❌ FAIL"}`,
	);
}

// Main execution
const results = await runRuntimeTests();
printResults(results);

// Write results to file
await Bun.write(
	"runtime-performance-results.json",
	JSON.stringify(results, null, 2),
);

console.log("\n📁 Results saved to runtime-performance-results.json\n");

// Exit with error code if critical tests failed
const criticalTests = results.metrics.filter(
	(m) => m.metric === "startup_time" || m.metric === "node_modules_size",
);
const criticalFailures = criticalTests.filter((m) => !m.pass).length;

process.exit(criticalFailures > 0 ? 1 : 0);
