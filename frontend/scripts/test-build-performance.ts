#!/usr/bin/env bun
/**
 * Build Performance Test Suite
 * Tests build times, output quality, and bundle sizes
 */

import { spawn } from "bun";
import { existsSync, rmSync } from "fs";
import { readdir, stat } from "fs/promises";
import { join } from "path";

interface BuildMetrics {
	app: string;
	buildTime: number;
	success: boolean;
	bundleSize: number;
	chunkCount: number;
	errors: string[];
}

interface TestResults {
	timestamp: string;
	overallSuccess: boolean;
	totalTime: number;
	apps: BuildMetrics[];
	summary: {
		successRate: string;
		avgBuildTime: number;
		totalBundleSize: number;
	};
}

const APPS = ["web", "docs", "storybook"];
const DIST_DIRS = {
	web: "apps/web/dist",
	docs: "apps/docs/dist",
	storybook: "apps/storybook/storybook-static",
};

async function cleanDist(app: string): Promise<void> {
	const distPath = DIST_DIRS[app as keyof typeof DIST_DIRS];
	if (existsSync(distPath)) {
		console.log(`  🧹 Cleaning ${distPath}...`);
		rmSync(distPath, { recursive: true, force: true });
	}
}

async function getDirectorySize(dirPath: string): Promise<number> {
	if (!existsSync(dirPath)) return 0;

	let totalSize = 0;
	const files = await readdir(dirPath, { recursive: true });

	for (const file of files) {
		const filePath = join(dirPath, file);
		try {
			const stats = await stat(filePath);
			if (stats.isFile()) {
				totalSize += stats.size;
			}
		} catch (err) {
			// Skip files that can't be accessed
		}
	}

	return totalSize;
}

async function countChunks(dirPath: string): Promise<number> {
	if (!existsSync(dirPath)) return 0;

	const files = await readdir(dirPath, { recursive: true });
	return files.filter((f) => f.endsWith(".js") || f.endsWith(".css")).length;
}

async function buildApp(app: string): Promise<BuildMetrics> {
	console.log(`\n📦 Building ${app}...`);

	const startTime = Date.now();
	const errors: string[] = [];
	let success = false;

	try {
		await cleanDist(app);

		const proc = spawn({
			cmd: ["bun", "run", "build"],
			cwd: `apps/${app}`,
			stdout: "pipe",
			stderr: "pipe",
		});

		const output = await new Response(proc.stdout).text();
		const errorOutput = await new Response(proc.stderr).text();

		const exitCode = await proc.exited;
		success = exitCode === 0;

		if (!success) {
			errors.push(errorOutput || "Build failed");
			console.log(`  ❌ Build failed`);
		} else {
			console.log(`  ✅ Build succeeded`);
		}
	} catch (err) {
		errors.push(err instanceof Error ? err.message : String(err));
		console.log(`  ❌ Build error: ${errors[0]}`);
	}

	const buildTime = Date.now() - startTime;
	const distPath = DIST_DIRS[app as keyof typeof DIST_DIRS];
	const bundleSize = await getDirectorySize(distPath);
	const chunkCount = await countChunks(distPath);

	console.log(`  ⏱️  Time: ${(buildTime / 1000).toFixed(2)}s`);
	console.log(`  📊 Size: ${(bundleSize / 1024 / 1024).toFixed(2)} MB`);
	console.log(`  📦 Chunks: ${chunkCount}`);

	return {
		app,
		buildTime,
		success,
		bundleSize,
		chunkCount,
		errors,
	};
}

async function runBuildTests(): Promise<TestResults> {
	console.log("🚀 Starting Build Performance Tests\n");
	console.log("=".repeat(60));

	const startTime = Date.now();
	const results: BuildMetrics[] = [];

	// Build each app sequentially to get accurate timings
	for (const app of APPS) {
		const metrics = await buildApp(app);
		results.push(metrics);
	}

	const totalTime = Date.now() - startTime;
	const successCount = results.filter((r) => r.success).length;
	const avgBuildTime =
		results.reduce((sum, r) => sum + r.buildTime, 0) / results.length;
	const totalBundleSize = results.reduce((sum, r) => sum + r.bundleSize, 0);

	return {
		timestamp: new Date().toISOString(),
		overallSuccess: successCount === APPS.length,
		totalTime,
		apps: results,
		summary: {
			successRate: `${successCount}/${APPS.length}`,
			avgBuildTime,
			totalBundleSize,
		},
	};
}

function printResults(results: TestResults): void {
	console.log("\n" + "=".repeat(60));
	console.log("📊 BUILD PERFORMANCE RESULTS");
	console.log("=".repeat(60));

	console.log(`\n⏰ Total Time: ${(results.totalTime / 1000).toFixed(2)}s`);
	console.log(`✅ Success Rate: ${results.summary.successRate}`);
	console.log(
		`📈 Avg Build Time: ${(results.summary.avgBuildTime / 1000).toFixed(2)}s`,
	);
	console.log(
		`💾 Total Bundle Size: ${(results.summary.totalBundleSize / 1024 / 1024).toFixed(2)} MB`,
	);

	console.log("\n📦 Individual App Metrics:");
	console.log("-".repeat(60));

	for (const app of results.apps) {
		const status = app.success ? "✅" : "❌";
		console.log(`\n${status} ${app.app.toUpperCase()}`);
		console.log(`   Build Time: ${(app.buildTime / 1000).toFixed(2)}s`);
		console.log(
			`   Bundle Size: ${(app.bundleSize / 1024 / 1024).toFixed(2)} MB`,
		);
		console.log(`   Chunks: ${app.chunkCount}`);

		if (app.errors.length > 0) {
			console.log(`   Errors: ${app.errors.join(", ")}`);
		}
	}

	console.log("\n" + "=".repeat(60));
	console.log("🎯 TARGET VALIDATION");
	console.log("=".repeat(60));

	const webBuild = results.apps.find((a) => a.app === "web");
	const webTime = webBuild ? webBuild.buildTime / 1000 : 0;
	const totalBuildTime = results.totalTime / 1000;

	console.log(
		`\n✓ Web build < 15s: ${webTime < 15 ? "✅ PASS" : "❌ FAIL"} (${webTime.toFixed(2)}s)`,
	);
	console.log(
		`✓ Full build < 45s: ${totalBuildTime < 45 ? "✅ PASS" : "❌ FAIL"} (${totalBuildTime.toFixed(2)}s)`,
	);
	console.log(
		`✓ All builds succeed: ${results.overallSuccess ? "✅ PASS" : "❌ FAIL"}`,
	);
}

// Main execution
const results = await runBuildTests();
printResults(results);

// Write results to file
await Bun.write(
	"build-performance-results.json",
	JSON.stringify(results, null, 2),
);

console.log("\n📁 Results saved to build-performance-results.json\n");

// Exit with error code if tests failed
process.exit(results.overallSuccess ? 0 : 1);
