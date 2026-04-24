#!/usr/bin/env bun
/**
 * Test Static Site Generation
 *
 * This script tests the static export functionality and measures build performance.
 * It verifies that all pages can be pre-rendered at build time.
 */

import { execSync } from 'node:child_process';
import { existsSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

interface BuildMetrics {
  buildTime: number;
  totalPages: number;
  totalSize: number;
  staticFiles: number;
  errors: string[];
}

const metrics: BuildMetrics = {
  buildTime: 0,
  errors: [],
  staticFiles: 0,
  totalPages: 0,
  totalSize: 0,
};

// Step 1: Build the site

const startTime = Date.now();

try {
  execSync('bun run build', {
    cwd: process.cwd(),
    stdio: 'inherit',
  });

  metrics.buildTime = Date.now() - startTime;
} catch (error) {
  process.exit(1);
}

// Step 2: Analyze build output

const buildDir = join(process.cwd(), '.next');
const staticDir = join(buildDir, 'static');

if (!existsSync(buildDir)) {
  process.exit(1);
}

// Count static files
function countFiles(dir: string, ext?: string): number {
  if (!existsSync(dir)) {
    return 0;
  }

  let count = 0;
  const files = readdirSync(dir, { withFileTypes: true });

  for (const file of files) {
    const fullPath = join(dir, file.name);

    if (file.isDirectory()) {
      count += countFiles(fullPath, ext);
    } else if (!ext || file.name.endsWith(ext)) {
      count += 1;
      metrics.totalSize += statSync(fullPath).size;
    }
  }

  return count;
}

metrics.staticFiles = countFiles(staticDir);
metrics.totalPages = countFiles(join(buildDir, 'server/app'), '.html');

// Step 3: Report results

// Step 4: Performance targets

const buildTimeTarget = 60; // 60 seconds
const buildTimePassed = metrics.buildTime < buildTimeTarget * 1000;

const minPages = 10;
const pagesPassed = metrics.totalPages >= minPages;

// Step 5: Check for common issues

const serverDir = join(buildDir, 'server');
if (!existsSync(serverDir)) {
  metrics.errors.push('Server directory not found - static generation may have failed');
}

const appDir = join(serverDir, 'app');
if (existsSync(appDir)) {
  const files = readdirSync(appDir);
  console.log(`App directory contains ${files.length} entries.`);
} else {
  metrics.errors.push('App directory not found');
}

if (metrics.errors.length > 0) {
  metrics.errors.forEach((error) => {
    console.error('Static export error:', error);
  });
  process.exit(1);
}

// Step 6: Next steps

const allPassed = buildTimePassed && pagesPassed && metrics.errors.length === 0;
process.exit(allPassed ? 0 : 1);
