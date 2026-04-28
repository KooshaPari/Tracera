# Epic 1: Project Foundation & Setup – Implementation Plan

## Overview

**Epic 1** enables users to initialize TraceRTM, configure database, and create their first project.

**Goal:** Users can install TraceRTM and start managing their first project within minutes.

**FRs Covered:** FR83-FR88 (Configuration & Setup)

**Effort:** 15 days

**Stories:** 6

---

## Stories Breakdown

### Story 1.1: Package Installation & Environment Setup (2 days)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ `pip install tracertm` works
- ✅ `rtm --version` displays version
- ✅ `rtm --help` shows available commands
- ✅ Shell completion scripts available (Bash/Zsh/Fish)

**Technical:**
- Implement `setup.py` / `pyproject.toml` with entry point `rtm`
- Use Typer for CLI framework
- Include shell completion generation
- Dependencies: SQLAlchemy 2.0+, Pydantic v2, Typer, Rich

**FRs:** FR83

---

### Story 1.2: Database Connection & Migration System (3 days)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ `rtm config init` creates config file
- ✅ Database connection validated
- ✅ Alembic migrations create all tables
- ✅ Indexes created for performance
- ✅ `rtm db status` health check works

**Technical:**
- SQLAlchemy models: Project, Item, Link, Event, Agent
- Alembic migration for initial schema
- Connection pooling (pool_size=20, max_overflow=10)
- Health check command

**FRs:** FR84, FR85

---

### Story 1.3: Project Initialization Workflow (2 days)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ `rtm project init my-first-project` creates project
- ✅ Default config (8 core views enabled)
- ✅ Project ID returned and set as current
- ✅ `rtm project list` verifies creation

**Technical:**
- Implement `ProjectRepository.create()`
- Store project config in JSONB field
- Set current project in config file
- Implement `rtm project switch <name>`

**FRs:** FR83, FR86

---

### Story 1.4: Configuration Management (2 days)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ `rtm config set default_view FEATURE` works
- ✅ `rtm config set output_format json` works
- ✅ `rtm config show` displays current config
- ✅ Project-specific config overrides global
- ✅ Config persisted to `~/.tracertm/config.yaml`

**Technical:**
- Config hierarchy: CLI flags > env vars > project config > global config
- Pydantic for config validation
- YAML config files
- ConfigManager singleton pattern

**FRs:** FR85-FR87

---

### Story 1.5: Backup & Restore Capability (2 days)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ `rtm backup --output my-project-backup.json` exports data
- ✅ `rtm restore --input my-project-backup.json` restores data
- ✅ Backup includes: projects, items, links, events, agents
- ✅ Restore validates data before applying
- ✅ Backup completes in <5s for 10K items

**Technical:**
- Implement `ExportService.export_project()` (JSON/YAML)
- Implement `ImportService.import_project()` with validation
- Pydantic schemas for validation
- Support incremental backups (events only)
- Compress large backups with gzip

**FRs:** FR88

---

### Story 1.6: Error Handling & User-Friendly Messages (2 days)
**Status:** ⏳ TODO

**Acceptance Criteria:**
- ✅ Clear, actionable error messages (no stack traces)
- ✅ Error messages include suggestions
- ✅ Errors logged to file
- ✅ Meaningful exit codes (0=success, 1=error, 2=validation)
- ✅ Stack traces only with `--debug` flag

**Technical:**
- Exception hierarchy (TraceRTMError, ValidationError, NotFoundError, etc.)
- Rich for colored error output
- Error handling pattern in CLI commands
- Logging to `~/.tracertm/logs/tracertm.log`
- Suggestions in error messages

**FRs:** NFR-U3, NFR-R3

---

## Implementation Order

1. **Story 1.1** – Package setup (foundation)
2. **Story 1.2** – Database setup (foundation)
3. **Story 1.3** – Project init (core feature)
4. **Story 1.4** – Config management (core feature)
5. **Story 1.5** – Backup/restore (nice-to-have)
6. **Story 1.6** – Error handling (cross-cutting)

---

## Success Criteria

- [ ] All 6 stories completed
- [ ] All acceptance criteria met
- [ ] All FRs (FR83-FR88) covered
- [ ] Tests passing (>80% coverage)
- [ ] Documentation complete
- [ ] Ready for Epic 2

---

## Next Steps

1. Start with Story 1.1 (package setup)
2. Implement each story in order
3. Test after each story
4. Document as you go
5. Move to Epic 2 when complete

