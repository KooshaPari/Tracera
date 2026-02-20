#!/usr/bin/env bun
/**
 * Search Performance Benchmark
 *
 * Measures search performance to ensure <100ms response time target is met.
 * Tests various query types and result set sizes.
 *
 * Run: bun run scripts/benchmark-search.ts
 */

import Fuse from 'fuse.js';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

interface SearchDocument {
  id: string;
  url: string;
  title: string;
  description: string;
  content: string;
  headings: string[];
  structuredData?: Record<string, unknown>;
  priority: number;
}

interface BenchmarkResult {
  query: string;
  duration: number;
  resultCount: number;
  avgMatchScore?: number;
}

/**
 * Test queries covering different scenarios
 */
const TEST_QUERIES = [
  // Short queries
  'api',
  'get',
  'auth',

  // Medium queries
  'getting started',
  'installation',
  'configuration',

  // Long queries
  'how to install and configure',
  'project management features',
  'authentication and authorization',

  // Specific queries
  'traceability matrix',
  'requirements management',
  'test execution',

  // Partial matches
  'proj',
  'req',
  'auth',
];

/**
 * Load search index
 */
function loadSearchIndex() {
  const indexPath = join(process.cwd(), 'public', 'search-index.json');

  try {
    const indexData = JSON.parse(readFileSync(indexPath, 'utf8'));
    return indexData;
  } catch (error) {
    console.error('Failed to load search index:', error);
    process.exit(1);
  }
}

/**
 * Run single search benchmark
 */
function benchmarkSearch(
  fuse: Fuse<SearchDocument>,
  query: string,
  maxResults = 20,
): BenchmarkResult {
  const startTime = performance.now();
  const results = fuse.search(query, { limit: maxResults });
  const duration = performance.now() - startTime;

  const avgMatchScore =
    results.length > 0
      ? results.reduce((sum, r) => sum + (r.score || 0), 0) / results.length
      : undefined;

  const result: BenchmarkResult = {
    duration,
    query,
    resultCount: results.length,
  };

  if (avgMatchScore !== undefined) {
    result.avgMatchScore = avgMatchScore;
  }

  return result;
}

/**
 * Run full benchmark suite
 */
function runBenchmarks() {
  // Load index
  const indexData = loadSearchIndex();

  // Create Fuse instance
  const fuseIndex = Fuse.parseIndex<SearchDocument>(indexData.index);
  const fuse = new Fuse<SearchDocument>(indexData.documents, indexData.options, fuseIndex);

  // Run benchmarks
  const results: BenchmarkResult[] = [];

  for (const query of TEST_QUERIES) {
    const result = benchmarkSearch(fuse, query);
    results.push(result);

    const status = result.duration < 100 ? '✅' : '⚠️';
    const durationMs = result.duration.toFixed(1);
    const scoreLabel =
      result.avgMatchScore !== undefined
        ? `avg score ${(1 - result.avgMatchScore).toFixed(3)}`
        : 'no score';

    console.log(
      `${status} "${query}" — ${durationMs}ms, ${result.resultCount} results, ${scoreLabel}`,
    );
  }

  // Calculate statistics

  const durations = results.map((r) => r.duration);
  const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
  const minDuration = Math.min(...durations);
  const maxDuration = Math.max(...durations);
  const p95Duration = durations.toSorted((a, b) => a - b)[Math.floor(durations.length * 0.95)];
  const under100ms = results.filter((r) => r.duration < 100).length;
  const successRate = (under100ms / results.length) * 100;

  // Result counts
  const avgResults = results.reduce((sum, r) => sum + r.resultCount, 0) / results.length;
  const totalResults = results.reduce((sum, r) => sum + r.resultCount, 0);

  // Match quality
  const avgScores = results
    .filter((r) => r.avgMatchScore !== undefined)
    .map((r) => r.avgMatchScore!);
  const avgMatchQuality =
    avgScores.length > 0 ? avgScores.reduce((sum, s) => sum + s, 0) / avgScores.length : 0;

  // Pass/fail
  console.log(
    `Average duration: ${avgDuration.toFixed(1)}ms (min ${minDuration.toFixed(1)}ms, max ${maxDuration.toFixed(1)}ms, p95 ${p95Duration.toFixed(1)}ms)`,
  );
  console.log(`Success rate (<100ms): ${successRate.toFixed(1)}%`);
  console.log(`Average results: ${avgResults.toFixed(1)} (total ${totalResults})`);
  if (avgScores.length > 0) {
    console.log(`Average match quality: ${(1 - avgMatchQuality).toFixed(3)}`);
  }

  if (successRate === 100 && avgDuration < 100) {
    process.exit(0);
  } else if (successRate >= 95) {
    process.exit(0);
  } else {
    process.exit(1);
  }
}

// Run benchmarks
runBenchmarks();
