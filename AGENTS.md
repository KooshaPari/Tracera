# Tracera — AGENTS.md

**Date:** 2026-06-21
**Status:** ACTIVE
**Substrate type:** app / multi-stack (Rust + Python + Go + TypeScript)
**Worklog schema:** v2.1 (ADR-025 / ADR-030) — 11 columns including `device:` field

## Project Overview

Tracera is an agent-native requirements traceability and project-management system built around the Rust `tracera-core` crate, the `traceability-core` domain model from `phenotype-pm-core`, and polyglot integration surfaces in Python, Go, and TypeScript.

**Repository:** `Tracera/`
**Language:** Rust (primary), Python, Go, TypeScript
**Build System:** Cargo (Rust), uv (Python), Go Modules, pnpm (TS)
**License:** MIT
**CI/CD:** GitHub Actions (`.github/workflows/`)

## Tier-0 meta-bundle (v22-SD1 hygiene batch)

This path received tier-0 governance hygiene on 2026-06-21:

- Meta-bundle: `README.md`, `AGENTS.md`, `SPEC.md`, `llms.txt`,
  `CHANGELOG.md`, `WORKLOG.md` (v2.1 schema with `device:` field), `LICENSE`.
- Repo config: `justfile`, `.editorconfig`, `.gitattributes`, `.pre-commit-config.yaml`.
- CI: `.github/workflows/` (lint + test + build + audit).
- Device values: `macbook` / `heavy-runner` / `subagent` / `ci`.

## Key Commands

```bash
# Rust core
cargo build --release
cargo test

# Python bindings
uv sync
uv run pytest

# Go services
cd backend/ && go build ./...

# Frontend
cd web/ && pnpm install && pnpm build

# Quality gate (via just)
just ci
```

## Architecture

```
Tracera/
├── crates/        # Rust workspace (tracera-core, tracera-gpu, tracera-pipeline)
├── python/        # Python bindings (PyO3 / Maturin)
├── backend/       # Go microservices (API, ingestion)
├── web/           # TypeScript frontend (WebGPU visualization)
├── alembic/       # Database migrations
├── proto/         # Protobuf / gRPC contracts
├── tests/         # Integration tests (Python)
└── docs/          # Documentation
```

## Code Standards

- **Rust:** `cargo fmt` + `cargo clippy` + `cargo test`
- **Python:** `ruff` (lint + format) + `mypy` (type check)
- **Go:** `gofmt` + `go vet` + `golangci-lint`
- **TypeScript:** `eslint` + `prettier` + `tsc --noEmit`

## Testing Strategy

- Unit tests: `cargo test`, `pytest`, `go test`
- Integration: `tests/` directory
- GPU tests: Require `wgpu` + Vulkan/Metal/DX12
- CI: Runs on Ubuntu, macOS, Windows

## Documentation

- `README.md` — Project overview
- `SPEC.md` — Project specification (tier-0)
- `llms.txt` — Agent-readable project summary
- `docs/` — Full documentation
- `AGENTS.md` — This file (agent context)

## Phenotype Integration

Tracera is part of the Phenotype ecosystem:
- Uses `phenotype-skills` for plugin runtime
- Integrates with `phenotype-observability` for telemetry
- Can deploy to `nanovms` for edge compute
- Worklog uses `pheno-worklog-schema` v2.1 (with `device:` field per ADR-025 / ADR-030)

## Team

- See `CODEOWNERS` for domain ownership
- `docs/team.md` for full team roster

## Notes

- **Active** — actively maintained
- Requires GPU for full test suite
- Uses workspace Cargo for multi-crate Rust
- Convention: `chore/<req-id>-<slug>-<date>` / `feat/<req-id>-<slug>-<date>`
- Worklog: v2.1 schema, 11 columns (`Date | Task ID | Layer | Action | Files | Notes | Device | Actor | Hash | Branch | PR-URL`)

## Cross-references

- ADR-023 — Agent-effort governance (lib substrate placement).
- ADR-025 / ADR-030 — `pheno-worklog-schema` v2.1 (WORKLOG.md `device:` field).
- ADR-039 — pheno-flake refresh template.
- ADR-040 — Test coverage gates per tier.
