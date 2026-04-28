import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { htmlReport } from 'https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// Memory leak detection specific metrics
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');
const memoryUsageMB = new Gauge('memory_usage_mb');
const memoryGrowthRate = new Gauge('memory_growth_rate_mb_per_hour');
const heapUsageMB = new Gauge('heap_usage_mb');
const connectionPoolSize = new Gauge('connection_pool_size');
const cacheSize = new Gauge('cache_size_mb');
const cacheEntries = new Gauge('cache_entries_count');
const activeQueries = new Gauge('active_queries');
const memoryLeakDetected = new Counter('memory_leak_detected');
const oomWarnings = new Counter('oom_warnings');

// Memory leak detection test - 12 hour focused test
export const options = {
  scenarios: {
    memory_leak_detection: {
      executor: 'constant-vus',
      vus: 25,
      duration: '12h',
      gracefulStop: '5m',
    },
  },
  thresholds: {
    // Memory growth thresholds
    memory_growth_rate_mb_per_hour: ['value<50'], // Should not grow more than 50MB/hour
    memory_usage_mb: ['value<2048'],              // Should stay under 2GB
    heap_usage_mb: ['value<1536'],                // Heap should stay under 1.5GB
    // Cache should stabilize
    cache_size_mb: ['value<512'],                 // Cache should not exceed 512MB
    cache_entries_count: ['value<100000'],        // Cache entries should stabilize
    // Connection pool should be stable
    connection_pool_size: ['value<80'],           // Should not grow indefinitely
    active_queries: ['value<50'],                 // Active queries should stay low
    // Leak detection
    memory_leak_detected: ['count<5'],            // Should not detect leaks
    oom_warnings: ['count<1'],                    // No OOM warnings
    // Performance should remain stable
    http_req_duration: ['p(95)<800'],
    http_req_failed: ['rate<0.02'],
  },
  timeout: '120s',
  noConnectionReuse: false,
  userAgent: 'k6-soak-test/memory-leak-detection',
};

// Environment configuration
const BASE_URL = __ENV.API_URL || 'http://localhost:3030';
const PROJECT_ID = __ENV.PROJECT_ID || 'memory-leak-test';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';
const MONITORING_ENDPOINT = __ENV.MONITORING_ENDPOINT || '';

// Memory tracking state
let iterationCount = 0;
let memoryMeasurements = [];
let lastMemoryCheck = Date.now();
const MEMORY_CHECK_INTERVAL = 60000; // Check every 1 minute
const LEAK_DETECTION_WINDOW = 10;     // Use last 10 measurements for trend

function getHeaders(includeAuth = true) {
  const headers = {
    'Content-Type': 'application/json',
    'X-Test-Type': 'memory-leak-detection',
    'X-Test-Iteration': iterationCount.toString(),
  };
  if (includeAuth && AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  return headers;
}

export function setup() {
  console.log('🔍 Starting Memory Leak Detection Test');
  console.log(`Target URL: ${BASE_URL}`);
  console.log(`Duration: 12 hours`);
  console.log(`Start time: ${new Date().toISOString()}`);
  console.log('Monitoring for memory growth patterns...');

  // Get baseline memory
  if (MONITORING_ENDPOINT) {
    const health = http.get(MONITORING_ENDPOINT);
    if (health.status === 200) {
      const metrics = JSON.parse(health.body);
      console.log(`Baseline memory: ${metrics.memory_usage_mb}MB`);
      console.log(`Baseline heap: ${metrics.heap_usage_mb}MB`);
      console.log(`Baseline connections: ${metrics.connection_pool_size}`);
    }
  }

  return {
    startTime: Date.now(),
    baselineMemory: 0,
  };
}

export default function(data) {
  iterationCount++;
  const currentTime = Date.now();

  // Frequent memory monitoring
  if (currentTime - lastMemoryCheck > MEMORY_CHECK_INTERVAL) {
    checkMemoryUsage(data);
    lastMemoryCheck = currentTime;
  }

  // Execute workload designed to expose memory leaks
  const scenario = Math.random();

  if (scenario < 0.25) {
    // 25% - Repeated list operations (cache stress)
    testRepeatedListOperations();
  } else if (scenario < 0.45) {
    // 20% - Large result sets (memory allocation)
    testLargeResultSets();
  } else if (scenario < 0.60) {
    // 15% - Graph operations (complex object graphs)
    testGraphOperations();
  } else if (scenario < 0.75) {
    // 15% - Search with various queries (search index stress)
    testSearchVariations();
  } else if (scenario < 0.85) {
    // 10% - Create and delete cycles (allocation churn)
    testCreateDeleteCycle();
  } else if (scenario < 0.95) {
    // 10% - Connection stress (pool management)
    testConnectionStress();
  } else {
    // 5% - Complex nested queries (deep object trees)
    testComplexNestedQueries();
  }

  // Variable sleep to create realistic load pattern
  sleep(0.5 + Math.random() * 2);
}

function testRepeatedListOperations() {
  group('Repeated List Operations', function() {
    // Same query multiple times - should use cache, not accumulate
    const url = `${BASE_URL}/api/v1/items?project_id=${PROJECT_ID}&limit=100&offset=0`;

    for (let i = 0; i < 3; i++) {
      const res = http.get(url, {
        headers: getHeaders(),
        tags: { operation: 'repeated_list' },
      });

      check(res, {
        'repeated list status is 200': (r) => r.status === 200,
      });

      if (i < 2) sleep(0.1);
    }
  });
}

function testLargeResultSets() {
  group('Large Result Sets', function() {
    // Request large result sets to test memory allocation
    const limit = 100 + Math.floor(Math.random() * 100); // 100-200 items
    const url = `${BASE_URL}/api/v1/items?project_id=${PROJECT_ID}&limit=${limit}&offset=0`;

    const res = http.get(url, {
      headers: getHeaders(),
      tags: { operation: 'large_results' },
    });

    check(res, {
      'large results status is 200': (r) => r.status === 200,
      'large results duration < 1000ms': (r) => r.timings.duration < 1000,
    });
  });
}

function testGraphOperations() {
  group('Graph Operations', function() {
    // Complex graph queries that create temporary object graphs
    const itemId = `item-${Math.floor(Math.random() * 500)}`;
    const depth = 3 + Math.floor(Math.random() * 3); // 3-5 levels

    // Test ancestors
    const ancestorsUrl = `${BASE_URL}/api/v1/graph/ancestors/${itemId}?depth=${depth}`;
    const ancestorsRes = http.get(ancestorsUrl, {
      headers: getHeaders(),
      tags: { operation: 'graph_ancestors' },
    });

    check(ancestorsRes, {
      'ancestors status is 200 or 404': (r) => r.status === 200 || r.status === 404,
    });

    sleep(0.2);

    // Test descendants
    const descendantsUrl = `${BASE_URL}/api/v1/graph/descendants/${itemId}?depth=${depth}`;
    const descendantsRes = http.get(descendantsUrl, {
      headers: getHeaders(),
      tags: { operation: 'graph_descendants' },
    });

    check(descendantsRes, {
      'descendants status is 200 or 404': (r) => r.status === 200 || r.status === 404,
    });
  });
}

function testSearchVariations() {
  group('Search Variations', function() {
    // Different search queries to stress search index and cache
    const queries = [
      'test',
      'feature',
      'bug',
      'task',
      'requirement',
      'user story',
      'integration test',
      'performance optimization',
    ];

    const query = queries[Math.floor(Math.random() * queries.length)];
    const searchQuery = {
      query: query,
      project_id: PROJECT_ID,
      limit: 50,
    };

    const url = `${BASE_URL}/api/v1/search`;
    const res = http.post(url, JSON.stringify(searchQuery), {
      headers: getHeaders(),
      tags: { operation: 'search_variations' },
    });

    check(res, {
      'search status is 200': (r) => r.status === 200,
    });
  });
}

function testCreateDeleteCycle() {
  group('Create-Delete Cycle', function() {
    // Create item
    const newItem = {
      project_id: PROJECT_ID,
      title: `Leak Test Item ${Date.now()}-${iterationCount}`,
      description: 'Testing memory allocation and deallocation',
      type: 'task',
      status: 'todo',
    };

    const createRes = http.post(`${BASE_URL}/api/v1/items`, JSON.stringify(newItem), {
      headers: getHeaders(),
      tags: { operation: 'create_for_delete' },
    });

    if (createRes.status === 201) {
      try {
        const created = JSON.parse(createRes.body);
        const itemId = created.id;

        sleep(0.5);

        // Delete item
        const deleteRes = http.del(`${BASE_URL}/api/v1/items/${itemId}`, null, {
          headers: getHeaders(),
          tags: { operation: 'delete_created' },
        });

        check(deleteRes, {
          'delete status is 200 or 204': (r) => r.status === 200 || r.status === 204,
        });
      } catch (e) {
        // Item creation might have failed
      }
    }
  });
}

function testConnectionStress() {
  group('Connection Stress', function() {
    // Multiple rapid requests to stress connection pool
    const requests = [];
    for (let i = 0; i < 5; i++) {
      requests.push({
        method: 'GET',
        url: `${BASE_URL}/api/v1/items?project_id=${PROJECT_ID}&limit=10&offset=${i * 10}`,
        params: {
          headers: getHeaders(),
          tags: { operation: 'connection_stress' },
        },
      });
    }

    const responses = http.batch(requests);
    check(responses, {
      'all requests succeeded': (rs) => rs.every(r => r.status === 200),
    });
  });
}

function testComplexNestedQueries() {
  group('Complex Nested Queries', function() {
    // Query with complex filters and includes
    const url = `${BASE_URL}/api/v1/items?project_id=${PROJECT_ID}&limit=50&include=links,metadata,tags&filter_type=task&filter_status=in_progress`;

    const res = http.get(url, {
      headers: getHeaders(),
      tags: { operation: 'complex_nested' },
    });

    check(res, {
      'complex query status is 200': (r) => r.status === 200,
    });
  });
}

function checkMemoryUsage(data) {
  if (!MONITORING_ENDPOINT) return;

  group('Memory Check', function() {
    const res = http.get(MONITORING_ENDPOINT, {
      tags: { operation: 'memory_check' },
      timeout: '30s',
    });

    if (res.status === 200) {
      try {
        const metrics = JSON.parse(res.body);
        const elapsedHours = ((Date.now() - data.startTime) / 3600000).toFixed(2);

        // Record current measurements
        memoryUsageMB.add(metrics.memory_usage_mb || 0);
        heapUsageMB.add(metrics.heap_usage_mb || 0);
        connectionPoolSize.add(metrics.connection_pool_size || 0);
        cacheSize.add(metrics.cache_size_mb || 0);
        cacheEntries.add(metrics.cache_entries || 0);
        activeQueries.add(metrics.active_queries || 0);

        // Store measurement for trend analysis
        memoryMeasurements.push({
          timestamp: Date.now(),
          memory: metrics.memory_usage_mb,
          heap: metrics.heap_usage_mb,
        });

        // Keep only recent measurements
        if (memoryMeasurements.length > 60) {
          memoryMeasurements.shift();
        }

        // Set baseline
        if (data.baselineMemory === 0) {
          data.baselineMemory = metrics.memory_usage_mb;
        }

        // Detect memory leaks using linear regression
        if (memoryMeasurements.length >= LEAK_DETECTION_WINDOW) {
          const growthRate = calculateMemoryGrowthRate();
          memoryGrowthRate.add(growthRate);

          // Leak detection threshold: >20MB/hour sustained growth
          if (growthRate > 20) {
            memoryLeakDetected.add(1);
            console.warn(`🚨 MEMORY LEAK DETECTED: Growth rate ${growthRate.toFixed(2)}MB/hour at ${elapsedHours}h`);
            console.warn(`   Current: ${metrics.memory_usage_mb}MB, Baseline: ${data.baselineMemory}MB`);
          }
        }

        // OOM warning
        if (metrics.memory_usage_mb > 1800) { // Approaching 2GB limit
          oomWarnings.add(1);
          console.error(`🔴 OOM WARNING: Memory at ${metrics.memory_usage_mb}MB (${elapsedHours}h)`);
        }

        // Periodic detailed report
        if (memoryMeasurements.length % 10 === 0) {
          console.log(`📊 [${elapsedHours}h] Memory: ${metrics.memory_usage_mb}MB (+${(metrics.memory_usage_mb - data.baselineMemory).toFixed(2)}MB), Heap: ${metrics.heap_usage_mb}MB, Cache: ${metrics.cache_size_mb}MB (${metrics.cache_entries} entries), Connections: ${metrics.connection_pool_size}`);
        }

      } catch (e) {
        console.error(`Memory check error: ${e.message}`);
      }
    }
  });
}

function calculateMemoryGrowthRate() {
  if (memoryMeasurements.length < LEAK_DETECTION_WINDOW) {
    return 0;
  }

  // Use last N measurements for linear regression
  const recentMeasurements = memoryMeasurements.slice(-LEAK_DETECTION_WINDOW);

  // Simple linear regression to calculate growth rate
  const n = recentMeasurements.length;
  let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;

  for (let i = 0; i < n; i++) {
    const x = i;
    const y = recentMeasurements[i].memory;
    sumX += x;
    sumY += y;
    sumXY += x * y;
    sumX2 += x * x;
  }

  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);

  // Convert slope (MB per measurement) to MB per hour
  // Measurements are 1 minute apart
  const growthRatePerHour = slope * 60;

  return growthRatePerHour;
}

export function teardown(data) {
  const endTime = Date.now();
  const duration = endTime - data.startTime;
  const durationHours = (duration / 3600000).toFixed(2);

  console.log('✅ Memory Leak Detection Test Completed');
  console.log(`Duration: ${durationHours} hours`);
  console.log(`Memory measurements collected: ${memoryMeasurements.length}`);

  if (MONITORING_ENDPOINT) {
    const health = http.get(MONITORING_ENDPOINT);
    if (health.status === 200) {
      const metrics = JSON.parse(health.body);
      const memoryGrowth = metrics.memory_usage_mb - data.baselineMemory;
      const growthPercent = ((memoryGrowth / data.baselineMemory) * 100).toFixed(2);

      console.log('\n=== Final Memory Analysis ===');
      console.log(`Baseline memory: ${data.baselineMemory}MB`);
      console.log(`Final memory: ${metrics.memory_usage_mb}MB`);
      console.log(`Total growth: ${memoryGrowth.toFixed(2)}MB (${growthPercent}%)`);
      console.log(`Final heap: ${metrics.heap_usage_mb}MB`);
      console.log(`Final cache: ${metrics.cache_size_mb}MB (${metrics.cache_entries} entries)`);
      console.log(`Final connections: ${metrics.connection_pool_size}`);

      if (memoryGrowth > 100) {
        console.warn('⚠️  Significant memory growth detected - review for potential leaks');
      } else {
        console.log('✅ Memory usage appears stable');
      }
    }
  }
}

export function handleSummary(data) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

  // Include memory measurements in summary
  const enhancedData = {
    ...data,
    memoryMeasurements: memoryMeasurements,
  };

  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    [`soak-results/memory-leak-${timestamp}.json`]: JSON.stringify(enhancedData, null, 2),
    [`soak-results/memory-leak-${timestamp}.html`]: htmlReport(data),
    'soak-results/memory-leak-latest.json': JSON.stringify(enhancedData, null, 2),
  };
}
