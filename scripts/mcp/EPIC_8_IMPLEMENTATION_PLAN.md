# Epic 8: Import/Export & Data Portability – Implementation Plan

## Overview

**Epic 8** enables users to backup, migrate, and integrate TraceRTM with external tools through multiple export/import formats.

**Goal:** Users can backup projects, migrate between environments, and integrate with external tools.

**FRs Covered:** FR74-FR82 (Data Import/Export)

**Effort:** 12 days

**Stories:** 5

---

## Stories Breakdown

### Story 8.1: JSON Export (2 days)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ `rtm export --format json --output my-project.json` exports all data
- ✅ Export includes: projects, items, links, events, agents
- ✅ JSON is valid and parseable
- ✅ Export specific views: `rtm export --view FEATURE --format json`
- ✅ Export completes in <5s for 10K items

**Technical:**
- Implement `ExportService.export_json()`
- Use Pydantic `.model_dump_json()` for serialization
- Support incremental export (only changed items)
- Compress large exports with gzip
- Validate JSON structure before writing

**FRs:** FR74, FR75

---

### Story 8.2: YAML Export (2 days)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ `rtm export --format yaml --output my-project.yaml` exports all data
- ✅ YAML is human-readable and editable
- ✅ Export specific items: `rtm export <item-id> --format yaml`
- ✅ YAML includes comments for clarity
- ✅ Export completes in <5s for 10K items

**Technical:**
- Implement `ExportService.export_yaml()`
- Use PyYAML for serialization
- Add comments for structure clarity
- Support multi-document YAML (one per item)
- Validate YAML structure before writing

**FRs:** FR76, FR75

---

### Story 8.3: CSV Export (2 days)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ `rtm export --format csv --output items.csv` exports items
- ✅ CSV includes: id, type, view, title, status, owner, created_at, updated_at
- ✅ Customize columns: `rtm export --format csv --columns id,title,status`
- ✅ CSV compatible with Excel and Google Sheets
- ✅ Export completes in <5s for 10K items

**Technical:**
- Implement `ExportService.export_csv()`
- Use Python csv module
- Support custom column selection
- Flatten nested data (metadata as JSON string)
- Handle special characters and escaping

**FRs:** FR77, FR75

---

### Story 8.4: JSON Import (3 days)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ `rtm import --format json --input my-project.json` imports all data
- ✅ Import validates data before applying
- ✅ Import into new project: `rtm import --input backup.json --project new-project`
- ✅ Handle conflicts (skip, overwrite, merge)
- ✅ Import completes in <10s for 10K items

**Technical:**
- Implement `ImportService.import_json()`
- Validate with Pydantic schemas
- Use database transactions for atomicity
- Implement conflict resolution strategies
- Log import operations to event_log

**FRs:** FR78, FR79

---

### Story 8.5: CSV Import (2 days)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ `rtm import --format csv --input items.csv` imports items
- ✅ CSV must have headers: type, view, title, description, status
- ✅ Import validates each row before creating
- ✅ Invalid rows skipped with error report
- ✅ Import completes in <10s for 1000 items

**Technical:**
- Implement `ImportService.import_csv()`
- Validate CSV headers and data types
- Use batch operations for performance
- Generate error report for invalid rows
- Support dry-run mode: `--dry-run`

**FRs:** FR80, FR79

---

### Story 8.6: Incremental Sync & Merge (1 day)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ `rtm sync --from remote-backup.json` syncs only changed items
- ✅ Sync detects conflicts (same item modified in both)
- ✅ Choose conflict resolution: skip, overwrite, merge
- ✅ Bidirectional sync: `rtm sync --bidirectional`
- ✅ Sync completes in <5s for 1000 changed items

**Technical:**
- Implement `SyncService.sync()`
- Compare versions to detect changes
- Implement 3-way merge for conflicts
- Use event_log for change detection
- Support dry-run mode

**FRs:** FR81, FR82

---

## Implementation Order

1. **Story 8.1** – JSON export (foundation)
2. **Story 8.2** – YAML export (similar to JSON)
3. **Story 8.3** – CSV export (different format)
4. **Story 8.4** – JSON import (foundation)
5. **Story 8.5** – CSV import (similar to JSON)
6. **Story 8.6** – Incremental sync (advanced)

---

## Success Criteria

- [ ] All 5 stories completed
- [ ] All acceptance criteria met
- [ ] All FRs (FR74-FR82) covered
- [ ] Tests passing (>80% coverage)
- [ ] Documentation complete
- [ ] Ready for Epics 6-7

---

## Next Steps

1. Start with Story 8.1 (JSON export)
2. Implement each story in order
3. Test after each story
4. Document as you go
5. Move to Epics 6-7 when complete

