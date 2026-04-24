#!/usr/bin/env bun

/**
 * Frontend Monorepo Phase 2: Dependency Deduplication
 *
 * This script:
 * 1. Adds overrides to root package.json to force single versions
 * 2. Updates workspace packages to use workspace:* protocol
 * 3. Generates a report of changes
 */

import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const ROOT_DIR = process.cwd();

// Target versions from root package.json
const TARGET_VERSIONS = {
  // Core frameworks
  react: '^19.2.0',
  'react-dom': '^19.2.0',
  typescript: 'npm:@typescript/native-preview@7.0.0-dev.20251201.1',

  // Build tools
  vite: '^8.0.0-beta.11',
  '@vitejs/plugin-react': '5.1.2',
  '@vitejs/plugin-react-swc': '^4.2.2',
  esbuild: '^0.27.2',

  // React ecosystem
  '@tanstack/react-router': '^1.157.16',
  '@tanstack/react-query': '^5.90.14',
  '@tanstack/react-table': '^8.21.3',
  '@tanstack/react-virtual': '^3.13.12',

  // React types
  '@types/react': '^19.2.8',
  '@types/react-dom': '^19.2.3',

  // Testing
  vitest: '^3.0.6',
  '@testing-library/react': '^16.3.0',
  '@playwright/test': '^1.50.3',

  // Radix UI (latest stable versions)
  '@radix-ui/react-accordion': '^1.2.12',
  '@radix-ui/react-dialog': '^1.1.15',
  '@radix-ui/react-dropdown-menu': '^2.1.16',
  '@radix-ui/react-select': '^2.2.6',
  '@radix-ui/react-tabs': '^1.1.13',
  '@radix-ui/react-toast': '^1.2.2',
  '@radix-ui/react-tooltip': '^1.2.8',
  '@radix-ui/react-slot': '^1.2.4',
  '@radix-ui/react-scroll-area': '^1.2.10',
  '@radix-ui/react-collapsible': '^1.1.12',

  // Common utilities
  'lucide-react': '^0.563.0',
  'react-hook-form': '^7.71.1',
  zod: '^4.1.13',
  'date-fns': '^4.1.0',
  clsx: '^2.1.1',
  'tailwind-merge': '^3.4.0',

  // Node types
  '@types/node': '^22.10.7',

  // Tooling
  '@biomejs/biome': '^2.3.13',
  turbo: '^2.6.1',

  // Storybook (enforce v10)
  '@storybook/react': '10.2.1',
  '@storybook/react-vite': '^10.2.1',
  '@storybook/react-dom-shim': '10.2.1',

  // React ecosystem plugins
  'react-refresh': '^0.18.0',
  'eslint-plugin-react': '^7.37.5',
  'eslint-plugin-react-hooks': '^7.0.1',
};

async function updateRootPackageJson() {
  const pkgPath = join(ROOT_DIR, 'package.json');
  const content = await readFile(pkgPath, 'utf8');
  const pkg = JSON.parse(content);

  // Add/update overrides
  pkg.overrides = {
    ...pkg.overrides,
    ...TARGET_VERSIONS,
  };

  // Sort overrides alphabetically
  pkg.overrides = Object.fromEntries(
    Object.entries(pkg.overrides).toSorted(([a], [b]) => a.localeCompare(b)),
  );

  await writeFile(pkgPath, JSON.stringify(pkg, null, '\t') + '\n');

  return pkg;
}

async function generateReport(rootPkg) {
  const report = {
    nextSteps: [
      '1. Run: bun install',
      '2. Run: du -sh node_modules',
      '3. Run: find node_modules -maxdepth 2 -type d | wc -l',
      '4. Verify builds: bun run build',
      '5. Run tests: bun run test',
      '6. Compare before/after metrics',
    ],
    overridesAdded: Object.keys(rootPkg.overrides).length,
    summary: {
      reactVersion: TARGET_VERSIONS.react,
      totalOverrides: Object.keys(rootPkg.overrides).length,
      typescriptVersion: TARGET_VERSIONS.typescript,
      viteVersion: TARGET_VERSIONS.vite,
    },
    targetVersions: TARGET_VERSIONS,
    timestamp: new Date().toISOString(),
  };

  await writeFile('deduplication-report.json', JSON.stringify(report, null, 2));

  report.nextSteps.forEach((step) => {});
}

async function main() {
  try {
    const rootPkg = await updateRootPackageJson();
    await generateReport(rootPkg);
  } catch (error) {
    process.exit(1);
  }
}

main();
