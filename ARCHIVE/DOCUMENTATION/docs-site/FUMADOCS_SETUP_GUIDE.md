# Fumadocs Setup Guide for TraceRTM Documentation

## Current Fumadocs Setup

The project already uses fumadocs. Current configuration:
- `fumadocs-core` for routing
- `fumadocs-ui` for components
- `fumadocs-mdx` for MDX support
- Custom page layout in `app/docs/[[...slug]]/page.tsx`

## Recommended Enhancements

### 1. Sidebar Configuration Structure

Create `lib/docs-config.ts`:
```typescript
export const docsConfig = {
  baseUrl: '/docs',
  sidebar: {
    'getting-started': {
      title: 'Getting Started',
      icon: 'rocket',
      items: [
        { title: 'Overview', href: '/docs/getting-started' },
        { title: 'Installation', href: '/docs/getting-started/installation' },
        // ... more items
      ]
    },
    'wiki': {
      title: 'Wiki',
      icon: 'book',
      items: [
        {
          title: 'Concepts',
          items: [
            { title: 'Traceability', href: '/docs/wiki/concepts/traceability' },
            // ... more items
          ]
        },
        // ... more sections
      ]
    },
    // ... more sections
  }
}
```

### 2. Custom Components to Create

**InteractiveDemo.tsx** - Tabbed interface for CLI vs Web UI
**Mermaid.tsx** - Diagram rendering
**CodeBlock.tsx** - Enhanced code blocks with copy button
**APIEndpoint.tsx** - Formatted API documentation
**Breadcrumb.tsx** - Custom breadcrumb navigation
**TableOfContents.tsx** - Auto-generated from headings
**RelatedPages.tsx** - "See Also" section
**Pagination.tsx** - Previous/Next navigation

### 3. MDX Frontmatter Schema

```yaml
---
title: Page Title
description: Short description for SEO
icon: IconName
category: Category Name
order: 1
tags: [tag1, tag2]
---
```

### 4. Search Configuration

- Use Algolia for production search
- Index all pages with metadata
- Implement Cmd+K shortcut
- Filter by category/section

### 5. Directory Structure

```
content/docs/
├── 00-getting-started/
├── 01-wiki/
│   ├── 01-concepts/
│   ├── 02-guides/
│   ├── 03-examples/
│   └── 04-use-cases/
├── 02-api-reference/
│   ├── 01-rest-api/
│   ├── 02-cli/
│   └── 03-sdks/
├── 03-development/
│   ├── 01-architecture/
│   ├── 02-setup/
│   ├── 03-contributing/
│   ├── 04-internals/
│   └── 05-deployment/
└── 04-changelog/
```

### 6. Build Configuration

Update `next.config.js`:
```javascript
const withMDX = require('@next/mdx')({
  extension: /\.mdx?$/,
  options: {
    remarkPlugins: [
      require('remark-gfm'),
      require('remark-frontmatter'),
    ],
    rehypePlugins: [
      require('rehype-highlight'),
      require('rehype-slug'),
    ],
  },
})

module.exports = withMDX({
  pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx'],
})
```

### 7. Performance Optimization

- Lazy load code examples
- Optimize images with next/image
- Use dynamic imports for heavy components
- Implement incremental static regeneration (ISR)
- Cache search results

### 8. Version Management

Store versions in `/docs/versions/`:
```
versions/
├── v2.0/
├── v1.5/
└── v1.0/
```

Implement version selector in header to switch between versions.

## Next Steps

1. Create sidebar configuration
2. Implement custom components
3. Set up search infrastructure
4. Create directory hierarchy
5. Migrate existing content
6. Add new pages progressively
7. Test and optimize

