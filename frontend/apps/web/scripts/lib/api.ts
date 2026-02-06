/**
 * API utilities for mock data generation
 */

import type { CreateItemInput, LinkType, Project } from './types';

const API_URL = process.env.VITE_API_URL || 'http://localhost:4000';

export function getApiUrl(): string {
  return API_URL;
}

export async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function createItemWithRetry(data: CreateItemInput, retries = 3): Promise<any> {
  await sleep(50);

  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(`${API_URL}/api/v1/items`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Bulk-Operation': 'true',
        },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        const errorText = await res.text();
        const isRateLimited =
          res.status === 429 ||
          errorText.includes('429') ||
          errorText.includes('Rate limit') ||
          errorText.includes('rate limit');

        if (isRateLimited) {
          await sleep(2000 * (i + 1));
          continue;
        }
        throw new Error(`Failed to create item: ${res.status} ${errorText}`);
      }

      return await res.json();
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      if (
        errorMsg.includes('429') ||
        errorMsg.includes('Rate limit') ||
        errorMsg.includes('rate limit')
      ) {
        if (i < retries - 1) {
          await sleep(2000 * (i + 1));
          continue;
        }
      }
      if (i === retries - 1) throw error;
      await sleep(1000 * (i + 1));
    }
  }
}

export async function createLinkWithRetry(
  projectId: string,
  sourceId: string,
  targetId: string,
  type: LinkType,
  retries = 3,
): Promise<any> {
  await sleep(50);

  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(`${API_URL}/api/v1/links`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Bulk-Operation': 'true',
        },
        body: JSON.stringify({
          project_id: projectId,
          source_id: sourceId,
          target_id: targetId,
          type: type,
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        const isRateLimited =
          res.status === 429 ||
          errorText.includes('429') ||
          errorText.includes('Rate limit') ||
          errorText.includes('rate limit');

        if (isRateLimited) {
          await sleep(2000 * (i + 1));
          continue;
        }
        throw new Error(`Failed to create link: ${res.status} ${errorText}`);
      }

      return await res.json();
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      if (
        errorMsg.includes('429') ||
        errorMsg.includes('Rate limit') ||
        errorMsg.includes('rate limit')
      ) {
        if (i < retries - 1) {
          await sleep(2000 * (i + 1));
          continue;
        }
      }
      if (i === retries - 1) throw error;
      await sleep(1000 * (i + 1));
    }
  }
}

export async function checkProjectItems(projectId: string): Promise<number> {
  try {
    const res = await fetch(`${API_URL}/api/v1/items?project_id=${projectId}&limit=1`);
    if (!res.ok) return 0;
    const data = await res.json();
    return data.total || 0;
  } catch {
    return 0;
  }
}

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_URL}/api/v1/projects`);
  if (!res.ok) throw new Error('Failed to fetch projects');
  const data = await res.json();
  return data.projects || data;
}

export async function createProject(name: string, description: string): Promise<Project> {
  const res = await fetch(`${API_URL}/api/v1/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, description }),
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Failed to create project: ${error}`);
  }

  return await res.json();
}
