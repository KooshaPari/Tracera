# Contributing to Tracera

Thanks for your interest in contributing to Tracera! This guide covers the
practical steps for getting a change from your workstation through CI.

---

## Code of Conduct

Be respectful, constructive, and assume good intent. We are here to build
something useful together.

---

## Development Setup

### Prerequisites

| Tool | Version | Notes |
|---|---|---|
| **Rust** | stable (MSRV 1.82) | Install via [rustup](https://rustup.rs) |
| **Bun** | latest | For the frontend (`frontend/`) |
| **Python** | 3.11+ with `uv` | For Python tooling and tests |
| **Go** | 1.22+ | For Go modules |
| **Trunk.io** | 1.22+ | Unified linting — see `trunk.yaml` |

The project pins the stable Rust toolchain with `rust-toolchain.toml` (includes
the `wasm32-unknown-unknown` target for edge builds).

### Clone and Build

```bash
git clone https://github.com/kooshapari/Tracera.git
cd Tracera

# Rust workspace
cargo build --workspace

# Frontend
cd frontend && bun install && bun run dev

# API server
cargo run -p tracera-server
```

---

## Project Layout

```
Tracera/
├── src/                  # Rust core (hexagonal: domain + adapters)
├── crates/               # Cargo workspace members
│   ├── tracera-server/   # HTTP API server (axum + sqlx)
│   ├── tracera-cli/      # CLI (manages Compose stack across runtimes)
│   ├── tracera-edge/     # Cloudflare Worker edge API
│   └── tracertm-mcp/     # MCP stdio server
├── frontend/             # Web app (Bun + TypeScript)
├── docs/                 # Canonical guides, contracts, runbooks
├── deploy/               # Docker Compose / self-host configs
├── audit/                # Scorecard and audit output
└── assets/brand/         # Brand iconography
```

---

## Branching & Commits

1. **Fork** the repository (or create a feature branch if you have push access).
2. Branch from `main` with a descriptive name:
   ```
   feat/add-trace-link-batch-api
   fix/server-panic-on-empty-run
   docs/update-getting-started
   ```
3. Write **clear, concise commit messages**. Prefer conventional prefixes:
   `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `ci:`.

---

## Making Changes

### Rust

Run the full lint + test suite locally before pushing:

```bash
# Format
cargo fmt --all

# Lint (must pass with zero warnings)
cargo clippy --all-targets --all-features -- -D warnings

# Tests
cargo test --all --workspace --verbose
cargo test --all --workspace --doc
```

### Python

```bash
uv run ruff check .
uv run ruff format --check .
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest --cov -v
```

### Go

```bash
golangci-lint run
go test -v -race ./...
```

### TypeScript / Frontend

```bash
cd frontend
bun install
bun run lint    # or: npx biome lint .
bun run format  # or: npx biome format --check .
bun test
```

### Trunk.io (Unified)

Trunk provides a single command for all linters defined in `trunk.yaml`:

```bash
trunk check
trunk fmt
```

---

## Quality Gates

All of these must pass in CI before a PR can merge:

| Gate | Command |
|---|---|
| Rust formatting | `cargo fmt --all -- --check` |
| Rust lints | `cargo clippy --all-targets --all-features -- -D warnings` |
| Rust tests | `cargo test --all --workspace --verbose` |
| Python lint | `ruff check` + `ruff format --check` |
| Python tests | `pytest --cov` |
| Go lint | `golangci-lint run` |
| Go tests | `go test -v -race ./...` |
| TypeScript lint | `biome lint` + `biome format --check` |
| Trunk.io | `trunk check` |
| Dependency audit | `cargo deny check` |

---

## Dependency Policy

We use `cargo-deny` to enforce a license allowlist and block unknown registries.
See `deny.toml` for the full policy.

**Allowed licenses:** Apache-2.0, BSD-3-Clause, BSL-1.0, CC0-1.0,
ISC, LGPL-2.1, MIT, MIT-0, Unicode-3.0, Unlicense, Zlib.

If your change introduces a new dependency, run:

```bash
cargo deny check
```

and confirm no advisories or license violations are introduced.

---

## Pull Requests

1. **Keep PRs focused.** One logical change per PR makes review faster and
   bisection easier.
2. **Write a clear PR description.** Explain *what* changed, *why*, and
   *how to test it*.
3. **Link related issues** if applicable.
4. **Ensure CI is green.** PRs with failing checks will not be merged.
5. **Respond to review feedback promptly.** Push follow-up commits to the same
   branch — do not force-push during review unless asked.

---

## Governance & Traceability

Tracera maintains traceability from functional requirements through endpoints
to tests. If your change touches API endpoints:

1. Update `docs/governance/policy/endpoint_traceability_map.md` with the new
   or modified endpoint.
2. Add corresponding test linkage evidence.
3. Mirror the change in
   `docs/governance/policy/coverage_matrix_self_application.md`.
4. If governance or security rationale changes, update
   `docs/governance/policy/adr_index.md`.

---

## Reporting Issues

Open an issue on GitHub with:

- A clear title and description.
- Steps to reproduce (for bugs).
- Expected vs. actual behavior.
- Environment details (OS, Rust version, etc.).

---

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE).
