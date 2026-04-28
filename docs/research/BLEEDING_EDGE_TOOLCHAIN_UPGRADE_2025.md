# TraceRTM Bleeding-Edge Toolchain Upgrade 2025

## Overview

The TraceRTM frontend monorepo has been upgraded to the absolute latest 2025 web development toolchain with cutting-edge TypeScript, linting, and build configurations.

## Toolchain Stack

### Core Languages & Runtime
- **TypeScript**: 5.9.3 (latest stable, prepared for TS 6.0+)
  - Target: ES2022 (stable esbuild target)
  - Lib: ES2022 + DOM + DOM.Iterable
  - Strict mode: All options enabled
  - Module resolution: bundler (modern esm-first)
  - Exact optional properties: true
  - Unused locals/parameters: flagged as errors

- **Bun**: 1.2.9 (cutting-edge runtime)
  - Primary runtime for all development and builds
  - Package manager: bun (replaces npm/pnpm)
  - Bundler/transpiler: Fully integrated
  - Test runner: vitest + bun:test compatible

- **Node.js**: 22.x (type definitions via @types/node@22.19.1)

### Linting & Formatting
- **Biome**: 2.3.8 (Rust-based, replaces ESLint + Prettier)
  - Single tool for linting + formatting
  - 10-100x faster than ESLint
  - React 19 support built-in
  - Import organization (natsort)
  - Unified configuration in biome.json

- **oxlint**: 0.16.12 (optional, ultra-fast linter)
  - Rust-based alternative/supplement to Biome
  - Great for CI/CD performance
  - Can run in parallel with Biome

### Build Tools
- **Vite**: 7.2.4 (latest v7)
  - Modern ESM-first bundler
  - Lightning-fast HMR
  - Native Rolldown integration in development

- **TanStack Tools** (Latest):
  - @tanstack/react-router@1.91.2 - File-based routing
  - @tanstack/start@1.91.2 - Full-stack meta-framework
  - @tanstack/react-query@5.90.11 - Server state
  - @tanstack/react-table@8.21.3 - Table rendering
  - @tanstack/react-virtual@3.13.12 - Virtual scrolling

### Testing Stack
- **Vitest**: 4.0.14
  - Unit & component tests
  - jsdom environment
  - V8 coverage provider
  - 80% coverage thresholds

- **Playwright**: 1.57.0
  - E2E testing (205 tests)
  - Visual regression (248 test executions)
  - Cross-browser (Chromium, Firefox, WebKit)
  - Screenshots, videos, traces

### UI & Styling
- **React**: 19.2.0 (latest, with stable features)
- **TailwindCSS**: 4.1.17 (latest v4, new engine)
- **Radix UI**: Latest versions for all components
- **PostCSS**: 8.5.6
- **Autoprefixer**: 10.4.22

### Development Dependencies
- **TypeScript ESLint**: typescript-eslint@8.17.0 (for IDE support, Biome for linting)
- **React Testing Library**: @testing-library/react@16.0.1
- **jest-axe**: 10.0.0 (accessibility testing)
- **axe-core**: 4.11.0 (a11y validation engine)
- **DOMPurify**: 3.2.7 (XSS prevention)
- **zod**: 4.1.13 (runtime validation)
- **zustand**: 5.0.9 (state management)
- **MSW**: 2.12.3 (API mocking)

## Configuration Files

### Root Level
```
/bunfig.toml              # Bun runtime configuration
/biome.json              # Unified linter/formatter config
/tsconfig.json           # Root TypeScript config
```

### Frontend Monorepo
```
frontend/package.json              # Workspace definition
frontend/tsconfig.json             # Shared TS config
frontend/biome.json                # Local biome config (extends root)

frontend/apps/web/
├── vitest.config.ts              # Unit/component test config
├── playwright.config.ts           # E2E test config
├── playwright-visual.config.ts   # Visual regression config
└── tsconfig.json                 # App-specific TS config

frontend/packages/*/tsconfig.json  # Package-specific configs
```

## Scripts

### Linting & Formatting
```bash
# Check code
bun run lint

# Fix issues automatically
bun run lint:fix

# Format code
bun run format

# Check formatting (no write)
bun run format:check
```

### Building
```bash
# Build all frontend packages
bun run build

# Build specific package
cd frontend/apps/web && bun run build
```

### Testing
```bash
# Run all unit/component tests
bun run test

# Watch mode
bun run test:watch

# Coverage report
bun run test:coverage

# E2E tests
bun run test:e2e

# Visual regression
bun run test:visual

# Accessibility tests
bun run test:a11y

# Security tests
bun run test:security
```

### Type Checking
```bash
bun run typecheck
```

## Upgrade Details

### TypeScript Configuration Strategy
- **Stable Target**: ES2022 (widely supported in modern browsers and Node.js)
- **Strict Mode**: All features enabled for maximum type safety
- **Module Resolution**: "bundler" for modern ESM with proper package.json exports resolution
- **Future Ready**: Configurations prepared for TypeScript 6.0 upgrade when released
  - Keep watching for noUncheckedSideEffectImports (TS 5.10+)
  - Ready for ES2024 when stable

### Biome Configuration
- **React 19 JSX**: react-jsx preset
- **Imports**: Organized with natsort for consistency
- **Formatting**: 2-space indentation, 100 char line width
- **Linting**: All errors active, optional warnings
- **No ESLint**: Completely replaced

### Bun Integration
- **Package Manager**: bun replaces npm/pnpm
- **Lockfile**: bun.lockb (binary, faster than package-lock.json)
- **Runtime**: Used for all development scripts
- **Type Support**: @types/bun@1.3.3

## Test Coverage Summary

| Test Type | Count | Status |
|-----------|-------|--------|
| Unit | ~300 | ✅ Complete |
| Component | ~150 | ✅ Complete |
| Integration | ~20 | ✅ Complete |
| E2E | 205 | ✅ Complete |
| Visual Regression | 248 executions | ✅ Complete |
| Accessibility (a11y) | 80 | ✅ Complete |
| Security | 226 | ✅ Complete |
| **Total** | **~1,230+** | ✅ **Comprehensive** |

## Performance Notes

### Build Performance
- Vite v7: Near-instant HMR
- Biome linting: 10-100x faster than ESLint
- Bun package manager: Extremely fast installs
- Bun runtime: Faster than Node.js for build scripts

### Runtime Performance
- ES2022 target: No transpilation overhead for modern browsers
- Tree-shaking: Enabled by default with esbuild
- Code splitting: Automatic with Vite
- Lazy loading: React Router file-based routes

## Migration from Previous Setup

### ESLint → Biome
```bash
# Old (no longer used)
npm run lint    # ESLint

# New
bun run lint    # Biome (faster, simpler)
```

### npm/pnpm → bun
```bash
# Old
npm install
pnpm install

# New
bun install     # Much faster
```

### TypeScript 5.8 → 5.9
- Full compatibility maintained
- Stricter checking enabled
- Ready for TS 6.0 when released

## Known Limitations & Next Steps

### Current Build Issue
- TanStack Start/Vinxi needs configuration update for latest compatibility
- Build works with individual packages, some dependencies need addressing
- Workaround: Use vite directly for web app if needed

### Future Upgrades
- **TypeScript 6.0**: When officially released, update constraints and enable:
  - `noUncheckedSideEffectImports`
  - ES2024 target (once esbuild supports it)

- **Rolldown**: When v1.0 released, can replace Rollup in Vite completely

- **Oxc**: Can be primary linter if performance needed in CI/CD

## Verification Commands

```bash
# Check versions
bun --version           # Should be 1.2.9+
bun run --version      # Package manager version

# Type check
bun run typecheck

# Lint entire monorepo
bun run lint

# Build specific app
cd frontend/apps/web && bun run build

# Run tests
bun run test:a11y
bun run test:security
bun run test:e2e
bun run test:visual
```

## Documentation

See also:
- `docs/STATUS.md` - Project status and tech stack
- `frontend/apps/web/MSW_SETUP.md` - Mock Service Worker setup
- `frontend/apps/web/vitest.config.ts` - Unit test configuration
- `frontend/apps/web/playwright.config.ts` - E2E configuration

---

**Last Updated**: December 2, 2025
**Status**: ✅ Toolchain ready for production development
**Next Phase**: Fix TanStack Start build configuration for full integration
