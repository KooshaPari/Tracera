# Tracera — AGENTS.md

## Project Overview

Tracera is an agent-native requirements traceability and project-management system built around the Rust `tracera-core` crate, the `traceability-core` domain model from `phenotype-pm-core`, and polyglot integration surfaces in Python, Go, and TypeScript.

**Repository:** `Tracera/`
**Language:** Rust (primary), Python, Go, TypeScript
**Build System:** Cargo (Rust), Poetry (Python), Go Modules, pnpm (TS)
**License:** MIT
**CI/CD:** GitHub Actions (`.github/workflows/`)

## Key Commands

```bash
# Rust core
cargo build --release
cargo test

# Python bindings
poetry install
poetry run pytest

# Go services
cd services/ && go build ./...

# Frontend
cd web/ && pnpm install && pnpm build
```

## Architecture

```
Tracera/
├── src/           # Rust core (GPU compute, data pipeline)
├── python/        # Python bindings (PyO3/Maturin)
├── services/      # Go microservices (API, ingestion)
├── web/           # TypeScript frontend (WebGPU visualization)
├── tests/         # Integration tests
└── docs/          # Documentation
```

## Code Standards

- **Rust:** `cargo fmt` + `cargo clippy` + `cargo test`
- **Python:** `ruff` (lint + format) + `mypy` (type check)
- **Go:** `go fmt` + `go vet` + `golangci-lint`
- **TypeScript:** `eslint` + `prettier` + `tsc --noEmit`

## Testing Strategy

- Unit tests: `cargo test`, `pytest`, `go test`
- Integration: `tests/` directory
- GPU tests: Require `wgpu` + Vulkan/Metal/DX12
- CI: Runs on Ubuntu, macOS, Windows

## Documentation

- `README.md` — Project overview
- `docs/` — Full documentation
- `AGENTS.md` — This file (agent context)

## Phenotype Integration

Tracera is part of the Phenotype ecosystem:
- Uses `phenotype-skills` for plugin runtime
- Integrates with `phenotype-observability` for telemetry
- Can deploy to `nanovms` for edge compute

## Team

- See `CODEOWNERS` for domain ownership
- `docs/team.md` for full team roster

## Notes

- **Active** — actively maintained
- Requires GPU for full test suite
- Uses workspace Cargo for multi-crate Rust
