# Bundle Optimization Phase 1 - Completion Guide

**Working Directory**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/docs/`

## 🚨 Current Status: BLOCKED

**Root Cause**: Build infrastructure issues preventing bundle analysis
**Impact**: Cannot measure bundle size improvements
**Priority**: HIGH - Must fix before proceeding

## 🔧 Step-by-Step Fix Instructions

### Step 1: Fix Module Resolution Issues

The build is failing because it cannot find several modules. Check each one:

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/docs

# Check if these files exist:
ls -la app/api/search/route.ts
ls -la source.ts
ls -la components/mdx-components.tsx
ls -la components/icon-sprite.tsx  # May be missing

# Check tsconfig.json paths
cat tsconfig.json | grep -A 10 "paths"
```

**Expected paths in tsconfig.json**:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

**Fix if missing files**:

```bash
# If icon-sprite.tsx is missing, create a placeholder:
cat > components/icon-sprite.tsx << 'EOF'
export function IconSprite() {
  return null;
}
EOF
```

### Step 2: Clean Next.js Configuration

Remove duplicate/conflicting config files:

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/docs

# List all Next.js configs
ls -la next.config.*

# Should only have:
# - next.config.ts (main config with optimizations)

# Remove others:
rm -f next.config.analyze.ts
rm -f next.config.js
```

### Step 3: Update Next.js Configuration

Remove deprecated `swcMinify` option (it's now default in Next.js 15):

```typescript
// Edit next.config.ts
// Remove this line:
  swcMinify: true,  // ❌ Remove - deprecated
```

**Updated next.config.ts**:

```typescript
import type { NextConfig } from 'next';
import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

const nextConfig: NextConfig = {
  reactStrictMode: true,
  pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx'],

  experimental: {
    optimizePackageImports: ['fumadocs-ui', 'fumadocs-core', 'fumadocs-openapi', 'lucide-react'],
  },

  productionBrowserSourceMaps: false,

  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        usedExports: true,
        sideEffects: true,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            react: {
              test: /[\\/]node_modules[\\/](react|react-dom|scheduler)[\\/]/,
              name: 'react',
              priority: 40,
            },
            fumadocs: {
              test: /[\\/]node_modules[\\/](fumadocs-ui|fumadocs-core|fumadocs-openapi|fumadocs-mdx)[\\/]/,
              name: 'fumadocs',
              priority: 35,
            },
            lucide: {
              test: /[\\/]node_modules[\\/]lucide-react[\\/]/,
              name: 'lucide-icons',
              priority: 25,
            },
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendor',
              priority: 20,
            },
          },
        },
      };
    }
    return config;
  },

  compress: true,
  poweredByHeader: false,
};

export default withBundleAnalyzer(withMDX(nextConfig));
```

### Step 4: Clean Build Environment

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/docs

# Remove build artifacts
rm -rf .next
rm -rf node_modules/.cache

# Optionally reinstall dependencies
rm -rf node_modules
bun install
```

### Step 5: Test Build

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/docs

# Try building without analysis first
bun run build

# If successful, try with analysis
ANALYZE=true bun run build
```

**Expected Output**:

```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages
✓ Finalizing page optimization

Route (app)                              Size     First Load JS
┌ ○ /                                    X.XX kB    XXX kB
├ ○ /docs                                X.XX kB    XXX kB
└ ○ /api-reference                       X.XX kB    XXX kB
```

### Step 6: Analyze Bundle

Once build works:

```bash
# Build with analyzer
ANALYZE=true bun run build

# This will open a browser with bundle visualization
# Check these chunks:
# - react.js (should be <50KB)
# - fumadocs.js (should be <100KB)
# - lucide-icons.js (should be <40KB)
# - vendor.js (should be <80KB)
# - main.js (should be <100KB)
```

### Step 7: Remove Unused Dependencies

**Only after build works and is analyzed**, remove unused deps:

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/docs

# Remove unused production dependencies
bun remove @alloc/quick-lru @radix-ui/react-dropdown-menu \
  @radix-ui/react-slot @tailwindcss/typography \
  class-variance-authority cmdk fast-uri get-nonce \
  hast-util-to-html json-schema-traverse \
  micromark-factory-destination micromark-factory-label \
  micromark-factory-space micromark-factory-title \
  micromark-factory-whitespace tailwindcss-animate zod

# Remove unused dev dependencies
bun remove @types/react-dom autoprefixer postcss

# Rebuild to verify nothing broke
bun run build
```

### Step 8: Benchmark Results

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/docs

# Check bundle sizes
ls -lh .next/static/chunks/*.js

# Run Lighthouse
bun run lighthouse

# Compare before/after
cat << EOF
BEFORE (estimated):
- Total bundle: ~800KB
- Main chunk: ~500KB
- Vendor: ~300KB

AFTER (target):
- Total bundle: <200KB (75% reduction)
- Main chunk: <100KB
- Vendor: <80KB
EOF
```

## 📊 Success Metrics

Run these checks to verify success:

```bash
# 1. Build succeeds
bun run build && echo "✅ Build successful"

# 2. Bundle analyzer shows chunks
ANALYZE=true bun run build && echo "✅ Analysis complete"

# 3. Check gzipped sizes
find .next/static/chunks -name "*.js" -exec sh -c 'gzip -c {} | wc -c | numfmt --to=iec-i --suffix=B --padding=10 && echo " {}"' \;

# 4. Lighthouse score
bun run lighthouse | grep "Performance score"

# 5. No errors in build log
bun run build 2>&1 | grep -i error && echo "❌ Errors found" || echo "✅ No errors"
```

## 🎯 Target Metrics

| Metric                 | Target | How to Check                                                         |
| ---------------------- | ------ | -------------------------------------------------------------------- |
| Total bundle (gzipped) | <200KB | `find .next/static/chunks -name "*.js" -exec gzip -c {} \; \| wc -c` |
| Main chunk             | <100KB | Check bundle analyzer                                                |
| React chunk            | <50KB  | Check bundle analyzer                                                |
| Fumadocs chunk         | <100KB | Check bundle analyzer                                                |
| Vendor chunk           | <80KB  | Check bundle analyzer                                                |
| Lighthouse Performance | >90    | `bun run lighthouse`                                                 |

## 🚫 Common Issues & Fixes

### Issue: "Cannot find module '@/source'"

**Cause**: Next.js hasn't generated .source yet
**Fix**:

```bash
# .source is generated during Next.js build
# Make sure source.config.ts exists
ls -la source.config.ts
```

### Issue: "swcMinify is not a valid option"

**Cause**: Deprecated in Next.js 15
**Fix**: Remove from next.config.ts

### Issue: Build hangs or takes >5 minutes

**Cause**: Bundle analyzer might be enabled
**Fix**:

```bash
# Build without analyzer
unset ANALYZE
bun run build
```

### Issue: "Cannot find module 'tailwindcss'"

**Cause**: Missing or incorrect global Next.js
**Fix**:

```bash
# Use local Next.js
./node_modules/.bin/next build
# OR
bun x next build
```

## 📁 Files Modified in Phase 1

```
frontend/apps/docs/
├── next.config.ts                          # ✅ Code splitting + optimization
├── components/
│   ├── mdx-components.tsx                  # ✅ Using lazy components
│   └── mdx-components-lazy.tsx             # ✅ NEW: Lazy loaders
├── app/
│   └── api-reference/[[...slug]]/page.tsx  # ✅ Lazy APIPage
├── package.json                            # ⚠️ Dependencies updated
├── BUNDLE_OPTIMIZATION_PHASE_1_SUMMARY.md  # ✅ Summary doc
└── BUNDLE_OPTIMIZATION_COMPLETION_GUIDE.md # ✅ This file
```

## 🔄 Rollback Plan

If optimizations cause issues:

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/docs

# Revert next.config.ts
git checkout next.config.ts

# Revert component changes
git checkout components/mdx-components.tsx
rm components/mdx-components-lazy.tsx

# Revert API reference
git checkout app/api-reference/[[...slug]]/page.tsx

# Reinstall original dependencies
git checkout package.json
bun install

# Test
bun run build
```

## 📝 Next Phase (Phase 2)

After Phase 1 completes:

1. **Further dynamic imports**: Search components, code blocks
2. **Image optimization**: WebP conversion, responsive images
3. **Font optimization**: Subset fonts, preload critical fonts
4. **CSS optimization**: PurgeCSS, critical CSS extraction
5. **Service Worker**: Precache critical assets
6. **HTTP/3 & Brotli**: Better compression

**Expected additional reduction**: 10-20% (20-40KB)

## 🆘 Getting Help

If blocked:

1. **Check build logs**:

   ```bash
   bun run build 2>&1 | tee build-error.log
   cat build-error.log | grep -A 5 "Error"
   ```

2. **Verify environment**:

   ```bash
   node --version  # Should be 20+
   bun --version   # Should be 1.2+
   next --version  # Should be 15+
   ```

3. **Check for conflicts**:

   ```bash
   # Multiple Next.js versions?
   find . -name "next" -type f

   # Multiple config files?
   ls next.config.*
   ```

## ✅ Completion Checklist

- [ ] Module resolution fixed (all imports work)
- [ ] Config consolidated (only next.config.ts exists)
- [ ] swcMinify removed from config
- [ ] Build completes successfully
- [ ] Bundle analyzer generates report
- [ ] Chunks are properly split (react, fumadocs, lucide, vendor)
- [ ] Unused dependencies removed
- [ ] Total bundle <200KB gzipped
- [ ] Lighthouse performance >90
- [ ] All tests pass
- [ ] Documentation updated

## 📚 References

- [Next.js Code Splitting](https://nextjs.org/docs/app/building-your-application/optimizing/lazy-loading)
- [Webpack Manual Chunks](https://webpack.js.org/plugins/split-chunks-plugin/)
- [@next/bundle-analyzer](https://www.npmjs.com/package/@next/bundle-analyzer)
- [Fumadocs Optimization](https://fumadocs.vercel.app/docs/headless/mdx/configuration)
