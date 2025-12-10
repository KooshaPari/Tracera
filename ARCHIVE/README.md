# ARCHIVE - Historical Documentation & Backups

This directory contains archived materials from previous phases, historical reports, and backup snapshots. These are retained for reference and compliance but are not part of the active project.

## Directory Structure

### 📦 SNAPSHOTS/ (242 files)
Database and project snapshots taken during development.
- Format: `tracertm_backup_YYYYMMDD_HHMMSS.json.gz`
- Use for: Historical data recovery, rollback reference
- Status: Read-only backups

### 📊 TEST_REPORTS/ (205+ files)
Historical test coverage, integration test, and API test reports from development phases.
- Includes: Coverage reports, test summaries, quick references, edge case documentation
- Time period: December 2024 - December 2025
- Status: Reference material

### 📋 PHASE_REPORTS/ (73+ files)
Completed phase deliverables, work package reports, and milestone documentation.
- Phase 1-4 completion reports
- Weekly dashboards and status updates
- Execution manifests and delivery summaries
- Status: Historical record

### 📝 AGENT_DOCS/ (5 files)
Agent assignment tracking, workload analysis, and collaboration documentation.
- AGENT_ASSIGNMENTS_UPDATED.md
- AGENT_QUICK_START.md
- AGENT_WORKLOAD_BALANCE_ANALYSIS.md
- WORK_PACKAGES_AGENTS.md
- FINAL_ESCALATION_COMPLETE_ALL_11_AGENTS.md

### 📖 NOTES/ (35+ files)
Reference guides, quick references, indices, and assessment documentation.
- Quick reference guides (API, CLI, Services, E2E)
- Assessment and review documents
- Onboarding and checklist materials
- Implementation guides
- Status: Reference material

### 🗂️ OLD_DOCS/ (12 files)
Historical implementation notes and fixes from earlier development phases.
- Critical fixes applied
- Database initialization fixes
- TUI widget event handling fixes
- Pre-launch blockers and validations
- Standup logs and execution status
- Status: Historical reference

### 🔄 TEMPORARY/ (empty)
Placeholder for temporary files during development cleanup.

### 📁 OLD_REPORTS/ (empty)
Placeholder for consolidated old reports.

## Usage

### When to Reference
- **Historical context**: Understanding previous implementation decisions
- **Data recovery**: Using backup snapshots if needed
- **Compliance**: Maintaining audit trail of development
- **Lessons learned**: Reviewing what worked and what didn't

### When NOT to Use
- Active development: Use files in root directory and PHASES/, DEFERRED_WORK/, etc.
- Current documentation: Refer to INDEX.md and other root-level guides
- Production code: Never take code from ARCHIVE

## Statistics

| Category | Count | Size |
|----------|-------|------|
| Backups (SNAPSHOTS) | 242 | ~500MB |
| Test Reports | 205 | ~85MB |
| Phase Reports | 73 | ~2MB |
| Agent Docs | 5 | ~100KB |
| Notes/Guides | 35 | ~900KB |
| Old Docs | 12 | ~270KB |
| **TOTAL** | **572** | **~588MB** |

## Organization Date

Organized: December 10, 2025
Previous state: 326 markdown files + 242 backups scattered in root directory
Current state: Consolidated and organized by category

## Related Documents

- **ROOT/INDEX.md** - Main project navigation
- **ROOT/00_START_HERE.md** - Project entry point
- **DEFERRED_WORK/** - Incomplete items (archived in PHASES/)
- **PHASES/** - Active phase documentation
- **GOVERNANCE_AUDIT_REPORT.md** - Compliance documentation

---

**Note:** This archive is for historical reference only. Active project files remain in the root directory and organized subdirectories.
