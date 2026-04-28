# ADR-0001: Monorepo Consolidation and Canonicalization

Status: Draft
Date: 2025-10-12
Authors: Pheno-SDK maintainers

## Context
The monorepo has grown into many kits with overlapping scope and divergent naming and packaging styles. This inconsistency increases cognitive load, complicates dependency management, and slows adoption.

## Decision
Standardize project naming, package imports, and internal layout; adopt hexagonal architecture (ports & adapters) conventions; and execute long-term breaking migrations (no shims) with coordinated refactors across code, tests, and docs.

## Scope
- Kits: adapter-kit, api-gateway-kit, filewatch-kit, stream-kit, observability-kit, resource-management-kit, process-monitor-sdk, orchestrator-kit, tui-kit, top-level tui_kit, lib/service_orchestration, mcp-* family.
- Out of scope: Runtime feature changes and external API redesigns.

## Naming conventions
- Project folders: kebab-case with “-kit” suffix (SDKs keep “-sdk” only when intended as public SDKs).
- Python packages (imports): snake_case with “_kit” (or “_sdk” for SDKs).
- One internal package per project. No parallel legacy names inside the same project.

Examples
- api-gateway-kit → api_gateway_kit
- filewatch-kit → filewatch_kit
- observability-kit → observability_kit (with shim `observability` → `observability_kit`)

## Standard layout (per kit)
- pyproject.toml (single build backend)
- Makefile (setup, build, test, test-cov, lint, format, type-check, deps-tree, deps-audit, clean, clean-all)
- <pkg_name>/
  - domain/ (entities, value_objects, specifications)
  - ports/ (interfaces/protocols)
  - adapters/ (db, http, cli, cloud)
  - services/ (use-cases/orchestration)
  - entrypoints/ (CLI/API/workers)
- tests/, examples/, docs/
- .pre-commit-config.yaml, LICENSE, README.md

## Architecture guidance (hexagonal / DDD)
- Domain is dependency-free relative to adapters.
- Ports define boundaries as ABCs/protocols.
- Adapters implement ports and depend inward (dependency inversion).
- Application/services orchestrate domain use-cases.
- Entrypoints compose adapters via DI (constructor/function injection), not global state.

## Packaging
- Prefer pyproject-only across all kits; remove legacy setup.py/requirements.txt after migration.
- Use a single build backend across kits (recommend `hatchling` or `setuptools`).
- Keep common tooling config in the repo root; per-kit Makefiles implement a shared interface of targets.

## Migration policy (breaking, no shims)
- Perform coordinated codebase-wide refactors to move/rename packages and modules to their canonical names.
- Update all internal imports, tests, examples, and docs in the same PR.
- Publish a migration guide with old→new import mappings; provide codemod scripts to assist.
- Release as a major version bump for affected kits; no runtime shims or deprecation warnings.

## Concrete consolidations (phase 1)
- TUI: make `tui-kit` canonical; merge all remaining functionality from top-level `tui_kit` into `tui-kit/tui_kit`; update all imports; remove top-level `tui_kit`.
- API Gateway: collapse `api_gateway` into `api_gateway_kit`; update imports; remove `api_gateway`.
- Filewatch: collapse `filewatch` into `filewatch_kit`; update imports; remove `filewatch`.
- Stream: move top-level modules under `stream_kit`; update imports; remove duplicated top-level modules.
- Observability: rename internal `observability` → `observability_kit`; update imports; remove `observability`.
- Orchestrator: move `lib/service_orchestration` under `orchestrator_kit`; update imports; remove legacy path.

## Phased rollout
- Weeks 0–2: RFC approval, diff-and-merge plan per kit (no shims), begin TUI merge PR.
- Weeks 2–4: API Gateway, Filewatch, Stream consolidations (imports updated, legacy paths removed).
- Weeks 4–6: Packaging modernization and Makefile standardization.
- Weeks 6–8: Centralize shared utilities and refresh docs; cut major releases.

## Risks and mitigations
- Import collisions: resolve by consolidating to a single canonical package and updating all imports in one PR.
- Hidden consumers of legacy names: repo-wide search and codemods; publish migration notes in CHANGELOG.
- Tooling drift: unify Makefile targets and root tooling configs.

## Status tracking
- Each consolidation lands as its own PR; CI must pass `pheno check` and integration tests.

## Alternatives considered
- Big-bang rename with no phased plan: rejected as too risky; instead we sequence per kit with end-to-end updates.
- Runtime shims and deprecation warnings: rejected per policy; we prefer clean breaks with clear migration guides.
