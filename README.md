# Tracera

<p align="center">
  <a href="assets/brand/icon.svg"><img src="assets/brand/icon.svg" alt="Tracera" width="160" height="160"></a>
</p>
<p align="center"><em>Hexagonal trace-link matrix for Agentic + LLM observability — Rust core, web UI, Electrobun desktop.</em></p>
<p align="center"><sub>Tracera (navy + teal + indigo) palette · <a href="assets/brand/favicon.svg">favicon</a> · <a href="docs/assets/identity/">visual identity demo</a></sub></p>

[![AI slop inside](https://sladge.net/badge.svg)](https://sladge.net) [![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/KooshaPari/Tracera/total)](https://github.com/KooshaPari/Tracera/releases)

---

Tracera is the Phenotype-org **trace + observability + audit ledger** for
agentic and LLM workflows. It captures structured trace-links across runs,
distills short-term + long-term memory, and serves an Electrobun desktop
viewer over OKF-bundled session history. The supported runtime is the Rust
workspace; older Python/FastAPI references are retained only as historical
migration material.

## Where to start

- Docs: see [`docs/01-getting-started/README.md`](docs/01-getting-started/README.md)
- API reference: [`docs/06-api-reference/README.md`](docs/06-api-reference/README.md)
- Governance: [`docs/governance/README.md`](docs/governance/README.md)
- Self-hosted deploy: [`deploy/selfhost/README.md`](deploy/selfhost/README.md)

## Repository layout

- `src/` — Rust core (hexagonal: domain + adapters)
- `crates/` — Cargo workspace members
- `frontend/` — web app
- `docs/` — canonical guides, contracts, and operational runbooks
- `assets/brand/` — Tracera brand iconography (source of truth: `icon.svg`)
- `audit/` — scorecard + L-pillar audit output

## Build

```bash
# Rust workspace
cargo build --workspace

# Frontend
cd frontend && bun install && bun run dev

# Rust API server
cargo run -p tracera-server
```

See the getting-started guide for the full setup, including the
desktop-app packaging recipe.
