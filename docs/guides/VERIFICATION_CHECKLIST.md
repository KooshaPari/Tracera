# Post-Upgrade Verification Checklist

## Installation Verification
- [x] Root dependencies installed (`bun install` succeeded)
- [x] TypeScript 6.0.0-dev.20251201 installed
- [x] Biome 2.3.8 installed
- [x] All workspace packages resolved

## Toolchain Verification
```bash
# Verify versions
bun --version          # Should show 1.2.9+
tsc --version          # Should show 6.0.0-dev
biome --version        # Should show 2.3.8

# Test tooling
bun run lint           # Run Biome linter
bun run format:check   # Check formatting
bun run typecheck      # Type-check with TS 6.0
```

## Package-Level Tests

### Root
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
bun run lint
bun run format:check
```

### Frontend Monorepo
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend
bun run lint
bun run lint:oxc       # Test oxlint
bun run typecheck
```

### Web App
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web
bun run lint
bun run typecheck
bun run test           # Vitest
bun run test:e2e       # Playwright
```

## Expected Results

### TypeScript Version
```
$ tsc --version
Version 6.0.0-dev.20251201
```

### Biome Version
```
$ biome --version
2.3.8
```

### Bun Version
```
$ bun --version
1.2.9+
```

## Common Issues & Solutions

### Issue: Biome errors about configuration
**Solution**: Ensure only one biome.json at root (nested configs removed)

### Issue: TypeScript compilation errors
**Solution**: Review strict mode options in tsconfig.json, TS 6.0 is stricter

### Issue: Import errors
**Solution**: Run `bun run lint:fix` to auto-organize imports

### Issue: oxlint not found
**Solution**: Run `bun install` again to ensure oxlint binary is installed

## Next Actions

1. **Run full test suite**:
   ```bash
   cd frontend/apps/web
   bun run test:all
   ```

2. **Build verification**:
   ```bash
   bun run build
   ```

3. **Development server**:
   ```bash
   bun run dev
   ```

4. **Apply auto-fixes**:
   ```bash
   bun run lint:fix
   bun run format
   ```

## Sign-Off

- [x] Dependencies installed successfully
- [x] TypeScript 6.0-dev active
- [x] Biome configured
- [x] All package.json files updated
- [x] All tsconfig.json files updated
- [x] ESLint configs removed
- [ ] Full test suite passes (run manually)
- [ ] Build succeeds (run manually)
- [ ] Dev server starts (run manually)

**Upgrade Completed**: December 1, 2025
**Toolchain**: TypeScript 6.0-dev + Biome 2.3.8 + Bun 1.2.9
