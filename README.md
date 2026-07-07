# Tracera

<p align="center">
  <a href="assets/brand/icon.svg"><img src="assets/brand/icon.svg" alt="Tracera" width="160" height="160"></a>
</p>
<p align="center"><em>Hexagonal trace-link matrix for Agentic + LLM observability — Rust core, Python SDK, Electron desktop.</em></p>
<p align="center"><sub>Tracera (navy + teal + indigo) palette · <a href="assets/brand/favicon.svg">favicon</a> · <a href="docs/assets/identity/">visual identity demo</a></sub></p>

---

Tracera is the Phenotype-org **trace + observability + audit ledger** for
agentic and LLM workflows. It captures structured trace-links across runs,
distills short-term + long-term memory, and serves an Electron desktop
viewer over OKF-bundled session history.

## Where to start

- Docs: see [`docs/01-getting-started/README.md`](docs/01-getting-started/README.md)
- API reference: [`docs/06-api-reference/README.md`](docs/06-api-reference/README.md)
- Governance: [`docs/governance/README.md`](docs/governance/README.md)
- Self-hosted deploy: [`deploy/selfhost/README.md`](deploy/selfhost/README.md)

## Repository layout

- `src/` — Rust core (hexagonal: domain + adapters)
- `crates/` — Cargo workspace members
- `frontend/` — web app
- `backend/` — Python SDK / service layer
- `assets/brand/` — Tracera brand iconography (source of truth: `icon.svg`)
- `audit/` — scorecard + L-pillar audit output

## Build

```bash
# Rust workspace
cargo build --workspace

# Frontend
cd frontend && bun install && bun run dev

# Backend / API
cd backend && uv sync && uv run pytest
```

See the getting-started guide for the full setup, including the
desktop-app packaging recipe.
