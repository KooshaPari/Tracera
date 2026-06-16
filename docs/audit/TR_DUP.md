# Duplication Audit Report — TR_DUP

Generated: 2026-06-14
Scope: Go (`backend/`), Python (`src/tracertm/`), TypeScript (`frontend/`)
Method: Direct source search + line-verified reads (no build/test runs)

---

## 1. Parallel Model Definitions — Core Domain Entities (Item, Project, Link, Agent, Profile, View)
**Impact:** Cross-layer (all 3 stacks) | **~6 entities x 5 locations = 30+ definitions**

The same six domain entities are defined with nearly identical field names and semantics in Go (GORM + sqlc), Python (SQLAlchemy), and TypeScript. Every structural change requires synchronized edits in 5+ locations.

| Layer | File | Lines | Key Fields |
|-------|------|-------|------------|
| Go (service/GORM) | `backend/internal/models/models.go` | 39–176 | `Item`, `Project`, `Link`, `Agent`, `View`, `Profile` with `gorm` tags |
| Go (DB/sqlc) | `backend/internal/db/models.go` | 12–22, 136–150, 181–190, 250–281 | `Agent`, `Item`, `Link`, `Profile`, `Project` with `pgtype` types |
| Python (SQLAlchemy) | `src/tracertm/models/item.py` | 24–153 | `Item` with `__getattr__`/`__setattr__` aliasing for Go compatibility |
| Python (SQLAlchemy) | `src/tracertm/models/project.py` | 23–64 | `Project` |
| Python (SQLAlchemy) | `src/tracertm/models/link.py` | 23–140 | `Link` |
| Python (SQLAlchemy) | `src/tracertm/models/agent.py` | 18–61 | `Agent` |
| TS (interfaces) | `frontend/packages/types/src/types.ts` | 61–68, 70–104, 240–264, 278–284 | `Project`, `Item`, `Link`, `Agent` interfaces |

**DRY recommendation:** Adopt a canonical schema source (OpenAPI or Protobuf) and generate model definitions for all three layers. In Go, drop the GORM `models` package and use sqlc-generated types as the single source of truth.

---

## 2. DTO Serialization — Model-to-DB Conversion (Item, Project, Link, Agent)
**Impact:** Within Go layer + cross-layer with Python | **~4 handlers x ~50 lines = 200+ lines**

Every Go handler contains a private conversion helper that maps `models.X` to `db.X` (or `db.GetItemRow`). The pattern is identical: parse UUID strings into `pgtype.UUID`, convert `datatypes.JSON` to `[]byte`, wrap timestamps in `pgtype.Timestamp`, and return the db struct. The Python layer (`src/tracertm/api/routers/`, `src/tracertm/api/handlers/`) also manually serializes the same fields into API response dictionaries.

| Entity | Go Handler | Function | Lines |
|--------|-----------|----------|-------|
| Item | `backend/internal/handlers/item_handler.go` | `modelItemToGetItemRow` | 703–764 |
| Project | `backend/internal/handlers/handlers.go` | `modelProjectToDBProject` | 386–430 |
| Link | `backend/internal/handlers/link_handler.go` | `modelLinkToDBLink` | 245–266 |
| Agent | `backend/internal/handlers/agent_handler.go` | `modelAgentToDbAgent` | 814–847 |

**DRY recommendation:** In Go, write a generic `ToDBRow` helper using Go generics that can handle any model with `ID`, `ProjectID`, `Metadata`, `CreatedAt`, `UpdatedAt`, `DeletedAt` fields. In Python, use Pydantic `model_dump()` on schema classes rather than hand-writing serialization.

---

## 3. UUID Validation, Normalization & Generation
**Impact:** Cross-layer (Go + Python + TS) | **Same regex, same logic, 3 implementations**

Go and Python both implement the exact same UUID regex (`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`), normalization (lowercase + trim), and batch validation. The frontend also validates UUIDs with a case-insensitive regex.

| Layer | File | Lines |
|-------|------|-------|
| Go | `backend/internal/validation/id_validator.go` | 11–47 |
| Python | `src/tracertm/validation/id_validator.py` | 6–72 |
| TS | `frontend/apps/web/src/utils/validators.ts` | 28–32 |

**DRY recommendation:** Use language-specific standard-library UUID parsers instead of custom regex (Go: `uuid.Parse`, Python: `uuid.UUID`, Frontend: `z.string().uuid()`). If regex is required, store the pattern in a single shared config file consumed at build time.

---

## 4. String Length & Required Field Validation
**Impact:** Cross-layer (Go + Python + TS) | **Same limits, 3 syntaxes**

All three layers enforce identical title length (500), project name length (100), and required checks with whitespace trimming.

| Layer | File | Lines | Mechanism |
|-------|------|-------|-----------|
| Go | `backend/internal/validation/validators.go` | 20–56 | `ValidateStringLength`, `ValidateNonEmpty`, `ValidateRequiredString` |
| Python | `src/tracertm/schemas/item.py` | 11–17 | Pydantic `Field(min_length=1, max_length=500)` |
| TS | `frontend/apps/web/src/lib/validation/schemas.ts` | 40–63 | Zod `shortTextSchema` / `mediumTextSchema` with `.min(1).max(500)` |
| TS | `frontend/apps/web/src/utils/validators.ts` | 42–48 | `hasMinLength` / `hasMaxLength` helpers |

**DRY recommendation:** Centralize validation constraints in a shared JSON/YAML schema definition. Generate Zod schemas, Pydantic models, and Go validation constants from this single source. Start with the existing `frontend/apps/web/src/lib/validation/schemas.ts` as the canonical TS source.

---

## 5. File Upload Validation (MIME Types, Size Limits, Filename Security)
**Impact:** Cross-layer (Go + TS) | **Identical allowlists and size constants**

Both layers define identical allowlists for image MIME types and document types, with the same size limits (10 MB default, 5 MB images, 20 MB documents). Both also check for path traversal (`..` and `/`) in filenames.

| Layer | File | Lines |
|-------|------|-------|
| Go | `backend/internal/validation/validators.go` | 202–339 |
| TS | `frontend/apps/web/src/lib/validation/schemas.ts` | 258–292 |

**DRY recommendation:** Move file upload constraints into a shared configuration file (e.g., `config/upload-limits.yaml`) that is loaded by both the Go backend and the frontend build pipeline. The frontend can import the constants at build time.

---

## 6. Email Validation
**Impact:** Cross-layer (Go + TS) | **Dual regex + parser in Go; simple regex in TS**

Go validates email with both `mail.ParseAddress` (RFC 5322) and a regex. Frontend uses Zod's built-in `.email()` plus a simple regex in `validators.ts`. Both use the same 255-character max length.

| Layer | File | Lines |
|-------|------|-------|
| Go | `backend/internal/validation/validators.go` | 85–107 |
| TS | `frontend/apps/web/src/lib/validation/schemas.ts` | 7–11 |
| TS | `frontend/apps/web/src/utils/validators.ts` | 8–11 |

**DRY recommendation:** The frontend should rely on Zod's `.email()` (sufficient for client-side UX). The backend should use a single shared email validator and avoid dual-regex + parser validation. Move the email regex into a shared schema definition if client-side parity is needed.

---

## 7. Service-to-DB Model Conversion Helpers (`model*ToDB*` Pattern)
**Impact:** Within Go layer — spans 4 handlers | **~200 lines of identical code**

Every handler has a private conversion helper that maps `models.X` to `db.X`. The pattern is identical: parse UUID strings, convert JSON metadata, wrap timestamps, handle soft-delete timestamps. This is the same cluster as #2 but scoped to the within-Go duplication specifically.

| Handler | Function | Lines |
|---------|----------|-------|
| `backend/internal/handlers/item_handler.go` | `modelItemToGetItemRow` | 703–764 |
| `backend/internal/handlers/handlers.go` | `modelProjectToDBProject` | 386–430 |
| `backend/internal/handlers/link_handler.go` | `modelLinkToDBLink` | 245–266 |
| `backend/internal/handlers/agent_handler.go` | `modelAgentToDbAgent` | 814–847 |

**DRY recommendation:** Write a generic `ToDBRow` function using Go generics or code generation (e.g., `go generate` with a custom template) that can handle any model with standard fields (`ID`, `ProjectID`, `Metadata`, `CreatedAt`, `UpdatedAt`, `DeletedAt`).

---

## 8. Frontend Form Schemas Duplicating Central Validation Library
**Impact:** Within Frontend layer — every form component redefines its own Zod schema | **~3 forms, ~50 lines**

`CreateItemForm.tsx` and `CreateProjectForm.tsx` define their own Zod schemas inline instead of importing the canonical schemas from `lib/validation/schemas.ts`. The field names, types, and constraints are identical.

| File | Inline Schema | Lines | Duplicates Central Schema |
|------|-------------|-------|---------------------------|
| `frontend/apps/web/src/components/forms/CreateItemForm.tsx` | `itemSchema` | 28–37 | `createItemSchema` (`lib/validation/schemas.ts:148–159`) |
| `frontend/apps/web/src/components/forms/CreateProjectForm.tsx` | `projectSchema` | 11–14 | `createProjectSchema` (`lib/validation/schemas.ts:191–199`) |

**DRY recommendation:** Form components should import and reuse schemas from `lib/validation/schemas.ts`. If a form needs extra fields, extend the base schema with `.extend()` or `.merge()` rather than redefining the entire object.

---

## 9. UUID Generation on Model Creation (BeforeCreate Hooks / `generate_*_uuid`)
**Impact:** Within Go + Python layers | **6 Go hooks + 15+ Python functions**

Every Go model has a copy-pasted `BeforeCreate` hook that generates `uuid.New().String()` if `ID == ""`. Every Python model has a copy-pasted `generate_*_uuid()` function that calls `uuid.uuid4()`.

| Layer | File | Lines | Count |
|-------|------|-------|-------|
| Go | `backend/internal/models/models.go` | 91–120, 170–176 | 6 hooks (`Item`, `Link`, `Project`, `Agent`, `View`, `Profile`) |
| Python | `src/tracertm/models/item.py` | 19–21 | `generate_item_uuid` |
| Python | `src/tracertm/models/project.py` | 18–20 | `generate_project_uuid` |
| Python | `src/tracertm/models/link.py` | 18–20 | `generate_link_uuid` |
| Python | `src/tracertm/models/agent.py` | 13–15 | `generate_agent_uuid` |
| Python | `src/tracertm/models/view.py` | 13–15 | `generate_view_uuid` |
| Python | `src/tracertm/models/workflow.py` | 13–15 | `generate_workflow_uuid` |
| Python | `src/tracertm/models/test_case.py` | 19–21 | `generate_test_case_uuid` |
| Python | `src/tracertm/models/specification.py` | 23–25 | `generate_specification_uuid` |
| Python | `src/tracertm/models/process.py` | 19–21 | `generate_process_uuid` |
| Python | `src/tracertm/models/problem.py` | 19–21 | `generate_problem_uuid` |
| Python | `src/tracertm/models/node_kind.py` | 13–15 | `generate_node_kind_uuid` |
| Python | `src/tracertm/models/link_type.py` | 13–15 | `generate_link_type_uuid` |
| Python | `src/tracertm/models/graph.py` | 13–15 | `generate_graph_uuid` |
| Python | `src/tracertm/models/agent_session.py` | 13–15 | `generate_agent_session_uuid` |
| Python | `src/tracertm/models/agent_lock.py` | 13–15 | `generate_lock_uuid` |

**DRY recommendation:** In Go, use a GORM plugin or a single generic `BeforeCreate` on a base struct. In Python, define a single `generate_uuid` utility in `models/base.py` and use `default=generate_uuid` everywhere.

---

## 10. System Admin Email Check
**Impact:** Within Python layer — duplicated across 3 files | **~45 lines, verbatim copies**

The `_system_admin_emails()` and `_is_system_admin_email()` functions are duplicated verbatim (including the same global cache variable name `_admin_emails_cache`) in three separate Python files. This is a security-critical function that should have a single source of truth.

| File | `_system_admin_emails` | `_is_system_admin_email` |
|------|------------------------|--------------------------|
| `src/tracertm/api/security.py` | 119–126 | 129–132 |
| `src/tracertm/api/middleware/auth.py` | 130–138 | 141–145 |
| `src/tracertm/api/handlers/auth.py` | 61–69 | 72–76 |

**DRY recommendation:** Remove the duplicate implementations from `handlers/auth.py` and `middleware/auth.py`. Import both functions from `api/security.py` (the canonical security module). If circular imports are a concern, move the functions into a dedicated `src/tracertm/auth/admin.py` module.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Cross-layer duplication clusters | 6 |
| Within-Go duplication clusters | 2 |
| Within-Python duplication clusters | 1 |
| Within-Frontend duplication clusters | 1 |
| Total duplicated lines (estimated) | ~500+ |
| Files affected | 20+ |
| Domains with parallel models | 6 (Item, Project, Link, Agent, Profile, View) |
