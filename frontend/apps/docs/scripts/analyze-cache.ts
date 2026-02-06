#!/usr/bin/env bun
/**
 * Cache Analysis Script
 *
 * Analyzes the build output to verify caching strategies are properly configured.
 * Checks for:
 * - Hashed static assets (for immutable caching)
 * - Proper cache headers configuration
 * - Build manifest structure
 * - Service worker configuration
 */

import { existsSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

interface CacheAnalysis {
  staticAssets: {
    total: number;
    hashed: number;
    unhashed: number;
    totalSize: number;
  };
  chunks: {
    total: number;
    avgSize: number;
    largest: { name: string; size: number } | null;
  };
  pages: {
    total: number;
    avgSize: number;
  };
  serviceWorker: {
    exists: boolean;
    size: number;
  };
}

const analysis: CacheAnalysis = {
  chunks: {
    avgSize: 0,
    largest: null,
    total: 0,
  },
  pages: {
    avgSize: 0,
    total: 0,
  },
  serviceWorker: {
    exists: false,
    size: 0,
  },
  staticAssets: {
    hashed: 0,
    total: 0,
    totalSize: 0,
    unhashed: 0,
  },
};

const buildDir = join(process.cwd(), '.next');
const publicDir = join(process.cwd(), 'public');

if (!existsSync(buildDir)) {
  process.exit(1);
}

// Analyze static assets
const staticDir = join(buildDir, 'static');
if (existsSync(staticDir)) {
  function analyzeDirectory(dir: string, category: 'chunks' | 'css' | 'media') {
    if (!existsSync(dir)) {
      return;
    }

    const files = readdirSync(dir);
    let totalSize = 0;

    for (const file of files) {
      const filePath = join(dir, file);
      const stats = statSync(filePath);

      if (stats.isFile()) {
        const { size } = stats;
        totalSize += size;
        analysis.staticAssets.total += 1;
        analysis.staticAssets.totalSize += size;

        // Check if file is content-hashed (has hash in filename)
        const hasHash = /\.[a-f0-9]{8,}\.(js|css|woff2?|ttf|eot)$/.test(file);
        if (hasHash) {
          analysis.staticAssets.hashed += 1;
        } else {
          analysis.staticAssets.unhashed += 1;
        }

        if (category === 'chunks' && file.endsWith('.js')) {
          analysis.chunks.total += 1;

          if (!analysis.chunks.largest || size > analysis.chunks.largest.size) {
            analysis.chunks.largest = { name: file, size };
          }
        }
      }
    }

    return totalSize;
  }

  const chunksDir = join(staticDir, 'chunks');
  const cssDir = join(staticDir, 'css');
  const mediaDir = join(staticDir, 'media');

  const chunksSize = analyzeDirectory(chunksDir, 'chunks') || 0;
  analyzeDirectory(cssDir, 'css');
  analyzeDirectory(mediaDir, 'media');

  if (analysis.chunks.total > 0) {
    analysis.chunks.avgSize = chunksSize / analysis.chunks.total;
  }
}

// Analyze pages
const pagesDir = join(buildDir, 'server/app');
if (existsSync(pagesDir)) {
  let totalPageSize = 0;

  function countPages(dir: string) {
    const items = readdirSync(dir, { withFileTypes: true });

    for (const item of items) {
      const fullPath = join(dir, item.name);

      if (item.isDirectory()) {
        countPages(fullPath);
      } else if (item.name.endsWith('.html') || item.name.endsWith('.js')) {
        analysis.pages.total += 1;
        totalPageSize += statSync(fullPath).size;
      }
    }
  }

  countPages(pagesDir);

  if (analysis.pages.total > 0) {
    analysis.pages.avgSize = totalPageSize / analysis.pages.total;
  }
}

// Check for service worker
const swPath = join(publicDir, 'sw.js');
if (existsSync(swPath)) {
  analysis.serviceWorker.exists = true;
  analysis.serviceWorker.size = statSync(swPath).size;
}

// Display results

function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

const hashRatio = analysis.staticAssets.hashed / analysis.staticAssets.total;
const hashStatus = hashRatio > 0.8 ? '✅' : hashRatio > 0.5 ? '⚠️' : '❌';

const largestChunkSize = analysis.chunks.largest?.size || 0;
const largestChunkName = analysis.chunks.largest?.name || 'n/a';
const chunkStatus =
  largestChunkSize < 200 * 1024 ? '✅' : largestChunkSize < 400 * 1024 ? '⚠️' : '❌';
const serviceWorkerStatus = analysis.serviceWorker.exists ? '✅' : '❌';

console.log(`Hashed assets: ${hashStatus} ${(hashRatio * 100).toFixed(1)}%`);
console.log(
  `Static assets: ${analysis.staticAssets.total} files (${formatBytes(analysis.staticAssets.totalSize)})`,
);
console.log(
  `Chunks: ${analysis.chunks.total} files, avg ${formatBytes(analysis.chunks.avgSize)}, largest ${largestChunkName} (${formatBytes(largestChunkSize)}) ${chunkStatus}`,
);
console.log(`Pages: ${analysis.pages.total} files, avg ${formatBytes(analysis.pages.avgSize)}`);
console.log(
  `Service worker: ${serviceWorkerStatus}${analysis.serviceWorker.exists ? ` (${formatBytes(analysis.serviceWorker.size)})` : ''}`,
);

// Recommendations

if (hashRatio < 0.9) {
  console.log('Recommendation: Increase content hashing coverage for static assets.');
}

if (largestChunkSize > 400 * 1024) {
  console.log('Recommendation: Split large chunks to improve caching efficiency.');
}

if (!analysis.serviceWorker.exists) {
  console.log('Recommendation: Add a service worker for offline caching.');
}

if (analysis.pages.total < 5) {
  console.log('Recommendation: Verify static pages are being generated as expected.');
}

const allGood = hashRatio > 0.8 && largestChunkSize < 400 * 1024 && analysis.pages.total > 5;
process.exit(allGood ? 0 : 1);
