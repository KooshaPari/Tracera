# Build Optimization Quick Start

## 🚀 Quick Commands

```bash
# Development
bun run dev              # Start dev server (~3s)

# Production Builds
bun run build            # Full build with type checking (<15s)
bun run build:fast       # Skip type check (<10s)
bun run build:clean      # Clean + rebuild (<20s)

# Type Checking
bun run typecheck        # Check types only (<3s)

# CI/CD
bun run ci:build         # Build + typecheck + lint (parallel)
bun run ci:test          # Run all tests
```

## 📊 Performance Targets

| Operation | Target | Before |
|-----------|--------|--------|
| Full Build | <15s | ~45s |
| Incremental Build | <5s | ~30s |
| TypeScript Check | <3s | ~10s |
| Dev Server Start | <3s | ~8s |

## 🎯 Key Optimizations

### 1. Vite Config
- ✅ Tree-shaking optimized
- ✅ Modern browser target (esnext)
- ✅ Gzip size reporting disabled
- ✅ Manual chunk splitting configured
- ✅ Dev server warmup enabled

### 2. TypeScript
- ✅ Project references configured
- ✅ Incremental compilation enabled
- ✅ Declaration maps generated
- ✅ Build info cached (.tsbuildinfo)

### 3. Turbo
- ✅ Smart task caching
- ✅ Parallel execution
- ✅ Build info in outputs
- ✅ Fast build task added

## 🔧 When to Use Each Command

### Development
```bash
# First time
bun install
bun run build:clean

# Regular development
bun run dev

# After git pull (dependencies changed)
bun install
bun run build:fast
```

### Testing Locally
```bash
# Quick iteration
bun run build:fast

# Full validation before commit
bun run build
bun run typecheck
bun run lint
```

### CI/CD
```bash
# Install (with lockfile)
bun install --frozen-lockfile

# Build and validate
bun run ci:build

# Test
bun run ci:test
```

## 🐛 Troubleshooting

### Build is slow
```bash
# Clear cache and rebuild
bun run build:clean
rm -rf node_modules/.cache
turbo run build --force
```

### Type errors
```bash
# Rebuild TypeScript declarations
tsc --build --force
bun run typecheck
```

### Cache issues
```bash
# Clear Turbo cache
turbo run build --force

# Clear all caches
rm -rf node_modules/.cache
rm -rf .turbo
find . -name ".tsbuildinfo" -delete
```

## 📁 File Changes

### Modified Files
- ✅ `apps/web/vite.config.mjs` - Vite optimizations
- ✅ `apps/web/tsconfig.json` - Project references
- ✅ `apps/web/package.json` - Build scripts
- ✅ `tsconfig.json` - Root references
- ✅ `turbo.json` - Task configuration

### Created Files
- ✅ `packages/*/tsconfig.json` - TypeScript configs (5 files)
- ✅ `BUILD_OPTIMIZATION_GUIDE.md` - Full documentation
- ✅ `BUILD_OPTIMIZATION_QUICKSTART.md` - This file

## 🎓 Learn More

See [BUILD_OPTIMIZATION_GUIDE.md](./BUILD_OPTIMIZATION_GUIDE.md) for:
- Detailed optimization explanations
- Architecture decisions
- Best practices
- Advanced usage patterns
- Profiling and monitoring

---

**Status**: ✅ Complete
**Phase**: 3 - Build Performance Optimization
**Last Updated**: 2026-01-30
