# TraceRTM Documentation Generation Scripts

This directory contains scripts for generating the TraceRTM documentation structure.

## Scripts

### generate-mdx-files.ts

Basic MDX generator that uses the current DOCS_STRUCTURE from `structure.ts`.

**Usage:**
```bash
bun run scripts/generate-mdx-files.ts
```

**What it does:**
- Reads structure from the imported DOCS_STRUCTURE
- Creates directories based on the `path` property
- Generates index.mdx files with frontmatter and content
- Skips existing files
- Reports statistics on completion

**Output:**
- Creates ~37 pages from current structure
- Shows progress with checkmarks

### generate-all-mdx.ts

Enhanced MDX generator with intelligent content generation for massive documentation structures.

**Usage:**
```bash
bun run scripts/generate-all-mdx.ts
```

**What it does:**
- Uses the EXPANDED_STRUCTURE (313 pages)
- Generates topic-specific content based on page path
- Shows progress percentage in real-time
- High-performance generation (2000+ pages/second)

**Content Templates:**
- **Installation**: Step-by-step guides, troubleshooting
- **API**: Complete endpoint documentation with examples
- **Guide**: Comprehensive workflows and best practices
- **Compliance**: Standards and implementation details
- **Changelog**: Version history with migration guides
- **Security**: Authentication, authorization, encryption
- **Performance**: Optimization strategies and monitoring
- **Default**: Generic structure for other pages

**Output:**
- Creates 313+ pages from expanded structure
- Real-time progress: `[XX%] Processing N/Total: path/to/page`
- Final statistics with speed metrics

### expanded-structure.ts

Defines the expanded documentation structure (313 pages).

**Usage:**
```typescript
import { EXPANDED_STRUCTURE } from './expanded-structure'
```

**Structure:**
```typescript
export const EXPANDED_STRUCTURE = {
  'section-key': {
    title: 'Section Title',
    description: 'Description',
    path: '00-section',
    icon: 'IconName',
    children: {
      'subsection-key': {
        title: 'Subsection Title',
        path: '01-subsection',
        children: { /* ... */ }
      }
    }
  }
}
```

**Utilities:**
- `countPages(structure)`: Count total pages in structure

## Quick Start

### Generate All Documentation

```bash
# From docs-site directory
cd docs-site

# Make scripts executable (if needed)
chmod +x scripts/*.ts

# Generate all pages
bun run scripts/generate-all-mdx.ts
```

### Verify Generation

```bash
# Count generated files
find content/docs -name "index.mdx" | wc -l

# Check a sample file
cat content/docs/00-getting-started/01-installation/index.mdx

# View directory structure
tree content/docs -L 3
```

## Adding New Documentation Sections

### Step 1: Update Structure

Edit `expanded-structure.ts`:

```typescript
export const EXPANDED_STRUCTURE = {
  // ... existing sections ...
  'new-section': {
    title: 'New Section',
    description: 'Description of new section',
    path: '07-new-section',
    icon: 'IconName',
    children: {
      'subsection': {
        title: 'Subsection',
        path: '01-subsection',
        children: {
          'page': { title: 'Page Title', path: '01-page' }
        }
      }
    }
  }
}
```

### Step 2: Generate Pages

```bash
bun run scripts/generate-all-mdx.ts
```

### Step 3: Update Navigation

Copy the structure to `app/docs/[[...slug]]/structure.ts`:

```typescript
// app/docs/[[...slug]]/structure.ts
export const DOCS_STRUCTURE = {
  // Copy from expanded-structure.ts
  'new-section': {
    title: 'New Section',
    description: 'Description of new section',
    path: '07-new-section',
    icon: 'IconName',
    children: { /* ... */ }
  }
}
```

### Step 4: Verify

```bash
# Start dev server
bun run dev

# Navigate to http://localhost:3000/docs/new-section
```

## Custom Content Templates

To add custom content for specific page types, edit `generate-all-mdx.ts`:

### Add Detection Logic

```typescript
function generateEnhancedContent(title: string, description: string | undefined, slug: string[]): string {
  const slugStr = slug.join('/')

  // Add your custom detection
  if (slugStr.includes('your-keyword')) {
    content = generateYourCustomContent(title, slugStr)
  }
  // ... existing conditions ...
}
```

### Add Template Function

```typescript
function generateYourCustomContent(title: string, slug: string): string {
  return `
## Overview

Custom content for ${title}.

## Your Custom Sections

- Section 1
- Section 2

\`\`\`typescript
// Your code examples
\`\`\`

## More Custom Content

...
`
}
```

## Directory Structure

```
scripts/
├── README.md                   # This file
├── generate-mdx-files.ts      # Basic generator
├── generate-all-mdx.ts         # Enhanced generator
└── expanded-structure.ts       # Structure definition
```

## Output Structure

```
content/docs/
├── 00-getting-started/
│   ├── index.mdx
│   ├── 01-installation/
│   │   ├── index.mdx
│   │   ├── 01-windows/
│   │   │   └── index.mdx
│   │   └── ...
│   └── ...
├── 01-wiki/
│   └── ...
├── 02-api-reference/
│   └── ...
└── ...
```

## Performance

- **Generation Speed**: ~2,000 pages/second
- **Memory Usage**: Minimal (streaming generation)
- **Disk I/O**: Async operations with fs/promises

## Troubleshooting

### Permission Errors

```bash
# Make scripts executable
chmod +x scripts/*.ts

# Run with explicit permissions
sudo bun run scripts/generate-all-mdx.ts
```

### Missing Dependencies

```bash
# Install Bun dependencies
bun install
```

### Structure Not Found

Make sure you're in the correct directory:

```bash
cd docs-site
pwd  # Should end with /docs-site
```

### Empty Files Generated

Check the content templates in `generate-all-mdx.ts`. Each template function should return non-empty content.

## Best Practices

1. **Always back up** before regenerating:
   ```bash
   cp -r content/docs content/docs.backup
   ```

2. **Test locally** before deploying:
   ```bash
   bun run dev
   # Check http://localhost:3000/docs
   ```

3. **Validate MDX syntax** after generation:
   ```bash
   # Check for frontmatter
   head -n 10 content/docs/00-getting-started/index.mdx
   ```

4. **Keep structure organized**:
   - Use numbered prefixes (00-, 01-, etc.)
   - Group related content
   - Maintain consistent hierarchy

5. **Update incrementally**:
   - Add sections one at a time
   - Test after each addition
   - Commit changes frequently

## Examples

### Generate Single Section

Temporarily modify `generate-all-mdx.ts` to process only one section:

```typescript
// In main() function
const testStructure = {
  'test-section': EXPANDED_STRUCTURE['getting-started']
}
await processStructure(testStructure, [])
```

### Custom Content for Specific Pages

```typescript
// In generateEnhancedContent()
if (slugStr === 'getting-started/installation/windows') {
  return generateWindowsInstallContent(title)
}
```

### Count Pages Before Generating

```typescript
import { countPages } from './expanded-structure'

const total = countPages(EXPANDED_STRUCTURE)
console.log(`Will generate ${total} pages`)
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Generate Docs
on:
  push:
    paths:
      - 'docs-site/scripts/expanded-structure.ts'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: cd docs-site && bun run scripts/generate-all-mdx.ts
      - run: git add content/docs
      - run: git commit -m "Regenerate documentation"
      - run: git push
```

## Support

For issues or questions:
1. Check this README
2. Review the code comments in the scripts
3. Check the DOCUMENTATION_GENERATION_SUMMARY.md
4. Open an issue on GitHub

---

**Last Updated**: 2025-12-02
**Scripts Version**: 1.0.0
