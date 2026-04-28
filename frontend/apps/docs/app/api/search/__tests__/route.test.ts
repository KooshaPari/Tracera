import { describe, it, expect, vi } from 'vitest';

// Mock source before importing route
const mockGetPages = vi.fn().mockReturnValue([
  {
    url: '/docs/getting-started',
    data: {
      title: 'Getting Started',
      description: 'Learn how to get started with TracerTM',
      structuredData: { heading: 'Introduction' },
    },
  },
  {
    url: '/docs/guides/deployment',
    data: {
      title: 'Deployment Guide',
      description: null,
      structuredData: { heading: 'Deploy' },
    },
  },
  {
    url: '/docs/api-reference',
    data: {
      title: null,
      description: undefined,
      structuredData: {},
    },
  },
]);

vi.mock('@/source', () => ({
  source: {
    getPages: mockGetPages,
  },
}));

// Mock fumadocs search API creation
const mockGET = vi.fn();
vi.mock('fumadocs-core/search/server', () => ({
  createSearchAPI: vi.fn((_type: string, config: any) => {
    // Capture the config for assertion
    (globalThis as any).__searchAPIConfig = config;
    return { GET: mockGET };
  }),
}));

describe('search API route', () => {
  it('exports a GET handler', async () => {
    const { GET } = await import('../route');
    expect(GET).toBeDefined();
    expect(typeof GET).toBe('function');
  });

  it('creates search API with "advanced" mode', async () => {
    await import('../route');
    const { createSearchAPI } = await import('fumadocs-core/search/server');
    expect(createSearchAPI).toHaveBeenCalledWith('advanced', expect.any(Object));
  });

  it('maps pages to search indexes with correct structure', async () => {
    await import('../route');
    const config = (globalThis as any).__searchAPIConfig;

    expect(config.indexes).toHaveLength(3);

    // First page - with all fields
    expect(config.indexes[0]).toEqual({
      id: '/docs/getting-started',
      url: '/docs/getting-started',
      title: 'Getting Started',
      description: 'Learn how to get started with TracerTM',
      structuredData: { heading: 'Introduction' },
    });
  });

  it('uses empty string as fallback when description is null/undefined', async () => {
    await import('../route');
    const config = (globalThis as any).__searchAPIConfig;

    // Second page has null description
    expect(config.indexes[1].description).toBe('');
    // Third page has undefined description
    expect(config.indexes[2].description).toBe('');
  });

  it('uses page URL as fallback when title is null', async () => {
    await import('../route');
    const config = (globalThis as any).__searchAPIConfig;

    // Third page has null title, should fall back to URL
    expect(config.indexes[2].title).toBe('/docs/api-reference');
  });

  it('uses page URL as the id for each index entry', async () => {
    await import('../route');
    const config = (globalThis as any).__searchAPIConfig;

    config.indexes.forEach((index: any) => {
      expect(index.id).toBe(index.url);
    });
  });
});
