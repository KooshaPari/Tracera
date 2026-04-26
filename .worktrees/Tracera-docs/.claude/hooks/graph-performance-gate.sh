#!/usr/bin/env bash
# Graph Performance Gate Hook
# Measures FPS, layout timing, and culling timing for 10k node render via Playwright.
# Exit codes: 0=pass, 1=fail (critical), 2=warn (regression)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

log() {
  printf '%s\n' "[graph-perf] $*"
}

die() {
  printf '%s\n' "[graph-perf] ERROR: $*" >&2
  exit 1
}

if ! command -v node >/dev/null 2>&1; then
  die "node is required but not found in PATH"
fi

if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
  die "frontend dependencies missing. Run 'cd frontend && bun install'"
fi

if [ ! -e "$ROOT_DIR/frontend/node_modules/playwright" ] && [ ! -e "$ROOT_DIR/frontend/node_modules/playwright-core" ]; then
  die "Playwright not installed. Run 'cd frontend && bun install'"
fi

PLAYWRIGHT_CHROMIUM_PATH=$(cd "$ROOT_DIR/frontend" && node -e "const { chromium } = require('playwright'); const fs = require('fs'); const p = chromium.executablePath(); if (p && fs.existsSync(p)) { console.log(p); }" 2>/dev/null || true)
if [ -z "$PLAYWRIGHT_CHROMIUM_PATH" ]; then
  die "Playwright Chromium not installed. Run 'cd frontend && bunx playwright install chromium'"
fi

BASELINE_FILE="${GRAPH_PERF_BASELINE_FILE:-$ROOT_DIR/.claude/perf-baselines/graph-performance-baseline.json}"
RESULT_FILE="${GRAPH_PERF_RESULT_FILE:-$ROOT_DIR/artifacts/performance/graph-performance-latest.json}"

MIN_FPS="${GRAPH_PERF_MIN_FPS:-60}"
MAX_LAYOUT_MS="${GRAPH_PERF_LAYOUT_MS:-100}"
MAX_CULLING_MS="${GRAPH_PERF_CULLING_MS:-50}"
NODE_COUNT="${GRAPH_PERF_NODE_COUNT:-10000}"
EDGE_COUNT="${GRAPH_PERF_EDGE_COUNT:-15000}"
DURATION_MS="${GRAPH_PERF_DURATION_MS:-2000}"
WARN_PCT="${GRAPH_PERF_WARN_PCT:-0.1}"
HEADLESS="${GRAPH_PERF_HEADLESS:-true}"

CURRENT_BRANCH="$(git -C "$ROOT_DIR" branch --show-current 2>/dev/null || true)"
UPDATE_BASELINE="${GRAPH_PERF_UPDATE_BASELINE:-}"
if [ "$CURRENT_BRANCH" = "main" ]; then
  UPDATE_BASELINE="1"
fi

log "Starting graph performance gate"
log "Nodes: ${NODE_COUNT} | Edges: ${EDGE_COUNT} | Duration: ${DURATION_MS}ms"

(cd "$ROOT_DIR/frontend" && \
  BASELINE_FILE="$BASELINE_FILE" \
  RESULT_FILE="$RESULT_FILE" \
  GRAPH_PERF_MIN_FPS="$MIN_FPS" \
  GRAPH_PERF_LAYOUT_MS="$MAX_LAYOUT_MS" \
  GRAPH_PERF_CULLING_MS="$MAX_CULLING_MS" \
  GRAPH_PERF_NODE_COUNT="$NODE_COUNT" \
  GRAPH_PERF_EDGE_COUNT="$EDGE_COUNT" \
  GRAPH_PERF_DURATION_MS="$DURATION_MS" \
  GRAPH_PERF_WARN_PCT="$WARN_PCT" \
  GRAPH_PERF_HEADLESS="$HEADLESS" \
  GRAPH_PERF_UPDATE_BASELINE="$UPDATE_BASELINE" \
  node --input-type=module <<'NODE'
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const log = (msg) => console.log(`[graph-perf] ${msg}`);
const error = (msg) => console.error(`[graph-perf] ERROR: ${msg}`);

const parseNumber = (value, fallback) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const baselineFile = process.env.BASELINE_FILE;
const resultFile = process.env.RESULT_FILE;

const minFps = parseNumber(process.env.GRAPH_PERF_MIN_FPS, 60);
const maxLayoutMs = parseNumber(process.env.GRAPH_PERF_LAYOUT_MS, 100);
const maxCullingMs = parseNumber(process.env.GRAPH_PERF_CULLING_MS, 50);
const nodeCount = parseNumber(process.env.GRAPH_PERF_NODE_COUNT, 10000);
const edgeCount = parseNumber(process.env.GRAPH_PERF_EDGE_COUNT, 15000);
const durationMs = parseNumber(process.env.GRAPH_PERF_DURATION_MS, 2000);
const warnPct = parseNumber(process.env.GRAPH_PERF_WARN_PCT, 0.1);
const headless = String(process.env.GRAPH_PERF_HEADLESS ?? 'true').toLowerCase() !== 'false';
const updateBaseline = String(process.env.GRAPH_PERF_UPDATE_BASELINE ?? '') === '1';

const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Graph Performance Gate</title>
  <style>
    html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #0b0f14; }
    canvas { display: block; width: 100%; height: 100%; }
  </style>
</head>
<body>
  <canvas id="graph"></canvas>
</body>
</html>`;

let browser;
try {
  browser = await chromium.launch({
    headless,
    args: ['--disable-dev-shm-usage'],
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  await page.setContent(html, { waitUntil: 'domcontentloaded' });

  const metrics = await page.evaluate(async ({ nodeCount, edgeCount, durationMs }) => {
    const canvas = document.getElementById('graph');
    if (!(canvas instanceof HTMLCanvasElement)) {
      throw new Error('Canvas not available');
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      throw new Error('Canvas 2D context not available');
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;

    const spacing = 50;
    const gridSize = Math.ceil(Math.sqrt(nodeCount));
    const graphWidth = gridSize * spacing;
    const graphHeight = gridSize * spacing;

    const layoutStart = performance.now();
    const nodes = new Array(nodeCount);
    for (let i = 0; i < nodeCount; i++) {
      const row = Math.floor(i / gridSize);
      const col = i - row * gridSize;
      nodes[i] = {
        x: col * spacing,
        y: row * spacing,
      };
    }

    const edges = new Array(edgeCount);
    for (let i = 0; i < edgeCount; i++) {
      const source = i % nodeCount;
      const target = (source + 13 + (i % 97)) % nodeCount;
      edges[i] = [source, target];
    }
    const layoutMs = performance.now() - layoutStart;

    let frameCount = 0;
    let cullingTotal = 0;
    let cullingSamples = 0;
    let visibleNodesTotal = 0;
    let visibleEdgesTotal = 0;

    const visibleFlags = new Uint8Array(nodeCount);

    const metrics = await new Promise((resolve) => {
      const start = performance.now();

      const drawFrame = () => {
        const now = performance.now();
        const t = now - start;

        const panX = ((Math.sin(t / 1200) + 1) / 2) * Math.max(graphWidth - width, 0);
        const panY = ((Math.cos(t / 1500) + 1) / 2) * Math.max(graphHeight - height, 0);

        const view = {
          minX: panX,
          minY: panY,
          maxX: panX + width,
          maxY: panY + height,
        };

        const cullStart = performance.now();
        visibleFlags.fill(0);
        let visibleCount = 0;
        for (let i = 0; i < nodes.length; i++) {
          const n = nodes[i];
          if (n.x >= view.minX && n.x <= view.maxX && n.y >= view.minY && n.y <= view.maxY) {
            visibleFlags[i] = 1;
            visibleCount++;
          }
        }

        let visibleEdgeCount = 0;
        for (let i = 0; i < edges.length; i++) {
          const [s, t2] = edges[i];
          if (visibleFlags[s] && visibleFlags[t2]) {
            visibleEdgeCount++;
          }
        }
        const cullMs = performance.now() - cullStart;
        cullingTotal += cullMs;
        cullingSamples++;
        visibleNodesTotal += visibleCount;
        visibleEdgesTotal += visibleEdgeCount;

        ctx.clearRect(0, 0, width, height);
        ctx.save();
        ctx.translate(-view.minX, -view.minY);

        ctx.strokeStyle = 'rgba(56, 189, 248, 0.25)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let i = 0; i < edges.length; i++) {
          const [s, t2] = edges[i];
          if (!visibleFlags[s] || !visibleFlags[t2]) {
            continue;
          }
          const a = nodes[s];
          const b = nodes[t2];
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
        }
        ctx.stroke();

        ctx.fillStyle = '#38bdf8';
        for (let i = 0; i < nodes.length; i++) {
          if (!visibleFlags[i]) {
            continue;
          }
          const n = nodes[i];
          ctx.beginPath();
          ctx.arc(n.x, n.y, 2, 0, Math.PI * 2);
          ctx.fill();
        }

        ctx.restore();

        frameCount++;
        if (t < durationMs) {
          requestAnimationFrame(drawFrame);
        } else {
          const fps = (frameCount * 1000) / Math.max(t, 1);
          resolve({
            avgVisibleEdges: visibleEdgesTotal / Math.max(cullingSamples, 1),
            avgVisibleNodes: visibleNodesTotal / Math.max(cullingSamples, 1),
            cullingMs: cullingTotal / Math.max(cullingSamples, 1),
            fps,
            layoutMs,
            totalEdges: edgeCount,
            totalNodes: nodeCount,
          });
        }
      };

      requestAnimationFrame(drawFrame);
    });

    return metrics;
  }, { nodeCount, edgeCount, durationMs });

  const environment = {
    devicePixelRatio: await page.evaluate(() => window.devicePixelRatio),
    headless,
    node: process.version,
    platform: process.platform,
    userAgent: await page.evaluate(() => navigator.userAgent),
    viewport: { width: 1280, height: 720 },
  };

  const result = {
    environment,
    metrics: {
      avgVisibleEdges: Number(metrics.avgVisibleEdges.toFixed(2)),
      avgVisibleNodes: Number(metrics.avgVisibleNodes.toFixed(2)),
      cullingMs: Number(metrics.cullingMs.toFixed(2)),
      edgeCount: metrics.totalEdges,
      fps: Number(metrics.fps.toFixed(2)),
      layoutMs: Number(metrics.layoutMs.toFixed(2)),
      nodeCount: metrics.totalNodes,
    },
    timestamp: new Date().toISOString(),
  };

  if (resultFile) {
    fs.mkdirSync(path.dirname(resultFile), { recursive: true });
    fs.writeFileSync(resultFile, JSON.stringify(result, null, 2));
    log(`Saved latest metrics to ${resultFile}`);
  }

  let baseline = null;
  if (baselineFile && fs.existsSync(baselineFile)) {
    baseline = JSON.parse(fs.readFileSync(baselineFile, 'utf8'));
  }

  if (!baseline && baselineFile) {
    fs.mkdirSync(path.dirname(baselineFile), { recursive: true });
    fs.writeFileSync(baselineFile, JSON.stringify(result, null, 2));
    log(`Baseline created at ${baselineFile}`);
  }

  const failures = [];
  const warnings = [];

  if (result.metrics.fps < minFps) {
    failures.push(`FPS ${result.metrics.fps} < ${minFps}`);
  }
  if (result.metrics.layoutMs > maxLayoutMs) {
    failures.push(`Layout ${result.metrics.layoutMs}ms > ${maxLayoutMs}ms`);
  }
  if (result.metrics.cullingMs > maxCullingMs) {
    failures.push(`Culling ${result.metrics.cullingMs}ms > ${maxCullingMs}ms`);
  }

  log(`FPS: ${result.metrics.fps} (min ${minFps})`);
  log(`Layout: ${result.metrics.layoutMs}ms (max ${maxLayoutMs}ms)`);
  log(`Culling: ${result.metrics.cullingMs}ms (max ${maxCullingMs}ms)`);

  if (baseline?.metrics) {
    const regress = (label, current, base, higherIsWorse) => {
      if (!Number.isFinite(current) || !Number.isFinite(base) || base === 0) {
        return;
      }
      const delta = current - base;
      const pct = Math.abs(delta / base);
      const isRegression = higherIsWorse ? delta > 0 : delta < 0;
      if (isRegression && pct >= warnPct) {
        warnings.push(
          `${label} regressed ${(pct * 100).toFixed(1)}% (baseline ${base} -> current ${current})`,
        );
      }
    };

    regress('FPS', result.metrics.fps, baseline.metrics.fps, false);
    regress('Layout', result.metrics.layoutMs, baseline.metrics.layoutMs, true);
    regress('Culling', result.metrics.cullingMs, baseline.metrics.cullingMs, true);

    log(
      `Baseline: FPS ${baseline.metrics.fps}, Layout ${baseline.metrics.layoutMs}ms, Culling ${baseline.metrics.cullingMs}ms`,
    );
  }

  let exitCode = 0;
  if (failures.length > 0) {
    log('Performance thresholds failed:');
    for (const failure of failures) {
      log(`  - ${failure}`);
    }
    exitCode = 1;
  } else if (warnings.length > 0) {
    log('Performance regressions detected:');
    for (const warning of warnings) {
      log(`  - ${warning}`);
    }
    exitCode = 2;
  }

  if (updateBaseline && exitCode === 0 && baselineFile) {
    fs.mkdirSync(path.dirname(baselineFile), { recursive: true });
    fs.writeFileSync(baselineFile, JSON.stringify(result, null, 2));
    log(`Baseline updated at ${baselineFile}`);
  }

  if (exitCode === 0) {
    log('Graph performance gate passed');
  }

  process.exitCode = exitCode;
  await page.close();
  await context.close();
} catch (err) {
  error(err instanceof Error ? err.message : String(err));
  process.exitCode = 1;
} finally {
  if (browser) {
    await browser.close();
  }
}
NODE
)

exit $?
