# TracerTM Documentation Site

Fumadocs-powered documentation site for TracerTM.

## Quick Start

```bash
# Development
cd frontend
bun run dev:docs

# Build
bun run build:docs

# Production
cd apps/docs
bun run start
```

## Structure

```
apps/docs/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout with RootProvider
│   ├── page.tsx           # Landing page
│   ├── layout.config.tsx  # Shared layout configuration
│   └── docs/              # Documentation routes
│       ├── layout.tsx     # Docs layout with sidebar
│       └── [[...slug]]/page.tsx  # Dynamic doc pages
├── content/docs/          # MDX documentation files
│   ├── index.mdx         # Welcome page
│   └── meta.json         # Navigation metadata
├── components/            # Reusable components
├── lib/                   # Utilities
├── public/                # Static assets
└── source.config.ts       # Fumadocs MDX configuration
```

## Current Status

**Phases 1-7 Complete:**

- ✅ Basic infrastructure working
- ✅ Monorepo integration complete
- ✅ Dev server runs on port 3001
- ✅ Build succeeds
- ✅ Turbo pipeline integration active
- ✅ OpenAPI documentation generation
- ✅ Search functionality configured
- ✅ Deployment pipeline configured
- ✅ CI/CD with GitHub Actions

**Production Deployment:**

- URL: https://docs.tracertm.com
- Auto-deploys from main branch
- Preview deployments for PRs

## Configuration Files

- `package.json` - Dependencies and scripts
- `next.config.ts` - Next.js configuration with MDX support
- `source.config.ts` - Fumadocs MDX processing
- `tailwind.config.ts` - Tailwind CSS with design tokens
- `tsconfig.json` - TypeScript extending workspace root

## Development

The site uses:

- **Next.js 16** with App Router and Turbopack
- **Fumadocs** for documentation features
- **MDX** for content with GFM and syntax highlighting
- **Tailwind CSS** for styling

## URLs

- Dev: http://localhost:3001
- Landing: http://localhost:3001/
- Docs: http://localhost:3001/docs

## Integration

Integrated into frontend monorepo:

- Workspace: `@tracertm/docs`
- Scripts: `dev:docs`, `build:docs` in frontend root
- Turbo tasks: Uses standard build/dev/typecheck

## Deployment

### Quick Deploy

```bash
# Preview deployment
bun run deploy:preview

# Production deployment
bun run deploy:prod
```

### Automated Deployment

Automatic deployment via GitHub Actions:

- **Preview**: Every pull request gets a unique preview URL
- **Production**: Auto-deploys on push to main branch

### Setup Guide

See detailed deployment documentation:

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Complete deployment guide
- **[GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md)** - CI/CD setup instructions

### Environment Variables

Copy `.env.example` to `.env.local` and configure:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DOCS_URL=http://localhost:3001
```

For production, set these in Vercel dashboard.

## Scripts

| Command                    | Description               |
| -------------------------- | ------------------------- |
| `bun run dev`              | Start development server  |
| `bun run build`            | Build for production      |
| `bun run start`            | Start production server   |
| `bun run lint`             | Run ESLint                |
| `bun run typecheck`        | Run TypeScript checks     |
| `bun run openapi`          | Generate OpenAPI spec     |
| `bun run openapi:sync`     | Sync OpenAPI from backend |
| `bun run deploy`           | Deploy to Vercel          |
| `bun run deploy:preview`   | Deploy preview            |
| `bun run deploy:prod`      | Deploy to production      |
| `bun run test:e2e`         | Run E2E tests             |
| `bun run test:performance` | Run performance tests     |

## Documentation

- [Quick Start](./QUICK_START.md) - Get started quickly
- [Deployment Guide](./DEPLOYMENT.md) - Full deployment documentation
- [GitHub Actions Setup](./GITHUB_ACTIONS_SETUP.md) - CI/CD configuration
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) - Technical overview
