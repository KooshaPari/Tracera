/**
 * Fumadocs MDX Configuration
 *
 * Full MDX collection API with:
 * - GitHub Flavored Markdown (tables, strikethrough, etc.)
 * - Syntax highlighting with Shiki
 * - Heading IDs for ToC generation
 * - Incremental parsing and caching
 * - Automatic frontmatter processing
 * - OpenAPI spec integration for API documentation
 */

import { defineConfig, defineDocs } from 'fumadocs-mdx/config';
import { rehypeCode, remarkGfm, remarkHeading } from 'fumadocs-core/mdx-plugins';

// Define documentation content sources with full configuration
export const { docs, meta } = defineDocs({
  dir: 'content/docs',
  // Enable incremental parsing for better performance
  incremental: true,
  // Configure frontmatter schema
  schema: {
    frontmatter: (z) => ({
      description: z.string().optional(),
      icon: z.string().optional(),
      index: z.boolean().default(false),
      title: z.string().optional(),
    }),
  },
});

/**
 * OpenAPI Documentation Source
 *
 * OpenAPI integration will be configured in a future phase.
 * For now, the spec is available at:
 * content/docs/03-api-reference/openapi.yaml
 *
 * To regenerate: bun run scripts/generate-openapi.ts
 */

export default defineConfig({
  // Enable caching for faster rebuilds
  cache: true,

  // Global configuration for all docs
  global: {
    // Enable structured data for better search indexing
    structuredData: true,
  },

  mdxOptions: {
    // Remark plugins for parsing Markdown
    remarkPlugins: [
      remarkGfm,      // GitHub Flavored Markdown (tables, task lists, etc.)
      remarkHeading,  // Heading IDs for Table of Contents
    ],

    // Rehype plugins for HTML transformation
    rehypePlugins: (defaults) => [
      ...defaults,
      [
        rehypeCode,
        {
          // Syntax highlighting themes for light/dark mode
          themes: {
            dark: 'github-dark',
            light: 'github-light',
          },
          // Enable line numbers and copy button
          defaultLanguage: 'plaintext',
          defaultColor: false,
          // Support for meta strings (line highlighting, etc.)
          meta: {
            __raw: true,
          },
        },
      ],
    ],
  },
});
