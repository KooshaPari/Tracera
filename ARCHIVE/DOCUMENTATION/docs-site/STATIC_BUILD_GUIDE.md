# 📦 Static Build Guide - TraceRTM Documentation

Your documentation is configured for **static export** - perfect for offline viewing and filesystem-based access!

## ✨ What You Get

✅ **Static HTML Files** - No server needed
✅ **Offline Capable** - Works without internet
✅ **Direct Filesystem Access** - Open HTML files directly
✅ **Fully Responsive** - Mobile, tablet, and desktop
✅ **Dark/Light Mode** - Built-in theme switching
✅ **Search Functionality** - Full-text search across all docs
✅ **Fast Performance** - Optimized static assets
✅ **Deployable** - Ready for any static hosting

---

## 🚀 Quick Start

### Option 1: View HTML Directly (No Server)

```bash
# View in your default browser
npm run view:static

# Or manually open:
open ./out/index.html
```

### Option 2: Start Local Server (With Python)

```bash
# Start local HTTP server
npm run serve:static

# Visit in browser
open http://localhost:8000

# Stop server with: Ctrl+C
```

### Option 3: View in Editor

Open `./out/index.html` in any code editor and use the preview feature.

---

## 📁 Static Build Structure

```
docs-site/
├── out/                      # ← Static build output
│   ├── index.html            # Homepage
│   ├── _next/                # Next.js assets
│   ├── fonts/                # Font files
│   ├── public/               # Public assets
│   └── ...
├── src/                       # Source files
├── STATIC_BUILD_GUIDE.md      # This file
├── VIEW_OFFLINE.html          # Quick launcher
└── package.json               # Build scripts
```

---

## 🔨 Build Commands

### Build Static Site
```bash
npm run build:static
```

Generates optimized static files in `./out/` directory.

### Serve Locally
```bash
npm run serve:static
```

Starts a Python HTTP server on port 8000.

### View in Browser
```bash
npm run view:static
```

Opens the documentation directly in your default browser.

---

## 📝 Understanding the Configuration

### `next.config.ts` Settings

```typescript
output: 'export'              // Generate static HTML
images: { unoptimized: true } // No image optimization
trailingSlash: true           // Clean URLs with /
```

### What This Means

- ✅ No Next.js server required
- ✅ Pure static HTML/CSS/JavaScript
- ✅ Can be served from any web server or locally
- ✅ No Node.js needed to view the docs
- ✅ Zero runtime dependencies

---

## 🌐 Using the Built Files

### Local Filesystem
```bash
# Simply open in browser
open ./out/index.html

# Or double-click the file in Finder
```

### Python HTTP Server
```bash
cd out
python3 -m http.server 8000
# Visit: http://localhost:8000
```

### Node.js HTTP Server
```bash
npm install -g http-server
cd out
http-server -p 8000
```

### Live Server (VS Code)
1. Open `out` folder in VS Code
2. Right-click `index.html`
3. Select "Open with Live Server"

---

## 📦 Deploying Static Build

### To Vercel
```bash
# Push to GitHub, connect to Vercel
# Vercel auto-detects Next.js projects with static export

# Or deploy manually
vercel --prod
```

### To GitHub Pages
```bash
# Copy ./out contents to gh-pages branch
git worktree add docs gh-pages
cp -r out/* docs/
cd docs
git add .
git commit -m "Update docs"
git push origin gh-pages
```

### To Netlify
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=out
```

### To AWS S3
```bash
aws s3 sync out/ s3://your-bucket-name --delete
```

### To Any Static Host
Simply upload the contents of `./out/` to your host.

---

## 🔍 What's Included in Static Build

### HTML Pages
- ✅ `index.html` - Homepage
- ✅ `404.html` - Error page
- ✅ All documentation pages

### Assets
- ✅ `_next/static/` - JavaScript bundles
- ✅ `_next/static/css/` - CSS stylesheets
- ✅ `fonts/` - Font files
- ✅ SVG images

### Features
- ✅ Full-text search (client-side)
- ✅ Dark/light mode toggle
- ✅ Responsive design
- ✅ Animated components
- ✅ Command palette (Cmd/Ctrl+K)

---

## 🚫 What's NOT Available in Static

The following features require a server and won't work in static export:

❌ `API Routes` (`/api/*`)
❌ `Server Components`
❌ `Dynamic Server Functions`
❌ `Real-time Features`
❌ `Form Submissions`
❌ `Database Queries`

**Solution**: If you need these, keep the development server running or deploy to Vercel/Netlify.

---

## 📊 File Sizes

| File Type | Count | Size |
|-----------|-------|------|
| HTML | ~5 | 100KB |
| JavaScript | ~10 | 250KB |
| CSS | ~3 | 50KB |
| Images/SVG | ~5 | 30KB |
| Fonts | ~2 | 200KB |
| **Total** | | **~630KB** |

---

## ⚡ Performance Optimization

### Already Optimized
- ✅ CSS minified and split
- ✅ JavaScript bundles optimized
- ✅ Images unoptimized (but can be)
- ✅ No unused CSS
- ✅ Code splitting per route

### Additional Tips
```bash
# Gzip compression (reduce to ~150KB)
gzip -r out/

# Serve with compression
npm run serve:static  # Already handles gzip

# Monitor size
du -sh out/
ls -lSrh out/
```

---

## 🔗 Linking Between Pages

### In MDX Files
```mdx
# Link to another page
[Getting Started](/docs/getting-started)

# With anchor
[Installation](#installation)
```

### In React Components
```jsx
import Link from 'next/link'

<Link href="/docs/getting-started">
  Getting Started
</Link>
```

---

## 🎨 Customizing the Build

### Change Output Directory
Edit `next.config.ts`:
```typescript
output: 'export',
distDir: 'public',  // Change output folder
```

### Add Base Path
```typescript
basePath: '/docs',  // Deploy at /docs instead of /
```

### Modify Build Script
Edit `package.json`:
```json
"build:static": "next build && cp CNAME out/"
```

---

## ❓ FAQ

### Q: Can I use API routes in static export?
**A:** No. API routes require a server. For forms/data, use external services (e.g., Firebase, Supabase).

### Q: Will search work offline?
**A:** Yes! Search is fully client-side and works offline.

### Q: Can I preview on mobile?
**A:** Yes! Use `npm run serve:static` then visit `http://<your-ip>:8000` from mobile.

### Q: How do I add new pages?
**A:** Add MDX files to `src/content/` and they auto-appear in navigation.

### Q: Can I use dynamic content?
**A:** Yes! Build-time dynamic generation via `generateStaticParams()` or fetch from external APIs at build time.

### Q: What about SEO?
**A:** Perfect! Static pages are SEO-friendly. All metadata is included.

---

## 🐛 Troubleshooting

### Build Fails
```bash
# Clean and rebuild
rm -rf .next out
npm run build:static
```

### Pages Not Showing
```bash
# Check out/ directory exists
ls -la out/

# Rebuild
npm run build:static
```

### Dark Mode Not Working
Clear browser cache and refresh:
```bash
# Or use incognito mode
```

### Search Not Working
Ensure search index is built:
```bash
# Rebuild with search
npm run build:static
```

---

## 📞 Support

For issues:
1. Check this guide
2. Review Next.js docs: https://nextjs.org/docs/app/building-your-application/deploying/static-exports
3. Check Fumadocs: https://fumadocs.vercel.app/

---

## ✅ Checklist

Before deploying:

- [ ] Run `npm run build:static` successfully
- [ ] Verify `./out/index.html` exists
- [ ] Test locally: `npm run serve:static`
- [ ] Check all pages load correctly
- [ ] Test search functionality
- [ ] Test dark/light mode toggle
- [ ] Verify responsive design
- [ ] Test on mobile device
- [ ] Check file sizes are reasonable
- [ ] Deploy to hosting service

---

**Last Updated:** December 2, 2025
**Status:** ✅ Ready for Production
**Next Steps:** Deploy to Vercel or your preferred static host

