#!/usr/bin/env node
/**
 * Performance Results Analyzer for 10k Concurrent Users Load Test
 *
 * Analyzes k6 test results and system monitoring data to identify
 * bottlenecks and generate optimization recommendations.
 */

const fs = require('fs');
const path = require('path');

// Configuration
const RESULTS_DIR = process.argv[2] || './performance-results';
const THRESHOLDS = {
  responseTime: {
    p50: 200,
    p95: 500,
    p99: 1000,
    avg: 300,
  },
  throughput: 1000, // req/s
  errorRate: 0.01, // 1%
  cacheHitRate: 0.80, // 80%
  cpuUsage: 80, // 80%
  memoryUsage: 85, // 85%
  dbConnections: 100, // max active connections
};

// Bottleneck severity levels
const SEVERITY = {
  CRITICAL: 'CRITICAL',
  HIGH: 'HIGH',
  MEDIUM: 'MEDIUM',
  LOW: 'LOW',
  INFO: 'INFO',
};

class PerformanceAnalyzer {
  constructor(resultsDir) {
    this.resultsDir = resultsDir;
    this.k6Results = null;
    this.monitoringData = {
      cpu: [],
      memory: [],
      backend: [],
      database: [],
      redis: [],
      network: [],
      responseTimes: [],
    };
    this.bottlenecks = [];
    this.recommendations = [];
  }

  /**
   * Load k6 test results
   */
  loadK6Results() {
    console.log('Loading k6 test results...');

    // Find the most recent k6 results file
    const files = fs.readdirSync(this.resultsDir)
      .filter(f => f.startsWith('10k-users-') && f.endsWith('.json'))
      .sort()
      .reverse();

    if (files.length === 0) {
      console.error('No k6 results found in', this.resultsDir);
      return false;
    }

    const resultFile = path.join(this.resultsDir, files[0]);
    console.log('Loading:', resultFile);

    try {
      this.k6Results = JSON.parse(fs.readFileSync(resultFile, 'utf8'));
      return true;
    } catch (error) {
      console.error('Error loading k6 results:', error.message);
      return false;
    }
  }

  /**
   * Load monitoring data
   */
  loadMonitoringData() {
    console.log('Loading monitoring data...');

    const monitoringDir = path.join(this.resultsDir, 'monitoring');
    if (!fs.existsSync(monitoringDir)) {
      console.warn('No monitoring data found');
      return false;
    }

    // Load CSV files
    const csvTypes = ['cpu', 'memory', 'backend', 'database', 'redis', 'network', 'response_times'];

    for (const type of csvTypes) {
      const files = fs.readdirSync(monitoringDir)
        .filter(f => f.startsWith(type) && f.endsWith('.csv'))
        .sort()
        .reverse();

      if (files.length > 0) {
        const csvPath = path.join(monitoringDir, files[0]);
        this.monitoringData[type.replace('_', '')] = this.parseCSV(csvPath);
      }
    }

    return true;
  }

  /**
   * Parse CSV file
   */
  parseCSV(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.trim().split('\n');
    const headers = lines[0].split(',');
    const data = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      const row = {};
      headers.forEach((header, index) => {
        row[header] = values[index];
      });
      data.push(row);
    }

    return data;
  }

  /**
   * Analyze k6 metrics
   */
  analyzeK6Metrics() {
    console.log('\nAnalyzing k6 metrics...');

    const metrics = this.k6Results.metrics;
    if (!metrics) {
      console.error('No metrics found in k6 results');
      return;
    }

    // Response time analysis
    this.analyzeResponseTimes(metrics);

    // Error rate analysis
    this.analyzeErrorRates(metrics);

    // Throughput analysis
    this.analyzeThroughput(metrics);

    // Custom metrics analysis
    this.analyzeCustomMetrics(metrics);
  }

  /**
   * Analyze response times
   */
  analyzeResponseTimes(metrics) {
    const duration = metrics.http_req_duration?.values || {};

    console.log('Response Time Analysis:');
    console.log(`  P50: ${duration['p(50)']?.toFixed(2)}ms (Target: < ${THRESHOLDS.responseTime.p50}ms)`);
    console.log(`  P95: ${duration['p(95)']?.toFixed(2)}ms (Target: < ${THRESHOLDS.responseTime.p95}ms)`);
    console.log(`  P99: ${duration['p(99)']?.toFixed(2)}ms (Target: < ${THRESHOLDS.responseTime.p99}ms)`);
    console.log(`  Avg: ${duration.avg?.toFixed(2)}ms (Target: < ${THRESHOLDS.responseTime.avg}ms)`);

    // Check for violations
    if (duration['p(95)'] > THRESHOLDS.responseTime.p95) {
      this.addBottleneck(
        SEVERITY.HIGH,
        'Response Time',
        `P95 response time (${duration['p(95)'].toFixed(2)}ms) exceeds threshold (${THRESHOLDS.responseTime.p95}ms)`,
        [
          'Add database indexes for frequently queried fields',
          'Implement query result caching with Redis',
          'Optimize N+1 query patterns',
          'Consider read replicas for database',
        ]
      );
    }

    if (duration['p(99)'] > THRESHOLDS.responseTime.p99) {
      this.addBottleneck(
        SEVERITY.CRITICAL,
        'Response Time',
        `P99 response time (${duration['p(99)'].toFixed(2)}ms) exceeds threshold (${THRESHOLDS.responseTime.p99}ms)`,
        [
          'Investigate slowest queries (99th percentile)',
          'Implement request timeouts (e.g., 5s)',
          'Add circuit breakers for external services',
          'Review database query plans',
        ]
      );
    }

    if (duration.avg > THRESHOLDS.responseTime.avg) {
      this.addBottleneck(
        SEVERITY.MEDIUM,
        'Response Time',
        `Average response time (${duration.avg.toFixed(2)}ms) exceeds threshold (${THRESHOLDS.responseTime.avg}ms)`,
        [
          'Profile application code for hot paths',
          'Optimize serialization/deserialization',
          'Review middleware overhead',
          'Consider response compression',
        ]
      );
    }
  }

  /**
   * Analyze error rates
   */
  analyzeErrorRates(metrics) {
    const httpFailed = metrics.http_req_failed?.values || {};
    const httpReqs = metrics.http_reqs?.values || {};
    const customErrors = metrics.errors?.values || {};

    const totalRequests = httpReqs.count || 0;
    const failedRequests = httpFailed.count || 0;
    const errorRate = failedRequests / Math.max(totalRequests, 1);

    console.log('\nError Rate Analysis:');
    console.log(`  Total Requests: ${totalRequests.toLocaleString()}`);
    console.log(`  Failed Requests: ${failedRequests.toLocaleString()}`);
    console.log(`  Error Rate: ${(errorRate * 100).toFixed(2)}% (Target: < ${THRESHOLDS.errorRate * 100}%)`);

    if (errorRate > THRESHOLDS.errorRate) {
      this.addBottleneck(
        SEVERITY.CRITICAL,
        'Error Rate',
        `Error rate (${(errorRate * 100).toFixed(2)}%) exceeds threshold (${THRESHOLDS.errorRate * 100}%)`,
        [
          'Review error logs for patterns',
          'Implement retry logic with exponential backoff',
          'Check database connection pool saturation',
          'Monitor for timeout errors',
          'Implement graceful degradation',
        ]
      );
    }

    // Check database connection errors
    const dbErrors = metrics.db_connection_errors?.values || {};
    if ((dbErrors.count || 0) > 100) {
      this.addBottleneck(
        SEVERITY.HIGH,
        'Database Connections',
        `High number of database connection errors (${dbErrors.count})`,
        [
          'Increase database connection pool size',
          'Implement connection health checks',
          'Add connection retry logic',
          'Consider database scaling (vertical or horizontal)',
          'Review connection timeout settings',
        ]
      );
    }
  }

  /**
   * Analyze throughput
   */
  analyzeThroughput(metrics) {
    const httpReqs = metrics.http_reqs?.values || {};
    const duration = this.k6Results.state?.testRunDurationMs || 1;
    const rps = (httpReqs.count || 0) / (duration / 1000);

    console.log('\nThroughput Analysis:');
    console.log(`  Total Requests: ${httpReqs.count?.toLocaleString()}`);
    console.log(`  Test Duration: ${(duration / 60000).toFixed(2)} minutes`);
    console.log(`  Throughput: ${rps.toFixed(2)} req/s (Target: > ${THRESHOLDS.throughput} req/s)`);

    if (rps < THRESHOLDS.throughput) {
      this.addBottleneck(
        SEVERITY.HIGH,
        'Throughput',
        `Throughput (${rps.toFixed(2)} req/s) is below target (${THRESHOLDS.throughput} req/s)`,
        [
          'Scale horizontally (add more backend instances)',
          'Optimize request handler performance',
          'Review load balancer configuration',
          'Implement connection pooling',
          'Consider CDN for static assets',
          'Optimize database query performance',
        ]
      );
    }
  }

  /**
   * Analyze custom metrics
   */
  analyzeCustomMetrics(metrics) {
    console.log('\nCustom Metrics Analysis:');

    // Slow requests
    const slowRequests = metrics.slow_requests?.values || {};
    const totalRequests = metrics.http_reqs?.values?.count || 1;
    const slowRequestRate = (slowRequests.count || 0) / totalRequests;

    console.log(`  Slow Requests: ${slowRequests.count || 0} (${(slowRequestRate * 100).toFixed(2)}%)`);

    if (slowRequestRate > 0.05) {
      this.addBottleneck(
        SEVERITY.MEDIUM,
        'Slow Requests',
        `High rate of slow requests (${(slowRequestRate * 100).toFixed(2)}%)`,
        [
          'Identify slow endpoints with profiling',
          'Add endpoint-specific timeouts',
          'Implement query caching',
          'Optimize database queries',
        ]
      );
    }

    // Cache hit rate
    const cacheHit = metrics.cache_hit_rate?.values || {};
    const cacheHitRate = cacheHit.rate || 0;

    console.log(`  Cache Hit Rate: ${(cacheHitRate * 100).toFixed(2)}% (Target: > ${THRESHOLDS.cacheHitRate * 100}%)`);

    if (cacheHitRate < THRESHOLDS.cacheHitRate) {
      this.addBottleneck(
        SEVERITY.MEDIUM,
        'Cache Performance',
        `Cache hit rate (${(cacheHitRate * 100).toFixed(2)}%) is below target (${THRESHOLDS.cacheHitRate * 100}%)`,
        [
          'Review cache key strategy',
          'Increase cache TTL for stable data',
          'Implement cache warming on startup',
          'Add cache preloading for common queries',
          'Consider Redis cluster for cache scaling',
        ]
      );
    }
  }

  /**
   * Analyze system monitoring data
   */
  analyzeMonitoringData() {
    console.log('\nAnalyzing system monitoring data...');

    this.analyzeCPU();
    this.analyzeMemory();
    this.analyzeDatabase();
    this.analyzeRedis();
    this.analyzeNetwork();
  }

  /**
   * Analyze CPU usage
   */
  analyzeCPU() {
    if (this.monitoringData.cpu.length === 0) return;

    console.log('\nCPU Usage Analysis:');

    const cpuUsage = this.monitoringData.cpu.map(row => ({
      timestamp: parseInt(row.timestamp),
      user: parseFloat(row.cpu_user),
      system: parseFloat(row.cpu_system),
      idle: parseFloat(row.cpu_idle),
      iowait: parseFloat(row.cpu_iowait),
    }));

    const avgUser = cpuUsage.reduce((sum, d) => sum + d.user, 0) / cpuUsage.length;
    const avgSystem = cpuUsage.reduce((sum, d) => sum + d.system, 0) / cpuUsage.length;
    const avgIdle = cpuUsage.reduce((sum, d) => sum + d.idle, 0) / cpuUsage.length;
    const avgIoWait = cpuUsage.reduce((sum, d) => sum + d.iowait, 0) / cpuUsage.length;
    const maxUsage = Math.max(...cpuUsage.map(d => 100 - d.idle));

    console.log(`  Average User CPU: ${avgUser.toFixed(2)}%`);
    console.log(`  Average System CPU: ${avgSystem.toFixed(2)}%`);
    console.log(`  Average Idle CPU: ${avgIdle.toFixed(2)}%`);
    console.log(`  Average IO Wait: ${avgIoWait.toFixed(2)}%`);
    console.log(`  Peak CPU Usage: ${maxUsage.toFixed(2)}%`);

    if (maxUsage > THRESHOLDS.cpuUsage) {
      this.addBottleneck(
        SEVERITY.HIGH,
        'CPU Usage',
        `Peak CPU usage (${maxUsage.toFixed(2)}%) exceeds threshold (${THRESHOLDS.cpuUsage}%)`,
        [
          'Scale horizontally (add more CPU cores)',
          'Profile CPU usage to identify hot code paths',
          'Optimize compute-intensive operations',
          'Consider caching for expensive computations',
          'Review goroutine/thread pool sizing',
        ]
      );
    }

    if (avgIoWait > 20) {
      this.addBottleneck(
        SEVERITY.MEDIUM,
        'I/O Wait',
        `High I/O wait time (${avgIoWait.toFixed(2)}%)`,
        [
          'Optimize disk I/O operations',
          'Use SSD storage for database',
          'Implement connection pooling',
          'Review database query patterns',
          'Consider read replicas',
        ]
      );
    }
  }

  /**
   * Analyze memory usage
   */
  analyzeMemory() {
    if (this.monitoringData.memory.length === 0) return;

    console.log('\nMemory Usage Analysis:');

    const memUsage = this.monitoringData.memory.map(row => ({
      timestamp: parseInt(row.timestamp),
      total: parseFloat(row.total_mb),
      used: parseFloat(row.used_mb),
      free: parseFloat(row.free_mb),
      available: parseFloat(row.available_mb),
      usagePercent: parseFloat(row.usage_percent),
    }));

    const avgUsage = memUsage.reduce((sum, d) => sum + d.usagePercent, 0) / memUsage.length;
    const maxUsage = Math.max(...memUsage.map(d => d.usagePercent));

    console.log(`  Average Memory Usage: ${avgUsage.toFixed(2)}%`);
    console.log(`  Peak Memory Usage: ${maxUsage.toFixed(2)}%`);

    if (maxUsage > THRESHOLDS.memoryUsage) {
      this.addBottleneck(
        SEVERITY.HIGH,
        'Memory Usage',
        `Peak memory usage (${maxUsage.toFixed(2)}%) exceeds threshold (${THRESHOLDS.memoryUsage}%)`,
        [
          'Increase available memory',
          'Profile memory usage for leaks',
          'Review cache TTL and size limits',
          'Implement memory-efficient data structures',
          'Consider memory pooling',
        ]
      );
    }
  }

  /**
   * Analyze database performance
   */
  analyzeDatabase() {
    if (this.monitoringData.database.length === 0) return;

    console.log('\nDatabase Analysis:');

    const dbData = this.monitoringData.database.map(row => ({
      timestamp: parseInt(row.timestamp),
      total: parseFloat(row.connections),
      active: parseFloat(row.active_connections),
      idle: parseFloat(row.idle_connections),
      waiting: parseFloat(row.waiting_connections),
    }));

    const avgActive = dbData.reduce((sum, d) => sum + d.active, 0) / dbData.length;
    const maxActive = Math.max(...dbData.map(d => d.active));
    const maxWaiting = Math.max(...dbData.map(d => d.waiting));

    console.log(`  Average Active Connections: ${avgActive.toFixed(2)}`);
    console.log(`  Peak Active Connections: ${maxActive.toFixed(2)}`);
    console.log(`  Peak Waiting Connections: ${maxWaiting.toFixed(2)}`);

    if (maxActive > THRESHOLDS.dbConnections) {
      this.addBottleneck(
        SEVERITY.HIGH,
        'Database Connections',
        `Peak active connections (${maxActive}) exceeds threshold (${THRESHOLDS.dbConnections})`,
        [
          'Increase database connection pool size',
          'Optimize query execution time',
          'Implement connection pooling at application level',
          'Consider database scaling (vertical or horizontal)',
          'Review long-running transactions',
        ]
      );
    }

    if (maxWaiting > 10) {
      this.addBottleneck(
        SEVERITY.MEDIUM,
        'Database Connection Pool',
        `High number of waiting connections (${maxWaiting})`,
        [
          'Increase connection pool size',
          'Reduce query execution time',
          'Implement query timeout',
          'Review connection pool configuration',
        ]
      );
    }
  }

  /**
   * Analyze Redis performance
   */
  analyzeRedis() {
    if (this.monitoringData.redis.length === 0) return;

    console.log('\nRedis Analysis:');

    const redisData = this.monitoringData.redis.map(row => ({
      timestamp: parseInt(row.timestamp),
      clients: parseFloat(row.connected_clients),
      memory: parseFloat(row.used_memory_mb),
      hits: parseFloat(row.keyspace_hits),
      misses: parseFloat(row.keyspace_misses),
      hitRate: parseFloat(row.hit_rate),
    }));

    const avgClients = redisData.reduce((sum, d) => sum + d.clients, 0) / redisData.length;
    const avgMemory = redisData.reduce((sum, d) => sum + d.memory, 0) / redisData.length;
    const avgHitRate = redisData.reduce((sum, d) => sum + d.hitRate, 0) / redisData.length;

    console.log(`  Average Connected Clients: ${avgClients.toFixed(2)}`);
    console.log(`  Average Memory Usage: ${avgMemory.toFixed(2)} MB`);
    console.log(`  Average Cache Hit Rate: ${(avgHitRate * 100).toFixed(2)}%`);

    if (avgHitRate < THRESHOLDS.cacheHitRate) {
      this.addBottleneck(
        SEVERITY.MEDIUM,
        'Redis Cache',
        `Low cache hit rate (${(avgHitRate * 100).toFixed(2)}%)`,
        [
          'Review cache key strategy',
          'Increase cache TTL',
          'Implement cache warming',
          'Optimize cache key patterns',
        ]
      );
    }
  }

  /**
   * Analyze network traffic
   */
  analyzeNetwork() {
    if (this.monitoringData.network.length === 0) return;

    console.log('\nNetwork Analysis:');

    const netData = this.monitoringData.network.map(row => ({
      timestamp: parseInt(row.timestamp),
      rxBytes: parseFloat(row.rx_bytes),
      txBytes: parseFloat(row.tx_bytes),
    }));

    const totalRx = netData[netData.length - 1]?.rxBytes - netData[0]?.rxBytes;
    const totalTx = netData[netData.length - 1]?.txBytes - netData[0]?.txBytes;

    console.log(`  Total Data Received: ${(totalRx / 1024 / 1024).toFixed(2)} MB`);
    console.log(`  Total Data Transmitted: ${(totalTx / 1024 / 1024).toFixed(2)} MB`);
  }

  /**
   * Add a bottleneck
   */
  addBottleneck(severity, category, description, recommendations) {
    this.bottlenecks.push({
      severity,
      category,
      description,
      recommendations,
    });
  }

  /**
   * Generate report
   */
  generateReport() {
    console.log('\n\n');
    console.log('═'.repeat(80));
    console.log('  BOTTLENECK ANALYSIS AND OPTIMIZATION RECOMMENDATIONS');
    console.log('═'.repeat(80));
    console.log('');

    if (this.bottlenecks.length === 0) {
      console.log('✓ No critical bottlenecks detected');
      console.log('✓ System is performing within acceptable parameters');
      return;
    }

    // Group bottlenecks by severity
    const bySeverity = {
      [SEVERITY.CRITICAL]: [],
      [SEVERITY.HIGH]: [],
      [SEVERITY.MEDIUM]: [],
      [SEVERITY.LOW]: [],
      [SEVERITY.INFO]: [],
    };

    this.bottlenecks.forEach(b => bySeverity[b.severity].push(b));

    // Display bottlenecks
    for (const severity of Object.keys(bySeverity)) {
      const items = bySeverity[severity];
      if (items.length === 0) continue;

      console.log('');
      console.log(`${severity} ISSUES (${items.length}):`);
      console.log('-'.repeat(80));

      items.forEach((item, index) => {
        console.log('');
        console.log(`${index + 1}. [${item.category}] ${item.description}`);
        console.log('');
        console.log('   Recommendations:');
        item.recommendations.forEach(rec => {
          console.log(`   • ${rec}`);
        });
      });
    }

    console.log('');
    console.log('═'.repeat(80));
    console.log('');

    // Save report to file
    const reportPath = path.join(this.resultsDir, 'bottleneck-analysis.txt');
    const reportContent = this.formatReportForFile();
    fs.writeFileSync(reportPath, reportContent);
    console.log(`Report saved to: ${reportPath}`);
  }

  /**
   * Format report for file output
   */
  formatReportForFile() {
    let content = `
╔══════════════════════════════════════════════════════════════════════════════╗
║              10K CONCURRENT USERS - BOTTLENECK ANALYSIS REPORT               ║
╚══════════════════════════════════════════════════════════════════════════════╝

Generated: ${new Date().toISOString()}
Results Directory: ${this.resultsDir}

`;

    if (this.bottlenecks.length === 0) {
      content += '✓ No critical bottlenecks detected\n';
      content += '✓ System is performing within acceptable parameters\n';
      return content;
    }

    // Group by severity
    const bySeverity = {
      [SEVERITY.CRITICAL]: [],
      [SEVERITY.HIGH]: [],
      [SEVERITY.MEDIUM]: [],
      [SEVERITY.LOW]: [],
      [SEVERITY.INFO]: [],
    };

    this.bottlenecks.forEach(b => bySeverity[b.severity].push(b));

    // Add bottlenecks to report
    for (const severity of Object.keys(bySeverity)) {
      const items = bySeverity[severity];
      if (items.length === 0) continue;

      content += `\n${severity} ISSUES (${items.length}):\n`;
      content += '─'.repeat(80) + '\n';

      items.forEach((item, index) => {
        content += `\n${index + 1}. [${item.category}] ${item.description}\n\n`;
        content += '   Recommendations:\n';
        item.recommendations.forEach(rec => {
          content += `   • ${rec}\n`;
        });
      });
    }

    content += '\n' + '═'.repeat(80) + '\n';

    return content;
  }

  /**
   * Run the analyzer
   */
  async run() {
    console.log('═'.repeat(80));
    console.log('  Performance Results Analyzer - 10k Concurrent Users Load Test');
    console.log('═'.repeat(80));
    console.log('');

    // Load data
    const k6Loaded = this.loadK6Results();
    const monitoringLoaded = this.loadMonitoringData();

    if (!k6Loaded && !monitoringLoaded) {
      console.error('No test results found. Please run the load test first.');
      process.exit(1);
    }

    // Analyze
    if (k6Loaded) {
      this.analyzeK6Metrics();
    }

    if (monitoringLoaded) {
      this.analyzeMonitoringData();
    }

    // Generate report
    this.generateReport();
  }
}

// Main execution
if (require.main === module) {
  const analyzer = new PerformanceAnalyzer(RESULTS_DIR);
  analyzer.run().catch(error => {
    console.error('Analysis failed:', error);
    process.exit(1);
  });
}

module.exports = PerformanceAnalyzer;
