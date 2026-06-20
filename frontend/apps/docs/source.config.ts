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

import { rehypeCode, remarkGfm, remarkHeading } from 'fumadocs-core/mdx-plugins';
import { defineConfig, defineDocs, frontmatterSchema } from 'fumadocs-mdx/config';
import { z } from 'zod';

// Define documentation content sources with full configuration
export const { docs, meta } = defineDocs({
  dir: 'content/docs',
  docs: {
    schema: frontmatterSchema.extend({
      index: z.boolean().optional(),
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
  experimentalBuildCache: '.cache/fumadocs',

  mdxOptions: {
    // Remark plugins for parsing Markdown
    remarkPlugins: [
      remarkGfm, // GitHub Flavored Markdown (tables, task lists, etc.)
      remarkHeading, // Heading IDs for Table of Contents
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
