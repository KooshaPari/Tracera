# Documentation Consolidation Scripts

Scripts for consolidating and centralizing TraceRTM documentation.

## Overview

These scripts help migrate 11,256+ markdown files into a unified Fumadocs structure:
1. **Scan** - Inventory all documentation
2. **Detect** - Find duplicates
3. **Merge** - Merge duplicate content
4. **Convert** - Convert MD → MDX
5. **Index** - Generate modular indexes
6. **Update** - Fix links and redirects

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run full consolidation pipeline
python consolidate.py --all

# Or run individual steps
python scan_docs.py
python detect_duplicates.py
python merge_content.py
python convert_to_mdx.py
python generate_indexes.py
python update_links.py
```

## Output

All scripts output to `consolidation-output/`:
- `docs_inventory.json` - Complete file inventory
- `duplicates.json` - Duplicate detection results
- `migration_map.json` - Source → target mapping
- `merged/` - Merged content files
- `converted/` - Converted MDX files
- `indexes/` - Generated index files
