import type { Reporter, TestCase, TestResult } from '@playwright/test/reporter';

import * as fs from 'node:fs';
import * as path from 'node:path';

/**
 * Failed Routes Reporter
 *
 * Custom Playwright reporter that generates a JSON report of all failed routes
 * during E2E testing. This helps identify which routes need attention.
 */
class FailedRoutesReporter implements Reporter {
  private failedRoutes: Set<string> = new Set();
  private testResults: {
    title: string;
    url?: string;
    status: 'passed' | 'failed' | 'skipped' | 'timedout';
    error?: string;
    duration: number;
  }[] = [];
  private totalDuration = 0;
  private startTime = Date.now();

  onTestEnd(test: TestCase, result: TestResult) {
    // Extract URL from test title if present
    const urlMatch = test.title.match(/\b(https?:\/\/[^\s]+)\b/);
    const url = urlMatch ? urlMatch[0] : undefined;

    // Track failed routes
    if (result.status === 'failed' && url) {
      this.failedRoutes.add(url);
    }

    // Map Playwright status to our status type
    let status: 'passed' | 'failed' | 'skipped' | 'timedout' = 'passed';
    if (result.status === 'failed') {
      status = 'failed';
    } else if (result.status === 'skipped') {
      status = 'skipped';
    } else if (result.status === 'timedOut' || result.status === 'interrupted') {
      status = 'timedout';
    }

    // Store test result details
    this.testResults.push({
      title: test.title,
      url,
      status,
      error: result.error?.message,
      duration: result.duration,
    });

    this.totalDuration += result.duration;
  }

  onEnd() {
    const reportDir = 'playwright-report';

    // Create directory if it doesn't exist
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }

    // Generate comprehensive report
    const report = {
      timestamp: new Date().toISOString(),
      wallClock: Date.now() - this.startTime,
      totalDuration: this.totalDuration,
      summary: {
        total: this.testResults.length,
        passed: this.testResults.filter((r) => r.status === 'passed').length,
        failed: this.testResults.filter((r) => r.status === 'failed').length,
        skipped: this.testResults.filter((r) => r.status === 'skipped').length,
        timedout: this.testResults.filter((r) => r.status === 'timedout').length,
      },
      failedRoutes: [...this.failedRoutes].toSorted(),
      details: this.testResults,
    };

    // Write JSON report
    const reportPath = path.join(reportDir, 'failed-routes.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n📊 Failed Routes Report written to: ${reportPath}`);

    // Print summary
    console.log(`\n📈 Test Summary:`);
    console.log(`  Total Tests: ${report.summary.total}`);
    console.log(`  Passed: ${report.summary.passed}`);
    console.log(`  Failed: ${report.summary.failed}`);
    console.log(`  Skipped: ${report.summary.skipped}`);
    console.log(`  Timed Out: ${report.summary.timedout}`);
    console.log(`  Total Duration: ${(report.totalDuration / 1000).toFixed(2)}s`);

    // Print failed routes summary
    if (this.failedRoutes.size > 0) {
      console.log(`\n❌ Failed Routes (${this.failedRoutes.size}):`);
      this.failedRoutes.forEach((route) => {
        console.log(`  - ${route}`);
      });
    } else {
      console.log(`\n✅ All routes passed!`);
    }
  }
}

export default FailedRoutesReporter;
