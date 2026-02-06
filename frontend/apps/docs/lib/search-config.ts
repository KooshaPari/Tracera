/**
 * Search Configuration
 *
 * Optimizes search performance and relevance:
 * - Prioritizes certain page types (getting started, guides)
 * - Configures search index weights
 * - Defines search result formatting
 */

export interface SearchIndexConfig {
  /**
   * Weight multipliers for different content types
   * Higher weights appear higher in search results
   */
  weights: {
    title: number;
    description: number;
    heading: number;
    content: number;
  };

  /**
   * Pages to prioritize in search results
   * Use URL patterns to match pages
   */
  priorityPages: string[];

  /**
   * Minimum query length before searching
   */
  minQueryLength: number;

  /**
   * Maximum number of results to show
   */
  maxResults: number;
}

export const searchConfig: SearchIndexConfig = {
  weights: {
    title: 10, // Titles are most important
    description: 5, // Descriptions are very relevant
    heading: 3, // Headings are moderately important
    content: 1, // Content is baseline relevance
  },

  priorityPages: [
    '/docs', // Documentation home
    '/docs/getting-started', // Getting started
    '/docs/getting-started/quick-start', // Quick start guide
    '/docs/guides', // Guides section
  ],

  minQueryLength: 2,
  maxResults: 50,
};

/**
 * Format search result preview
 * Truncates content and highlights matches
 */
export function formatSearchPreview(
  content: string,
  query: string,
  maxLength: number = 150,
): string {
  const lowerContent = content.toLowerCase();
  const lowerQuery = query.toLowerCase();
  const index = lowerContent.indexOf(lowerQuery);

  if (index === -1) {
    return content.slice(0, maxLength) + (content.length > maxLength ? '...' : '');
  }

  // Show context around the match
  const start = Math.max(0, index - 50);
  const end = Math.min(content.length, index + query.length + 100);

  let preview = content.slice(start, end);

  if (start > 0) preview = '...' + preview;
  if (end < content.length) preview = preview + '...';

  return preview;
}
