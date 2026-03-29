export function createSiteMeta({ base = '/' } = {}) {
  return {
    base,
    title: 'trace',
    description: 'trace documentation',
    themeConfig: {
      nav: [
        { text: 'Home', link: base || '/' },
        { text: 'Wiki', link: base + 'wiki/' },
        { text: 'Development Guide', link: base + 'development/' },
        { text: 'Document Index', link: base + 'index/' },
        { text: 'API', link: base + 'api/' },
        { text: 'Roadmap', link: base + 'roadmap/' },
      ],
      sidebar: {},
      search: { provider: 'local' },
    },
  }
}
