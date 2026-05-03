# TraceRTM Frontend

Bun-powered TypeScript monorepo using Turborepo. Contains the web app, desktop app, Storybook, and shared packages.

## Structure

- `apps/web` -- Next.js web application
- `apps/desktop` -- Desktop client
- `apps/docs` -- Documentation site
- `apps/storybook` -- Component storybook
- `packages/ui` -- Shared component library
- `packages/api-client` -- Generated API client
- `packages/config` -- Shared configuration
- `packages/types` -- Shared TypeScript types
- `packages/state` -- State management
- `packages/env-manager` -- Environment configuration

## Commands

```bash
bun install          # Install dependencies
bun run dev          # Start web app dev server
bun run dev:all      # Start all apps in parallel
bun run build        # Build all workspaces
bun run typecheck    # Type-check all workspaces
```
