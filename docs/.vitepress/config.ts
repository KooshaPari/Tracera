import { defineConfig } from 'vitepress'
import { createSiteMeta } from './site-meta.mjs'

const repoName = process.env.GITHUB_REPOSITORY?.split('/').at(-1) ?? 'trace'
const base = process.env.GITHUB_ACTIONS === 'true' ? `/${repoName}/` : '/'
const siteMeta = createSiteMeta({ base })

export default defineConfig({
  base,
  title: siteMeta.title,
  description: siteMeta.description,
  srcDir: 'site',
  lastUpdated: true,
  cleanUrls: true,
  ignoreDeadLinks: true,

  themeConfig: {
    nav: siteMeta.themeConfig.nav,
    sidebar: {
      '/wiki/': [{ text: 'Wiki (User Guides)', items: [{ text: 'Overview', link: '/wiki/' }] }],
      '/development/': [{ text: 'Development Guide', items: [{ text: 'Overview', link: '/development/' }] }],
      '/index/': [{
        text: 'Document Index',
        items: [
          { text: 'Overview', link: '/index/' },
          { text: 'Raw/All', link: '/index/raw-all' },
          { text: 'Planning', link: '/index/planning' },
          { text: 'Specs', link: '/index/specs' },
          { text: 'Research', link: '/index/research' },
          { text: 'Worklogs', link: '/index/worklogs' },
          { text: 'Other', link: '/index/other' },
        ],
      }],
      '/api/': [{ text: 'API', items: [{ text: 'Overview', link: '/api/' }] }],
      '/roadmap/': [{ text: 'Roadmap', items: [{ text: 'Overview', link: '/roadmap/' }] }],
      '/': [{
        text: 'Quick Links',
        items: [
          { text: 'Wiki', link: '/wiki/' },
          { text: 'Development Guide', link: '/development/' },
          { text: 'Document Index', link: '/index/' },
          { text: 'API', link: '/api/' },
          { text: 'Roadmap', link: '/roadmap/' },
        ],
      }]
    },
    search: { provider: 'local' },
    socialLinks: [{ icon: 'github', link: 'https://github.com/kooshapari/trace' }]
  }
})
