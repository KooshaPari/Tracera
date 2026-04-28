# TraceRTM Traceability System Guide

**Version:** 1.0.0
**Date:** 2026-02-12
**Status:** Active

---

## Overview

The TraceRTM traceability system provides bidirectional traceability between documentation artifacts (Epics, FRs, ADRs, User Stories) and code artifacts (Models, Services, APIs, Tests). The system uses auto-discovery to scan documentation and code, extract references, and build a comprehensive link database.

---

## Components

### 1. JSON Schema

**File:** `docs/schemas/traceability_links_schema.json`

Defines the structure of traceability links:

- **DocReference** - References to documentation (Epic/FR/ADR/Journey/Task)
- **CodeReference** - References to code (Model/Service/API/Handler/Tool/Test)
- **TraceLink** - Bidirectional links with metadata and confidence scores

**Link Types:**
- `traces_to` - Requirement traces to higher-level artifact (FR → Epic)
- `implements` - Code implements a requirement (Service → FR)
- `tested_by` - Requirement/code tested by test case
- `documents` - Documentation describes code
- `depends_on` - Dependency relationship
- `supersedes` - Newer artifact replaces older one
- `relates_to` - General relationship
- `refines` - More detailed specification
- `validates` - Validation relationship

**Confidence Levels:**
- `high` - Explicit reference in documentation
- `medium` - Discovered from code comments or file naming
- `low` - Weak heuristic match

### 2. Link Database

**File:** `docs/generated/traceability_links.json`

Auto-generated database of all discovered traceability links. Contains:

```json
{
  "version": "1.0.0",
  "project": {
    "name": "TraceRTM",
    "id": "tracertm",
    "description": "Requirements Traceability Matrix System"
  },
  "generated_at": "2026-02-12T11:52:53.264971+00:00",
  "links": [...],
  "statistics": {
    "total_links": 1594,
    "by_type": {...},
    "by_confidence": {...}
  }
}
```

### 3. Auto-Discovery Script

**File:** `scripts/python/discover_traceability_links.py`

Python script that scans the codebase and documentation to auto-discover traceability links.

**Usage:**

```bash
# Standard usage - output to default location
python scripts/python/discover_traceability_links.py

# Custom output location
python scripts/python/discover_traceability_links.py --output my_links.json

# Verbose mode
python scripts/python/discover_traceability_links.py --verbose
```

**Discovery Phases:**

1. **Phase 1: Document Scanning**
   - Scans all `docs/**/*.md` files
   - Extracts FR/Epic/ADR/User Story IDs using regex
   - Records file path and line number for each reference

2. **Phase 2: Code Scanning**
   - Uses Python AST to parse source files
   - Extracts class/function definitions with precise line numbers
   - Maps code artifacts to modules

3. **Phase 3: Explicit Link Extraction**
   - Parses "Traces to:", "Implemented in:", "Tested in:" sections
   - Creates high-confidence links from structured documentation

4. **Phase 4: Docstring Reference Scanning**
   - Searches code comments for FR/ADR/Epic mentions
   - Creates medium-confidence links

5. **Phase 5: Test File Matching**
   - Matches `test_*.py` files to source files by name
   - Creates tested_by links

---

## Link Examples

### FR → Epic (traces_to)

```json
{
  "id": "uuid",
  "from": {
    "type": "FR",
    "id": "FR-DISC-001",
    "file": "docs/reference/FUNCTIONAL_REQUIREMENTS.md",
    "line": 26
  },
  "to": {
    "type": "Epic",
    "id": "EPIC-001",
    "file": "docs/reference/PRD.md",
    "line": 109
  },
  "linkType": "traces_to",
  "confidence": "high"
}
```

### FR → Code (implements)

```json
{
  "id": "uuid",
  "from": {
    "type": "FR",
    "id": "FR-DISC-001",
    "file": "docs/reference/FUNCTIONAL_REQUIREMENTS.md",
    "line": 26
  },
  "to": {
    "type": "Service",
    "name": "GitHubImportService",
    "file": "src/tracertm/services/github_import_service.py",
    "line_start": 1,
    "line_end": 350
  },
  "linkType": "implements",
  "confidence": "high"
}
```

### Code → Test (tested_by)

```json
{
  "id": "uuid",
  "from": {
    "type": "Service",
    "name": "AutoLinkService",
    "file": "src/tracertm/services/auto_link_service.py",
    "line_start": 45
  },
  "to": {
    "type": "Test",
    "name": "test_auto_link",
    "file": "tests/test_auto_link.py",
    "line_start": 1
  },
  "linkType": "tested_by",
  "confidence": "medium"
}
```

---

## Improving Link Quality

### Add Explicit Documentation Links

In `docs/reference/FUNCTIONAL_REQUIREMENTS.md`, add structured sections:

```markdown
### FR-DISC-001: GitHub Issue Import

#### Traceability

**Traces to:**
- **Epic:** EPIC-001 (External Integration)
- **User Stories:** US-INT-001 (Import from GitHub)

**Implemented in:**
- **File(s):** `src/tracertm/services/github_import_service.py:1-350`
- **Functions/Classes:** `GitHubImportService.import_from_github()`
- **API Endpoints:** `POST /api/v1/integrations/github/app/installations/{id}/link`

**Tested in:**
- **Integration Tests:** `tests/integration/test_github_import.py::test_import_issues`
```

### Add Code Annotations

In Python source files, add references in docstrings:

```python
class GitHubImportService:
    """
    GitHub integration service.

    Implements:
        - FR-DISC-001: GitHub Issue Import
        - EPIC-001: External Integration

    Related ADRs:
        - ADR-0001: TraceRTM v2 Architecture
        - ADR-0002: FastMCP Integration
    """

    def import_from_github(self, installation_id: str) -> dict:
        """
        Import GitHub issues as traceability items.

        Implements FR-DISC-001.
        """
        pass
```

---

## Current Statistics

As of 2026-02-12:

- **Total Links:** 1,594
- **Documentation References:** 667 (FRs, Epics, ADRs, User Stories)
- **Code References:** 2,943 (Classes, Functions, Services)

**By Link Type:**
- `traces_to`: 5 (high confidence)
- `implements`: 2 (medium confidence)
- `tested_by`: 1,587 (medium confidence)

**By Confidence:**
- High: 5 (0.3%)
- Medium: 1,589 (99.7%)
- Low: 0 (0%)

**Coverage:**
- 5 out of 29 FRs have explicit traces_to links (17%)
- ~54% of code files have matched test files

---

## Future Enhancements

### Phase 1: Enhanced Discovery
- [ ] Add Go code scanning (AST parsing for `.go` files)
- [ ] Add TypeScript/JavaScript scanning
- [ ] Extract ADR "Related Requirements" sections
- [ ] Parse OpenAPI spec annotations for API → FR links

### Phase 2: Link Validation
- [ ] Verify links point to existing artifacts
- [ ] Detect broken links (file moved/deleted)
- [ ] Flag outdated links (last modified > 90 days)

### Phase 3: Visualization
- [ ] Generate traceability matrix HTML report
- [ ] Build interactive graph visualization (D3.js)
- [ ] Create coverage heat maps
- [ ] Export to PlantUML/Mermaid diagrams

### Phase 4: Integration
- [ ] MCP tool: `get_traceability_links(item_id)`
- [ ] MCP tool: `validate_traceability(project_id)`
- [ ] API endpoint: `GET /api/v1/traceability/links`
- [ ] Real-time link updates via file watcher

---

## Troubleshooting

### No links discovered from docs

**Problem:** Script finds 0 documentation references.

**Solution:** Ensure `docs/` directory exists and contains `.md` files with FR/Epic/ADR IDs.

### Low link count

**Problem:** Expected more links than discovered.

**Solution:**
1. Add explicit "Traces to:", "Implemented in:", "Tested in:" sections to FRs
2. Add FR/ADR references to code docstrings
3. Ensure consistent ID formats (FR-DISC-001, EPIC-001, ADR-0001)

### Syntax errors during code scanning

**Problem:** Script warns about files with syntax errors.

**Solution:** These warnings are expected for files with syntax issues. The script skips them and continues. Fix syntax errors to enable scanning.

---

## Reference

### ID Formats

- **Epic:** `EPIC-NNN` or `E1.2.3`
- **FR:** `FR-CATEGORY-NNN` (e.g., FR-DISC-001)
- **ADR:** `ADR-NNNN` (e.g., ADR-0001)
- **User Story:** `US-CATEGORY-NNN` (e.g., US-INT-001)
- **Requirement:** `REQ-CATEGORY-NNN`

### File Patterns

- **Services:** `src/tracertm/services/*.py`
- **Models:** `src/tracertm/models/*.py`
- **APIs:** `src/tracertm/api/*.py`
- **Tests:** `tests/**/test_*.py`
- **Documentation:** `docs/**/*.md`

---

**Maintained by:** TraceRTM Team
**Last Updated:** 2026-02-12
