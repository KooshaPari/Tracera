#!/usr/bin/env bun
/**
 * Master Performance Test Runner
 * Runs all performance tests and generates a comprehensive report
 */

import { spawn } from 'bun';

interface TestSuite {
  name: string;
  script: string;
  critical: boolean;
}

const TEST_SUITES: TestSuite[] = [
  {
    critical: false,
    name: 'Optimization Validation',
    script: 'bun scripts/validate-optimizations.ts',
  },
  {
    critical: true,
    name: 'Build Performance',
    script: 'bun scripts/test-build-performance.ts',
  },
  {
    critical: true,
    name: 'Runtime Performance',
    script: 'bun scripts/test-runtime-performance.ts',
  },
  {
    critical: true,
    name: 'Unit Tests',
    script: 'bun test',
  },
  {
    critical: true,
    name: 'E2E Tests',
    script: 'bun --cwd apps/web run test:e2e',
  },
];

interface SuiteResult {
  suite: string;
  passed: boolean;
  duration: number;
  critical: boolean;
  error?: string;
}

async function runSuite(suite: TestSuite): Promise<SuiteResult> {
  const startTime = Date.now();

  try {
    const [cmd, ...args] = suite.script.split(' ');
    const proc = spawn({
      cmd: [cmd, ...args],
      stderr: 'inherit',
      stdout: 'inherit',
    });

    const exitCode = await proc.exited;
    const duration = Date.now() - startTime;
    const passed = exitCode === 0;

    return {
      critical: suite.critical,
      duration,
      passed,
      suite: suite.name,
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    console.log(`\n❌ ${suite.name}: ERROR (${(duration / 1000).toFixed(2)}s)`);
    console.error(error);

    return {
      critical: suite.critical,
      duration,
      error: error instanceof Error ? error.message : String(error),
      passed: false,
      suite: suite.name,
    };
  }
}

async function runAllTests() {
  const results: SuiteResult[] = [];
  const startTime = Date.now();

  for (const suite of TEST_SUITES) {
    const result = await runSuite(suite);
    results.push(result);
  }

  const totalDuration = Date.now() - startTime;

  // Print summary

  const passed = results.filter((r) => r.passed).length;
  const failed = results.filter((r) => !r.passed).length;
  const criticalFailed = results.filter((r) => r.critical && !r.passed).length;

  for (const result of results) {
    const status = result.passed ? '✅' : '❌';
    const critical = result.critical ? '🚨' : '  ';

    if (result.error) {
    }
  }

  // Write summary to file
  const summary = {
    results,
    summary: {
      criticalFailed,
      failed,
      passed,
      total: results.length,
    },
    timestamp: new Date().toISOString(),
    totalDuration,
  };

  await Bun.write('performance-test-summary.json', JSON.stringify(summary, null, 2));

  // Generate markdown report
  await generateMarkdownReport(summary);

  if (criticalFailed === 0) {
  } else {
  }

  // Exit with error if critical tests failed
  process.exit(criticalFailed > 0 ? 1 : 0);
}

async function generateMarkdownReport(summary: any) {
  const report = `# Frontend Performance Test Report

**Generated:** ${summary.timestamp}
**Total Duration:** ${(summary.totalDuration / 1000).toFixed(2)}s

## Summary

- ✅ Passed: ${summary.summary.passed}/${summary.summary.total}
- ❌ Failed: ${summary.summary.failed}/${summary.summary.total}
- 🚨 Critical Failures: ${summary.summary.criticalFailed}

## Test Results

${summary.results
  .map((r: SuiteResult) => {
    const status = r.passed ? '✅ PASS' : '❌ FAIL';
    const critical = r.critical ? '(Critical)' : '';
    return `### ${r.suite} ${critical}

**Status:** ${status}
**Duration:** ${(r.duration / 1000).toFixed(2)}s
${r.error ? `**Error:** ${r.error}` : ''}
`;
  })
  .join('\n')}

## Success Criteria Validation

| Criteria | Target | Status |
|----------|--------|--------|
| Dev startup | < 3s | ${checkResult('Runtime Performance', summary.results)} |
| Web build | < 15s | ${checkResult('Build Performance', summary.results)} |
| Full build | < 45s | ${checkResult('Build Performance', summary.results)} |
| HMR | < 100ms | ${checkResult('Runtime Performance', summary.results)} |
| node_modules | < 400MB | ${checkResult('Runtime Performance', summary.results)} |
| All tests | Passing | ${summary.summary.failed === 0 ? '✅' : '❌'} |

## Files Generated

- \`performance-test-summary.json\` - Complete test results
- \`optimization-validation-results.json\` - Optimization checks
- \`build-performance-results.json\` - Build metrics
- \`runtime-performance-results.json\` - Runtime metrics

## Next Steps

${
  summary.summary.criticalFailed === 0
    ? '✅ All critical tests passed! The frontend is optimized and ready for production.'
    : `❌ ${summary.summary.criticalFailed} critical test(s) failed. Review the details above and fix issues before deployment.`
}
`;

  await Bun.write('PERFORMANCE_TEST_REPORT.md', report);
}

function checkResult(suiteName: string, results: SuiteResult[]): string {
  const result = results.find((r) => r.suite === suiteName);
  return result?.passed ? '✅' : '❌';
}

// Run all tests
await runAllTests();
