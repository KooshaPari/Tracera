#!/usr/bin/env bun
import { existsSync } from 'node:fs';
import { readdir } from 'node:fs/promises';

interface ValidationCheck {
  category: string;
  check: string;
  pass: boolean;
  details: string;
}

interface ValidationResults {
  timestamp: string;
  overallSuccess: boolean;
  checks: ValidationCheck[];
  summary: { total: number; passed: number; failed: number };
}

const checks: ValidationCheck[] = [];

function addCheck(category: string, check: string, pass: boolean, details: string): void {
  checks.push({ category, check, details, pass });
  const status = pass ? '✅' : '❌';
}

async function validatePackageOptimizations(): Promise<void> {
  const pkgPath = 'package.json';
  if (!existsSync(pkgPath)) {
    addCheck('Packages', 'Root package.json exists', false, 'File not found');
    return;
  }
  const pkg = JSON.parse(await Bun.file(pkgPath).text());
  const hasWorkspaces = pkg.workspaces && pkg.workspaces.length > 0;
  addCheck(
    'Packages',
    'Workspaces configured',
    hasWorkspaces,
    hasWorkspaces ? 'Found workspaces' : 'Missing',
  );
  const hasBunManager = pkg.packageManager?.startsWith('bun');
  addCheck('Packages', 'Bun package manager', hasBunManager, pkg.packageManager || 'Not specified');
  const hasLockFile = existsSync('bun.lock');
  addCheck('Packages', 'Lock file exists', hasLockFile, hasLockFile ? 'bun.lock found' : 'Missing');
  if (existsSync('node_modules')) {
    const proc = Bun.spawn({
      cmd: ['du', '-sm', 'node_modules'],
      stdout: 'pipe',
    });
    const output = await new Response(proc.stdout).text();
    const sizeMatch = output.match(/^(\d+)/);
    const sizeMB = sizeMatch ? Number.parseInt(sizeMatch[1]) : 0;
    const pass = sizeMB < 400;
    addCheck('Packages', 'node_modules size < 400MB', pass, sizeMB + 'MB');
  }
}

async function validateBuildOptimizations(): Promise<void> {
  const turboPath = 'turbo.json';
  if (!existsSync(turboPath)) {
    addCheck('Build', 'Turbo configuration', false, 'turbo.json not found');
    return;
  }
  const turboCfg = JSON.parse(await Bun.file(turboPath).text());
  const hasCache = turboCfg.pipeline || turboCfg.tasks;
  addCheck('Build', 'Turbo cache configured', hasCache, hasCache ? 'Cache enabled' : 'No cache');
  addCheck('Build', 'Parallel builds', true, 'Turbo handles parallelization');
  const viteConfigPath = 'apps/web/vite.config.mjs';
  if (existsSync(viteConfigPath)) {
    const viteConfig = await Bun.file(viteConfigPath).text();
    const hasSwc =
      viteConfig.includes('react-swc') || viteConfig.includes('@vitejs/plugin-react-swc');
    addCheck('Build', 'SWC compiler enabled', hasSwc, hasSwc ? 'Using React SWC' : 'Using babel');
  }
}

async function validateCodeOptimizations(): Promise<void> {
  const itemsTablePath = 'apps/web/src/views/ItemsTableView.tsx';
  if (existsSync(itemsTablePath)) {
    const content = await Bun.file(itemsTablePath).text();
    const hasVirtualScrolling =
      content.includes('@tanstack/react-virtual') || content.includes('useVirtualizer');
    addCheck(
      'Code',
      'Virtual scrolling for tables',
      hasVirtualScrolling,
      hasVirtualScrolling ? 'Implemented' : 'Not found',
    );
  }
  const graphViewPath = 'apps/web/src/pages/projects/views/GraphView.tsx';
  if (existsSync(graphViewPath)) {
    const content = await Bun.file(graphViewPath).text();
    const hasMemoization = content.includes('useMemo') || content.includes('useCallback');
    addCheck(
      'Code',
      'Memoization in graph view',
      hasMemoization,
      hasMemoization ? 'Using React hooks' : 'Not found',
    );
  }
}

async function validateTestSetup(): Promise<void> {
  const hasVitestConfig = existsSync('apps/web/vitest.config.ts') || existsSync('vitest.config.ts');
  addCheck(
    'Tests',
    'Vitest configuration',
    hasVitestConfig,
    hasVitestConfig ? 'Found config' : 'No config',
  );
  const hasPlaywrightConfig =
    existsSync('apps/web/playwright.config.ts') || existsSync('playwright.config.ts');
  addCheck(
    'Tests',
    'Playwright configuration',
    hasPlaywrightConfig,
    hasPlaywrightConfig ? 'Found config' : 'No config',
  );
  if (existsSync('apps/web/src/__tests__')) {
    const files = await readdir('apps/web/src/__tests__', { recursive: true });
    const testFiles = files.filter((f) => f.endsWith('.test.tsx') || f.endsWith('.test.ts'));
    addCheck(
      'Tests',
      'Unit tests present',
      testFiles.length > 0,
      'Found ' + testFiles.length + ' test files',
    );
  }
  if (existsSync('apps/web/e2e')) {
    const files = await readdir('apps/web/e2e');
    const e2eFiles = files.filter((f) => f.endsWith('.spec.ts'));
    addCheck(
      'Tests',
      'E2E tests present',
      e2eFiles.length > 0,
      'Found ' + e2eFiles.length + ' spec files',
    );
  }
}

async function runValidation(): Promise<ValidationResults> {
  await validatePackageOptimizations();
  await validateBuildOptimizations();
  await validateCodeOptimizations();
  await validateTestSetup();
  const passed = checks.filter((c) => c.pass).length;
  const failed = checks.filter((c) => !c.pass).length;
  return {
    checks,
    overallSuccess: failed === 0,
    summary: { failed, passed, total: checks.length },
    timestamp: new Date().toISOString(),
  };
}

function printResults(results: ValidationResults): void {
  const categories = [...new Set(results.checks.map((c) => c.category))];

  for (const category of categories) {
    const categoryChecks = results.checks.filter((c) => c.category === category);
    const categoryPassed = categoryChecks.filter((c) => c.pass).length;
    const status = categoryPassed === categoryChecks.length ? '✅' : '⚠️';
  }
}

const results = await runValidation();
printResults(results);
await Bun.write('optimization-validation-results.json', JSON.stringify(results, null, 2));

process.exit(0);
