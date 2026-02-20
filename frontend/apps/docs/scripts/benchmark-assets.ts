#!/usr/bin/env bun

/**
 * Asset Performance Benchmark Script
 *
 * Measures and reports asset performance metrics:
 * - Total asset size
 * - Bundle size breakdown
 * - Image optimization results
 * - Font loading performance
 * - Lighthouse asset scores
 */

import { readFile, readdir, stat } from 'node:fs/promises';
import { extname, join } from 'node:path';

interface AssetMetrics {
  images: {
    count: number;
    totalSize: number;
    byFormat: Record<string, { count: number; size: number }>;
  };
  fonts: {
    count: number;
    totalSize: number;
    byType: Record<string, { count: number; size: number }>;
  };
  svgs: {
    count: number;
    totalSize: number;
    spriteCount: number;
  };
  bundle: {
    js: number;
    css: number;
    total: number;
  };
  totalAssetSize: number;
}

/**
 * Format bytes to human-readable size
 */
function formatBytes(bytes: number): string {
  if (bytes === 0) {
    return '0 Bytes';
  }
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Get file size
 */
async function getFileSize(path: string): Promise<number> {
  try {
    const stats = await stat(path);
    return stats.size;
  } catch {
    return 0;
  }
}

/**
 * Find files recursively
 */
async function findFiles(dir: string, extensions: string[]): Promise<string[]> {
  const files: string[] = [];

  try {
    const entries = await readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = join(dir, entry.name);

      if (entry.isDirectory()) {
        if (!['node_modules', '.git', '.turbo'].includes(entry.name)) {
          files.push(...(await findFiles(fullPath, extensions)));
        }
      } else if (entry.isFile()) {
        const ext = extname(entry.name).toLowerCase();
        if (extensions.includes(ext)) {
          files.push(fullPath);
        }
      }
    }
  } catch {
    // Directory doesn't exist or can't be read
  }

  return files;
}

/**
 * Analyze images
 */
async function analyzeImages(publicDir: string): Promise<AssetMetrics['images']> {
  const imageExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif'];
  const imageFiles = await findFiles(publicDir, imageExtensions);

  const metrics: AssetMetrics['images'] = {
    byFormat: {},
    count: imageFiles.length,
    totalSize: 0,
  };

  for (const file of imageFiles) {
    const size = await getFileSize(file);
    const ext = extname(file).toLowerCase().slice(1);

    metrics.totalSize += size;

    if (!metrics.byFormat[ext]) {
      metrics.byFormat[ext] = { count: 0, size: 0 };
    }
    metrics.byFormat[ext].count += 1;
    metrics.byFormat[ext].size += size;
  }

  return metrics;
}

/**
 * Analyze SVGs
 */
async function analyzeSVGs(
  publicDir: string,
  componentsDir: string,
): Promise<AssetMetrics['svgs']> {
  const svgFiles = await findFiles(publicDir, ['.svg']);

  // Check for sprite system
  const spriteFile = join(componentsDir, 'icon-sprite.tsx');
  const hasSpriteSystem = await stat(spriteFile)
    .then(() => true)
    .catch(() => false);

  let spriteCount = 0;
  if (hasSpriteSystem) {
    const content = await readFile(spriteFile, 'utf8');
    spriteCount = (content.match(/<symbol/g) || []).length;
  }

  let totalSize = 0;
  for (const file of svgFiles) {
    totalSize += await getFileSize(file);
  }

  return {
    count: svgFiles.length,
    spriteCount,
    totalSize,
  };
}

/**
 * Analyze fonts
 */
async function analyzeFonts(publicDir: string): Promise<AssetMetrics['fonts']> {
  const fontExtensions = ['.woff', '.woff2', '.ttf', '.otf', '.eot'];
  const fontFiles = await findFiles(publicDir, fontExtensions);

  const metrics: AssetMetrics['fonts'] = {
    byType: {},
    count: fontFiles.length,
    totalSize: 0,
  };

  for (const file of fontFiles) {
    const size = await getFileSize(file);
    const ext = extname(file).toLowerCase().slice(1);

    metrics.totalSize += size;

    if (!metrics.byType[ext]) {
      metrics.byType[ext] = { count: 0, size: 0 };
    }
    metrics.byType[ext].count += 1;
    metrics.byType[ext].size += size;
  }

  return metrics;
}

/**
 * Analyze bundle
 */
async function analyzeBundle(nextDir: string): Promise<AssetMetrics['bundle']> {
  const staticDir = join(nextDir, 'static');

  const jsFiles = await findFiles(staticDir, ['.js']);
  const cssFiles = await findFiles(staticDir, ['.css']);

  let jsSize = 0;
  let cssSize = 0;

  for (const file of jsFiles) {
    jsSize += await getFileSize(file);
  }

  for (const file of cssFiles) {
    cssSize += await getFileSize(file);
  }

  return {
    css: cssSize,
    js: jsSize,
    total: jsSize + cssSize,
  };
}

/**
 * Main benchmark function
 */
async function benchmark(): Promise<void> {
  const publicDir = join(process.cwd(), 'public');
  const nextDir = join(process.cwd(), '.next');
  const componentsDir = join(process.cwd(), 'components');

  const metrics: AssetMetrics = {
    bundle: await analyzeBundle(nextDir),
    fonts: await analyzeFonts(publicDir),
    images: await analyzeImages(publicDir),
    svgs: await analyzeSVGs(publicDir, componentsDir),
    totalAssetSize: 0,
  };

  metrics.totalAssetSize =
    metrics.images.totalSize +
    metrics.fonts.totalSize +
    metrics.svgs.totalSize +
    metrics.bundle.total;

  // Print results
  console.log(`Total asset size: ${formatBytes(metrics.totalAssetSize)}`);
  console.log(
    `Bundle size: ${formatBytes(metrics.bundle.total)} (JS ${formatBytes(metrics.bundle.js)}, CSS ${formatBytes(metrics.bundle.css)})`,
  );
  console.log(`Images: ${metrics.images.count} files (${formatBytes(metrics.images.totalSize)})`);

  for (const [format, data] of Object.entries(metrics.images.byFormat)) {
    console.log(`  ${format.toUpperCase()}: ${data.count} files (${formatBytes(data.size)})`);
  }

  if (metrics.svgs.spriteCount > 0) {
    console.log(`SVGs: ${metrics.svgs.count} files (sprite count: ${metrics.svgs.spriteCount})`);
  } else {
    console.log(`SVGs: ${metrics.svgs.count} files (no sprite detected)`);
  }

  if (metrics.fonts.count > 0) {
    for (const [type, data] of Object.entries(metrics.fonts.byType)) {
      console.log(`Fonts (${type}): ${data.count} files (${formatBytes(data.size)})`);
    }
  } else {
    console.log('Fonts: none detected (likely using next/font)');
  }

  // Calculate optimization score
  const hasModernImageFormats = metrics.images.byFormat['webp'] || metrics.images.byFormat['avif'];
  const hasSpriteSystem = metrics.svgs.spriteCount > 0;
  const usesNextFonts = metrics.fonts.count === 0; // If no fonts in public, using Next.js fonts

  // Recommendations

  if (!hasModernImageFormats && metrics.images.count > 0) {
    console.log('Recommendation: Add WebP/AVIF variants to improve image performance.');
  }

  if (!hasSpriteSystem && metrics.svgs.count > 5) {
    console.log('Recommendation: Consider using an SVG sprite to reduce requests.');
  }

  if (!usesNextFonts && metrics.fonts.totalSize > 100_000) {
    console.log('Recommendation: Consider using next/font to optimize font loading.');
  }

  if (metrics.bundle.total > 500_000) {
    console.log('Recommendation: Reduce bundle size with code-splitting or lazy loading.');
  }
}

// Run benchmark
benchmark().catch((error) => {
  console.error('Benchmark failed:', error);
  process.exit(1);
});
