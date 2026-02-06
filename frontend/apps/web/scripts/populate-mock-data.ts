#!/usr/bin/env bun
/**
 * Script to populate TraceRTM with comprehensive, realistic mock data
 * Generates 10,000+ high-quality data entities across diverse real-world projects
 * Includes authentic requirements, features, code, tests, APIs, and proper traceability
 *
 * Usage: bun run populate-mock-data.ts
 */

import type { Project, ProjectConfig } from './lib/types';

import { createProject, fetchProjects, getApiUrl } from './lib/api';
import { populateProject } from './lib/populator';
import { PROJECTS, getProjectStats, getTotalItemCount } from './lib/projects';

async function main() {
  try {
    // Fetch existing projects
    const existingProjects = await fetchProjects();

    const createdProjects: {
      config: ProjectConfig;
      project: Project;
    }[] = [];

    // Create or find each project
    for (const config of PROJECTS) {
      let project = existingProjects.find(
        (p) => p.name.toLowerCase() === config.name.toLowerCase(),
      );

      if (!project) {
        try {
          project = await createProject(config.name, config.description);
        } catch {
          continue;
        }
      } else {
      }

      createdProjects.push({ config, project });
    }

    // Populate each project with data

    let totalItems = 0;
    let totalLinks = 0;

    for (const { config, project } of createdProjects) {
      const { itemCount, linkCount } = await populateProject(project.id, config);
      totalItems += itemCount;
      totalLinks += linkCount;
    }

    // Display final report
    const expectedTotal = getTotalItemCount();
    const stats = getProjectStats();

    for (const stat of stats) {
    }
  } catch {
    process.exit(1);
  }
}

main();
