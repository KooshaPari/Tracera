import { createSearchAPI } from 'fumadocs-core/search/server';

import { source } from '@/source';

/**
 * Search API Route
 *
 * Provides full-text search across all documentation pages.
 * Uses Fumadocs advanced search with:
 * - Title, description, and content indexing
 * - Structured data for better relevance
 * - Fast in-memory search (<100ms target)
 *
 * Accessible via:
 * - Cmd+K / Ctrl+K hotkey
 * - Search button in navigation
 * - Direct API: GET /api/search?query=...
 */
export const { GET } = createSearchAPI('advanced', {
  indexes: source.getPages().map((page) => ({
    description: page.data.description ?? '',
    id: page.url,
    structuredData: page.data.structuredData,
    title: page.data.title ?? page.url,
    url: page.url,
  })),
});
