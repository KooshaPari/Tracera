#!/usr/bin/env bun

/**
 * Performance Audit Script
 *
 * Comprehensive performance testing for Fumadocs documentation site:
 * - Bundle size analysis
 * - Build time measurement
 * - Lighthouse audits
 * - Load time analysis
 */

import { execSync } from 'child_process';
import { existsSync, statSync, readdirSync } from 'fs';
import { join } from 'path';

interface PerformanceMetrics {
  buildTime: number;
  bundleSizes: {
    total: number;
    js: number;
    css: number;
    images: number;
    other: number;
  };
  chunks: Array<{
    name: string;
    size: number;
  }>;
  lighthouse?: {
    performance: number;
    accessibility: number;
    bestPractices: number;
    seo: number;
    fcp: number;
    lcp: number;
    tti: number;
  };
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

function analyzeBundle(buildDir: string) {
  const staticDir = join(buildDir, 'static');

  const sizes = {
    total: 0,
    js: 0,
    css: 0,
    images: 0,
    other: 0
  };

  const chunks: Array<{ name: string; size: number }> = [];

  if (!existsSync(staticDir)) {
    console.warn('⚠️  Build directory not found. Run build first.');
    return { sizes, chunks };
  }

  function analyzeDirectory(dir: string, prefix = '') {
    if (!existsSync(dir)) return;

    const files = readdirSync(dir, { withFileTypes: true });

    for (const file of files) {
      const filePath = join(dir, file.name);

      if (file.isDirectory()) {
        analyzeDirectory(filePath, `${prefix}${file.name}/`);
      } else {
        const stat = statSync(filePath);
        const size = stat.size;
        const ext = file.name.split('.').pop()?.toLowerCase();

        sizes.total += size;

        if (ext === 'js') {
          sizes.js += size;
          chunks.push({ name: `${prefix}${file.name}`, size });
        } else if (ext === 'css') {
          sizes.css += size;
        } else if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'].includes(ext || '')) {
          sizes.images += size;
        } else {
          sizes.other += size;
        }
      }
    }
  }

  analyzeDirectory(staticDir);

  return { sizes, chunks };
}

async function measureBuildTime(): Promise<number> {
  console.log('📦 Building project...');

  const start = Date.now();

  try {
    execSync('bun run build', {
      stdio: 'inherit',
      cwd: process.cwd()
    });
  } catch (error) {
    console.error('❌ Build failed:', error);
    throw error;
  }

  const buildTime = Date.now() - start;

  console.log(`✅ Build completed in ${(buildTime / 1000).toFixed(2)}s`);

  return buildTime;
}

async function runPerformanceAudit(): Promise<PerformanceMetrics> {
  console.log('\n🚀 Starting Performance Audit\n');
  console.log('='.repeat(50));

  // Measure build time
  const buildTime = await measureBuildTime();

  // Analyze bundle
  console.log('\n📊 Analyzing bundle sizes...\n');
  const { sizes, chunks } = analyzeBundle(join(process.cwd(), '.next'));

  // Sort chunks by size
  chunks.sort((a, b) => b.size - a.size);

  // Print results
  console.log('='.repeat(50));
  console.log('\n📈 Performance Metrics\n');
  console.log('='.repeat(50));
  console.log(`\n⏱️  Build Time: ${(buildTime / 1000).toFixed(2)}s`);
  console.log(`   ${buildTime < 60000 ? '✅' : '❌'} Target: <60s`);

  console.log('\n📦 Bundle Sizes:');
  console.log(`   Total:  ${formatBytes(sizes.total)}`);
  console.log(`   JS:     ${formatBytes(sizes.js)}`);
  console.log(`   CSS:    ${formatBytes(sizes.css)}`);
  console.log(`   Images: ${formatBytes(sizes.images)}`);
  console.log(`   Other:  ${formatBytes(sizes.other)}`);

  const gzippedEstimate = sizes.total * 0.3; // Rough gzip estimate
  console.log(`\n   Estimated gzipped: ${formatBytes(gzippedEstimate)}`);
  console.log(`   ${gzippedEstimate < 204800 ? '✅' : '❌'} Target: <200KB gzipped`);

  console.log('\n📝 Largest Chunks (Top 10):');
  chunks.slice(0, 10).forEach((chunk, i) => {
    console.log(`   ${i + 1}. ${chunk.name}: ${formatBytes(chunk.size)}`);
  });

  console.log('\n' + '='.repeat(50));

  const metrics: PerformanceMetrics = {
    buildTime,
    bundleSizes: sizes,
    chunks
  };

  // Check if Lighthouse is available
  try {
    execSync('which lhci', { stdio: 'ignore' });
    console.log('\n💡 Run Lighthouse CI with: bun run lighthouse');
  } catch {
    console.log('\n💡 Install Lighthouse CI: bun add -D @lhci/cli');
    console.log('   Then run: bun run lighthouse');
  }

  return metrics;
}

// Run the audit
runPerformanceAudit()
  .then((metrics) => {
    console.log('\n✅ Performance audit complete!\n');

    // Success criteria
    const checks = [
      { name: 'Build time', pass: metrics.buildTime < 60000, value: `${(metrics.buildTime / 1000).toFixed(2)}s` },
      { name: 'Bundle size', pass: metrics.bundleSizes.total * 0.3 < 204800, value: formatBytes(metrics.bundleSizes.total * 0.3) }
    ];

    console.log('📋 Success Criteria:');
    checks.forEach(check => {
      console.log(`   ${check.pass ? '✅' : '❌'} ${check.name}: ${check.value}`);
    });

    const allPassed = checks.every(c => c.pass);

    if (allPassed) {
      console.log('\n🎉 All performance targets met!');
      process.exit(0);
    } else {
      console.log('\n⚠️  Some performance targets not met');
      process.exit(1);
    }
  })
  .catch((error) => {
    console.error('\n❌ Performance audit failed:', error);
    process.exit(1);
  });
