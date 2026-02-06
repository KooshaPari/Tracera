/**
 * Project population logic
 */

import type { ProjectConfig } from './types';

import { checkProjectItems } from './api';
import { createItemsByType, createTraceabilityLinks } from './generator';

export async function populateProject(
  projectId: string,
  projectConfig: ProjectConfig,
): Promise<{ itemCount: number; linkCount: number }> {
  console.log(`\n📦 Populating ${projectConfig.name} (${projectConfig.domain}) project...`);

  // Check if project already has items
  const existingCount = await checkProjectItems(projectId);
  const totalExpected = Object.values(projectConfig.itemCounts).reduce((a, b) => a + b, 0);

  if (existingCount > totalExpected * 0.8) {
    console.log(`  ⏭️  Skipping - project already has ${existingCount}/${totalExpected} items`);
    return { itemCount: 0, linkCount: 0 };
  }

  console.log(`  ℹ️  Found ${existingCount}/${totalExpected} existing items, will add more...`);

  // Create items by type
  const allItemsByType = await createItemsByType(
    projectId,
    projectConfig.name,
    projectConfig.domain,
    projectConfig.itemCounts,
  );

  // Create traceability links
  console.log('  Creating realistic traceability links...');
  const linkCount = await createTraceabilityLinks(projectId, allItemsByType);

  const totalItems = Object.values(allItemsByType).reduce((a, b) => a + b.length, 0);

  console.log(
    `✅ ${projectConfig.name} populated with ~${totalItems} items and ${linkCount} links`,
  );

  return { itemCount: totalItems, linkCount };
}
