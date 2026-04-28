export function createSiteMeta({ base = '/' } = {}) {
  return {
    base,
    title: 'trace',
    description: 'trace documentation',
    themeConfig: {
      nav: [
        { text: 'Home', link: '/' },
        { text: 'Wiki', link: '/wiki/' },
        { text: 'Development Guide', link: '/development/' },
        { text: 'Document Index', link: '/index/' },
        { text: 'API', link: '/api/' },
        { text: 'Roadmap', link: '/roadmap/' },
      ],
    },
  }
}
