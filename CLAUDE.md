# CLAUDE.md

## Project Overview

Tracera is the Phenotype-org trace, observability, and audit ledger for agentic and LLM workflows. It captures structured trace-links across runs, distills short-term and long-term memory, and serves an Electrobun desktop viewer over session history.

## Architecture

Hexagonal architecture (domain + adapters) in Rust, with a web frontend and Electrobun desktop app.

## Tech Stack

- **Language:** Rust (core), TypeScript (frontend)
- **Framework:** Hexagonal architecture; `cargo` workspace
- **Frontend:** Bun-based web app
- **Desktop:** Electrobun

## Repository Layout

- `src/` — Rust core (hexagonal: domain + adapters)
- `crates/` — Cargo workspace members
- `frontend/` — web app
- `docs/` — canonical guides, contracts, operational runbooks
- `assets/brand/` — brand iconography
- `audit/` — scorecard + audit output

## Build

```bash
cargo build --workspace          # Rust workspace
cd frontend && bun install && bun run dev  # Frontend
cargo run -p tracera-server      # API server
```

## Key Entry Points

- Docs: `docs/01-getting-started/README.md`
- API reference: `docs/06-api-reference/README.md`
- Governance: `docs/governance/README.md`
- Self-hosted deploy: `deploy/selfhost/README.md`

## Development Notes

- The supported runtime is the Rust workspace; older Python/FastAPI references are historical migration material.
- Part of the Phenotype polyrepo portfolio (alongside AgilePlus, Configra, etc.).
