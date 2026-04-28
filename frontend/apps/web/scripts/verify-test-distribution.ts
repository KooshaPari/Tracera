#!/usr/bin/env bun
/**
 * Verifies test pyramid distribution: 70% unit, 15% integration, 5% e2e, 10% other.
 * Run: bun run scripts/verify-test-distribution.ts
 *
 * Categories (by path):
 * - unit: all tests under src except integration/, e2e/, performance/, a11y/, security/, visual/
 * - integration: src/__tests__/integration/
 * - e2e: src/__tests__/e2e/
 * - other: a11y, security, performance, visual, accessibility, mobile, power-user, workers (integration-style)
 */

import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const SRC = join(import.meta.dir, '..', 'src');
const TARGET = { unit: 70, integration: 15, e2e: 5, other: 10 };

function countTestsInFile(filePath: string): number {
  const content = readFileSync(filePath, 'utf8');
  const itMatches = content.match(/\bit\s*\(\s*['"]/g);
  const testMatches = content.match(/\btest\s*\(\s*['"]/g);
  const its = itMatches?.length ?? 0;
  const tests = testMatches?.length ?? 0;
  return its + tests;
}

function walk(dir: string, ext: string[]): string[] {
  const out: string[] = [];
  try {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        out.push(...walk(full, ext));
      } else if (ext.some((e) => entry.name.endsWith(e))) {
        out.push(full);
      }
    }
  } catch {
    // Ignore
  }
  return out;
}

function categorize(path: string): 'unit' | 'integration' | 'e2e' | 'other' {
  const normalized = path.replaceAll('\\', '/');
  if (normalized.includes('/__tests__/integration/')) {
    return 'integration';
  }
  if (normalized.includes('/__tests__/e2e/')) {
    return 'e2e';
  }
  if (
    normalized.includes('/__tests__/a11y/') ||
    normalized.includes('/__tests__/accessibility/') ||
    normalized.includes('/__tests__/security/') ||
    normalized.includes('/__tests__/performance/') ||
    normalized.includes('/__tests__/visual/') ||
    normalized.includes('/__tests__/mobile/') ||
    normalized.includes('/__tests__/power-user/')
  ) {
    return 'other';
  }
  if (
    normalized.includes('.test.') ||
    normalized.includes('.spec.') ||
    normalized.includes('/__tests__/')
  ) {
    return 'unit';
  }
  return 'unit';
}

const files = walk(SRC, ['.test.ts', '.test.tsx', '.spec.ts', '.spec.tsx']);
const counts = { unit: 0, integration: 0, e2e: 0, other: 0 };

for (const file of files) {
  const cat = categorize(file);
  counts[cat] += countTestsInFile(file);
}

const total = counts.unit + counts.integration + counts.e2e + counts.other;
const pct = (n: number) => (total > 0 ? ((n / total) * 100).toFixed(1) : '0');
const unitPct = Number(pct(counts.unit));
const integrationPct = Number(pct(counts.integration));
const e2ePct = Number(pct(counts.e2e));
const otherPct = Number(pct(counts.other));

console.log('Test distribution (target: 70/15/5/10):');
console.log(`  unit:         ${counts.unit} (${pct(counts.unit)}%)  target 70%`);
console.log(`  integration: ${counts.integration} (${pct(counts.integration)}%)  target 15%`);
console.log(`  e2e:         ${counts.e2e} (${pct(counts.e2e)}%)  target 5%`);
console.log(`  other:       ${counts.other} (${pct(counts.other)}%)  target 10%`);
console.log(`  total:       ${total}`);

const ok =
  unitPct >= 65 &&
  integrationPct >= 5 &&
  integrationPct <= 25 &&
  e2ePct >= 2 &&
  e2ePct <= 15 &&
  otherPct >= 5 &&
  otherPct <= 15;
if (ok) {
  console.log('\nDistribution within acceptable range (70/15/5/10).');
} else {
  console.log('\nDistribution outside target 70/15/5/10. Adjust test mix if needed.');
}
