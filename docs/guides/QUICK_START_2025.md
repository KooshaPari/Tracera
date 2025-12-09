# Quick Start Guide - TraceRTM 2025 Toolchain

## Verified Toolchain Versions ✅

```bash
Bun:        1.2.9
TypeScript: 6.0.0-dev.20251201 (bleeding-edge)
Biome:      2.3.8
Vite:       7.2.4
Vitest:     4.0.14
Playwright: 1.57.0
React:      19.2.0
```

## Essential Commands

### Development
```bash
# Start development server
bun run dev

# Start all apps in monorepo
cd frontend && bun run dev:all
```

### Code Quality
```bash
# Lint entire project (Biome)
bun run lint

# Auto-fix lint issues
bun run lint:fix

# Ultra-fast lint with oxlint (optional)
cd frontend && bun run lint:oxc

# Format all files
bun run format

# Check formatting without changes
bun run format:check

# Type-check with TypeScript 6.0
bun run typecheck
```

### Testing
```bash
# Unit tests (Vitest)
cd frontend/apps/web
bun run test

# E2E tests (Playwright)
bun run test:e2e

# Visual regression tests
bun run test:visual

# All tests
bun run test:all
```

### Building
```bash
# Build entire project
bun run build

# Build frontend only
bun run build:frontend

# Preview production build
cd frontend/apps/web
bun run preview
```

### Cleanup
```bash
# Clean node_modules
bun run clean

# Clean build artifacts
bun run clean:build

# Full clean and reinstall
bun run clean && bun install
```

## Project Structure

```
trace/
├── package.json          # Root config (TypeScript 6.0-dev)
├── bunfig.toml          # Bun configuration
├── biome.json           # Biome linter/formatter config
├── tsconfig.json        # Root TypeScript config (ES2024)
│
└── frontend/            # Frontend monorepo
    ├── package.json     # Frontend workspace root
    ├── bunfig.toml      # Frontend Bun config
    │
    ├── apps/
    │   └── web/         # Main web application
    │       ├── package.json     # Vite 7 + Vitest 4 + Playwright 1.57
    │       ├── tsconfig.json    # TS 6.0 strict mode
    │       └── src/
    │
    └── packages/
        ├── ui/          # UI components (React 19)
        ├── types/       # Shared TypeScript types
        ├── state/       # State management
        ├── api-client/  # API client
        ├── config/      # Shared configs
        └── env-manager/ # Environment manager
```

## Key Features

### TypeScript 6.0-dev
- **Bleeding-edge features**: Latest TypeScript development build
- **Stricter type checking**: Enhanced safety with new compiler options
- **ES2024 target**: Modern JavaScript output
- **Bundler resolution**: Optimized for Vite/Bun

### Biome (Replaces ESLint + Prettier)
- **10-100x faster**: Written in Rust
- **Single tool**: Linting + Formatting combined
- **Auto-import sorting**: Automatic import organization
- **Git integration**: Respects .gitignore
- **Strict rules**: Error on unused imports/variables, explicit any

### Bun Runtime
- **Fast installs**: Native package manager
- **Native TypeScript**: Run .ts files directly
- **Drop-in replacement**: Compatible with npm/yarn
- **Monorepo support**: Workspace handling built-in

## Configuration Files

### `bunfig.toml` (Root)
```toml
[install]
auto = true
exact = true

[run]
shell = "bun"
bun = true
```

### `biome.json` (Root)
```json
{
  "linter": {
    "rules": {
      "noUnusedImports": "error",
      "noExplicitAny": "error",
      "noUnusedVariables": "error"
    }
  }
}
```

### `tsconfig.json` (Root)
```json
{
  "compilerOptions": {
    "target": "ES2024",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedSideEffectImports": true
  }
}
```

## Common Workflows

### Add a New Dependency
```bash
# In root
bun add -D <package>

# In workspace package
cd frontend/apps/web
bun add <package>
```

### Fix Code Issues
```bash
# Auto-fix linting issues
bun run lint:fix

# Format all files
bun run format

# Organize imports
bun run lint:fix  # Biome auto-organizes imports
```

### Run Tests Before Commit
```bash
cd frontend/apps/web
bun run lint && bun run typecheck && bun run test
```

### Update Dependencies
```bash
# Check for updates
bun outdated

# Update specific package
bun update <package>

# Update all packages
bun update
```

## Troubleshooting

### Biome Errors
```bash
# Check configuration
npx biome check --verbose

# Run migration if needed
npx biome migrate --write
```

### TypeScript Errors
```bash
# Check specific file
npx tsc --noEmit <file.ts>

# Check entire project
bun run typecheck
```

### Build Failures
```bash
# Clean and rebuild
bun run clean:build
bun run build
```

### Install Issues
```bash
# Clear cache and reinstall
rm -rf node_modules bun.lockb
bun install
```

## Editor Setup

### VS Code Extensions (Recommended)
- **Biome** (`biomejs.biome`) - Official Biome extension
- **TypeScript Nightly** - For TS 6.0 features
- **Bun for VS Code** - Bun support

### VS Code Settings
```json
{
  "editor.defaultFormatter": "biomejs.biome",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "quickfix.biome": "explicit",
    "source.organizeImports.biome": "explicit"
  },
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

## Performance Tips

1. **Use oxlint for CI**: Ultra-fast linting in pipelines
   ```bash
   bun run lint:oxc
   ```

2. **Enable Bun cache**: Already configured in bunfig.toml

3. **Parallel commands**: Use turbo for parallel task execution
   ```bash
   cd frontend && turbo lint typecheck
   ```

4. **Biome daemon**: Runs in background for faster checks

## Migration Notes

### From ESLint/Prettier
- Remove `.eslintrc.*` files
- Remove Prettier config
- Use `biome.json` instead
- Scripts changed: `lint` now runs Biome

### From TypeScript 5.x
- Stricter type checking enabled
- New compiler options active
- May need to fix new errors
- Better type inference

## Resources

- **TypeScript 6.0 Docs**: https://devblogs.microsoft.com/typescript/
- **Biome Docs**: https://biomejs.dev/
- **Bun Docs**: https://bun.sh/docs
- **Vite Docs**: https://vite.dev/
- **Vitest Docs**: https://vitest.dev/

## Support

For issues or questions:
1. Check UPGRADE_SUMMARY_2025_TOOLCHAIN.md
2. Check VERIFICATION_CHECKLIST.md
3. Review error messages carefully
4. Search Biome/TypeScript docs

---

**Last Updated**: December 1, 2025
**Toolchain**: TypeScript 6.0-dev + Biome 2.3.8 + Bun 1.2.9
