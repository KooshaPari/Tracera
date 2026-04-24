#!/usr/bin/env bun
/**
 * Search Index Builder
 *
 * Builds a precompiled search index at build time for optimal performance.
 * This script:
 * 1. Extracts all page content from documentation
 * 2. Creates a searchable index with Fuse.js
 * 3. Generates public/search-index.json for client-side use
 * 4. Optimizes for <100ms search response time
 *
 * Run: bun run scripts/build-search-index.ts
 */

import Fuse, { type IFuseOptions } from 'fuse.js';
import { mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

import { searchConfig } from '../lib/search-config';

interface SearchDocument {
  id: string;
  url: string;
  title: string;
  description: string;
  content: string;
  headings: string[];
  structuredData?: Record<string, unknown>;
  priority: number;
}

interface FrontMatter {
  title?: string;
  description?: string;
  icon?: string;
  index?: boolean;
}

/**
 * Extract priority score for a page
 * Higher priority pages appear first in search results
 */
function getPagePriority(url: string): number {
  const priorityIndex = searchConfig.priorityPages.findIndex((pattern) => url.includes(pattern));

  if (priorityIndex === -1) {
    return 0;
  }

  // Higher priority = lower index in priorityPages array
  return searchConfig.priorityPages.length - priorityIndex;
}

/**
 * Extract text content from MDX/Markdown
 * Removes code blocks, frontmatter, and formatting
 */
function extractContent(rawContent: string): string {
  if (!rawContent) {
    return '';
  }

  return (
    rawContent
      // Remove frontmatter
      .replace(/^---[\s\S]*?---/m, '')
      // Remove code blocks
      .replaceAll(/```[\s\S]*?```/g, '')
      // Remove inline code
      .replaceAll(/`[^`]+`/g, '')
      // Remove links but keep text
      .replaceAll(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      // Remove HTML tags
      .replaceAll(/<[^>]+>/g, '')
      // Remove extra whitespace
      .replaceAll(/\s+/g, ' ')
      .trim()
  );
}

/**
 * Extract headings from content
 */
function extractHeadings(rawContent: string): string[] {
  if (!rawContent) {
    return [];
  }

  const headings: string[] = [];
  const headingRegex = /^#{1,6}\s+(.+)$/gm;
  let match;

  while ((match = headingRegex.exec(rawContent)) !== null) {
    headings.push(match[1].trim());
  }

  return headings;
}

/**
 * Parse frontmatter from MDX content
 */
function parseFrontMatter(content: string): FrontMatter {
  const frontMatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!frontMatterMatch) {
    return {};
  }

  const frontMatterText = frontMatterMatch[1] ?? '';
  const frontMatter: FrontMatter = {};

  // Simple YAML parsing for common fields
  const titleMatch = frontMatterText.match(/title:\s*['"]?([^'":\n]+)['"]?/);
  if (titleMatch) {
    frontMatter.title = titleMatch[1].trim();
  }

  const descMatch = frontMatterText.match(/description:\s*['"]?([^'":\n]+)['"]?/);
  if (descMatch) {
    frontMatter.description = descMatch[1].trim();
  }

  return frontMatter;
}

/**
 * Recursively find all MDX files in a directory
 */
function findMDXFiles(dir: string, fileList: string[] = []): string[] {
  const files = readdirSync(dir);

  for (const file of files) {
    const filePath = join(dir, file);
    const stat = statSync(filePath);

    if (stat.isDirectory()) {
      findMDXFiles(filePath, fileList);
    } else if (file.endsWith('.mdx') || file.endsWith('.md')) {
      fileList.push(filePath);
    }
  }

  return fileList;
}

/**
 * Convert file path to URL
 */
function filePathToURL(filePath: string, contentDir: string): string {
  const relativePath = relative(contentDir, filePath);
  const pathWithoutExt = relativePath.replace(/\.(mdx?|md)$/, '');

  // Convert to URL format
  let url = '/docs/' + pathWithoutExt.split(sep).join('/');

  // Handle index files
  if (url.endsWith('/index')) {
    url = url.replace(/\/index$/, '');
  }

  return url || '/docs';
}

/**
 * Build search index from all pages
 */
function buildSearchIndex(): SearchDocument[] {
  const contentDir = join(process.cwd(), 'content', 'docs');
  const mdxFiles = findMDXFiles(contentDir);

  const documents: SearchDocument[] = mdxFiles.map((filePath) => {
    const rawContent = readFileSync(filePath, 'utf8');
    const frontMatter = parseFrontMatter(rawContent);
    const content = extractContent(rawContent);
    const headings = extractHeadings(rawContent);
    const url = filePathToURL(filePath, contentDir);

    return {
      id: url,
      url,
      title: frontMatter.title || '',
      description: frontMatter.description || '',
      content: content.slice(0, 1000), // Reduced content length for better performance
      headings: headings.slice(0, 10), // Limit headings to first 10
      priority: getPagePriority(url),
    };
  });

  return documents;
}

/**
 * Create Fuse.js index configuration
 * Optimized for fast search (<100ms)
 */
function createFuseIndex(documents: SearchDocument[]) {
  const fuseOptions: IFuseOptions<SearchDocument> = {
    // Performance optimizations - tuned for <100ms
    threshold: 0.35, // Balanced fuzzy matching
    distance: 80, // Moderate distance
    minMatchCharLength: searchConfig.minQueryLength,
    ignoreLocation: false, // Enable location-based scoring for speed
    location: 0, // Prefer matches at the beginning
    useExtendedSearch: false, // Disable for better performance
    findAllMatches: false, // Stop after finding first match in field
    isCaseSensitive: false,
    shouldSort: true, // Sort by relevance

    // Keys to search with weights (fewer fields = faster search)
    keys: [
      {
        name: 'title',
        weight: searchConfig.weights.title,
      },
      {
        name: 'description',
        weight: searchConfig.weights.description,
      },
      {
        name: 'headings',
        weight: searchConfig.weights.heading,
      },
    ],

    // Include metadata for highlighting
    includeScore: true,
    includeMatches: true,
  };

  const fuse = new Fuse(documents, fuseOptions);

  // Get the serializable index
  const index = fuse.getIndex();

  return {
    documents,
    index: index.toJSON(),
    options: fuseOptions,
  };
}

/**
 * Main execution
 */
async function main() {
  try {
    // Build search index
    const documents = buildSearchIndex();

    // Create Fuse.js index
    const searchIndex = createFuseIndex(documents);

    // Ensure public directory exists
    const publicDir = join(process.cwd(), 'public');
    mkdirSync(publicDir, { recursive: true });

    // Write index to public directory
    const outputPath = join(publicDir, 'search-index.json');
    writeFileSync(outputPath, JSON.stringify(searchIndex, null, 2));

    // Calculate and display stats
    const indexSize = JSON.stringify(searchIndex).length;
    console.log(`Search index built: ${documents.length} docs, ${indexSize} bytes`);

    process.exit(0);
  } catch (error) {
    console.error('Failed to build search index:', error);
    process.exit(1);
  }
}

main();
