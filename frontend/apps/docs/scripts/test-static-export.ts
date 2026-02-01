#!/usr/bin/env bun
/**
 * Test Static Site Generation
 *
 * This script tests the static export functionality and measures build performance.
 * It verifies that all pages can be pre-rendered at build time.
 */

import { execSync } from 'child_process';
import { existsSync, statSync, readdirSync } from 'fs';
import { join } from 'path';

interface BuildMetrics {
  buildTime: number;
  totalPages: number;
  totalSize: number;
  staticFiles: number;
  errors: string[];
}

const metrics: BuildMetrics = {
  buildTime: 0,
  totalPages: 0,
  totalSize: 0,
  staticFiles: 0,
  errors: [],
};

console.log('🚀 Testing Static Site Generation...\n');

// Step 1: Build the site
console.log('📦 Building site with static generation...');
const startTime = Date.now();

try {
  execSync('bun run build', {
    stdio: 'inherit',
    cwd: process.cwd(),
  });

  metrics.buildTime = Date.now() - startTime;
  console.log(`✅ Build completed in ${(metrics.buildTime / 1000).toFixed(2)}s\n`);
} catch (error) {
  console.error('❌ Build failed:', error);
  process.exit(1);
}

// Step 2: Analyze build output
console.log('📊 Analyzing build output...\n');

const buildDir = join(process.cwd(), '.next');
const staticDir = join(buildDir, 'static');

if (!existsSync(buildDir)) {
  console.error('❌ Build directory not found');
  process.exit(1);
}

// Count static files
function countFiles(dir: string, ext?: string): number {
  if (!existsSync(dir)) return 0;

  let count = 0;
  const files = readdirSync(dir, { withFileTypes: true });

  for (const file of files) {
    const fullPath = join(dir, file.name);

    if (file.isDirectory()) {
      count += countFiles(fullPath, ext);
    } else if (!ext || file.name.endsWith(ext)) {
      count++;
      metrics.totalSize += statSync(fullPath).size;
    }
  }

  return count;
}

metrics.staticFiles = countFiles(staticDir);
metrics.totalPages = countFiles(join(buildDir, 'server/app'), '.html');

// Step 3: Report results
console.log('📈 Build Metrics:');
console.log('─'.repeat(50));
console.log(`Build Time:      ${(metrics.buildTime / 1000).toFixed(2)}s`);
console.log(`Total Pages:     ${metrics.totalPages}`);
console.log(`Static Files:    ${metrics.staticFiles}`);
console.log(`Total Size:      ${(metrics.totalSize / 1024 / 1024).toFixed(2)} MB`);
console.log('─'.repeat(50));

// Step 4: Performance targets
console.log('\n🎯 Performance Targets:');
console.log('─'.repeat(50));

const buildTimeTarget = 60; // 60 seconds
const buildTimePassed = metrics.buildTime < buildTimeTarget * 1000;
console.log(`Build Time < ${buildTimeTarget}s:     ${buildTimePassed ? '✅' : '❌'} (${(metrics.buildTime / 1000).toFixed(2)}s)`);

const minPages = 10;
const pagesPassed = metrics.totalPages >= minPages;
console.log(`Pages Generated >= ${minPages}:  ${pagesPassed ? '✅' : '❌'} (${metrics.totalPages})`);

console.log('─'.repeat(50));

// Step 5: Check for common issues
console.log('\n🔍 Checking for issues...');

const serverDir = join(buildDir, 'server');
if (!existsSync(serverDir)) {
  metrics.errors.push('Server directory not found - static generation may have failed');
}

const appDir = join(serverDir, 'app');
if (existsSync(appDir)) {
  const files = readdirSync(appDir);
  console.log(`✅ Found ${files.length} app directories`);
} else {
  metrics.errors.push('App directory not found');
}

if (metrics.errors.length > 0) {
  console.log('\n❌ Issues found:');
  metrics.errors.forEach(error => console.log(`  • ${error}`));
  process.exit(1);
}

console.log('✅ No issues found\n');

// Step 6: Next steps
console.log('📝 Next Steps:');
console.log('─'.repeat(50));
console.log('1. Run performance tests: bun run test:performance');
console.log('2. Run Lighthouse audit: bun run lighthouse');
console.log('3. Test with: bun run start');
console.log('4. For full static export, uncomment "output: \'export\'" in next.config.ts');
console.log('─'.repeat(50));

const allPassed = buildTimePassed && pagesPassed && metrics.errors.length === 0;
process.exit(allPassed ? 0 : 1);
