# Code Annotation Scripts

Three scripts for adding and validating FR/ADR/Epic references in code docstrings.

## Scripts Overview

### 1. annotate_services_with_frs.py
Annotates service files with FR/ADR/Epic references in docstrings.

**Features:**
- Reads FUNCTIONAL_REQUIREMENTS.md for FR → implementation mappings
- Reads PRD.md for Epic hierarchy
- Reads ADR files for architecture decision references
- Parses Python service files using AST
- Matches FRs to functions/classes based on implementation locations
- Updates docstrings with structured FR/ADR/Epic sections
- Preserves existing docstring content
- Optional ruff/mypy verification

**Usage:**
```bash
# Annotate all service files (dry-run)
python scripts/python/annotate_services_with_frs.py --dry-run

# Annotate all service files and write changes
python scripts/python/annotate_services_with_frs.py

# Annotate single file
python scripts/python/annotate_services_with_frs.py --file src/tracertm/services/github_import_service.py

# Annotate and verify with ruff/mypy
python scripts/python/annotate_services_with_frs.py --verify
```

**Example Transformation:**
```python
# Before
async def import_from_github(self, repo: str) -> ImportResult:
    """Import requirements from GitHub repository."""
    ...

# After
async def import_from_github(self, repo: str) -> ImportResult:
    """Import requirements from GitHub repository.

    Functional Requirements:
    - FR-DISC-001

    User Stories:
    - US-INT-001

    Epics:
    - E1.1: Multi-Source Import

    Architecture:
    - ADR-0002: FastMCP Integration
    - ADR-0015: Import/Export Strategy
    """
    ...
```

### 2. annotate_apis_with_frs.py
Annotates API endpoint functions with FR references in docstrings.

**Features:**
- Scans API router files in src/tracertm/api/routers/
- Finds endpoint decorators (@router.get, @router.post, etc.)
- Extracts endpoint paths and HTTP methods
- Matches endpoints to FRs from FUNCTIONAL_REQUIREMENTS.md
- Adds FR references to endpoint docstrings
- Preserves FastAPI doc metadata

**Usage:**
```bash
# Annotate all API routers (dry-run)
python scripts/python/annotate_apis_with_frs.py --dry-run

# Annotate all API routers and write changes
python scripts/python/annotate_apis_with_frs.py

# Annotate single router file
python scripts/python/annotate_apis_with_frs.py --file src/tracertm/api/routers/github.py

# Annotate and verify with ruff
python scripts/python/annotate_apis_with_frs.py --verify
```

**Example Transformation:**
```python
# Before
@router.post("/api/v1/integrations/github/app/installations/{id}/link")
async def link_installation(id: str) -> LinkResponse:
    """Link GitHub App installation to project."""
    ...

# After
@router.post("/api/v1/integrations/github/app/installations/{id}/link")
async def link_installation(id: str) -> LinkResponse:
    """Link GitHub App installation to project.

    Functional Requirements:
    - FR-DISC-001

    User Stories:
    - US-INT-001

    Epics:
    - E1.1
    """
    ...
```

### 3. verify_fr_references.py
Pre-commit validation script for FR/ADR/Epic references in docstrings.

**Features:**
- Extracts FR/ADR/Epic IDs from docstrings in Python files
- Validates IDs exist in master documents:
  - FUNCTIONAL_REQUIREMENTS.md
  - PRD.md
  - docs/adr/*.md
- Returns exit code 1 if invalid references found
- Warns if service/API files lack FR references
- Can be used as pre-commit hook

**Usage:**
```bash
# Validate specific files
python scripts/python/verify_fr_references.py file1.py file2.py

# Validate all staged files in git
python scripts/python/verify_fr_references.py --git-staged

# Validate all service/API files
python scripts/python/verify_fr_references.py --all
```

**Exit Codes:**
- 0: All references valid
- 1: Invalid references found
- 2: Configuration error (missing master docs)

**Example Output:**
```
INFO: Loaded 150 valid FRs
INFO: Loaded 42 valid Epics
INFO: Loaded 15 valid ADRs
INFO: Validating src/tracertm/services/example_service.py

=== ERRORS ===
ERROR: src/tracertm/services/example_service.py: Invalid FR reference: FR-FAKE-999

=== WARNINGS ===
WARNING: src/tracertm/services/new_service.py: Service/API file has no FR references
```

## Pre-commit Hook Setup

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: verify-fr-references
        name: Verify FR/ADR/Epic References
        entry: python scripts/python/verify_fr_references.py --git-staged
        language: system
        types: [python]
        pass_filenames: false
```

Or use git hooks manually:

```bash
# .git/hooks/pre-commit
#!/bin/bash
python scripts/python/verify_fr_references.py --git-staged
exit $?
```

## Workflow Integration

### Initial Annotation
```bash
# 1. Annotate all services
python scripts/python/annotate_services_with_frs.py --verify

# 2. Annotate all APIs
python scripts/python/annotate_apis_with_frs.py --verify

# 3. Verify all annotations
python scripts/python/verify_fr_references.py --all
```

### Continuous Validation
```bash
# Pre-commit validation
python scripts/python/verify_fr_references.py --git-staged

# CI validation
python scripts/python/verify_fr_references.py --all
```

## Requirements

**Input Files:**
- docs/reference/FUNCTIONAL_REQUIREMENTS.md (FR mappings)
- docs/reference/PRD.md (Epic hierarchy)
- docs/adr/*.md (ADR list)

**Python Dependencies:**
- Python 3.12+
- Standard library only (ast, re, argparse, logging, pathlib)

**Optional (for --verify flag):**
- ruff
- mypy

## Limitations

1. **Service Annotation:**
   - Only annotates functions/classes explicitly listed in FUNCTIONAL_REQUIREMENTS.md
   - Requires exact function/class name match
   - Skips functions without existing docstrings

2. **API Annotation:**
   - Only annotates endpoints explicitly listed in FUNCTIONAL_REQUIREMENTS.md
   - Requires exact path match (normalizes {id}, {name}, etc.)
   - Skips endpoints without existing docstrings

3. **Validation:**
   - Python files only (no Go, TypeScript)
   - Pattern-based extraction (may miss complex docstring formats)
   - Warnings for missing references (not errors)

## Troubleshooting

**No files updated:**
- Check FUNCTIONAL_REQUIREMENTS.md has "Implemented in:" sections
- Verify file paths match exactly
- Ensure functions/classes have existing docstrings

**Invalid reference errors:**
- Update master docs (FUNCTIONAL_REQUIREMENTS.md, PRD.md, adr/*.md)
- Check FR/ADR/Epic ID format (FR-XXX-NNN, ADR-NNNN, E1.1.2)

**Syntax errors:**
- Run ruff/mypy before annotation
- Check for malformed docstrings
- Verify Python version compatibility
