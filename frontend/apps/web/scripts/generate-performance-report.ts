/**
 * Performance Report Generator
 *
 * Generates HTML reports with charts and comparison tables from benchmark results
 */

import * as fs from 'node:fs/promises';
import * as path from 'node:path';

interface BenchmarkResults {
  timestamp: string;
  testEnvironment: {
    userAgent: string;
    viewport: { width: number; height: number };
    devicePixelRatio: number;
  };
  scenarios: {
    load10kGraph: any;
    continuousPan: any;
    zoomOperations: any;
    nodeSelection: any;
    lodTransitions: any;
  };
  summary: {
    overallScore: number;
    performanceGrade: string;
    readyForProduction: boolean;
    blockers: string[];
    recommendations: string[];
  };
}

/**
 * Generate HTML report from benchmark results
 */
async function generateHTMLReport(results: BenchmarkResults, outputPath: string): Promise<void> {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>10k Node Performance Baseline Report</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      color: #e8e8e8;
      padding: 2rem;
      line-height: 1.6;
    }
    .container { max-width: 1400px; margin: 0 auto; }
    .header {
      background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
      padding: 2rem;
      border-radius: 12px;
      margin-bottom: 2rem;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    h1 {
      color: #4ecca3;
      font-size: 2.5rem;
      margin-bottom: 0.5rem;
    }
    .timestamp {
      color: #94a3b8;
      font-size: 0.9rem;
    }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }
    .metric-card {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 1.5rem;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 30px rgba(78, 204, 163, 0.2);
    }
    .metric-label {
      color: #94a3b8;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 0.5rem;
    }
    .metric-value {
      font-size: 2rem;
      font-weight: 700;
      color: #4ecca3;
    }
    .metric-target {
      color: #64748b;
      font-size: 0.85rem;
      margin-top: 0.25rem;
    }
    .grade {
      font-size: 4rem;
      font-weight: 900;
      text-align: center;
      padding: 2rem;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.05);
      margin-bottom: 2rem;
    }
    .grade-A { color: #10b981; }
    .grade-B { color: #3b82f6; }
    .grade-C { color: #f59e0b; }
    .grade-D { color: #ef4444; }
    .grade-F { color: #dc2626; }
    .chart-container {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 2rem;
    }
    .comparison-table {
      width: 100%;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      overflow: hidden;
      margin-bottom: 2rem;
    }
    .comparison-table th,
    .comparison-table td {
      padding: 1rem;
      text-align: left;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .comparison-table th {
      background: rgba(78, 204, 163, 0.1);
      color: #4ecca3;
      font-weight: 600;
    }
    .status-pass { color: #10b981; }
    .status-fail { color: #ef4444; }
    .status-warn { color: #f59e0b; }
    .blockers, .recommendations {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 2rem;
    }
    .blockers h2 { color: #ef4444; }
    .recommendations h2 { color: #3b82f6; }
    .blockers ul, .recommendations ul {
      list-style: none;
      margin-top: 1rem;
    }
    .blockers li, .recommendations li {
      padding: 0.75rem;
      margin: 0.5rem 0;
      background: rgba(255, 255, 255, 0.05);
      border-left: 4px solid currentColor;
      border-radius: 4px;
    }
    .blockers li { border-color: #ef4444; }
    .recommendations li { border-color: #3b82f6; }
    .environment {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 2rem;
      font-size: 0.9rem;
      color: #94a3b8;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📊 10k Node Performance Baseline Report</h1>
      <p class="timestamp">Generated: ${new Date(results.timestamp).toLocaleString()}</p>
    </div>

    <div class="grade grade-${results.summary.performanceGrade}">
      ${results.summary.performanceGrade}
      <div style="font-size: 1rem; margin-top: 1rem; color: #94a3b8;">
        Overall Score: ${results.summary.overallScore}/100
      </div>
      <div style="font-size: 1rem; margin-top: 0.5rem;">
        ${results.summary.readyForProduction ? '✅ Production Ready' : '❌ Not Production Ready'}
      </div>
    </div>

    <div class="summary-grid">
      <div class="metric-card">
        <div class="metric-label">Initial Render Time</div>
        <div class="metric-value">${results.scenarios.load10kGraph.initialRenderTime}ms</div>
        <div class="metric-target">Target: &lt; 3000ms</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Pan FPS</div>
        <div class="metric-value">${results.scenarios.continuousPan.continuousPanFPS.toFixed(1)}</div>
        <div class="metric-target">Target: &gt; 30fps</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Zoom FPS</div>
        <div class="metric-value">${results.scenarios.zoomOperations.zoomFPS.toFixed(1)}</div>
        <div class="metric-target">Target: &gt; 30fps</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Node Selection</div>
        <div class="metric-value">${results.scenarios.nodeSelection.avgNodeSelectionTime.toFixed(0)}ms</div>
        <div class="metric-target">Target: &lt; 100ms</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Memory Usage</div>
        <div class="metric-value">${results.scenarios.load10kGraph.finalMemoryMB.toFixed(0)}MB</div>
        <div class="metric-target">Target: &lt; 500MB</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Culled Nodes</div>
        <div class="metric-value">${results.scenarios.load10kGraph.culledNodeCount}</div>
        <div class="metric-target">of ${results.scenarios.load10kGraph.totalNodes}</div>
      </div>
    </div>

    <div class="chart-container">
      <h2 style="margin-bottom: 1rem; color: #4ecca3;">Performance Metrics Comparison</h2>
      <canvas id="performanceChart"></canvas>
    </div>

    <div class="chart-container">
      <h2 style="margin-bottom: 1rem; color: #4ecca3;">Frame Rate Analysis</h2>
      <canvas id="fpsChart"></canvas>
    </div>

    <table class="comparison-table">
      <thead>
        <tr>
          <th>Metric</th>
          <th>Current</th>
          <th>Target (Phase 5-8)</th>
          <th>100k Goal</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Initial Render</td>
          <td>${results.scenarios.load10kGraph.initialRenderTime}ms</td>
          <td>&lt; 3000ms</td>
          <td>&lt; 5000ms</td>
          <td class="${results.scenarios.load10kGraph.initialRenderTime < 3000 ? 'status-pass' : 'status-fail'}">
            ${results.scenarios.load10kGraph.initialRenderTime < 3000 ? '✓ PASS' : '✗ FAIL'}
          </td>
        </tr>
        <tr>
          <td>Pan FPS</td>
          <td>${results.scenarios.continuousPan.continuousPanFPS.toFixed(1)} fps</td>
          <td>&gt; 30 fps</td>
          <td>&gt; 30 fps</td>
          <td class="${results.scenarios.continuousPan.continuousPanFPS > 30 ? 'status-pass' : 'status-warn'}">
            ${results.scenarios.continuousPan.continuousPanFPS > 30 ? '✓ PASS' : '⚠ WARN'}
          </td>
        </tr>
        <tr>
          <td>Zoom FPS</td>
          <td>${results.scenarios.zoomOperations.zoomFPS.toFixed(1)} fps</td>
          <td>&gt; 30 fps</td>
          <td>&gt; 30 fps</td>
          <td class="${results.scenarios.zoomOperations.zoomFPS > 30 ? 'status-pass' : 'status-warn'}">
            ${results.scenarios.zoomOperations.zoomFPS > 30 ? '✓ PASS' : '⚠ WARN'}
          </td>
        </tr>
        <tr>
          <td>Selection Time</td>
          <td>${results.scenarios.nodeSelection.avgNodeSelectionTime.toFixed(0)}ms</td>
          <td>&lt; 100ms</td>
          <td>&lt; 50ms</td>
          <td class="${results.scenarios.nodeSelection.avgNodeSelectionTime < 100 ? 'status-pass' : 'status-warn'}">
            ${results.scenarios.nodeSelection.avgNodeSelectionTime < 100 ? '✓ PASS' : '⚠ WARN'}
          </td>
        </tr>
        <tr>
          <td>Memory Usage</td>
          <td>${results.scenarios.load10kGraph.finalMemoryMB.toFixed(0)}MB</td>
          <td>&lt; 500MB</td>
          <td>&lt; 800MB</td>
          <td class="${results.scenarios.load10kGraph.finalMemoryMB < 500 ? 'status-pass' : 'status-warn'}">
            ${results.scenarios.load10kGraph.finalMemoryMB < 500 ? '✓ PASS' : '⚠ WARN'}
          </td>
        </tr>
        <tr>
          <td>LOD Transition</td>
          <td>${results.scenarios.lodTransitions.lodTransitionTime.toFixed(0)}ms</td>
          <td>&lt; 100ms</td>
          <td>&lt; 50ms</td>
          <td class="${results.scenarios.lodTransitions.lodTransitionTime < 100 ? 'status-pass' : 'status-warn'}">
            ${results.scenarios.lodTransitions.lodTransitionTime < 100 ? '✓ PASS' : '⚠ WARN'}
          </td>
        </tr>
      </tbody>
    </table>

    ${
      results.summary.blockers.length > 0
        ? `
    <div class="blockers">
      <h2>⚠️ Performance Blockers</h2>
      <ul>
        ${results.summary.blockers.map((b) => `<li>${b}</li>`).join('')}
      </ul>
    </div>
    `
        : ''
    }

    ${
      results.summary.recommendations.length > 0
        ? `
    <div class="recommendations">
      <h2>💡 Optimization Recommendations</h2>
      <ul>
        ${results.summary.recommendations.map((r) => `<li>${r}</li>`).join('')}
      </ul>
    </div>
    `
        : ''
    }

    <div class="environment">
      <h3 style="color: #4ecca3; margin-bottom: 1rem;">Test Environment</h3>
      <div><strong>Viewport:</strong> ${results.testEnvironment.viewport.width}x${results.testEnvironment.viewport.height}</div>
      <div><strong>Device Pixel Ratio:</strong> ${results.testEnvironment.devicePixelRatio}</div>
      <div><strong>User Agent:</strong> ${results.testEnvironment.userAgent}</div>
    </div>
  </div>

  <script>
    // Performance metrics chart
    const ctx1 = document.getElementById('performanceChart').getContext('2d');
    new Chart(ctx1, {
      type: 'bar',
      data: {
        labels: ['Render Time', 'Pan FPS', 'Zoom FPS', 'Selection', 'Memory'],
        datasets: [
          {
            label: 'Current',
            data: [
              ${results.scenarios.load10kGraph.initialRenderTime},
              ${results.scenarios.continuousPan.continuousPanFPS},
              ${results.scenarios.zoomOperations.zoomFPS},
              ${results.scenarios.nodeSelection.avgNodeSelectionTime},
              ${results.scenarios.load10kGraph.finalMemoryMB}
            ],
            backgroundColor: 'rgba(78, 204, 163, 0.8)',
          },
          {
            label: 'Target',
            data: [3000, 30, 30, 100, 500],
            backgroundColor: 'rgba(59, 130, 246, 0.5)',
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: '#e8e8e8' } },
          title: {
            display: true,
            text: 'Current vs Target Performance',
            color: '#4ecca3'
          }
        },
        scales: {
          y: {
            ticks: { color: '#94a3b8' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' }
          },
          x: {
            ticks: { color: '#94a3b8' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' }
          }
        }
      }
    });

    // FPS chart
    const ctx2 = document.getElementById('fpsChart').getContext('2d');
    new Chart(ctx2, {
      type: 'line',
      data: {
        labels: ['Pan', 'Zoom', 'Target'],
        datasets: [{
          label: 'FPS',
          data: [
            ${results.scenarios.continuousPan.continuousPanFPS},
            ${results.scenarios.zoomOperations.zoomFPS},
            30
          ],
          borderColor: 'rgba(78, 204, 163, 1)',
          backgroundColor: 'rgba(78, 204, 163, 0.2)',
          fill: true,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: '#e8e8e8' } },
          title: {
            display: true,
            text: 'Frame Rate Performance',
            color: '#4ecca3'
          }
        },
        scales: {
          y: {
            min: 0,
            max: 60,
            ticks: { color: '#94a3b8' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' }
          },
          x: {
            ticks: { color: '#94a3b8' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' }
          }
        }
      }
    });
  </script>
</body>
</html>`;

  await fs.writeFile(outputPath, html);
}

/**
 * Main execution
 */
async function main() {
  const resultsDir = path.join(__dirname, '../performance-results');

  try {
    // Find the most recent benchmark results
    const files = await fs.readdir(resultsDir);
    const jsonFiles = files.filter((f) => f.startsWith('10k-baseline-') && f.endsWith('.json'));

    if (jsonFiles.length === 0) {
      process.exit(1);
    }

    // Sort by timestamp and get the latest
    jsonFiles.sort();
    const latestFile = jsonFiles.at(-1);
    const resultsPath = path.join(resultsDir, latestFile);

    // Read results
    const resultsContent = await fs.readFile(resultsPath, 'utf8');
    const results: BenchmarkResults = JSON.parse(resultsContent);

    // Generate HTML report
    const reportPath = path.join(resultsDir, latestFile.replace('.json', '.html'));
    await generateHTMLReport(results, reportPath);
  } catch {
    process.exit(1);
  }
}

undefined;
