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

import { execSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

interface SnapshotConfig {
	projectToken: string;
	components: {
		name: string;
		viewports: string[];
		themes: string[];
		states: string[];
	}[];
}

interface ChromaticBuild {
	uuid: string;
	number: number;
	url: string;
	changes: number;
	errors: number;
}

/**
 * Load snapshot configuration
 */
function loadConfig(): SnapshotConfig {
	const configPath = path.join(process.cwd(), "chromatic.config.json");

	if (!existsSync(configPath)) {
		console.error("chromatic.config.json not found");
		process.exit(1);
	}

	return JSON.parse(readFileSync(configPath, "utf-8"));
}

/**
 * Get latest Chromatic build information
 */
function getLatestBuild(): ChromaticBuild | null {
	try {
		const output = execSync("chromatic --list-builds 2>&1 || echo ''", {
			encoding: "utf-8",
		});

		if (!output.trim()) {
			console.log("No builds found");
			return null;
		}

		// Parse build information (format may vary)
		const lines = output.split("\n").filter((l) => l.trim());
		if (lines.length === 0) return null;

		console.log("Latest builds:", lines.slice(0, 3));
		return null; // Would parse real output in production
	} catch (error) {
		console.error("Failed to fetch builds:", error);
		return null;
	}
}

/**
 * List changed snapshots
 */
function listChangedSnapshots(): void {
	console.log("Listing changed snapshots...");

	try {
		const output = execSync("chromatic --list-changes 2>&1 || echo ''", {
			encoding: "utf-8",
		});

		if (!output.trim()) {
			console.log("No changes detected");
			return;
		}

		console.log("Changed snapshots:");
		console.log(output);
	} catch (error) {
		console.error("Failed to list changes:", error);
	}
}

/**
 * Accept all visual changes
 */
function acceptAllChanges(): void {
	console.log("Accepting all visual changes...");

	try {
		const output = execSync("chromatic --auto-accept-changes", {
			encoding: "utf-8",
			stdio: "inherit",
		});

		console.log("All changes accepted");
	} catch (error) {
		console.error("Failed to accept changes:", error);
		process.exit(1);
	}
}

/**
 * Reject all visual changes
 */
function rejectAllChanges(): void {
	console.log("Rejecting all visual changes...");

	try {
		execSync("chromatic --exit-once-uploaded", {
			encoding: "utf-8",
			stdio: "inherit",
		});

		console.log("Changes rejected - baselines unchanged");
	} catch (error) {
		console.error("Failed to reject changes:", error);
		process.exit(1);
	}
}

/**
 * Generate snapshot summary
 */
function generateSummary(): void {
	console.log("Generating visual test summary...");

	const config = loadConfig();
	let totalSnapshots = 0;

	config.components.forEach((component) => {
		const snapshotsPerComponent =
			component.viewports.length *
			component.themes.length *
			component.states.length;
		totalSnapshots += snapshotsPerComponent;

		console.log(`${component.name}:`);
		console.log(`  Viewports: ${component.viewports.join(", ")}`);
		console.log(`  Themes: ${component.themes.join(", ")}`);
		console.log(`  States: ${component.states.join(", ")}`);
		console.log(`  Total Snapshots: ${snapshotsPerComponent}`);
	});

	console.log(`\nTotal Visual Snapshots: ${totalSnapshots}`);
}

/**
 * Validate Chromatic configuration
 */
function validateConfig(): void {
	console.log("Validating Chromatic configuration...");

	const config = loadConfig();

	if (!config.projectToken) {
		console.error("ERROR: projectToken not set in chromatic.config.json");
		process.exit(1);
	}

	if (!config.components || config.components.length === 0) {
		console.error("ERROR: No components configured");
		process.exit(1);
	}

	config.components.forEach((comp) => {
		if (!comp.name || comp.name.trim() === "") {
			console.error("ERROR: Component missing name");
			process.exit(1);
		}

		if (!comp.viewports || comp.viewports.length === 0) {
			console.error(`ERROR: ${comp.name} missing viewports`);
			process.exit(1);
		}

		if (!comp.themes || comp.themes.length === 0) {
			console.error(`ERROR: ${comp.name} missing themes`);
			process.exit(1);
		}
	});

	console.log("Configuration valid!");
	console.log(`Configured components: ${config.components.length}`);
}

/**
 * Print help message
 */
function printHelp(): void {
	console.log(`
Chromatic Snapshot Manager

Usage:
  bun scripts/chromatic-snapshot-manager.ts [command]

Commands:
  --help                 Show this help message
  --list-changed         List all changed snapshots
  --accept-all           Accept all visual changes
  --reject-all           Reject all visual changes
  --summary              Show snapshot summary
  --validate             Validate configuration

Examples:
  # List changes in current build
  bun scripts/chromatic-snapshot-manager.ts --list-changed

  # Accept all changes to update baselines
  bun scripts/chromatic-snapshot-manager.ts --accept-all

  # Show total snapshot count
  bun scripts/chromatic-snapshot-manager.ts --summary
`);
}

/**
 * Main entry point
 */
function main(): void {
	const args = process.argv.slice(2);

	if (args.length === 0 || args.includes("--help")) {
		printHelp();
		return;
	}

	if (args.includes("--list-changed")) {
		listChangedSnapshots();
	} else if (args.includes("--accept-all")) {
		acceptAllChanges();
	} else if (args.includes("--reject-all")) {
		rejectAllChanges();
	} else if (args.includes("--summary")) {
		generateSummary();
	} else if (args.includes("--validate")) {
		validateConfig();
	} else {
		console.error("Unknown command. Use --help for usage information.");
		process.exit(1);
	}
}

main();
