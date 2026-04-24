// source.config.ts
import { rehypeCode, remarkGfm, remarkHeading } from "fumadocs-core/mdx-plugins";
import { defineConfig, defineDocs, frontmatterSchema } from "fumadocs-mdx/config";
import { z } from "zod";
var { docs, meta } = defineDocs({
  dir: "content/docs",
  docs: {
    schema: frontmatterSchema.extend({
      index: z.boolean().optional()
    })
  }
});
var source_config_default = defineConfig({
  experimentalBuildCache: ".cache/fumadocs",
  mdxOptions: {
    // Remark plugins for parsing Markdown
    remarkPlugins: [
      remarkGfm,
      // GitHub Flavored Markdown (tables, task lists, etc.)
      remarkHeading
      // Heading IDs for Table of Contents
    ],
    // Rehype plugins for HTML transformation
    rehypePlugins: (defaults) => [
      ...defaults,
      [
        rehypeCode,
        {
          // Syntax highlighting themes for light/dark mode
          themes: {
            dark: "github-dark",
            light: "github-light"
          },
          // Enable line numbers and copy button
          defaultLanguage: "plaintext",
          defaultColor: false,
          // Support for meta strings (line highlighting, etc.)
          meta: {
            __raw: true
          }
        }
      ]
    ]
  }
});
export {
  source_config_default as default,
  docs,
  meta
};
