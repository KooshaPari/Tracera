# Phase 5: Quick Start Guide

## ✅ All Features Implemented

Phase 5 search and navigation optimization is **100% complete**. Here's how to use it:

---

## 🚀 Quick Commands

```bash
# Start development server
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/docs
bun run dev

# Build for production
bun run build

# Test production build
bun run start
```

---

## 🔍 Search Features

### Keyboard Shortcuts

- **Mac:** `Cmd + K`
- **Windows/Linux:** `Ctrl + K`

### What Gets Indexed

- Page titles (weight: 10)
- Descriptions (weight: 5)
- Headings (weight: 3)
- Content (weight: 1)

### Performance

- **Target:** <100ms per query
- **Method:** In-memory indexing
- **Features:** Fuzzy matching, result previews

---

## 🧭 Navigation Components

### 1. Breadcrumbs

Shows current page location in hierarchy.

**Where:** Top of every documentation page
**Example:** Docs > Guides > Configuration

### 2. Table of Contents

Lists all headings on current page.

**Where:** Right sidebar (sticky)
**Features:** Active section highlighting, scroll-to-section

### 3. Previous/Next

Navigate between adjacent pages.

**Where:** Bottom of every page
**Format:** "← Previous Page" and "Next Page →"

### 4. Sidebar

Auto-generated from content structure.

**Features:**

- Collapsible sections
- Active page highlighting
- Icon support

---

## 🎨 UI Enhancements

### Dark Mode

- **Toggle:** Click moon/sun icon in nav
- **Persistence:** Saves preference
- **Scope:** Entire site including code blocks

### Code Blocks

```typescript
// Automatic copy button
const example = 'Click copy icon ↗';
```

**Features:**

- Copy to clipboard
- Syntax highlighting (GitHub themes)
- Line highlighting: ` ```lang {1,3-5} `
- Language badges

### Links

- **Internal:** Standard navigation
- **External:** Icon indicator + new tab

---

## 📝 MDX Components Reference

### Tabs

```mdx
<Tabs items={['npm', 'bun']}>
  <Tab value='npm'>npm install</Tab>
  <Tab value='bun'>bun install</Tab>
</Tabs>
```

### Callouts

```mdx
<Callout type='info'>Information</Callout>
<Callout type='warning'>Warning</Callout>
<Callout type='error'>Error</Callout>
```

### Steps

```mdx
<Steps>
  <Step>First step</Step>
  <Step>Second step</Step>
</Steps>
```

### File Tree

```mdx
<Files>
  <Folder name='src'>
    <File name='index.ts' />
    <File name='utils.ts' />
  </Folder>
</Files>
```

### Images

```mdx
![Alt text](./image.png)

<!-- Automatically zoomable on click -->
```

---

## 📁 Key Files

### Configuration

- **Search:** `lib/search-config.ts`
- **Navigation:** `app/layout.config.tsx`
- **MDX:** `source.config.ts`

### Components

- **Navigation:** `components/navigation.tsx`
- **MDX:** `components/mdx-components.tsx`
- **Utils:** `lib/utils.ts`

### API Routes

- **Search:** `app/api/search/route.ts`

---

## 🧪 Quick Test

1. **Start server:**

   ```bash
   bun run dev
   ```

2. **Test search:**
   - Press `Cmd+K` (or `Ctrl+K`)
   - Type "getting started"
   - Results should appear instantly

3. **Test navigation:**
   - Click any sidebar link
   - Check breadcrumbs update
   - Verify "On this page" TOC
   - Scroll to see active section highlighting

4. **Test dark mode:**
   - Toggle theme
   - Check code blocks update
   - Reload page (preference persists)

---

## 🔧 Troubleshooting

### Search not working?

1. Check browser console for errors
2. Verify `/api/search` returns results:
   ```bash
   curl http://localhost:3001/api/search?query=test
   ```

### Navigation empty?

1. Ensure `.source` directory exists
2. Check `content/docs/meta.json` files exist
3. Verify MDX files have frontmatter

### Build failing?

1. Clean build:

   ```bash
   rm -rf .next
   pkill -f "next"
   bun run build
   ```

2. Check dependencies:
   ```bash
   cd frontend
   bun install
   ```

---

## ✅ Feature Checklist

**Search:**

- [x] Cmd+K / Ctrl+K opens search
- [x] Results appear instantly
- [x] Click result navigates to page
- [x] Search is fast (<100ms)

**Navigation:**

- [x] Sidebar shows all pages
- [x] Breadcrumbs show path
- [x] TOC highlights section
- [x] Previous/Next works

**UI:**

- [x] Dark mode toggle works
- [x] Code copy button works
- [x] External links have icon
- [x] Syntax highlighting works

---

## 📚 Documentation

- **Full Details:** `PHASE_5_SEARCH_NAVIGATION.md`
- **Summary:** `PHASE_5_COMPLETE_SUMMARY.md`
- **Fumadocs:** https://fumadocs.vercel.app/docs

---

## 🎯 Status

**Phase 5: COMPLETE** ✅

All search and navigation features implemented and ready to use.
