#!/usr/bin/env bun
/**
 * Build Performance Test Suite
 * Tests build times, output quality, and bundle sizes
 */

import { spawn } from 'bun';
import { existsSync, rmSync } from 'node:fs';
import { readdir, stat } from 'node:fs/promises';
import { join } from 'node:path';

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

const APPS = ['web', 'docs', 'storybook'];
const DIST_DIRS = {
  docs: 'apps/docs/dist',
  storybook: 'apps/storybook/storybook-static',
  web: 'apps/web/dist',
};

async function cleanDist(app: string): Promise<void> {
  const distPath = DIST_DIRS[app as keyof typeof DIST_DIRS];
  if (existsSync(distPath)) {
    rmSync(distPath, { force: true, recursive: true });
  }
}

async function getDirectorySize(dirPath: string): Promise<number> {
  if (!existsSync(dirPath)) {
    return 0;
  }

  let totalSize = 0;
  const files = await readdir(dirPath, { recursive: true });

  for (const file of files) {
    const filePath = join(dirPath, file);
    try {
      const stats = await stat(filePath);
      if (stats.isFile()) {
        totalSize += stats.size;
      }
    } catch {
      // Skip files that can't be accessed
    }
  }

  return totalSize;
}

async function countChunks(dirPath: string): Promise<number> {
  if (!existsSync(dirPath)) {
    return 0;
  }

  const files = await readdir(dirPath, { recursive: true });
  return files.filter((f) => f.endsWith('.js') || f.endsWith('.css')).length;
}

async function buildApp(app: string): Promise<BuildMetrics> {
  const startTime = Date.now();
  const errors: string[] = [];
  let success = false;

  try {
    await cleanDist(app);

    const proc = spawn({
      cmd: ['bun', 'run', 'build'],
      cwd: `apps/${app}`,
      stderr: 'pipe',
      stdout: 'pipe',
    });

    const _output = await new Response(proc.stdout).text();
    const errorOutput = await new Response(proc.stderr).text();

    const exitCode = await proc.exited;
    success = exitCode === 0;

    if (!success) {
      errors.push(errorOutput || 'Build failed');
    } else {
    }
  } catch (error) {
    errors.push(error instanceof Error ? error.message : String(error));
  }

  const buildTime = Date.now() - startTime;
  const distPath = DIST_DIRS[app as keyof typeof DIST_DIRS];
  const bundleSize = await getDirectorySize(distPath);
  const chunkCount = await countChunks(distPath);

  return {
    app,
    buildTime,
    bundleSize,
    chunkCount,
    errors,
    success,
  };
}

async function runBuildTests(): Promise<TestResults> {
  const startTime = Date.now();
  const results: BuildMetrics[] = [];

  // Build each app sequentially to get accurate timings
  for (const app of APPS) {
    const metrics = await buildApp(app);
    results.push(metrics);
  }

  const totalTime = Date.now() - startTime;
  const successCount = results.filter((r) => r.success).length;
  const avgBuildTime = results.reduce((sum, r) => sum + r.buildTime, 0) / results.length;
  const totalBundleSize = results.reduce((sum, r) => sum + r.bundleSize, 0);

  return {
    apps: results,
    overallSuccess: successCount === APPS.length,
    summary: {
      avgBuildTime,
      successRate: `${successCount}/${APPS.length}`,
      totalBundleSize,
    },
    timestamp: new Date().toISOString(),
    totalTime,
  };
}

function printResults(results: TestResults): void {
  for (const app of results.apps) {
    const status = app.success ? '✅' : '❌';

    if (app.errors.length > 0) {
    }
  }

  const webBuild = results.apps.find((a) => a.app === 'web');
  const webTime = webBuild ? webBuild.buildTime / 1000 : 0;
  const totalBuildTime = results.totalTime / 1000;
}

// Main execution
const results = await runBuildTests();
printResults(results);

// Write results to file
await Bun.write('build-performance-results.json', JSON.stringify(results, null, 2));

// Exit with error code if tests failed
process.exit(results.overallSuccess ? 0 : 1);
