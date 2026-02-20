import { defineConfig } from "vitepress";

const repo = process.env.GITHUB_REPOSITORY?.split("/")[1] ?? "trace";
const isCI = process.env.GITHUB_ACTIONS === "true";

export default defineConfig({
  title: "trace",
  description: "trace platform documentation",
  base: isCI ? `/${repo}/` : "/",
  srcDir: "site",
  cleanUrls: true,
  ignoreDeadLinks: true,
  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Repository Docs", link: "https://github.com/kooshapari/trace/tree/main/docs" }
    ],
    socialLinks: [
      { icon: "github", link: "https://github.com/kooshapari/trace" }
    ]
  }
});
