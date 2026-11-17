import { defineConfig } from 'vitepress'

// Landing + docs site. base is '/Tracera/' on kooshapari.github.io.
export default defineConfig({
  title: 'Tracera',
  description: 'Application monitoring and tracing',
  base: '/Tracera/',
  cleanUrls: true,
  themeConfig: {
    nav: [
      { text: 'Docs', link: '/01-getting-started/' },
      { text: 'Compete', link: '/compete/' }
    ],
    sidebar: [
      { text: 'Docs', link: '/01-getting-started/' },
      { text: 'Compete', link: '/compete/' }
    ]
  }
})
