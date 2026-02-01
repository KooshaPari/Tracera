# Documentation Organization Guide

## Overview

This guide explains the documentation structure and how to organize markdown files in this project.

## Core Principle

Keep the root directory clean by organizing all documentation into the `docs/` directory following a clear categorization system.

## Directory Structure

```
docs/
├── guides/                    # How-to guides and implementation documentation
│   └── quick-start/          # Quick start guides for getting started
├── reference/                 # API references and quick reference guides
├── reports/                   # Completion reports, summaries, and status reports
├── research/                  # Research documents and analysis
└── checklists/               # Implementation checklists and verification lists
```

## Root-Level Files (Allowed Only)

Only these files are permitted in the project root:
- `README.md` - Main project documentation
- `CHANGELOG.md` - Project changelog and release notes
- `AGENTS.md` - AI agent instructions
- `CLAUDE.md` / `claude.md` - Claude-specific development instructions
- `00_START_HERE.md` - Getting started overview (if applicable)

All other `.md` files must be organized into the `docs/` subdirectories.

## File Classification

### 1. Quick Start Guides
**Directory**: `docs/guides/quick-start/`

**Patterns**:
- Filenames matching `*QUICK_START*.md`
- Filenames matching `*QUICKSTART*.md`

**Purpose**: Get users up and running quickly

**Examples**:
- `FRONTEND_QUICK_START.md`
- `BACKEND_SETUP_QUICKSTART.md`
- `DOCKER_QUICK_START.md`

### 2. Quick References
**Directory**: `docs/reference/`

**Patterns**:
- Filenames matching `*QUICK_REFERENCE*.md`
- Filenames matching `*QUICK_REF*.md`
- API documentation
- Command references

**Purpose**: Quickly look up common tasks and reference information

**Examples**:
- `API_QUICK_REFERENCE.md`
- `CLI_QUICK_REF.md`
- `SCHEMA_QUICK_REFERENCE.md`

### 3. Implementation Guides
**Directory**: `docs/guides/`

**Patterns**:
- Filenames matching `*IMPLEMENTATION_GUIDE*.md`
- Filenames matching `*GUIDE*.md` (that aren't quick start or quick ref)
- General implementation documentation

**Purpose**: In-depth guides for implementing features

**Examples**:
- `CACHING_IMPLEMENTATION_GUIDE.md`
- `DATABASE_MIGRATION_GUIDE.md`
- `DEPLOYMENT_GUIDE.md`

### 4. Completion Reports & Summaries
**Directory**: `docs/reports/`

**Patterns**:
- Filenames matching `*COMPLETE*.md`
- Filenames matching `*COMPLETION*.md`
- Filenames matching `*SUMMARY*.md`
- Filenames matching `*REPORT*.md`
- Phase completion files: `PHASE_*.md`
- Test-related reports: `*TEST*.md`

**Purpose**: Track project completion status and document findings

**Examples**:
- `PHASE_1_COMPLETION.md`
- `TEST_COVERAGE_REPORT.md`
- `IMPLEMENTATION_SUMMARY.md`
- `FINAL_STATUS_REPORT.md`

### 5. Research & Analysis
**Directory**: `docs/research/`

**Patterns**:
- Filenames matching `*RESEARCH*.md`
- Filenames matching `*INDEX*.md` (that aren't quick references)

**Purpose**: Document research findings and analysis

**Examples**:
- `ARCHITECTURE_RESEARCH.md`
- `PERFORMANCE_RESEARCH.md`
- `TECHNOLOGY_COMPARISON_INDEX.md`

### 6. Checklists
**Directory**: `docs/checklists/`

**Patterns**:
- Filenames matching `*CHECKLIST*.md`

**Purpose**: Track implementation status and verification

**Examples**:
- `DEPLOYMENT_CHECKLIST.md`
- `RELEASE_READINESS_CHECKLIST.md`
- `SECURITY_AUDIT_CHECKLIST.md`

## Organization Tools

### Automated Organization Script

A script is available to automatically organize markdown files:

```bash
scripts/organize_docs.sh
```

**What it does**:
- Moves markdown files from root to appropriate `docs/` subdirectories
- Preserves files in allowed root locations
- Creates necessary directory structure
- Reports organization results

**Running the script**:
```bash
cd /path/to/project
./scripts/organize_docs.sh
```

**Output**:
```
Starting documentation organization...
=======================================
→ Moved: IMPLEMENTATION_GUIDE.md -> docs/guides/
→ Moved: QUICK_REFERENCE.md -> docs/reference/
→ Moved: COMPLETION_REPORT.md -> docs/reports/
✓ Keeping README.md (allowed in root)
...
Organization Summary
=======================================
Files moved:  34
Files skipped: 5
Errors:       0
```

## Creating New Documentation

When creating a new markdown file:

1. **Determine the file type** based on the classification above
2. **Choose the target directory** accordingly
3. **Create the file** in the appropriate `docs/` subdirectory
4. **Do NOT place it in the root** unless it's on the allowed list

### Example Workflow

```bash
# Creating an implementation guide
cat > docs/guides/MY_IMPLEMENTATION_GUIDE.md << 'EOF'
# My Implementation Guide
...
EOF

# Creating a quick reference
cat > docs/reference/MY_QUICK_REFERENCE.md << 'EOF'
# My Quick Reference
...
EOF

# Creating a completion report
cat > docs/reports/MY_COMPLETION_REPORT.md << 'EOF'
# My Completion Report
...
EOF
```

## Moving Existing Files

To move an existing file to the correct location:

```bash
# Option 1: Use the script (moves all misplaced files)
./scripts/organize_docs.sh

# Option 2: Manual move (for specific file)
git mv MYFILE.md docs/guides/MYFILE.md
git add docs/guides/MYFILE.md
```

## Guidelines

### Naming Conventions

- **Descriptive names**: Use clear, descriptive filenames
- **Consistent casing**: Use UPPER_CASE with underscores
- **Include type**: Include the file type in name (e.g., `_GUIDE`, `_REPORT`)
- **Avoid abbreviations**: Spell out names instead of abbreviating

**Good**:
- `DATABASE_MIGRATION_GUIDE.md`
- `API_QUICK_REFERENCE.md`
- `PHASE_1_COMPLETION_REPORT.md`

**Avoid**:
- `db_migration_guide.md` (lowercase)
- `api_qr.md` (abbreviation)
- `Phase1_Completion.md` (inconsistent casing)

### Content Organization

- **One topic per file**: Keep files focused
- **Clear headings**: Use hierarchy for structure
- **Examples included**: Show concrete examples
- **Links between docs**: Reference related documents
- **Updated dates**: Include when last updated

## Maintenance

### Regular Cleanup

Review documentation periodically:
- Archive outdated files to `docs/archive/`
- Update references in README
- Remove redundant documentation
- Consolidate similar documents

### Checking Organization

To verify proper organization:

```bash
# List all markdown files in root (should only be allowed ones)
ls *.md

# Count files by type
find docs -name "*.md" -path "*/guides/quick-start/*" | wc -l
find docs -name "*.md" -path "*/reference/*" | wc -l
find docs -name "*.md" -path "*/guides/*" | wc -l
find docs -name "*.md" -path "*/reports/*" | wc -l
find docs -name "*.md" -path "*/research/*" | wc -l
find docs -name "*.md" -path "*/checklists/*" | wc -l
```

## Benefits

This organization system provides:

1. **Clarity**: Developers know where to find documentation
2. **Scalability**: Easy to add new docs as project grows
3. **Maintenance**: Simple to locate and update files
4. **Discovery**: Clear structure aids document discovery
5. **Clean root**: Root directory remains clean and focused
6. **Consistency**: Standard structure across the project

## Related Documentation

- See `.github/pull_request_template.md` for PR guidelines
- Check `CLAUDE.md` for AI agent instructions
- Review `README.md` for project overview
