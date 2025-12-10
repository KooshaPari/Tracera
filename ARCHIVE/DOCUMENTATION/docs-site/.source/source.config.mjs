// source.config.ts
import { defineConfig, defineDocs } from "fumadocs-mdx/config";
import { rehypeCode, remarkGfm, remarkHeading } from "fumadocs-core/mdx-plugins";
var { docs, meta } = defineDocs({
  dir: "content/docs"
});
var source_config_default = defineConfig({
  mdxOptions: {
    // Remark plugins for parsing
    remarkPlugins: [
      remarkGfm,
      // GitHub Flavored Markdown
      remarkHeading
      // Heading IDs for ToC
    ],
    // Rehype plugins for HTML transformation
    rehypePlugins: (defaults) => [
      ...defaults,
      [
        rehypeCode,
        {
          // Syntax highlighting themes
          themes: {
            light: "github-light",
            dark: "github-dark"
          },
          // Code block transformers
          transformers: [
            // Add Twoslash for TypeScript type annotations
            // Commented out until @shikijs/twoslash is installed
            // transformerTwoslash({
            //   cache: createFileSystemTypesCache(),
            // }),
          ]
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
