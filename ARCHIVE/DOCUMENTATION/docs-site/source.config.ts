/**
 * Fumadocs MDX Configuration
 *
 * Configures MDX processing with:
 * - GitHub Flavored Markdown (tables, strikethrough, etc.)
 * - Syntax highlighting with Shiki
 * - Math support (KaTeX)
 * - Type annotations with Twoslash
 * - Heading IDs for ToC generation
 */

import { defineConfig, defineDocs } from 'fumadocs-mdx/config';
import { rehypeCode, remarkGfm, remarkHeading } from 'fumadocs-core/mdx-plugins';

// Define documentation content sources
export const { docs, meta } = defineDocs({
  dir: 'content/docs',
});

export default defineConfig({
  mdxOptions: {
    // Remark plugins for parsing
    remarkPlugins: [
      remarkGfm,      // GitHub Flavored Markdown
      remarkHeading,  // Heading IDs for ToC
    ],

    // Rehype plugins for HTML transformation
    rehypePlugins: (defaults) => [
      ...defaults,
      [
        rehypeCode,
        {
          // Syntax highlighting themes
          themes: {
            light: 'github-light',
            dark: 'github-dark',
          },
          // Code block transformers
          transformers: [
            // Add Twoslash for TypeScript type annotations
            // Commented out until @shikijs/twoslash is installed
            // transformerTwoslash({
            //   cache: createFileSystemTypesCache(),
            // }),
          ],
        },
      ],
    ],
  },
});
