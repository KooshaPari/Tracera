Bun-powered TypeScript monorepo using Turborepo for Tracera.

**Apps:** web (Next.js), desktop, docs, storybook
**Packages:** ui, api-client, config, types, state, env-manager

bun install          # install dependencies
bun run dev          # start web dev server
bun run dev:all      # start all apps in parallel
bun run build        # build all workspaces
bun run typecheck    # type-check all workspaces
