# CLAUDE.md — frontend (Tracera monorepo subdirectory)

TraceRTM frontend monorepo. React 19, TanStack Router, Tailwind CSS v4, Bun, Turborepo.

## Stack

| Layer | Technology |
|-------|------------|
| UI framework | React 19, React DOM 19 |
| Routing | TanStack Router v1 |
| Styling | Tailwind CSS v4, Geist font |
| State | TanStack Query, Zustand |
| Build | Vite 8, Turborepo 2 |
| Package manager | Bun (`packageManager: bun@1.1.38`) |
| Monorepo | Turborepo with `apps/*` and `packages/*` workspaces |
| Testing | Vitest |
| Storybook | Storybook 8.6.14 |
| Design | Radix UI, shadcn/ui patterns |

## Apps & Packages

```
apps/
  web/          # Main web application
  docs/         # Documentation site
  storybook/    # Storybook explorer
  desktop/      # Desktop app (Tauri or similar)
packages/
  <shared-ui>/  # Shared component library
  <shared-utils>/ # Shared utilities
```

## Dev Commands

```bash
# Install deps (runs postinstall patch scripts)
bun install

# Dev
bun run dev              # web app only
bun run dev:all          # all apps with turbo
bun run dev:docs         # docs only
bun run dev:storybook    # storybook only

# Build
bun run build            # all apps
bun run build:web        # web app only
bun run build:docs       # docs only

# Quality
bun run quality          # lint + typecheck + build + test
bun run check           # lint + format:check + typecheck
bun run lint            # oxlint (web + packages)
bun run format          # oxfmt
bun run typecheck        # oxlint-tsgolint

# Test
bun run test             # all packages via turbo
bun run test:parallel    # parallel test execution

# Figma sync
bun run figma:sync       # pull designs from Figma
bun run figma:push       # push to Figma
```

## Quality Standards

- oxlint for linting (React, TypeScript, import, JSX-a11y, perf, promise plugins)
- oxfmt for formatting
- stylelint for CSS
- TypeScript strict mode
- Zero new lint suppressions without inline justification
- Radix UI / headless patterns preferred — no plain HTML forms

## Design System

Rich UI mandate: use Radix UI, shadcn patterns, hover-to-expand, progressive disclosure. Dark mode first.

```css
/* impeccable CSS baseline — github.com/pbakaus/impeccable */
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; text-rendering: optimizeLegibility; }
img, video { max-width: 100%; height: auto; }
input, button, textarea, select { font: inherit; }
p, h1, h2, h3, h4, h5, h6 { overflow-wrap: break-word; }
```

Add the above to `globals.css` and app `custom.css` files.

## Postinstall Patches

The `postinstall` script runs multiple patch scripts. If build fails after deps change, check:
- `scripts/patch-jiti.sh`
- `scripts/patch-compose-refs.js`
- `scripts/patch-doctrine.js`
- `scripts/patch-enhanced-resolve.js`
- `scripts/patch-next-document.js`
- `scripts/patch-react-dom-shim.cjs`
- `scripts/patch-storybook-theming.cjs`

## Governance

- Reference: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
- Specs: `AgilePlus/kitty-specs/<feature-id>/`
- Worklog: `AgilePlus/.work-audit/worklog.md`

## Note

This is a Tracera monorepo subdirectory. All work is committed via the Tracera worktree (`/Users/kooshapari/CodeProjects/Phenotype/repos/`), not a standalone repo.
