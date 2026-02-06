#!/usr/bin/env bun

/**
 * Phase 4 Verification Script
 *
 * Verifies all Phase 4 asset optimizations are properly implemented:
 * - Image optimization configuration
 * - Font optimization
 * - SVG sprite system
 * - Asset compression
 * - Component integration
 */

import { access, readFile } from 'node:fs/promises';
import { join } from 'node:path';

interface VerificationResult {
  name: string;
  passed: boolean;
  message: string;
}

const results: VerificationResult[] = [];

/**
 * Check if file exists
 */
async function fileExists(path: string): Promise<boolean> {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if file contains text
 */
async function fileContains(path: string, text: string): Promise<boolean> {
  try {
    const content = await readFile(path, 'utf8');
    return content.includes(text);
  } catch {
    return false;
  }
}

/**
 * Verify Next.js Image Configuration
 */
async function verifyImageConfig(): Promise<void> {
  const configPath = join(process.cwd(), 'next.config.ts');

  const checks = [
    {
      name: 'Next.js Image Config File',
      test: () => fileExists(configPath),
    },
    {
      name: 'AVIF Format Support',
      test: () => fileContains(configPath, "formats: ['image/avif', 'image/webp']"),
    },
    {
      name: 'Device Sizes Configuration',
      test: () => fileContains(configPath, 'deviceSizes:'),
    },
    {
      name: 'Image Sizes Configuration',
      test: () => fileContains(configPath, 'imageSizes:'),
    },
    {
      name: 'SVG Security Configuration',
      test: () => fileContains(configPath, 'dangerouslyAllowSVG: true'),
    },
  ];

  for (const check of checks) {
    const passed = await check.test();
    results.push({
      message: passed ? '✓ Configured' : '✗ Missing or misconfigured',
      name: check.name,
      passed,
    });
  }
}

/**
 * Verify Font Optimization
 */
async function verifyFontOptimization(): Promise<void> {
  const layoutPath = join(process.cwd(), 'app/layout.tsx');

  const checks = [
    {
      name: 'Layout File Exists',
      test: () => fileExists(layoutPath),
    },
    {
      name: 'Font Display Swap',
      test: () => fileContains(layoutPath, "display: 'swap'"),
    },
    {
      name: 'Font Preload',
      test: () => fileContains(layoutPath, 'preload: true'),
    },
    {
      name: 'Font Fallback',
      test: () => fileContains(layoutPath, 'fallback:'),
    },
    {
      name: 'Font Variable',
      test: () => fileContains(layoutPath, 'variable:'),
    },
  ];

  for (const check of checks) {
    const passed = await check.test();
    results.push({
      message: passed ? '✓ Configured' : '✗ Missing or misconfigured',
      name: check.name,
      passed,
    });
  }
}

/**
 * Verify SVG Sprite System
 */
async function verifySpriteSystem(): Promise<void> {
  const spritePath = join(process.cwd(), 'components/icon-sprite.tsx');
  const layoutPath = join(process.cwd(), 'app/layout.tsx');

  const checks = [
    {
      name: 'Icon Sprite Component',
      test: () => fileExists(spritePath),
    },
    {
      name: 'Sprite Symbols Defined',
      test: () => fileContains(spritePath, '<symbol id="icon-'),
    },
    {
      name: 'Icon Component Export',
      test: () => fileContains(spritePath, 'export function Icon'),
    },
    {
      name: 'Sprite in Layout',
      test: () => fileContains(layoutPath, 'IconSprite'),
    },
    {
      name: 'Navigation Uses Sprite',
      test: () => fileContains(join(process.cwd(), 'components/navigation.tsx'), 'Icon name='),
    },
  ];

  for (const check of checks) {
    const passed = await check.test();
    results.push({
      message: passed ? '✓ Implemented' : '✗ Missing or not integrated',
      name: check.name,
      passed,
    });
  }
}

/**
 * Verify Optimized Image Components
 */
async function verifyImageComponents(): Promise<void> {
  const imagePath = join(process.cwd(), 'components/optimized-image.tsx');
  const mdxPath = join(process.cwd(), 'components/mdx-components.tsx');

  const checks = [
    {
      name: 'Optimized Image Component',
      test: () => fileExists(imagePath),
    },
    {
      name: 'OptimizedImage Export',
      test: () => fileContains(imagePath, 'export function OptimizedImage'),
    },
    {
      name: 'DocImage Export',
      test: () => fileContains(imagePath, 'export function DocImage'),
    },
    {
      name: 'Avatar Export',
      test: () => fileContains(imagePath, 'export function Avatar'),
    },
    {
      name: 'Logo Export',
      test: () => fileContains(imagePath, 'export function Logo'),
    },
    {
      name: 'MDX Integration',
      test: () => fileContains(mdxPath, 'DocImage'),
    },
  ];

  for (const check of checks) {
    const passed = await check.test();
    results.push({
      message: passed ? '✓ Implemented' : '✗ Missing',
      name: check.name,
      passed,
    });
  }
}

/**
 * Verify Asset Compression
 */
async function verifyCompression(): Promise<void> {
  const svgoPath = join(process.cwd(), 'svgo.config.js');
  const configPath = join(process.cwd(), 'next.config.ts');

  const checks = [
    {
      name: 'SVGO Configuration',
      test: () => fileExists(svgoPath),
    },
    {
      name: 'SVGO Plugins Configured',
      test: () => fileContains(svgoPath, 'plugins:'),
    },
    {
      name: 'Compression Enabled',
      test: () => fileContains(configPath, 'compress: true'),
    },
    {
      name: 'SWC Minification',
      test: () => fileContains(configPath, 'swcMinify: true'),
    },
  ];

  for (const check of checks) {
    const passed = await check.test();
    results.push({
      message: passed ? '✓ Configured' : '✗ Missing or disabled',
      name: check.name,
      passed,
    });
  }
}

/**
 * Verify Tools and Scripts
 */
async function verifyTools(): Promise<void> {
  const optimizePath = join(process.cwd(), 'scripts/optimize-assets.ts');
  const benchmarkPath = join(process.cwd(), 'scripts/benchmark-assets.ts');
  const packagePath = join(process.cwd(), 'package.json');

  const checks = [
    {
      name: 'Asset Optimization Script',
      test: () => fileExists(optimizePath),
    },
    {
      name: 'Benchmark Script',
      test: () => fileExists(benchmarkPath),
    },
    {
      name: 'Optimize Script in package.json',
      test: () => fileContains(packagePath, '"optimize:assets"'),
    },
    {
      name: 'Benchmark Script in package.json',
      test: () => fileContains(packagePath, '"benchmark:assets"'),
    },
    {
      name: 'SVGO Dependency',
      test: () => fileContains(packagePath, '"svgo"'),
    },
  ];

  for (const check of checks) {
    const passed = await check.test();
    results.push({
      message: passed ? '✓ Available' : '✗ Missing',
      name: check.name,
      passed,
    });
  }
}

/**
 * Verify Documentation
 */
async function verifyDocumentation(): Promise<void> {
  const checks = [
    {
      name: 'Phase 4 Documentation',
      test: () => fileExists(join(process.cwd(), 'PHASE_4_ASSET_OPTIMIZATION.md')),
    },
    {
      name: 'Quick Start Guide',
      test: () => fileExists(join(process.cwd(), 'ASSET_OPTIMIZATION_QUICK_START.md')),
    },
    {
      name: 'Completion Summary',
      test: () => fileExists(join(process.cwd(), 'PHASE_4_COMPLETION_SUMMARY.md')),
    },
  ];

  for (const check of checks) {
    const passed = await check.test();
    results.push({
      message: passed ? '✓ Available' : '✗ Missing',
      name: check.name,
      passed,
    });
  }
}

/**
 * Print results
 */
function printResults(): void {
  // Group by category
  const categories = [
    { count: 5, name: '📸 Image Optimization', start: 0 },
    { count: 5, name: '🔤 Font Optimization', start: 5 },
    { count: 5, name: '📝 SVG Sprite System', start: 10 },
    { count: 6, name: '🎨 Optimized Image Components', start: 15 },
    { count: 4, name: '⚡ Asset Compression', start: 21 },
    { count: 5, name: '🛠️ Tools and Scripts', start: 25 },
    { count: 3, name: '📚 Documentation', start: 30 },
  ];

  for (const category of categories) {
    const categoryResults = results.slice(category.start, category.start + category.count);

    for (const result of categoryResults) {
      const icon = result.passed ? '✓' : '✗';
      const color = result.passed ? '\x1B[32m' : '\x1B[31m';
      const reset = '\x1B[0m';
      console.log(`${color}${icon} ${result.title}${reset} — ${result.details}`);
    }
  }

  // Summary
  const passed = results.filter((r) => r.passed).length;
  const total = results.length;
  const percentage = Math.round((passed / total) * 100);

  if (percentage === 100) {
    console.log(`✅ Phase 4 verification passed (${passed}/${total})`);
  } else if (percentage >= 80) {
    console.log(`⚠️ Phase 4 verification partial (${passed}/${total})`);
  } else {
    console.log(`❌ Phase 4 verification failed (${passed}/${total})`);
  }
}

/**
 * Main verification function
 */
async function verify(): Promise<void> {
  try {
    await verifyImageConfig();
    await verifyFontOptimization();
    await verifySpriteSystem();
    await verifyImageComponents();
    await verifyCompression();
    await verifyTools();
    await verifyDocumentation();

    printResults();

    // Exit with appropriate code
    const passed = results.filter((r) => r.passed).length;
    const percentage = (passed / results.length) * 100;

    process.exit(percentage === 100 ? 0 : 1);
  } catch (error) {
    process.exit(1);
  }
}

// Run verification
verify();
