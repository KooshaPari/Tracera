# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Tier-0 meta-bundle (v22-SD1 hygiene batch, 2026-06-21):**
  - `SPEC.md` — new top-level project specification (was missing from tier-0).
  - `AGENTS.md` — v2.1 worklog schema reference (ADR-025 / ADR-030),
    including the `device:` field metadata.
- `llms.txt` — refreshed to reflect current project state (Tracera, not
  TracerTM; Rust + Go + Python + TypeScript; bun@1.1.38; Go 1.25; MSRV 1.82;
  OTLP wire via `pheno-otel`; justfile canonical task runner).

### Changed

- `AGENTS.md` — expanded with metadata header (Date / Status / Substrate
  type / Worklog schema), tier-0 meta-bundle section, updated command set
  (`uv` for Python, `bun` for frontend, `just ci` for the quality gate),
  and cross-references to ADR-023, ADR-025/030, ADR-039, ADR-040.
- `llms.txt` — replaced stale `TracerTM` / `task` content with current
  Tracera stack, persistence (PostgreSQL, Neo4j, Redis, NATS),
  observability (Grafana Alloy / Tempo / Loki / Prometheus), and v2.1
  worklog conventions.

### Deprecated

### Removed

### Fixed

### Security

## [0.2.0] - 2026-06-14

### Added

- Initial release with version tracking.

[Unreleased]: https://github.com/KooshaPari/Tracera/compare/0.2.0...HEAD
[0.2.0]: https://github.com/KooshaPari/Tracera/releases/tag/0.2.0
