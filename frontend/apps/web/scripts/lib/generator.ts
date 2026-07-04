/**
 * Item and link generation logic
 */

import type { ItemPriority, ItemStatus, ItemsByType, ItemType, LinkType } from './types';

import { createItemWithRetry, createLinkWithRetry } from './api';
import { codeSnippets, descriptions } from './data';

const statuses: ItemStatus[] = ['pending', 'in_progress', 'completed', 'blocked'];
const priorities: ItemPriority[] = ['low', 'medium', 'high', 'critical'];

export function randomChoice<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function generateId(prefix: string, index: number): string {
  return `${prefix}-${index}`;
}

export async function createItemsBatch(
  projectId: string,
  count: number,
  type: ItemType,
  titleFn: (i: number) => string,
  descriptionFn: (i: number) => string,
  parentIdFn?: (i: number, existingItems: any[]) => string | undefined,
  batchSize = 25,
): Promise<any[]> {
  const results: any[] = [];
  const batch: Promise<any>[] = [];

  for (let i = 1; i <= count; i++) {
    const parentId = parentIdFn ? parentIdFn(i - 1, results) : undefined;
    batch.push(
      createItemWithRetry({
        project_id: projectId,
        type,
        title: titleFn(i),
        description: descriptionFn(i),
        status: randomChoice(statuses),
        priority: randomChoice(priorities),
        parent_id: parentId,
      }),
    );

    if (i % batchSize === 0) {
      const batchResults = await Promise.all(batch.splice(0, batchSize));
      results.push(...batchResults);
      console.log(`    Created ${i}/${count} ${type}s`);
    }
  }

  if (batch.length > 0) {
    const batchResults = await Promise.all(batch);
    results.push(...batchResults);
    console.log(`    Created ${count}/${count} ${type}s`);
  }

  return results;
}

export async function createItemsByType(
  projectId: string,
  projectName: string,
  projectDomain: string,
  itemCounts: Record<string, number>,
): Promise<ItemsByType> {
  const allItemsByType: ItemsByType = {
    requirement: [],
    feature: [],
    code: [],
    test: [],
    api: [],
    database: [],
    wireframe: [],
    documentation: [],
    deployment: [],
  };

  for (const [type, count] of Object.entries(itemCounts)) {
    if (count === 0) continue;

    const itemType = type as ItemType;
    console.log(`  Creating ${count} ${type}...`);

    let items: any[] = [];

    switch (itemType) {
      case 'requirement':
        items = await createItemsBatch(
          projectId,
          count,
          itemType,
          (i) => `REQ-${i}: ${randomChoice(descriptions.requirement)}`,
          (i) =>
            `${projectName} requirement ${i}. Priority varies based on project phase and stakeholder input.`,
        );
        break;

      case 'feature':
        items = await createItemsBatch(
          projectId,
          count,
          itemType,
          (i) => `Feature ${i}: ${randomChoice(descriptions.feature)}`,
          (i) => `Feature implementation ${i} for ${projectName}. Enhances platform capabilities.`,
          (i) => allItemsByType.requirement[i % allItemsByType.requirement.length]?.id,
        );
        break;

      case 'code':
        items = await createItemsBatch(
          projectId,
          count,
          itemType,
          (i) => {
            const ext = projectDomain === 'ai' ? 'py' : 'ts';
            return `${projectDomain}/module_${i}.${ext}`;
          },
          (i) => {
            const lang =
              projectDomain === 'data' || projectDomain === 'ai' ? 'python' : 'typescript';
            const snippet = randomChoice(codeSnippets[lang as keyof typeof codeSnippets]);
            return `Code implementation for ${projectDomain}.\n\n\`\`\`${lang}\n${snippet}\n\`\`\``;
          },
          (i) => allItemsByType.feature[i % allItemsByType.feature.length]?.id,
        );
        break;

      case 'test':
        items = await createItemsBatch(
          projectId,
          count,
          itemType,
          (i) => `Test ${i}: ${randomChoice(descriptions.test)}`,
          (i) => `Comprehensive test coverage for code quality assurance.`,
          (i) => allItemsByType.code[i % allItemsByType.code.length]?.id,
        );
        break;

      case 'api':
        items = await createItemsBatch(
          projectId,
          count,
          itemType,
          (i) => `API ${i}: ${randomChoice(descriptions.api)}`,
          (i) => `API endpoint for ${projectName} integration.`,
        );
        break;

      case 'database':
        items = await createItemsBatch(
          projectId,
          count,
          itemType,
          (i) => `DB Schema ${i}: ${randomChoice(descriptions.database)}`,
          (i) => {
            const snippet = randomChoice(codeSnippets.sql);
            return `Database schema design.\n\n\`\`\`sql\n${snippet}\n\`\`\``;
          },
        );
        break;

      case 'wireframe':
        items = await createItemsBatch(
          projectId,
          count,
          itemType,
          (i) => `Wireframe ${i}: UI Design`,
          (i) => `User interface design for ${projectName}.`,
        );
        break;

      case 'documentation':
        items = await createItemsBatch(
          projectId,
          count,
          itemType,
          (i) => `Doc ${i}: ${randomChoice(descriptions.database)}`,
          (i) => `Technical documentation for system architecture and usage.`,
        );
        break;

      case 'deployment':
        items = await createItemsBatch(
          projectId,
          count,
          itemType,
          (i) => `Deploy ${i}: Environment Config`,
          (i) => `Deployment and infrastructure configuration.`,
        );
        break;
    }

    allItemsByType[itemType] = items;
  }

  return allItemsByType;
}

export async function createTraceabilityLinks(
  projectId: string,
  allItemsByType: ItemsByType,
): Promise<number> {
  const links: Array<{ source_id: string; target_id: string; type: LinkType }> = [];

  // Requirement → Feature (implements)
  if (allItemsByType.requirement.length > 0 && allItemsByType.feature.length > 0) {
    const linkCount = Math.min(
      allItemsByType.requirement.length,
      Math.floor(allItemsByType.feature.length * 1.2),
    );
    for (let i = 0; i < linkCount; i++) {
      const req = allItemsByType.requirement[i % allItemsByType.requirement.length];
      const feat =
        allItemsByType.feature[Math.floor(Math.random() * allItemsByType.feature.length)];
      if (req && feat && req.id !== feat.id) {
        links.push({
          source_id: feat.id,
          target_id: req.id,
          type: 'implements',
        });
      }
    }
  }

  // Feature → Code (implements)
  if (allItemsByType.feature.length > 0 && allItemsByType.code.length > 0) {
    const linkCount = Math.min(
      allItemsByType.feature.length,
      Math.floor(allItemsByType.code.length * 0.8),
    );
    for (let i = 0; i < linkCount; i++) {
      const feat = allItemsByType.feature[i % allItemsByType.feature.length];
      const code = allItemsByType.code[Math.floor(Math.random() * allItemsByType.code.length)];
      if (feat && code && feat.id !== code.id) {
        links.push({
          source_id: code.id,
          target_id: feat.id,
          type: 'implements',
        });
      }
    }
  }

  // Code → Test (tests)
  if (allItemsByType.code.length > 0 && allItemsByType.test.length > 0) {
    const linkCount = Math.min(allItemsByType.code.length, allItemsByType.test.length);
    for (let i = 0; i < linkCount; i++) {
      const code = allItemsByType.code[i % allItemsByType.code.length];
      const test = allItemsByType.test[i % allItemsByType.test.length];
      if (code && test && code.id !== test.id) {
        links.push({ source_id: test.id, target_id: code.id, type: 'tests' });
      }
    }
  }

  // Code → Database (depends_on)
  if (allItemsByType.code.length > 0 && allItemsByType.database.length > 0) {
    const linkCount = Math.min(allItemsByType.code.length / 2, allItemsByType.database.length * 3);
    for (let i = 0; i < linkCount; i++) {
      const code = allItemsByType.code[Math.floor(Math.random() * allItemsByType.code.length)];
      const db =
        allItemsByType.database[Math.floor(Math.random() * allItemsByType.database.length)];
      if (code && db && code.id !== db.id) {
        links.push({
          source_id: code.id,
          target_id: db.id,
          type: 'depends_on',
        });
      }
    }
  }

  // API → Code (depends_on)
  if (allItemsByType.api.length > 0 && allItemsByType.code.length > 0) {
    const linkCount = Math.min(allItemsByType.api.length, allItemsByType.code.length / 2);
    for (let i = 0; i < linkCount; i++) {
      const api = allItemsByType.api[i % allItemsByType.api.length];
      const code = allItemsByType.code[Math.floor(Math.random() * allItemsByType.code.length)];
      if (api && code && api.id !== code.id) {
        links.push({
          source_id: api.id,
          target_id: code.id,
          type: 'depends_on',
        });
      }
    }
  }

  // Feature → Wireframe (relates_to)
  if (allItemsByType.feature.length > 0 && allItemsByType.wireframe.length > 0) {
    const linkCount = Math.min(
      allItemsByType.feature.length / 2,
      allItemsByType.wireframe.length * 2,
    );
    for (let i = 0; i < linkCount; i++) {
      const feat =
        allItemsByType.feature[Math.floor(Math.random() * allItemsByType.feature.length)];
      const wire =
        allItemsByType.wireframe[Math.floor(Math.random() * allItemsByType.wireframe.length)];
      if (feat && wire && feat.id !== wire.id) {
        links.push({
          source_id: feat.id,
          target_id: wire.id,
          type: 'relates_to',
        });
      }
    }
  }

  // Create links in parallel batches
  console.log(`  Creating ${links.length} links...`);
  const linkBatches: Promise<any>[] = [];

  for (let i = 0; i < links.length; i++) {
    linkBatches.push(
      createLinkWithRetry(projectId, links[i].source_id, links[i].target_id, links[i].type).catch(
        () => null,
      ),
    );

    if ((i + 1) % 50 === 0) {
      await Promise.all(linkBatches.splice(0, 50));
      console.log(`    Created ${i + 1}/${links.length} links`);
    }
  }

  if (linkBatches.length > 0) {
    await Promise.all(linkBatches);
    console.log(`    Created ${links.length}/${links.length} links`);
  }

  return links.length;
}
