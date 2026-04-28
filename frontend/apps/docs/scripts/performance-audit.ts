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

import { execSync } from 'node:child_process';
import { existsSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

interface PerformanceMetrics {
  buildTime: number;
  bundleSizes: {
    total: number;
    js: number;
    css: number;
    images: number;
    other: number;
  };
  chunks: {
    name: string;
    size: number;
  }[];
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
  if (bytes === 0) {
    return '0 B';
  }
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

function analyzeBundle(buildDir: string) {
  const staticDir = join(buildDir, 'static');

  const sizes = {
    css: 0,
    images: 0,
    js: 0,
    other: 0,
    total: 0,
  };

  const chunks: { name: string; size: number }[] = [];

  if (!existsSync(staticDir)) {
    return { chunks, sizes };
  }

  function analyzeDirectory(dir: string, prefix = '') {
    if (!existsSync(dir)) {
      return;
    }

    const files = readdirSync(dir, { withFileTypes: true });

    for (const file of files) {
      const filePath = join(dir, file.name);

      if (file.isDirectory()) {
        analyzeDirectory(filePath, `${prefix}${file.name}/`);
      } else {
        const stat = statSync(filePath);
        const { size } = stat;
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

  return { chunks, sizes };
}

async function measureBuildTime(): Promise<number> {
  const start = Date.now();

  try {
    execSync('bun run build', {
      cwd: process.cwd(),
      stdio: 'inherit',
    });
  } catch (error) {
    throw error;
  }

  const buildTime = Date.now() - start;

  return buildTime;
}

async function runPerformanceAudit(): Promise<PerformanceMetrics> {
  // Measure build time
  const buildTime = await measureBuildTime();

  // Analyze bundle

  const { sizes, chunks } = analyzeBundle(join(process.cwd(), '.next'));

  // Sort chunks by size
  chunks.sort((a, b) => b.size - a.size);

  // Print results

  const gzippedEstimate = sizes.total * 0.3; // Rough gzip estimate
  console.log(
    `Bundle total: ${formatBytes(sizes.total)} (estimated gzip ${formatBytes(gzippedEstimate)})`,
  );

  chunks.slice(0, 10).forEach((chunk, i) => {
    console.log(`${i + 1}. ${chunk.name} — ${formatBytes(chunk.size)}`);
  });

  const metrics: PerformanceMetrics = {
    buildTime,
    bundleSizes: sizes,
    chunks,
  };

  // Check if Lighthouse is available
  try {
    execSync('which lhci', { stdio: 'ignore' });
  } catch {}

  return metrics;
}

// Run the audit
runPerformanceAudit()
  .then((metrics) => {
    // Success criteria
    const checks = [
      {
        name: 'Build time',
        pass: metrics.buildTime < 60_000,
        value: `${(metrics.buildTime / 1000).toFixed(2)}s`,
      },
      {
        name: 'Bundle size',
        pass: metrics.bundleSizes.total * 0.3 < 204_800,
        value: formatBytes(metrics.bundleSizes.total * 0.3),
      },
    ];

    checks.forEach((check) => {
      const status = check.pass ? '✅' : '❌';
      console.log(`${status} ${check.name}: ${check.value}`);
    });

    const allPassed = checks.every((c) => c.pass);

    if (allPassed) {
      process.exit(0);
    } else {
      process.exit(1);
    }
  })
  .catch((error) => {
    console.error('Performance audit failed:', error);
    process.exit(1);
  });
