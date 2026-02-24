import { defineConfig } from "vitepress";

// Import shared base config
import baseConfig from "../../../docs-hub/.vitepress/base.config";

const repo = process.env.GITHUB_REPOSITORY?.split("/")[1] ?? "trace";
const isCI = process.env.GITHUB_ACTIONS === "true";
const docsBase = isCI ? `/${repo}/` : "/";

export default defineConfig({
  ...baseConfig,
  // Project-specific overrides
  title: "trace",
  description: "trace platform documentation",
  base: docsBase,
  srcDir: "site",
  themeConfig: {
    ...baseConfig.themeConfig,
    nav: [
      { text: "Home", link: "/" },
      { text: "Repository Docs", link: "https://github.com/kooshapari/trace/tree/main/docs" }
    ],
    socialLinks: [
      { icon: "github", link: "https://github.com/kooshapari/trace" }
    ]
  }
});
