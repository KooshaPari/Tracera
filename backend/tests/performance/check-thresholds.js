#!/usr/bin/env node

/**
 * Performance Threshold Checker
 *
 * Validates k6 load test results against performance thresholds
 * and detects performance regressions compared to baseline
 *
 * Usage: node check-thresholds.js <results.json> [baseline.json]
 */

import fs from 'fs';
import path from 'path';

const THRESHOLDS = {
  p95_latency_ms: 500,
  p99_latency_ms: 1000,
  error_rate_percent: 1,
  min_rps: 100,
  regression_threshold_percent: 10,
};

class PerformanceValidator {
  constructor(resultsFile, baselineFile = null) {
    this.resultsFile = resultsFile;
    this.baselineFile = baselineFile;
    this.results = null;
    this.baseline = null;
    this.violations = [];
    this.warnings = [];
  }

  load() {
    try {
      const resultsData = fs.readFileSync(this.resultsFile, 'utf8');
      this.results = JSON.parse(resultsData);

      if (this.baselineFile && fs.existsSync(this.baselineFile)) {
        const baselineData = fs.readFileSync(this.baselineFile, 'utf8');
        this.baseline = JSON.parse(baselineData);
      }

      return true;
    } catch (error) {
      console.error(`Failed to load results: ${error.message}`);
      return false;
    }
  }

  validate() {
    if (!this.results) return false;

    const metrics = this.results.metrics || {};

    // Extract metrics
    const httpDuration = metrics.http_req_duration?.values || {};
    const httpFailed = metrics.http_req_failed?.values || {};
    const httpReqs = metrics.http_reqs?.values || {};

    const p95 = httpDuration['p(95)'] || null;
    const p99 = httpDuration['p(99)'] || null;
    const totalReqs = httpReqs.count || 0;
    const failedReqs = httpFailed.count || 0;
    const duration = (this.results.state?.testRunDurationMs || 0) / 1000;

    const errorRate = (failedReqs / Math.max(totalReqs, 1)) * 100;
    const rps = totalReqs / Math.max(duration, 1);

    // Check P95 latency
    if (p95 !== null && p95 > THRESHOLDS.p95_latency_ms) {
      this.violations.push(
        `P95 latency (${p95.toFixed(2)}ms) exceeds threshold (${THRESHOLDS.p95_latency_ms}ms)`
      );
    }

    // Check P99 latency
    if (p99 !== null && p99 > THRESHOLDS.p99_latency_ms) {
      this.violations.push(
        `P99 latency (${p99.toFixed(2)}ms) exceeds threshold (${THRESHOLDS.p99_latency_ms}ms)`
      );
    }

    // Check error rate
    if (errorRate > THRESHOLDS.error_rate_percent) {
      this.violations.push(
        `Error rate (${errorRate.toFixed(2)}%) exceeds threshold (${THRESHOLDS.error_rate_percent}%)`
      );
    }

    // Check RPS (warning only in CI)
    if (rps < THRESHOLDS.min_rps) {
      this.warnings.push(
        `RPS (${rps.toFixed(2)}) below target (${THRESHOLDS.min_rps}) - may be normal in CI environment`
      );
    }

    // Check regression vs baseline
    if (this.baseline) {
      this.checkRegression(metrics);
    }

    return this.violations.length === 0;
  }

  checkRegression(currentMetrics) {
    if (!this.baseline) return;

    const baselineMetrics = this.baseline.metrics || {};

    // Compare P95 latency
    const currentP95 = currentMetrics.http_req_duration?.values?.['p(95)'] || 0;
    const baselineP95 = baselineMetrics.http_req_duration?.values?.['p(95)'] || 0;

    if (baselineP95 > 0) {
      const regression = ((currentP95 - baselineP95) / baselineP95) * 100;
      if (regression > THRESHOLDS.regression_threshold_percent) {
        this.violations.push(
          `P95 latency regression (${regression.toFixed(1)}%) exceeds threshold (${THRESHOLDS.regression_threshold_percent}%): ` +
          `${currentP95.toFixed(2)}ms vs baseline ${baselineP95.toFixed(2)}ms`
        );
      } else if (regression > 0) {
        this.warnings.push(
          `P95 latency increased by ${regression.toFixed(1)}%: ` +
          `${currentP95.toFixed(2)}ms vs baseline ${baselineP95.toFixed(2)}ms`
        );
      }
    }

    // Compare error rate
    const currentError = currentMetrics.http_req_failed?.values?.rate || 0;
    const baselineError = baselineMetrics.http_req_failed?.values?.rate || 0;

    if (baselineError >= 0) {
      const errorRegression = ((currentError - baselineError) / Math.max(baselineError, 0.001)) * 100;
      if (errorRegression > THRESHOLDS.regression_threshold_percent) {
        this.violations.push(
          `Error rate regression (${errorRegression.toFixed(1)}%): ` +
          `${(currentError * 100).toFixed(2)}% vs baseline ${(baselineError * 100).toFixed(2)}%`
        );
      }
    }
  }

  report() {
    console.log('\n╔════════════════════════════════════════════════════════════════╗');
    console.log('║          Performance Threshold Validation Report                ║');
    console.log('╚════════════════════════════════════════════════════════════════╝\n');

    // Print thresholds
    console.log('Configured Thresholds:');
    console.log(`  P95 Latency:      < ${THRESHOLDS.p95_latency_ms}ms`);
    console.log(`  P99 Latency:      < ${THRESHOLDS.p99_latency_ms}ms`);
    console.log(`  Error Rate:       < ${THRESHOLDS.error_rate_percent}%`);
    console.log(`  Min RPS:          > ${THRESHOLDS.min_rps}`);
    console.log(`  Regression:       < ${THRESHOLDS.regression_threshold_percent}% vs baseline\n`);

    // Print violations
    if (this.violations.length > 0) {
      console.log('❌ VIOLATIONS (will fail CI):');
      this.violations.forEach(v => console.log(`   - ${v}`));
      console.log();
    } else {
      console.log('✅ All thresholds passed!\n');
    }

    // Print warnings
    if (this.warnings.length > 0) {
      console.log('⚠️  WARNINGS (informational):');
      this.warnings.forEach(w => console.log(`   - ${w}`));
      console.log();
    }

    return this.violations.length === 0;
  }
}

// Main execution
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node check-thresholds.js <results.json> [baseline.json]');
  process.exit(1);
}

const resultsFile = args[0];
const baselineFile = args[1] || null;

if (!fs.existsSync(resultsFile)) {
  console.error(`Results file not found: ${resultsFile}`);
  process.exit(1);
}

const validator = new PerformanceValidator(resultsFile, baselineFile);

if (!validator.load()) {
  process.exit(1);
}

if (!validator.validate()) {
  validator.report();
  process.exit(1);
}

validator.report();
process.exit(0);
