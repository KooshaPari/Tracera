# Quick Start - TracerTM Docs Site

## Start Dev Server

```bash
# From frontend root
bun run dev:docs

# OR from apps/docs
cd apps/docs
bun run dev
```

Open http://localhost:3001

## Build

```bash
# From frontend root
bun run build:docs

# OR from apps/docs
cd apps/docs
bun run build
```

## Project Structure

```
apps/docs/
├── app/                  # Next.js routes
│   ├── page.tsx         # Landing page (/)
│   └── docs/            # Docs routes (/docs/*)
├── content/docs/        # MDX files
│   ├── index.mdx       # /docs
│   └── meta.json       # Navigation
└── source.config.ts     # Fumadocs MDX config
```

## Adding Content

1. Create MDX file in `content/docs/`:

```mdx
---
title: My Page
description: Page description
---

# My Page

Content here...
```

2. Update `content/docs/meta.json`:

```json
{
  "title": "Documentation",
  "pages": ["index", "my-page"]
}
```

3. Restart dev server

## Current Implementation

**Working:**

- ✅ Dev server on port 3001
- ✅ Build completes successfully
- ✅ Landing page renders
- ✅ Docs layout with sidebar
- ✅ Tailwind styling
- ✅ Dark mode support
- ✅ Turbo integration

**Todo (Phase 3):**

- Full MDX collection API
- Content migration from archive
- Navigation structure
- Search functionality

**Todo (Phase 4):**

- OpenAPI documentation
- Build optimizations
- Deployment config

## Troubleshooting

**Dev server won't start:**

```bash
cd frontend
bun install
cd apps/docs
bun run dev
```

**Build fails:**

```bash
# Check TypeScript
bun run typecheck

# Clean and rebuild
rm -rf .next
bun run build
```

**Port 3001 in use:**

```bash
# Change port in package.json
"dev": "next dev --port 3002"
```

## Stack

- Next.js 16 (App Router + Turbopack)
- Fumadocs UI v16 (docs framework)
- React 19.2
- Tailwind CSS
- MDX (GFM + Shiki syntax highlighting)
