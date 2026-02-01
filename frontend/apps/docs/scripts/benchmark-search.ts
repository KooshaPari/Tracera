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
import { readFileSync } from 'fs';
import { join } from 'path';

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
    const indexData = JSON.parse(readFileSync(indexPath, 'utf-8'));
    return indexData;
  } catch (error) {
    console.error('❌ Failed to load search index:', error);
    console.log('💡 Run "bun run scripts/build-search-index.ts" first');
    process.exit(1);
  }
}

/**
 * Run single search benchmark
 */
function benchmarkSearch(
  fuse: Fuse<SearchDocument>,
  query: string,
  maxResults: number = 20
): BenchmarkResult {
  const startTime = performance.now();
  const results = fuse.search(query, { limit: maxResults });
  const duration = performance.now() - startTime;

  const avgMatchScore =
    results.length > 0
      ? results.reduce((sum, r) => sum + (r.score || 0), 0) / results.length
      : undefined;

  return {
    query,
    duration,
    resultCount: results.length,
    avgMatchScore,
  };
}

/**
 * Run full benchmark suite
 */
function runBenchmarks() {
  console.log('🚀 Starting search performance benchmark...\n');

  // Load index
  const indexData = loadSearchIndex();
  console.log(`✅ Loaded search index (${indexData.documents.length} documents)\n`);

  // Create Fuse instance
  const fuseIndex = Fuse.parseIndex<SearchDocument>(indexData.index);
  const fuse = new Fuse<SearchDocument>(indexData.documents, indexData.options, fuseIndex);

  // Run benchmarks
  const results: BenchmarkResult[] = [];

  console.log('📊 Running benchmarks...\n');

  for (const query of TEST_QUERIES) {
    const result = benchmarkSearch(fuse, query);
    results.push(result);

    const status = result.duration < 100 ? '✅' : '⚠️';
    const durationColor = result.duration < 100 ? '\x1b[32m' : '\x1b[33m';

    console.log(
      `${status} "${query}": ${durationColor}${result.duration.toFixed(2)}ms\x1b[0m (${result.resultCount} results)`
    );
  }

  // Calculate statistics
  console.log('\n📈 Statistics:\n');

  const durations = results.map((r) => r.duration);
  const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
  const minDuration = Math.min(...durations);
  const maxDuration = Math.max(...durations);
  const p95Duration = durations.sort((a, b) => a - b)[Math.floor(durations.length * 0.95)];
  const under100ms = results.filter((r) => r.duration < 100).length;
  const successRate = (under100ms / results.length) * 100;

  console.log(`Average: ${avgDuration.toFixed(2)}ms`);
  console.log(`Min: ${minDuration.toFixed(2)}ms`);
  console.log(`Max: ${maxDuration.toFixed(2)}ms`);
  console.log(`P95: ${p95Duration.toFixed(2)}ms`);
  console.log(`Under 100ms: ${under100ms}/${results.length} (${successRate.toFixed(1)}%)`);

  // Result counts
  const avgResults = results.reduce((sum, r) => sum + r.resultCount, 0) / results.length;
  const totalResults = results.reduce((sum, r) => sum + r.resultCount, 0);

  console.log(`\nAverage results per query: ${avgResults.toFixed(1)}`);
  console.log(`Total results: ${totalResults}`);

  // Match quality
  const avgScores = results
    .filter((r) => r.avgMatchScore !== undefined)
    .map((r) => r.avgMatchScore!);
  const avgMatchQuality = avgScores.reduce((sum, s) => sum + s, 0) / avgScores.length;

  console.log(`\nAverage match score: ${avgMatchQuality.toFixed(3)} (lower is better)`);

  // Pass/fail
  console.log('\n' + '='.repeat(60));

  if (successRate === 100 && avgDuration < 100) {
    console.log('✅ BENCHMARK PASSED');
    console.log(`All searches completed in <100ms (avg: ${avgDuration.toFixed(2)}ms)`);
    process.exit(0);
  } else if (successRate >= 95) {
    console.log('⚠️  BENCHMARK WARNING');
    console.log(`${successRate.toFixed(1)}% of searches under 100ms (target: 100%)`);
    console.log(`Average: ${avgDuration.toFixed(2)}ms`);
    process.exit(0);
  } else {
    console.log('❌ BENCHMARK FAILED');
    console.log(`Only ${successRate.toFixed(1)}% of searches under 100ms (target: 100%)`);
    console.log(`Average: ${avgDuration.toFixed(2)}ms (target: <100ms)`);
    process.exit(1);
  }
}

// Run benchmarks
runBenchmarks();
