# Documentation Consolidation & Centralization Plan

**Date**: 2025-12-03  
**Goal**: Merge/consolidate all documentation without regressing content, merge genuine duplicates, create modular indexes, centralize ALL documentation types  
**Framework**: Fumadocs (Next.js + MDX) deriving from local Markdown docsuite

---

## Executive Summary

**Current State**:
- **11,256 markdown files** totaling **2,184,279 lines**
- Documentation scattered across: `docs/`, `docs-site/`, `research/`, `PLANNING/`, root directory, `docs/07-reports/archive/`, etc.
- **Fumadocs** already configured in `docs-site/` with MDX support
- No unified structure or indexing system
- Many duplicate/overlapping documents

**Target State**:
- Single source of truth: `docs-site/content/docs/` (Fumadocs structure)
- All MD files → MDX conversion pipeline
- Modular indexes for discovery
- Centralized documentation registry
- No content loss, intelligent deduplication

---

## Part 1: Documentation Paradigm Analysis

### 1.1 Fumadocs Architecture (Current Setup)

**Fumadocs** is a Next.js-based documentation framework that:
- Uses **MDX** (Markdown + JSX) for content
- Supports **frontmatter** for metadata
- Auto-generates navigation from file structure
- Supports **multiple doc sources** (user, developer, API)
- Can derive MDX from Markdown sources

**Current Configuration** (`docs-site/source.config.ts`):
```typescript
export const { docs, meta } = defineDocs({
  dir: 'content/docs',  // Source directory
});
```

**How Fumadocs Works**:
1. Scans `content/docs/` for `.mdx` files
2. Processes frontmatter for metadata
3. Generates navigation from directory structure + `meta.json` files
4. Renders MDX with React components
5. Supports multiple doc trees (user, developer, API)

### 1.2 Documentation Paradigms

#### Option A: Single Source (Markdown) → MDX Pipeline ✅ RECOMMENDED
- **Source**: All docs in `docs-site/content/docs/` as `.md` or `.mdx`
- **Processing**: Fumadocs reads directly (supports both)
- **Benefits**: Simple, no conversion needed
- **Drawback**: MDX features require `.mdx` extension

#### Option B: Dual Source (MD → MDX Conversion)
- **Source**: Markdown in `docs/` directory
- **Build**: Convert `.md` → `.mdx` during build
- **Benefits**: Separate source from presentation
- **Drawback**: More complex, requires build step

#### Option C: Hybrid (MD for source, MDX for enhanced)
- **Source**: Markdown for basic docs
- **Enhanced**: MDX for interactive components
- **Benefits**: Best of both worlds
- **Drawback**: Two formats to manage

**Recommendation**: **Option A** - Use MDX directly (Fumadocs supports both `.md` and `.mdx`, but MDX is preferred for React components)

---

## Part 2: Current Documentation Inventory

### 2.1 Documentation Locations

```
trace/
├── docs/                          # Main docs directory (~456 files)
│   ├── 00-overview/              # Overview docs
│   ├── 01-getting-started/       # Getting started guides
│   ├── 02-architecture/          # Architecture docs
│   ├── 03-planning/              # Planning docs
│   ├── 04-implementation/        # Implementation guides
│   ├── 05-requirements/          # Requirements docs
│   ├── 05-research/              # Research findings
│   ├── 07-reports/               # Completion reports
│   │   └── archive/              # Archived reports
│   └── [root level files]        # Various docs
│
├── docs-site/                     # Fumadocs site (~50 files)
│   ├── content/docs/              # Current MDX content
│   ├── .source/                   # Fumadocs source config
│   └── [planning docs]           # Documentation planning
│
├── research/                      # Research docs (~8 files)
├── PLANNING/                      # Planning docs (~8 files)
├── PHASES/                        # Phase reports
├── STATUS/                        # Status reports
├── TESTING/                       # Testing docs
├── GUIDES/                        # Guide files
├── [root level]                   # 50+ planning/research docs
│
└── .bmad/                         # BMAD method docs
```

### 2.2 Documentation Types

#### Type 1: User Documentation
- Getting started guides
- User guides
- Tutorials
- FAQs
- Use cases
- Examples

#### Type 2: Developer Documentation
- Architecture docs
- API reference
- Setup guides
- Contributing guides
- Internals
- Deployment

#### Type 3: Planning & Research
- Research findings
- Planning documents
- Feature specifications
- Architecture decisions
- Roadmaps

#### Type 4: Reports & Status
- Completion reports
- Phase summaries
- Test reports
- Status updates

#### Type 5: Reference Documentation
- CLI reference
- API reference
- SDK reference
- Configuration reference

### 2.3 Duplicate Detection Strategy

**Duplicate Types**:
1. **Exact Duplicates** - Same content, different locations
2. **Near Duplicates** - Similar content, minor differences
3. **Versioned Duplicates** - Same doc, different versions
4. **Archived Duplicates** - Old versions in archive/

**Detection Method**:
- Content hash comparison (MD5/SHA256)
- Semantic similarity (for near duplicates)
- File name pattern matching
- Directory structure analysis

---

## Part 3: Consolidation Strategy

### 3.1 Target Structure (Fumadocs-Compliant)

```
docs-site/content/docs/
├── user/                          # User documentation
│   ├── meta.json                  # Navigation config
│   ├── index.mdx                  # Landing page
│   ├── getting-started/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   ├── installation.mdx
│   │   ├── quick-start.mdx
│   │   └── first-project.mdx
│   ├── concepts/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   ├── traceability.mdx
│   │   ├── views.mdx
│   │   ├── links.mdx
│   │   └── items.mdx
│   ├── guides/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   ├── cli-guide.mdx
│   │   ├── web-ui-guide.mdx
│   │   ├── tui-guide.mdx
│   │   └── best-practices.mdx
│   ├── examples/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   ├── simple-todo.mdx
│   │   ├── medium-web-app.mdx
│   │   └── complex-system.mdx
│   └── faq/
│       ├── meta.json
│       ├── index.mdx
│       └── troubleshooting.mdx
│
├── developer/                     # Developer documentation
│   ├── meta.json
│   ├── index.mdx
│   ├── setup/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   ├── local-development.mdx
│   │   ├── database.mdx
│   │   └── environment.mdx
│   ├── architecture/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   ├── overview.mdx
│   │   ├── system-design.mdx
│   │   ├── data-flow.mdx
│   │   └── security.mdx
│   ├── backend/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   ├── api-structure.mdx
│   │   ├── models.mdx
│   │   ├── services.mdx
│   │   └── testing.mdx
│   ├── frontend/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   ├── project-structure.mdx
│   │   ├── components.mdx
│   │   └── state-management.mdx
│   ├── cli/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   ├── architecture.mdx
│   │   ├── commands.mdx
│   │   └── tui.mdx
│   └── contributing/
│       ├── meta.json
│       ├── index.mdx
│       └── guidelines.mdx
│
├── api/                           # API reference
│   ├── meta.json
│   ├── index.mdx
│   ├── rest/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   ├── projects.mdx
│   │   ├── items.mdx
│   │   ├── links.mdx
│   │   └── search.mdx
│   ├── cli/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   └── commands.mdx
│   └── authentication.mdx
│
├── reference/                      # Reference documentation
│   ├── meta.json
│   ├── index.mdx
│   ├── cli-reference.mdx
│   ├── configuration.mdx
│   └── schemas.mdx
│
├── research/                      # Research & planning (indexed)
│   ├── meta.json
│   ├── index.mdx
│   ├── architecture-research.mdx
│   ├── backend-research.mdx
│   ├── frontend-research.mdx
│   └── [consolidated research]
│
└── archive/                       # Historical/archived docs
    ├── meta.json
    ├── index.mdx
    ├── phase-reports.mdx
    ├── completion-reports.mdx
    └── [archived content]
```

### 3.2 Content Migration Strategy

#### Phase 1: Inventory & Categorization
1. **Scan all `.md` files** (11,256 files)
2. **Extract metadata** (title, description, date, author)
3. **Categorize by type** (user, developer, API, research, archive)
4. **Detect duplicates** (content hash + similarity)
5. **Create migration map** (source → target)

#### Phase 2: Deduplication
1. **Identify exact duplicates** → Keep one, link others
2. **Identify near duplicates** → Merge content, preserve unique info
3. **Identify versioned docs** → Keep latest, archive old
4. **Create redirect map** (old paths → new paths)

#### Phase 3: Conversion & Migration
1. **Convert `.md` → `.mdx`** (add frontmatter, fix links)
2. **Organize by audience** (user/developer/api)
3. **Create modular indexes** (by topic, by type, by audience)
4. **Update internal links** (fix cross-references)
5. **Generate navigation** (meta.json files)

#### Phase 4: Index Creation
1. **Master index** (all docs)
2. **Audience indexes** (user, developer, API)
3. **Topic indexes** (architecture, CLI, testing, etc.)
4. **Type indexes** (guides, reference, research)
5. **Search index** (Fumadocs search integration)

---

## Part 4: Implementation Plan

### 4.1 Tools & Scripts Needed

#### Script 1: Documentation Scanner
```python
# scripts/consolidate-docs/scan_docs.py
"""
Scans all markdown files and creates inventory.
Outputs: docs_inventory.json
"""
```

**Features**:
- Find all `.md` files
- Extract frontmatter/metadata
- Calculate content hash
- Detect duplicates
- Categorize by type
- Generate migration map

#### Script 2: Duplicate Detector
```python
# scripts/consolidate-docs/detect_duplicates.py
"""
Detects exact and near duplicates.
Outputs: duplicates.json, merge_plan.json
"""
```

**Features**:
- Content hash comparison
- Semantic similarity (using embeddings)
- File name pattern matching
- Version detection
- Merge recommendations

#### Script 3: Content Merger
```python
# scripts/consolidate-docs/merge_content.py
"""
Merges duplicate/near-duplicate content intelligently.
Outputs: merged content files
"""
```

**Features**:
- Merge similar content
- Preserve unique information
- Handle conflicts
- Create redirects

#### Script 4: MD → MDX Converter
```python
# scripts/consolidate-docs/convert_to_mdx.py
"""
Converts Markdown to MDX with frontmatter.
Outputs: MDX files in target structure
"""
```

**Features**:
- Add frontmatter (title, description, etc.)
- Fix internal links
- Convert to MDX format
- Preserve formatting
- Handle code blocks

#### Script 5: Index Generator
```python
# scripts/consolidate-docs/generate_indexes.py
"""
Generates modular indexes for documentation.
Outputs: index.mdx files, meta.json files
"""
```

**Features**:
- Generate master index
- Generate audience indexes
- Generate topic indexes
- Generate type indexes
- Create navigation (meta.json)

#### Script 6: Link Updater
```python
# scripts/consolidate-docs/update_links.py
"""
Updates all internal links after migration.
Outputs: Updated MDX files
"""
```

**Features**:
- Find all internal links
- Map old paths → new paths
- Update links
- Create redirects
- Validate links

### 4.2 Fumadocs Configuration Updates

#### Update `source.config.ts`
```typescript
import { defineConfig, defineDocs } from 'fumadocs-mdx/config';
import { rehypeCode, remarkGfm, remarkHeading } from 'fumadocs-core/mdx-plugins';

// Multiple doc sources for different audiences
export const { docs: userDocs, meta: userMeta } = defineDocs({
  dir: 'content/docs/user',
});

export const { docs: developerDocs, meta: developerMeta } = defineDocs({
  dir: 'content/docs/developer',
});

export const { docs: apiDocs, meta: apiMeta } = defineDocs({
  dir: 'content/docs/api',
});

export const { docs: referenceDocs, meta: referenceMeta } = defineDocs({
  dir: 'content/docs/reference',
});

// Combined for search
export const { docs, meta } = defineDocs({
  dir: 'content/docs',
});

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [remarkGfm, remarkHeading],
    rehypePlugins: (defaults) => [
      ...defaults,
      [rehypeCode, {
        themes: {
          light: 'github-light',
          dark: 'github-dark',
        },
      }],
    ],
  },
});
```

#### Create `lib/source.ts`
```typescript
import { loader } from 'fumadocs-core/source';
import { createMDXSource } from 'fumadocs-mdx';
import { docs, meta } from '@/.source';

// User documentation source
export const userDocsSource = loader({
  baseUrl: '/docs/user',
  rootDir: 'user',
  source: createMDXSource(docs, meta),
});

// Developer documentation source
export const developerDocsSource = loader({
  baseUrl: '/docs/developer',
  rootDir: 'developer',
  source: createMDXSource(docs, meta),
});

// API documentation source
export const apiDocsSource = loader({
  baseUrl: '/docs/api',
  rootDir: 'api',
  source: createMDXSource(docs, meta),
});

// Combined source for search
export const allDocsSource = loader({
  baseUrl: '/docs',
  source: createMDXSource(docs, meta),
});
```

---

## Part 5: Modular Index System

### 5.1 Index Types

#### Master Index (`docs-site/content/docs/index.mdx`)
- Overview of all documentation
- Quick links to all sections
- Search interface
- Audience selector

#### Audience Indexes
- `user/index.mdx` - User documentation index
- `developer/index.mdx` - Developer documentation index
- `api/index.mdx` - API documentation index

#### Topic Indexes
- Architecture index
- CLI index
- Testing index
- Research index
- Planning index

#### Type Indexes
- Guides index
- Reference index
- Examples index
- Research index
- Reports index

### 5.2 Index Format (MDX)

```mdx
---
title: "Documentation Index"
description: "Complete index of all TraceRTM documentation"
---

# Documentation Index

## By Audience

<CardGrid>
  <Card href="/docs/user" title="User Documentation" />
  <Card href="/docs/developer" title="Developer Documentation" />
  <Card href="/docs/api" title="API Reference" />
</CardGrid>

## By Topic

<TopicGrid>
  <TopicCard topic="architecture" />
  <TopicCard topic="cli" />
  <TopicCard topic="testing" />
  <!-- etc -->
</TopicGrid>

## Search

<SearchBox />
```

---

## Part 6: Duplicate Detection & Merging

### 6.1 Duplicate Detection Algorithm

```python
def detect_duplicates():
    """
    Detect duplicates using multiple strategies.
    """
    # Strategy 1: Content hash (exact duplicates)
    exact_duplicates = find_by_content_hash()
    
    # Strategy 2: Semantic similarity (near duplicates)
    near_duplicates = find_by_semantic_similarity(threshold=0.85)
    
    # Strategy 3: File name patterns
    name_duplicates = find_by_filename_pattern()
    
    # Strategy 4: Directory structure
    structure_duplicates = find_by_structure()
    
    return {
        'exact': exact_duplicates,
        'near': near_duplicates,
        'name': name_duplicates,
        'structure': structure_duplicates,
    }
```

### 6.2 Merging Strategy

#### For Exact Duplicates
- **Action**: Keep one copy, create redirects
- **Location**: Keep the most authoritative location
- **Redirects**: Create redirect entries in old locations

#### For Near Duplicates
- **Action**: Merge content intelligently
- **Strategy**: 
  - Combine unique sections
  - Preserve latest information
  - Merge metadata
  - Create "See Also" links

#### For Versioned Docs
- **Action**: Keep latest version, archive old
- **Strategy**:
  - Move old versions to `archive/`
  - Create version history page
  - Link versions together

---

## Part 7: Migration Workflow

### 7.1 Phase 1: Preparation (Week 1)

**Tasks**:
1. ✅ Create consolidation scripts
2. ✅ Set up duplicate detection
3. ✅ Create migration map
4. ✅ Backup all docs

**Deliverables**:
- `docs_inventory.json` - Complete inventory
- `duplicates.json` - Duplicate detection results
- `migration_map.json` - Source → target mapping
- `merge_plan.json` - Merging strategy

### 7.2 Phase 2: Deduplication (Week 2)

**Tasks**:
1. Review duplicate detection results
2. Merge exact duplicates
3. Merge near duplicates
4. Archive old versions
5. Create redirect map

**Deliverables**:
- Merged content files
- Redirect map
- Archive directory structure

### 7.3 Phase 3: Conversion (Week 3)

**Tasks**:
1. Convert `.md` → `.mdx`
2. Add frontmatter to all files
3. Organize by audience
4. Create directory structure
5. Generate `meta.json` files

**Deliverables**:
- MDX files in target structure
- Navigation files (meta.json)
- Updated Fumadocs config

### 7.4 Phase 4: Indexing (Week 4)

**Tasks**:
1. Generate master index
2. Generate audience indexes
3. Generate topic indexes
4. Generate type indexes
5. Set up search

**Deliverables**:
- All index files
- Search integration
- Navigation structure

### 7.5 Phase 5: Link Updates & Validation (Week 5)

**Tasks**:
1. Update all internal links
2. Create redirects
3. Validate all links
4. Test navigation
5. Generate link report

**Deliverables**:
- Updated links
- Redirect system
- Validation report
- Navigation test results

---

## Part 8: Fumadocs Integration

### 8.1 MDX Derivation from Markdown

**Fumadocs supports both `.md` and `.mdx`**, but MDX is preferred for:
- React components
- Interactive elements
- Custom components
- Better frontmatter support

**Conversion Strategy**:
1. **Keep `.md` files** if they're simple (no React components needed)
2. **Convert to `.mdx`** if they need:
   - Interactive components
   - Custom React elements
   - Advanced frontmatter
   - Code examples with live previews

**Automatic Conversion**:
- Fumadocs can read `.md` files directly
- No conversion needed for basic docs
- Convert to `.mdx` only when needed

### 8.2 Frontmatter Schema

**Standard Frontmatter** (for all docs):
```yaml
---
title: "Page Title"
description: "SEO and preview description"
icon: "IconName"  # Optional Lucide icon
keywords:
  - keyword1
  - keyword2
audience: "user" | "developer" | "api" | "reference"
client: "web" | "cli" | "desktop" | "tui" | "all"
difficulty: "beginner" | "intermediate" | "advanced"
toc: true  # Show table of contents
index: false  # Exclude from search (for index pages)
updated: "2025-12-03"
source: "docs/03-planning/..."  # Original source location
related:
  - "/docs/user/concepts/traceability"
  - "/docs/developer/architecture/overview"
---
```

### 8.3 Navigation Configuration

**meta.json Structure** (per directory):
```json
{
  "title": "Section Title",
  "icon": "IconName",
  "items": [
    {
      "title": "Page Title",
      "href": "/docs/user/getting-started/installation",
      "icon": "IconName"
    },
    {
      "title": "Subsection",
      "items": [
        {
          "title": "Subpage",
          "href": "/docs/user/getting-started/quick-start"
        }
      ]
    }
  ]
}
```

---

## Part 9: Content Registry System

### 9.1 Documentation Registry

**Create `docs-site/content/.registry.json`**:
```json
{
  "version": "1.0.0",
  "lastUpdated": "2025-12-03",
  "totalDocs": 11256,
  "categories": {
    "user": { "count": 150, "path": "user/" },
    "developer": { "count": 200, "path": "developer/" },
    "api": { "count": 50, "path": "api/" },
    "reference": { "count": 100, "path": "reference/" },
    "research": { "count": 500, "path": "research/" },
    "archive": { "count": 10000, "path": "archive/" }
  },
  "indexes": {
    "master": "/docs/index.mdx",
    "user": "/docs/user/index.mdx",
    "developer": "/docs/developer/index.mdx",
    "api": "/docs/api/index.mdx",
    "topics": {
      "architecture": "/docs/developer/architecture/index.mdx",
      "cli": "/docs/reference/cli-reference.mdx",
      "testing": "/docs/developer/testing/index.mdx"
    }
  },
  "redirects": {
    "/old/path": "/new/path",
    "docs/03-planning/...": "/docs/developer/architecture/..."
  }
}
```

### 9.2 Feature Registry (For TraceRTM Integration)

**Create `docs-site/content/.features.json`**:
```json
{
  "features": [
    {
      "id": "FEAT-CLI-001",
      "name": "CLI Test Command",
      "status": "implemented",
      "interface": "cli",
      "priority": "high",
      "docs": [
        "/docs/developer/cli/test-command.mdx",
        "/docs/reference/cli-reference.mdx#test"
      ],
      "research": [
        "/docs/research/unified-test-cli-plan.mdx"
      ]
    }
  ]
}
```

---

## Part 10: Implementation Checklist

### Week 1: Preparation
- [ ] Create `scripts/consolidate-docs/` directory
- [ ] Implement `scan_docs.py` (inventory scanner)
- [ ] Implement `detect_duplicates.py` (duplicate detector)
- [ ] Run inventory scan on all 11,256 files
- [ ] Generate `docs_inventory.json`
- [ ] Generate `duplicates.json`
- [ ] Review duplicate detection results
- [ ] Create `migration_map.json`

### Week 2: Deduplication
- [ ] Implement `merge_content.py` (content merger)
- [ ] Merge exact duplicates
- [ ] Merge near duplicates (with review)
- [ ] Archive old versions
- [ ] Create `redirect_map.json`
- [ ] Generate merge report

### Week 3: Conversion
- [ ] Implement `convert_to_mdx.py` (MD → MDX converter)
- [ ] Add frontmatter to all files
- [ ] Organize by audience (user/developer/api)
- [ ] Create directory structure
- [ ] Generate `meta.json` files
- [ ] Update Fumadocs config

### Week 4: Indexing
- [ ] Implement `generate_indexes.py` (index generator)
- [ ] Generate master index
- [ ] Generate audience indexes
- [ ] Generate topic indexes
- [ ] Generate type indexes
- [ ] Set up Fumadocs search

### Week 5: Link Updates & Validation
- [ ] Implement `update_links.py` (link updater)
- [ ] Update all internal links
- [ ] Create redirect system
- [ ] Validate all links
- [ ] Test navigation
- [ ] Generate validation report

### Week 6: Testing & Polish
- [ ] Test Fumadocs build
- [ ] Test navigation
- [ ] Test search
- [ ] Fix broken links
- [ ] Update README
- [ ] Create migration guide

---

## Part 11: Risk Mitigation

### 11.1 Content Loss Prevention

**Strategies**:
1. **Full backup** before migration
2. **Git commits** at each phase
3. **Content hash verification** (before/after)
4. **Manual review** of merged content
5. **Redirect system** for old paths

### 11.2 Link Breakage Prevention

**Strategies**:
1. **Link mapping** (old → new)
2. **Redirect system** (301 redirects)
3. **Link validation** (automated checks)
4. **Broken link detection** (post-migration)

### 11.3 Navigation Issues

**Strategies**:
1. **Test navigation** at each phase
2. **Validate meta.json** files
3. **Test Fumadocs build** frequently
4. **User testing** before final migration

---

## Part 12: Success Metrics

### Metrics

1. **Content Preservation**: 100% (no content lost)
2. **Duplicate Reduction**: Target 50% reduction (5,628 → 2,814 files)
3. **Link Accuracy**: 100% (all links work)
4. **Navigation Quality**: All sections accessible
5. **Search Functionality**: Full-text search works
6. **Build Time**: <5 minutes for full site
7. **User Experience**: Clear navigation, easy discovery

---

## Part 13: Post-Migration Maintenance

### 13.1 Documentation Standards

**New Doc Creation**:
1. Create in appropriate `content/docs/{audience}/` directory
2. Add frontmatter with required fields
3. Update relevant `meta.json` file
4. Add to appropriate indexes
5. Update registry

### 13.2 Update Process

**When Updating Docs**:
1. Edit MDX file directly
2. Update `updated` field in frontmatter
3. Regenerate indexes if structure changes
4. Update registry if needed

### 13.3 Archive Process

**When Archiving Docs**:
1. Move to `archive/` directory
2. Update frontmatter: `status: archived`
3. Create redirect to replacement doc
4. Update registry

---

## Part 14: Integration with TraceRTM

### 14.1 Feature Traceability

**Link Features to Docs**:
- Each feature has `docs` field in registry
- Docs reference features via frontmatter
- Bidirectional linking

### 14.2 Auto-Generated Docs

**From Code**:
- CLI commands → Auto-generate API reference
- OpenAPI spec → Auto-generate API docs
- TypeScript types → Auto-generate type reference

### 14.3 Documentation as Code

**Paradigm**:
- Docs live in repo (version controlled)
- Docs are part of codebase
- Docs can reference code
- Code can reference docs

---

## Conclusion

This plan provides a comprehensive strategy for consolidating 11,256 markdown files into a unified Fumadocs-based documentation system without losing content, while merging duplicates intelligently and creating modular indexes for easy discovery.

**Total Effort**: ~120 hours (6 weeks)  
**Risk Level**: Medium (mitigated by backups and phased approach)  
**Expected Outcome**: Centralized, searchable, well-organized documentation system
