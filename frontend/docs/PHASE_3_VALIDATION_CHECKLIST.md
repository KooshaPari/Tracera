# Phase 3: Build Optimization - Validation Checklist

## Pre-Flight Checks

### Environment Setup
- [ ] Node.js version ≥ 20.19 or ≥ 22.12
- [ ] Bun version ≥ 1.1.38
- [ ] Clean working directory (`git status` shows no unexpected changes)
- [ ] All dependencies installed (`bun install`)

## Configuration Validation

### Vite Configuration
**File**: `apps/web/vite.config.mjs`

- [x] ✅ `build.target` set to `"esnext"`
- [x] ✅ `build.reportCompressedSize` set to `false`
- [x] ✅ `build.assetsInlineLimit` set to `4096`
- [x] ✅ `build.minify` set to `"esbuild"`
- [x] ✅ `build.cssCodeSplit` set to `true`
- [x] ✅ `build.rollupOptions.treeshake` configured with aggressive options
- [x] ✅ `build.rollupOptions.output.compact` set to `true`
- [x] ✅ `build.rollupOptions.output.format` set to `"es"`
- [x] ✅ `build.rollupOptions.output.manualChunks` configured
- [x] ✅ `server.host` set to `true`
- [x] ✅ `server.hmr` configured
- [x] ✅ `server.watch.ignored` includes heavy directories
- [x] ✅ `server.watch.usePolling` set to `false`
- [x] ✅ `server.warmup.clientFiles` configured
- [x] ✅ React Compiler plugin made optional

### TypeScript Configuration

#### Root Config
**File**: `tsconfig.json`

- [x] ✅ `references` array includes all packages
- [x] ✅ References: `./packages/types`
- [x] ✅ References: `./packages/state`
- [x] ✅ References: `./packages/ui`
- [x] ✅ References: `./packages/api-client`
- [x] ✅ References: `./packages/config`
- [x] ✅ References: `./apps/web`

#### Package Configs
**Files**: `packages/*/tsconfig.json`

For each package, verify:
- [x] ✅ `compilerOptions.composite` set to `true`
- [x] ✅ `compilerOptions.declaration` set to `true`
- [x] ✅ `compilerOptions.declarationMap` set to `true`
- [x] ✅ `compilerOptions.incremental` set to `true`
- [x] ✅ `compilerOptions.tsBuildInfoFile` set to `".tsbuildinfo"`
- [x] ✅ `compilerOptions.outDir` set to `"dist"`
- [x] ✅ `compilerOptions.rootDir` set to `"src"`
- [x] ✅ `references` array includes dependencies (where applicable)

Packages validated:
- [x] ✅ `packages/types/tsconfig.json`
- [x] ✅ `packages/state/tsconfig.json`
- [x] ✅ `packages/ui/tsconfig.json`
- [x] ✅ `packages/api-client/tsconfig.json`
- [x] ✅ `packages/config/tsconfig.json`

#### Web App Config
**File**: `apps/web/tsconfig.json`

- [x] ✅ `references` includes all shared packages

### Build Scripts

#### Package Scripts
**Files**: `packages/*/package.json`

For each package, verify scripts:
- [x] ✅ `build`: `"tsc --build"`
- [x] ✅ `clean`: `"tsc --build --clean"`
- [x] ✅ `typecheck`: `"tsc --noEmit"`

Packages validated:
- [x] ✅ `packages/types/package.json`
- [x] ✅ `packages/state/package.json`
- [x] ✅ `packages/ui/package.json`
- [x] ✅ `packages/api-client/package.json`
- [x] ✅ `packages/config/package.json`

#### Web App Scripts
**File**: `apps/web/package.json`

- [x] ✅ `build`: `"tsc --build && vite build"`
- [x] ✅ `build:fast`: `"vite build"`
- [x] ✅ `build:clean`: `"tsc --build --clean && rm -rf dist"`

### Turbo Configuration
**File**: `turbo.json`

- [x] ✅ `tasks.build.outputs` includes `".tsbuildinfo"`
- [x] ✅ `tasks.build:fast` task added
- [x] ✅ `tasks.build:clean` task added
- [x] ✅ `tasks.build.dependsOn` set to `["^build"]`

## Functional Testing

### Build Commands

#### Clean Build
```bash
bun run build:clean
bun run build
```

- [ ] ✅ Build completes successfully
- [ ] ✅ No TypeScript errors
- [ ] ✅ `.tsbuildinfo` files created in all packages
- [ ] ✅ `dist/` directory created in `apps/web`
- [ ] ✅ Build time < 20s (first build may be slower)

#### Incremental Build
```bash
# Run build twice
bun run build
bun run build
```

- [ ] ✅ Second build completes successfully
- [ ] ✅ Second build is significantly faster (< 5s)
- [ ] ✅ Turbo reports cache hits
- [ ] ✅ TypeScript uses cached build info

#### Fast Build
```bash
bun run build:fast
```

- [ ] ✅ Build completes successfully
- [ ] ✅ Build time < 10s
- [ ] ✅ Skips TypeScript compilation
- [ ] ✅ Output in `dist/` is correct

### TypeScript Validation

#### Type Checking
```bash
bun run typecheck
```

- [ ] ✅ No type errors
- [ ] ✅ All packages type-check successfully
- [ ] ✅ Cross-package types resolve correctly

#### Build Info Files
```bash
find . -name ".tsbuildinfo"
```

- [ ] ✅ `.tsbuildinfo` exists in all packages
- [ ] ✅ Files contain valid JSON
- [ ] ✅ Files are cached by Turbo

### Development Server

#### Server Startup
```bash
bun run dev
```

- [ ] ✅ Server starts in < 5s
- [ ] ✅ No errors in console
- [ ] ✅ HMR overlay enabled
- [ ] ✅ Routes warm up correctly

#### Hot Module Replacement
Make a change to a component:

- [ ] ✅ HMR update occurs in < 100ms
- [ ] ✅ Page updates without full reload
- [ ] ✅ React Fast Refresh works
- [ ] ✅ No console errors

### Bundle Analysis

#### Chunk Verification
```bash
bun run build
ls -lh apps/web/dist/assets/
```

Verify chunks exist:
- [ ] ✅ `vendor-react-*.js`
- [ ] ✅ `vendor-router-*.js`
- [ ] ✅ `vendor-radix-*.js`
- [ ] ✅ `vendor-icons-*.js`
- [ ] ✅ `vendor-forms-*.js`
- [ ] ✅ `vendor-table-*.js`
- [ ] ✅ Other vendor chunks as configured

#### Chunk Sizes
Verify reasonable sizes:
- [ ] ✅ `vendor-react` ≈ 150KB
- [ ] ✅ `vendor-router` ≈ 100KB
- [ ] ✅ `vendor-graph-elk` ≈ 300KB (lazy loaded)
- [ ] ✅ `vendor-monaco` ≈ 2MB (lazy loaded)

## Performance Benchmarks

### Build Time Targets

Run each command 3 times and average:

#### Full Build
```bash
time bun run build
```

- [ ] ✅ Average < 15s
- [ ] ✅ Consistent across runs (±2s)

#### Incremental Build
```bash
bun run build
time bun run build
```

- [ ] ✅ Average < 5s
- [ ] ✅ Turbo cache hits reported

#### TypeScript Only
```bash
time bun run typecheck
```

- [ ] ✅ Average < 3s

#### Dev Server Start
```bash
time bun run dev
```

- [ ] ✅ Server ready in < 3s

### Bundle Size Targets

```bash
bun run build
du -sh apps/web/dist/
```

- [ ] ✅ Total dist size reasonable (< 10MB)
- [ ] ✅ Largest chunks are lazy-loaded
- [ ] ✅ Core bundle is small (< 500KB)

## Turbo Validation

### Cache Behavior
```bash
# First build
bun run build

# Second build (should hit cache)
bun run build --dry-run=json
```

- [ ] ✅ All tasks show "cache hit"
- [ ] ✅ No tasks re-run unnecessarily

### Parallel Execution
```bash
turbo run build --graph
```

- [ ] ✅ Independent packages build in parallel
- [ ] ✅ Dependency order respected
- [ ] ✅ Visualization shows correct DAG

### Force Rebuild
```bash
turbo run build --force
```

- [ ] ✅ Cache ignored
- [ ] ✅ All tasks re-run
- [ ] ✅ New cache entries created

## Documentation Validation

### Files Created
- [x] ✅ `BUILD_OPTIMIZATION_GUIDE.md` exists
- [x] ✅ `BUILD_OPTIMIZATION_QUICKSTART.md` exists
- [x] ✅ `BUILD_OPTIMIZATION_ARCHITECTURE.md` exists
- [x] ✅ `PHASE_3_BUILD_OPTIMIZATION_SUMMARY.md` exists
- [x] ✅ `PHASE_3_VALIDATION_CHECKLIST.md` exists (this file)

### Documentation Quality
- [ ] ✅ All links work
- [ ] ✅ Code examples are correct
- [ ] ✅ Commands are accurate
- [ ] ✅ Diagrams are clear

## Troubleshooting Scenarios

### Scenario 1: Build Fails
```bash
bun run build:clean
rm -rf node_modules/.cache
bun install --force
bun run build
```

- [ ] ✅ Recovery procedure works
- [ ] ✅ Build succeeds after cleanup

### Scenario 2: Type Errors
```bash
tsc --build --clean
tsc --build --force
bun run typecheck
```

- [ ] ✅ Types rebuild correctly
- [ ] ✅ No lingering errors

### Scenario 3: Cache Corruption
```bash
turbo run build --force
rm -rf .turbo
bun run build
```

- [ ] ✅ Cache rebuilds
- [ ] ✅ Subsequent builds cache correctly

## Integration Testing

### CI/CD Simulation
```bash
# Simulate CI environment
rm -rf node_modules .turbo
bun install --frozen-lockfile
bun run ci:build
```

- [ ] ✅ Clean install works
- [ ] ✅ Build completes successfully
- [ ] ✅ All checks pass

### Developer Workflow
```bash
# Simulate typical workflow
git pull
bun install
bun run build:fast
bun run dev
```

- [ ] ✅ Quick start after pull
- [ ] ✅ Dev server starts fast
- [ ] ✅ HMR works correctly

## Final Validation

### Checklist Summary

#### Critical Items (Must Pass)
- [ ] ✅ All configuration files correct
- [ ] ✅ TypeScript project references working
- [ ] ✅ Incremental builds functional
- [ ] ✅ Full build < 15s
- [ ] ✅ Incremental build < 5s
- [ ] ✅ Dev server starts < 3s
- [ ] ✅ No TypeScript errors
- [ ] ✅ All chunks generated correctly

#### Important Items (Should Pass)
- [ ] ✅ Documentation complete
- [ ] ✅ Turbo caching works
- [ ] ✅ Bundle sizes reasonable
- [ ] ✅ HMR < 100ms
- [ ] ✅ Chunk splitting optimal

#### Nice-to-Have Items (Optional)
- [ ] Bundle analysis run
- [ ] Performance profiling done
- [ ] Cache warming tested
- [ ] Remote caching configured

## Sign-Off

### Developer
- [ ] All critical items passed
- [ ] All important items passed
- [ ] Documentation reviewed
- [ ] Ready for team review

### Reviewer
- [ ] Configuration validated
- [ ] Build times verified
- [ ] Bundle analysis reviewed
- [ ] Documentation approved

### Team Lead
- [ ] Performance targets met
- [ ] Architecture approved
- [ ] Ready for production

---

**Validation Date**: _____________
**Validated By**: _____________
**Status**: ⬜ Pending | ⬜ In Progress | ⬜ Complete | ⬜ Approved
**Phase**: 3 - Build Performance Optimization
