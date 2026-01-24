#!/usr/bin/env bun
/**
 * Script to populate TraceRTM with comprehensive, realistic mock data
 * Generates 10,000+ high-quality data entities across diverse real-world projects
 * Includes authentic requirements, features, code, tests, APIs, and proper traceability
 *
 * Usage: bun run populate-mock-data.ts
 */

import { createProject, fetchProjects, getApiUrl } from "./lib/api";
import { populateProject } from "./lib/populator";
import { getProjectStats, getTotalItemCount, PROJECTS } from "./lib/projects";
import type { Project, ProjectConfig } from "./lib/types";

async function main() {
	console.log("🚀 Starting comprehensive mock data population...");
	console.log(`API URL: ${getApiUrl()}`);
	console.log(`Projects to create: ${PROJECTS.length}`);

	try {
		// Fetch existing projects
		const existingProjects = await fetchProjects();

		const createdProjects: Array<{
			config: ProjectConfig;
			project: Project;
		}> = [];

		// Create or find each project
		for (const config of PROJECTS) {
			let project = existingProjects.find(
				(p) => p.name.toLowerCase() === config.name.toLowerCase(),
			);

			if (!project) {
				console.log(`\n📝 Creating project: ${config.name}...`);
				try {
					project = await createProject(config.name, config.description);
					console.log(`✓ Created project: ${config.name} (ID: ${project.id})`);
				} catch (error) {
					console.error(`✗ Failed to create project ${config.name}:`, error);
					continue;
				}
			} else {
				console.log(`✓ Found existing project: ${config.name}`);
			}

			createdProjects.push({ config, project });
		}

		// Populate each project with data
		console.log("\n🔄 Populating projects with data...");
		let totalItems = 0;
		let totalLinks = 0;

		for (const { config, project } of createdProjects) {
			const { itemCount, linkCount } = await populateProject(
				project.id,
				config,
			);
			totalItems += itemCount;
			totalLinks += linkCount;
		}

		// Display final report
		const expectedTotal = getTotalItemCount();
		const stats = getProjectStats();

		console.log("\n✅ Mock data population complete!");
		console.log(`   Projects created: ${createdProjects.length}`);
		console.log(
			`   Total data entities: ~${expectedTotal} (${totalItems} created this run)`,
		);
		console.log(`   Expected links: ~${Math.round(expectedTotal * 0.3)}`);
		console.log(`   Links created this run: ${totalLinks}`);
		console.log("\n📊 Project breakdown:");

		for (const stat of stats) {
			console.log(`   - ${stat.name}: ~${stat.items} items (${stat.domain})`);
		}

		console.log("\n💾 Mock data is ready for testing and development!");
	} catch (error) {
		console.error("❌ Error populating mock data:", error);
		process.exit(1);
	}
}

main();
