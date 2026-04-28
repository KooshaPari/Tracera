# Turbo Pipeline - Command Reference Card

## 🚀 Quick Commands

### Build

```bash
bun run build              # Optimized build (8 concurrent)
bun run build:web          # Web app only
bun run build:docs         # Docs only
bun run build:parallel     # Maximum parallelism
```

### Test

```bash
bun run test               # Tests (4 concurrent)
bun run test:parallel      # Maximum test parallelism
```

### Other

```bash
bun run typecheck          # Typecheck (8 concurrent)
bun run lint:turbo         # Lint (8 concurrent)
bun run clean              # Clean all caches
```

### CI/CD

```bash
bun run ci:build           # Build + typecheck + lint
bun run ci:test            # Tests with minimal output
```

### Benchmark

```bash
./scripts/benchmark-turbo.sh    # Run full benchmark
```

---

## 🔍 Verification Commands

### Cache Stats

```bash
turbo build --summarize           # Show cache hit rate
du -sh .turbo/cache              # Cache size
find .turbo/cache -type f | wc -l # Cache files
```

### Task Graph

```bash
turbo build --dry-run            # Show what would run
turbo build --dry-run --graph    # Dependency graph
```

### Performance

```bash
time bun run build               # Measure build time
turbo build --profile            # Profile performance
```

### Cache Control

```bash
turbo build --force              # Bypass cache
rm -rf .turbo/cache             # Clear cache
turbo clean                      # Clean all outputs
```

---

## 📊 Expected Performance

| Command              | Cold | Warm | Target |
| -------------------- | ---- | ---- | ------ |
| `bun run build`      | <45s | <5s  | ✓      |
| `bun run build:web`  | <15s | <3s  | ✓      |
| `bun run typecheck`  | <15s | <2s  | ✓      |
| `bun run lint:turbo` | <10s | <2s  | ✓      |

---

## 🛠️ Troubleshooting

### Slow Build

```bash
# Clear and rebuild
bun run clean
bun install
bun run build
```

### Cache Not Working

```bash
# Force rebuild
turbo build --force

# Check cache stats
turbo build --summarize
```

### Dependency Issues

```bash
# Reinstall
rm -rf node_modules
bun install
```

---

## 📚 Documentation

- **Quick Start**: `TURBO_QUICK_START.md`
- **Full Guide**: `TURBO_OPTIMIZATION_GUIDE.md`
- **Main Index**: `README_TURBO_OPTIMIZATION.md`

---

**Updated**: 2026-01-30
