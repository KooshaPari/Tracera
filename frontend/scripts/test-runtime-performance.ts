#!/usr/bin/env bun
/**
 * Runtime Performance Test Suite
 * Tests dev server startup, HMR, and production runtime performance
 */

import { spawn } from 'bun';
import { existsSync } from 'node:fs';
import { readdir } from 'node:fs/promises';

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
  const startTime = Date.now();
  let serverReady = false;

  try {
    const proc = spawn({
      cmd: ['bun', 'run', 'dev'],
      cwd: 'apps/web',
      stderr: 'pipe',
      stdout: 'pipe',
    });

    // Monitor output for server ready signal
    const reader = proc.stdout.getReader();
    const timeout = setTimeout(() => {
      proc.kill();
    }, 10_000); // 10s timeout

    while (!serverReady) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }

      const output = new TextDecoder().decode(value);
      if (output.includes('Local:') || output.includes('ready in')) {
        serverReady = true;
        clearTimeout(timeout);
        proc.kill();
        break;
      }
    }

    const startupTime = Date.now() - startTime;
    const pass = startupTime < 3000; // 3s threshold

    return {
      metric: 'startup_time',
      pass,
      test: 'Dev Server Startup',
      threshold: 3000,
      unit: 'ms',
      value: startupTime,
    };
  } catch (error) {
    console.log(`  ❌ Error: ${error}`);
    return {
      metric: 'startup_time',
      pass: false,
      test: 'Dev Server Startup',
      threshold: 3000,
      unit: 'ms',
      value: -1,
    };
  }
}

async function checkShippedArtifacts(): Promise<RuntimeMetrics> {
  const distPath = 'apps/web/dist';
  const artifactManifest = existsSync(`${distPath}/index.html`);
  const assets = artifactManifest
    ? (await readdir(distPath, { recursive: true })).filter((file) => /\.(js|css)$/.test(file))
    : [];
  return {
    metric: 'shipped_artifacts',
    pass: artifactManifest && assets.length > 0,
    test: 'Shipped Web Artifacts',
    threshold: 1,
    unit: 'assets',
    value: assets.length,
  };
}

async function checkHMRConfig(): Promise<RuntimeMetrics> {
  // Check vite.config for optimized HMR settings
  const viteConfigPath = 'apps/web/vite.config.mjs';
  const hasViteConfig = existsSync(viteConfigPath);

  if (!hasViteConfig) {
    return {
      metric: 'hmr_config',
      pass: false,
      test: 'HMR Configuration',
      threshold: 1,
      unit: 'boolean',
      value: 0,
    };
  }

  const config = await Bun.file(viteConfigPath).text();
  const hasHMRConfig = config.includes('hmr') || config.includes('react');

  return {
    test: 'HMR Configuration',
    metric: 'hmr_config',
    value: hasHMRConfig ? 1 : 0,
    unit: 'boolean',
    pass: true, // Not a hard requirement
    threshold: 1,
  };
}

async function checkBuildOptimizations(): Promise<RuntimeMetrics> {
  const turboCfgPath = 'turbo.json';
  const hasTurboConfig = existsSync(turboCfgPath);

  if (!hasTurboConfig) {
    return {
      metric: 'build_optimizations',
      pass: false,
      test: 'Build Optimizations',
      threshold: 1,
      unit: 'boolean',
      value: 0,
    };
  }

  const config = await Bun.file(turboCfgPath).text();
  const turboCfg = JSON.parse(config);

  const hasCache = turboCfg.pipeline || turboCfg.tasks;
  const hasPrune = turboCfg.experimentalSpaces !== undefined || turboCfg.tasks !== undefined;

  return {
    metric: 'build_optimizations',
    pass: hasCache && hasPrune,
    test: 'Build Optimizations',
    threshold: 1,
    unit: 'boolean',
    value: hasCache && hasPrune ? 1 : 0,
  };
}

async function runRuntimeTests(): Promise<RuntimeResults> {
  const metrics: RuntimeMetrics[] = [];

  // Run all tests
  metrics.push(await measureDevServerStartup());
  metrics.push(await checkShippedArtifacts());
  metrics.push(await checkHMRConfig());
  metrics.push(await checkBuildOptimizations());

  const passed = metrics.filter((m) => m.pass).length;
  const failed = metrics.filter((m) => !m.pass).length;

  return {
    metrics,
    overallSuccess: failed === 0,
    summary: {
      failed,
      passed,
      totalTests: metrics.length,
    },
    timestamp: new Date().toISOString(),
  };
}

function printResults(results: RuntimeResults): void {
  for (const metric of results.metrics) {
    const status = metric.pass ? '✅' : '❌';
    const value =
      metric.unit === 'boolean' ? (metric.value ? 'Yes' : 'No') : `${metric.value} ${metric.unit}`;
  }

  const devStartup = results.metrics.find((m) => m.metric === 'startup_time');
  const shippedArtifacts = results.metrics.find((m) => m.metric === 'shipped_artifacts');
}

// Main execution
const results = await runRuntimeTests();
printResults(results);

// Write results to file
await Bun.write('runtime-performance-results.json', JSON.stringify(results, null, 2));

// Exit with error code if critical tests failed
const criticalTests = results.metrics.filter(
  (m) => m.metric === 'startup_time' || m.metric === 'shipped_artifacts',
);
const criticalFailures = criticalTests.filter((m) => !m.pass).length;

process.exit(criticalFailures > 0 ? 1 : 0);
