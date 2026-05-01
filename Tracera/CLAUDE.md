# CLAUDE.md — Tracera

Extends parent governance. See:
- Global baseline: `~/.claude/CLAUDE.md`
- Phenotype root: `/Users/kooshapari/CodeProjects/Phenotype/repos/CLAUDE.md`

## Stack

- **Core**: Rust (`src/` — library crate)
- **Frontend**: React monorepo (`frontend/`) — Turborepo, TypeScript
- **Tests**: Python (`tests/`) — pytest

## Project Structure

```
src/               # Rust source (lib.rs + modules)
frontend/
  apps/
    web/           # Main web app
    docs/          # Documentation
    storybook/     # Component explorer
    desktop/       # Desktop app
  packages/
    ui/            # Shared UI components
    api-client/    # API client library
    types/         # Shared TypeScript types
    state/         # State management
    config/        # Shared config
    env-manager/   # Environment management
frontend/package.json  # Root workspace manifest
tests/             # Python integration/e2e tests
```

## Development

```bash
# Rust
cargo build --release
cargo test

# Frontend
cd frontend && npm install
npm run dev --workspace=apps/web

# Tests
pytest tests/ -q
```

## AgilePlus Mandate

All work MUST be tracked in AgilePlus.
Reference: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
