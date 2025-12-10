# Installation and Setup Steps

## 🚀 Quick Start

Follow these steps to get the documentation site running:

### 1. Install Dependencies

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs-site
npm install
```

This will install all required packages including:
- Next.js 16
- React 19
- Fumadocs packages
- Radix UI components
- CMDK for search
- Lucide icons
- And all other dependencies

### 2. Build Search Index

```bash
npm run index
```

This will:
- Scan the `src/content` directory
- Extract and clean content from MDX files
- Generate keywords
- Create `public/search-index.json`

Expected output:
```
Building search index...
Content directory: /path/to/docs-site/src/content
Indexed 4 documents
Search index written to: /path/to/docs-site/public/search-index.json
Done!
```

### 3. Start Development Server

```bash
npm run dev
```

Expected output:
```
   ▲ Next.js 16.0.6
   - Local:        http://localhost:3001
   - Environments: .env

 ✓ Ready in 2.3s
```

### 4. Open in Browser

Navigate to: **http://localhost:3001**

You should see:
- Homepage with documentation overview
- Navigation sidebar on the left (desktop)
- Hamburger menu icon (mobile)
- Search bar in header
- Docs section cards

### 5. Test Features

#### Test Sidebar Navigation
1. Look at the left sidebar (desktop) or click hamburger menu (mobile)
2. You should see 6 sections:
   - Getting Started (with 4 pages)
   - Guides
   - API Reference
   - Examples
   - FAQ
   - Contributing

3. Click on "Getting Started" to expand
4. Click on "Introduction"
5. Verify the page loads and active highlighting works

#### Test Search
1. Press `⌘K` (Mac) or `Ctrl+K` (Windows/Linux)
   - OR click the search bar in the header
2. A command palette should open
3. Type "installation"
4. You should see search results appear
5. Click a result or press Enter to navigate

#### Test Breadcrumb
1. Navigate to any page
2. Look above the content
3. You should see a breadcrumb trail like:
   `Home > Docs > Getting Started > Introduction`
4. Click on any breadcrumb to navigate

#### Test Mobile Navigation
1. Resize browser to mobile width (< 1024px)
2. Sidebar should hide
3. Hamburger menu icon should appear
4. Click hamburger to open mobile menu
5. Navigate to a page
6. Menu should close automatically

## 🔧 Troubleshooting

### Issue: Dependencies won't install

**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Issue: Search index build fails

**Solution**:
```bash
# Check if content directory exists
ls -la src/content/

# If it doesn't exist, it will create placeholder index
# This is normal for first run
```

### Issue: Port 3001 already in use

**Solution**:
```bash
# Use a different port
npm run dev -- -p 3002
```

### Issue: Page not found (404)

**Possible causes**:
1. MDX file doesn't exist
2. Navigation href doesn't match file path
3. Missing frontmatter in MDX file

**Solution**:
- Check file exists at the expected path
- Verify frontmatter has `title` and `description`
- Check navigation tree in `src/lib/source.ts`

### Issue: Search returns no results

**Solution**:
```bash
# Rebuild search index
npm run index

# Check if index was created
ls -la public/search-index.json

# Restart dev server
npm run dev
```

### Issue: Styles not loading

**Solution**:
```bash
# Clear Next.js cache
rm -rf .next

# Restart dev server
npm run dev
```

## 📦 Build for Production

### 1. Build

```bash
npm run build
```

Expected output:
```
Building search index...
Indexed 4 documents
...
Creating an optimized production build...
✓ Compiled successfully
...
```

### 2. Start Production Server

```bash
npm start
```

Visit: http://localhost:3000

### 3. Deploy to Vercel

```bash
# Install Vercel CLI (if not installed)
npm install -g vercel

# Deploy
vercel

# Follow prompts to configure
```

Or connect GitHub repository to Vercel:
1. Go to https://vercel.com
2. Click "New Project"
3. Import your repository
4. Configure:
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`
5. Deploy

## 📝 Adding New Content

### Add a New Page

1. **Create MDX file**:
```bash
touch src/content/guides/my-guide.mdx
```

2. **Add frontmatter and content**:
```mdx
---
title: My Guide
description: A helpful guide about something
---

# My Guide

Your content here...
```

3. **Update navigation** in `src/lib/source.ts`:
```typescript
{
  title: 'Guides',
  icon: 'Compass',
  children: [
    // ... existing items
    {
      title: 'My Guide',
      href: '/docs/guides/my-guide',
    },
  ],
}
```

4. **Rebuild search index**:
```bash
npm run index
```

5. **View in browser**:
Navigate to http://localhost:3001/docs/guides/my-guide

### Add a New Section

1. **Create directory**:
```bash
mkdir src/content/new-section
```

2. **Create index page**:
```bash
touch src/content/new-section/index.mdx
```

3. **Add to navigation**:
```typescript
{
  title: 'New Section',
  icon: 'FolderOpen',  // Any Lucide icon
  children: [
    {
      title: 'Overview',
      href: '/docs/new-section',
    },
  ],
}
```

4. **Rebuild and test**:
```bash
npm run index
npm run dev
```

## 🎨 Customization

### Change Colors

Edit `src/app/globals.css`:

```css
:root {
  /* Change primary color */
  --primary: 142 76% 36%;  /* Green instead of blue */
}
```

### Change Icons

Edit `src/lib/source.ts`:

Browse available icons at https://lucide.dev/

```typescript
{
  title: 'Guides',
  icon: 'Rocket',  // Change from Compass to Rocket
}
```

### Modify Search Scoring

Edit `src/lib/search-indexer.ts`:

```typescript
// Increase title match weight
if (doc.title.toLowerCase().includes(queryLower)) {
  score += 200;  // Changed from 100
}

// Change result limit
export function searchDocuments(index, query, limit = 20) {
  // Changed from 10 to 20
}
```

Then rebuild:
```bash
npm run index
npm run dev
```

## 📊 Project Status

✅ **COMPLETE AND READY**

All components implemented:
- [x] Sidebar navigation
- [x] Mobile navigation
- [x] Breadcrumb trail
- [x] Full-text search
- [x] Command palette (⌘K)
- [x] Search API
- [x] Search indexing
- [x] Sample content
- [x] Documentation

## 📚 Documentation Files

Read these for more information:

1. **README.md** - Comprehensive overview
2. **IMPLEMENTATION_GUIDE.md** - Detailed technical guide
3. **QUICK_START.md** - Quick reference
4. **COMPLETE_IMPLEMENTATION.md** - Implementation checklist
5. **FILES_CREATED.md** - Complete file listing

## 🎯 Next Steps

1. ✅ Install dependencies: `npm install`
2. ✅ Build search index: `npm run index`
3. ✅ Start dev server: `npm run dev`
4. 📝 Add more content to sections
5. 🎨 Customize colors and styling
6. 🚀 Deploy to production

## 💡 Tips

- Use `⌘K` / `Ctrl+K` to quickly search docs
- Sidebar sections are collapsible
- Mobile menu auto-closes on navigation
- Search results show content previews
- Breadcrumbs help with navigation context
- All pages are statically generated for performance

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review README.md
3. See IMPLEMENTATION_GUIDE.md for detailed info
4. Check browser console for errors
5. Verify all files are in place (see FILES_CREATED.md)

---

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs-site`

**Status**: ✅ Ready to run!

**Start Command**: `npm run dev`

**URL**: http://localhost:3001
