# Agents

## Key Commands

```bash
# Rust
cargo build --release
cargo test
cargo clippy --all

# Frontend
cd frontend && npm install
npm run dev --workspace=apps/web

# Tests
pytest tests/ -q

# Quality gate
cargo fmt --all && cargo clippy --all && cargo test
```

## Stack

- **Core**: Rust (`src/` — library crate)
- **Frontend**: React monorepo (`frontend/`) — Turborepo, TypeScript
- **Tests**: Python (`tests/`) — pytest
