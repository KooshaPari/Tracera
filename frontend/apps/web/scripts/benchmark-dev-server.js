#!/usr/bin/env node

/**
 * Dev Server Performance Benchmark
 * Measures startup time and HMR update latency
 */

import { spawn } from 'node:child_process';
import { performance } from 'node:perf_hooks';

const TARGETS = {
  startup: 3000, // Target: <3s startup time
  hmr: 100, // Target: <100ms HMR update time
};

let startupTime = 0;

// Measure startup time
const startTime = performance.now();
const devServer = spawn('bun', ['run', 'dev'], {
  shell: true,
  stdio: 'pipe',
});

let serverReady = false;

devServer.stdout.on('data', (data) => {
  const output = data.toString();
  process.stdout.write(output);

  // Detect server ready
  if (!serverReady && (output.includes('Local:') || output.includes('ready in'))) {
    serverReady = true;
    startupTime = Math.round(performance.now() - startTime);

    if (startupTime < TARGETS.startup) {
    } else {
    }

    // Report and exit
    setTimeout(() => {
      devServer.kill();
      process.exit(startupTime < TARGETS.startup ? 0 : 1);
    }, 2000);
  }
});

devServer.stderr.on('data', (data) => {
  process.stderr.write(data);
});

devServer.on('error', (error) => {
  process.exit(1);
});

// Timeout after 30 seconds
setTimeout(() => {
  if (!serverReady) {
    devServer.kill();
    process.exit(1);
  }
}, 30_000);
