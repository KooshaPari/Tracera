import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Trace',
  description: 'Project documentation',
  srcDir: 'site',
  ignoreDeadLinks: true,
  cleanUrls: true,
  markdown: {
    lineNumbers: true,
    theme: {
      light: 'github-light',
      dark: 'github-dark',
    },
  },
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Getting Started', link: '/01-getting-started' },
      { text: 'Architecture', link: '/02-architecture' },
    ],
    sidebar: [
      { text: 'Overview', link: '/' },
      { text: 'Getting Started', link: '/01-getting-started' },
      { text: 'Architecture', link: '/02-architecture' },
      { text: 'Guides', link: '/04-guides' },
      { text: 'API Reference', link: '/06-api-reference' },
    ],
    socialLinks: [{ icon: 'github', link: 'https://github.com/KooshaPari/trace' }],
    search: { provider: 'local' },
  },
})
