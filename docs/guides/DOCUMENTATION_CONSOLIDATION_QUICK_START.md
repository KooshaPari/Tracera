# Documentation Consolidation - Quick Start Guide

**Goal**: Consolidate 11,256 markdown files to **<2,000 files** (83% reduction) in unified Fumadocs structure

---

## Quick Overview

**Current**: Documentation scattered across multiple directories  
**Target**: Single source of truth in `docs-site/content/docs/`  
**Framework**: Fumadocs (Next.js + MDX)  
**Approach**: MDX derives from Markdown (Fumadocs supports both)

---

## Step 1: Run Aggressive Inventory Scan

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
pip install -r scripts/consolidate-docs/requirements.txt
python scripts/consolidate-docs/scan_aggressive.py
```

**Output**: `consolidation-output/docs_inventory_aggressive.json`

This creates a complete inventory of **project files only** (excludes dependencies) with:
- File paths and metadata
- Content hashes (for duplicate detection)
- Consolidation categorization (reports, plans, research, etc.)
- Consolidation strategy assignment
- Frontmatter extraction
- Link extraction

**Expected**: ~8,000-9,000 project files (excludes ~2,000-3,000 dependency files)

---

## Step 2: Review Consolidation Plan

```bash
# View statistics
cat consolidation-output/docs_inventory_aggressive.json | jq '.statistics'

# View consolidation plan
cat consolidation-output/docs_inventory_aggressive.json | jq '.statistics.consolidation_plan'

# View by consolidation category
cat consolidation-output/docs_inventory_aggressive.json | jq '.statistics.by_consolidation_category'
```

**Expected Reduction**:
- Historical Reports: 321 → 10 files (97% reduction)
- Planning Documents: 454 → 20 files (96% reduction)
- Research Documents: 500 → 50 files (90% reduction)
- README Files: 3,300 → 5 files (99.8% reduction)
- **Total Target**: <2,000 files (83% reduction)

---

## Step 3: Run Duplicate Detection

```bash
python scripts/consolidate-docs/detect_duplicates.py
```

**Output**: `consolidation-output/duplicates.json`

This identifies:
- Exact duplicates (same content hash)
- Near duplicates (semantic similarity)
- Versioned docs (same name, different dates)
- Name-based duplicates

---

## Step 4: Review & Approve Merges

```bash
# View duplicate groups
cat consolidation-output/duplicates.json | jq '.exact_duplicates'

# Review merge recommendations
cat consolidation-output/duplicates.json | jq '.merge_recommendations'
```

**Action**: Review and approve merge strategy

---

## Step 5: Merge Content

```bash
python scripts/consolidate-docs/merge_content.py
```

**Output**: `consolidation-output/merged/` directory

This merges duplicates intelligently:
- Combines unique sections
- Preserves latest information
- Creates redirects for old paths

---

## Step 6: Convert to MDX

```bash
python scripts/consolidate-docs/convert_to_mdx.py
```

**Output**: `consolidation-output/converted/` directory

This converts Markdown to MDX:
- Adds frontmatter
- Fixes internal links
- Organizes by audience
- Creates directory structure

---

## Step 7: Generate Indexes

```bash
python scripts/consolidate-docs/generate_indexes.py
```

**Output**: `consolidation-output/indexes/` directory

This generates:
- Master index
- Audience indexes (user, developer, API)
- Topic indexes (architecture, CLI, testing, etc.)
- Type indexes (guides, reference, research)

---

## Step 8: Update Links

```bash
python scripts/consolidate-docs/update_links.py
```

**Output**: Updated MDX files with fixed links

This:
- Updates all internal links
- Creates redirects
- Validates links
- Generates link report

---

## Step 9: Migrate to Fumadocs

```bash
# Copy converted files to Fumadocs structure
cp -r consolidation-output/converted/* docs-site/content/docs/

# Copy indexes
cp -r consolidation-output/indexes/* docs-site/content/docs/

# Update Fumadocs config
# (See DOCUMENTATION_CONSOLIDATION_PLAN.md for config details)
```

---

## Step 10: Test & Validate

```bash
cd docs-site
npm run dev

# Test navigation
# Test search
# Validate links
# Check redirects
```

---

## Expected Results

**Before**:
- 11,256 markdown files
- Scattered across 10+ directories
- No unified structure
- Many duplicates

**After**:
- ~5,000-6,000 consolidated MDX files
- Organized by audience (user/developer/api)
- Modular indexes for discovery
- Unified Fumadocs structure
- No content loss
- All links working

---

## Next Steps

1. **Run inventory scan** (Step 1)
2. **Review results** (Step 2)
3. **Continue with consolidation** (Steps 3-10)

See `DOCUMENTATION_CONSOLIDATION_PLAN.md` for detailed plan.
