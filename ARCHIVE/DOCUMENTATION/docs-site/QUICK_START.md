# Quick Start Guide - Fumadocs Documentation Site

## Installation

```bash
cd docs-site
npm install
```

## Development

```bash
# Build search index
npm run index

# Start dev server
npm run dev
```

Visit: http://localhost:3001

## Adding Content

### 1. Create MDX File

```bash
# Create new file
touch src/content/section/page-name.mdx
```

```mdx
---
title: Page Title
description: Brief description
---

# Page Title

Your content here...
```

### 2. Update Navigation

Edit `src/lib/source.ts`:

```typescript
{
  title: 'Section',
  icon: 'BookOpen',
  children: [
    {
      title: 'Page Name',
      href: '/docs/section/page-name',
    },
  ],
}
```

### 3. Rebuild Index

```bash
npm run index
```

## Key Features

### Sidebar Navigation
- Hierarchical menu
- Collapsible sections
- Active page highlighting
- Icon integration

### Mobile Menu
- Hamburger toggle
- Full-screen overlay
- Same navigation tree

### Search
- **Keyboard**: ⌘K (Mac) or Ctrl+K (Windows/Linux)
- **Click**: Search bar in header
- **Features**: Real-time, fuzzy matching, keyboard navigation

### Breadcrumbs
- Auto-generated from URL
- Clickable parent links
- SEO-friendly

## Project Structure

```
src/
├── app/
│   ├── api/search/        # Search API
│   ├── docs/              # Docs pages
│   └── globals.css        # Styles
├── components/
│   ├── sidebar.tsx        # Desktop nav
│   ├── mobile-nav.tsx     # Mobile nav
│   ├── breadcrumb.tsx     # Breadcrumb
│   └── command-palette.tsx # Search UI
├── content/               # MDX files
│   ├── getting-started/
│   ├── guides/
│   ├── api-reference/
│   ├── examples/
│   ├── faq/
│   └── contributing/
└── lib/
    ├── source.ts          # Nav tree
    ├── search-indexer.ts  # Search logic
    └── utils.ts           # Utilities
```

## Common Tasks

### Add New Section

1. Create directory: `mkdir src/content/new-section`
2. Create files: `touch src/content/new-section/page.mdx`
3. Update navigation in `src/lib/source.ts`
4. Rebuild: `npm run index`

### Change Icons

Edit `src/lib/source.ts`:

```typescript
{
  title: 'Section',
  icon: 'Rocket',  // Any Lucide icon name
}
```

Browse icons: https://lucide.dev/

### Customize Colors

Edit `src/app/globals.css`:

```css
:root {
  --primary: 221.2 83.2% 53.3%;  /* Change HSL values */
}
```

### Adjust Search

Edit `src/lib/search-indexer.ts`:

```typescript
// Change result limit
export function searchDocuments(index, query, limit = 20) {

// Adjust scoring
if (doc.title.includes(query)) {
  score += 200;  // Increase weight
}
```

## Keyboard Shortcuts

- **⌘K / Ctrl+K**: Open search
- **↑ / ↓**: Navigate results
- **Enter**: Select result
- **Esc**: Close search

## Troubleshooting

### Search not working
```bash
# Rebuild search index
npm run index

# Check index exists
ls public/search-index.json
```

### Navigation broken
- Check file paths match navigation tree
- Verify MDX frontmatter
- Check for typos in hrefs

### Build errors
```bash
# Clean and rebuild
rm -rf .next node_modules
npm install
npm run build
```

## Build & Deploy

```bash
# Build for production
npm run build

# Test production build
npm start

# Deploy to Vercel
vercel deploy
```

## Configuration Files

- `fumadocs.config.ts` - Fumadocs settings
- `next.config.ts` - Next.js configuration
- `tailwind.config.ts` - Tailwind CSS
- `tsconfig.json` - TypeScript
- `package.json` - Dependencies

## Environment Variables

Optional:
```env
NEXT_PUBLIC_SITE_URL=https://docs.tracertm.io
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

## Resources

- Documentation: See README.md
- Implementation: See IMPLEMENTATION_GUIDE.md
- Fumadocs: https://fumadocs.vercel.app/
- Lucide Icons: https://lucide.dev/

## Support

- Issues: GitHub Issues
- Questions: Discussions
- Updates: Check CHANGELOG.md

---

For detailed information, see IMPLEMENTATION_GUIDE.md
