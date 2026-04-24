#!/usr/bin/env node

/**
 * Chromatic Snapshot Manager
 * Utilities for managing visual test baselines and snapshots
 *
 * Usage:
 *   bun scripts/chromatic-snapshot-manager.ts --help
 *   bun scripts/chromatic-snapshot-manager.ts --list-changed
 *   bun scripts/chromatic-snapshot-manager.ts --accept-all
 */

import { execSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';

interface SnapshotConfig {
  projectToken: string;
  components: {
    name: string;
    viewports: string[];
    themes: string[];
    states: string[];
  }[];
}

/**
 * Load snapshot configuration
 */
function loadConfig(): SnapshotConfig {
  const configPath = path.join(process.cwd(), 'chromatic.config.json');

  if (!existsSync(configPath)) {
    process.exit(1);
  }

  return JSON.parse(readFileSync(configPath, 'utf8'));
}

/**
 * List changed snapshots
 */
function listChangedSnapshots(): void {
  try {
    const output = execSync("chromatic --list-changes 2>&1 || echo ''", {
      encoding: 'utf8',
    });

    if (!output.trim()) {
      return;
    }
  } catch {}
}

/**
 * Accept all visual changes
 */
function acceptAllChanges(): void {
  try {
    execSync('chromatic --auto-accept-changes', {
      encoding: 'utf8',
      stdio: 'inherit',
    });
  } catch {
    process.exit(1);
  }
}

/**
 * Reject all visual changes
 */
function rejectAllChanges(): void {
  try {
    execSync('chromatic --exit-once-uploaded', {
      encoding: 'utf8',
      stdio: 'inherit',
    });
  } catch {
    process.exit(1);
  }
}

/**
 * Generate snapshot summary
 */
function generateSummary(): void {
  const config = loadConfig();
  let totalSnapshots = 0;

  config.components.forEach((component) => {
    const snapshotsPerComponent =
      component.viewports.length * component.themes.length * component.states.length;
    totalSnapshots += snapshotsPerComponent;
  });
}

/**
 * Validate Chromatic configuration
 */
function validateConfig(): void {
  const config = loadConfig();

  if (!config.projectToken) {
    process.exit(1);
  }

  if (!config.components || config.components.length === 0) {
    process.exit(1);
  }

  config.components.forEach((comp) => {
    if (!comp.name || comp.name.trim() === '') {
      process.exit(1);
    }

    if (!comp.viewports || comp.viewports.length === 0) {
      process.exit(1);
    }

    if (!comp.themes || comp.themes.length === 0) {
      process.exit(1);
    }
  });
}

/**
 * Print help message
 */
function printHelp(): void {}

/**
 * Main entry point
 */
function main(): void {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help')) {
    printHelp();
    return;
  }

  if (args.includes('--list-changed')) {
    listChangedSnapshots();
  } else if (args.includes('--accept-all')) {
    acceptAllChanges();
  } else if (args.includes('--reject-all')) {
    rejectAllChanges();
  } else if (args.includes('--summary')) {
    generateSummary();
  } else if (args.includes('--validate')) {
    validateConfig();
  } else {
    process.exit(1);
  }
}

main();
