# AgilePlus

**AgilePlus is a local-first, spec-driven agile work-tracking CLI for AI-agent and human teams.** It models features, work packages, and acceptance criteria as versioned specs on disk, with optional sync to GitHub Issues, dashboards, and P2P merge for multi-actor collaboration.

Implemented as a hexagonal Rust workspace plus a Python MCP server, with adapters for SQLite, gRPC, NATS, GitHub, and Plane.so.

**Status:** Active development (pre-1.0). Workspace version `0.1.1`. Several crates listed in `Cargo.toml` are scaffolded but not yet wired end-to-end.

## Quick Start

Install (from this repo):

```bash
cargo install --path crates/agileplus-cli
```

Three-step flow:

```bash
# 1. Create a feature spec (slug-based, kebab-case)
agileplus specify --feature my-feature-slug

# 2. Generate work packages and tasks for the feature
agileplus tasks --feature my-feature-slug

# 3. Update work-package state as you progress
agileplus status my-feature-slug --wp wp-001 --state doing
```

See **[`docs/guide/quick-start.md`](docs/guide/quick-start.md)** for the full quickstart, including project init, dashboard, and GitHub sync.

## What it does

The `agileplus` CLI walks a feature through a structured lifecycle backed by a local SQLite database (`.agileplus/agileplus.db`) and an evidence ledger:

```
triage → specify → research → plan → implement → validate → ship → retrospective
```

Each `specify` produces a `kitty-specs/<slug>/` directory holding `spec.md`, `plan.md`, and `tasks.md`. Work packages from `plan` are scoped to explicit file paths and tracked as immutable events.

## Stack

- **Core:** Rust 2024 edition, MSRV 1.85, workspace resolver 3
- **HTTP / RPC:** Axum 0.8, Tonic 0.13 (gRPC), Prost 0.13
- **Storage:** SQLite (`crates/agileplus-sqlite`)
- **Messaging:** async-nats (`crates/agileplus-nats`)
- **Observability:** OpenTelemetry 0.31 + tracing-opentelemetry 0.32
- **MCP server:** Python (`agileplus/`, `agileplus-mcp/`)
- **Plugin host:** `libs/plugin-registry`, `libs/plugin-cli`, `libs/plugin-git`, `libs/plugin-grpc`, `libs/plugin-integration`

## Repository Layout

```
AgilePlus/
├── crates/                   # Rust workspace (CLI, dashboard, sqlite, p2p, grpc, ...)
├── libs/                     # Shared libs (nexus, hexagonal-rs, hexkit, intent-registry, ...)
├── agileplus/                # Python MCP server
├── agileplus-agents/         # Agent tooling
├── agileplus-mcp/            # MCP protocol implementation
├── apps/                     # Application entry points
├── kitty-specs/              # Live AgilePlus feature specs (eat-our-own-dogfood)
├── docs/
│   ├── guide/                # Canonical user guide (start here)
│   ├── guides/               # Contributor/developer references
│   ├── adr/                  # Architecture Decision Records
│   └── reference/            # API and CLI reference
├── proto/                    # gRPC proto definitions
├── scripts/                  # Helper scripts (dev-up, install-hooks, ...)
└── .work-audit/              # Worklog and audit trail
```

> **Note on `docs/guide/` vs `docs/guides/`:** `docs/guide/` (singular) is the **canonical** product user guide. `docs/guides/` (plural) holds supplementary contributor/developer references (e.g. `DEV_STACK.md`, `FR_ANNOTATION_GUIDE.md`). When linking from external docs, prefer `docs/guide/`.

## Install (from source)

Rust toolchain required (MSRV 1.85):

```bash
git clone https://github.com/KooshaPari/AgilePlus.git
cd AgilePlus
cargo build --release
# binary at target/release/agileplus
```

## Usage

```bash
# List features in the local database
agileplus list

# Create or revise a spec
agileplus specify --feature my-feature --from-file path/to/draft.md

# Generate a plan with work packages
agileplus plan --feature my-feature

# Validate governance compliance
agileplus validate --feature my-feature

# Manage the triage queue / cycles / modules
agileplus queue list
agileplus cycle list
agileplus module list

# Run the local platform services
agileplus platform up
agileplus dashboard
```

Full surface: `agileplus --help`.

## Development

```bash
cargo build           # build the workspace
cargo test            # run tests
cargo clippy --all    # lints
cargo fmt --all       # format
buf generate          # regenerate gRPC stubs (requires buf)

# Python MCP server
cd agileplus && python -m agileplus
```

## Documentation

| Topic | Path |
|-------|------|
| Quick start | [`docs/guide/quick-start.md`](docs/guide/quick-start.md) |
| Getting started (concepts) | [`docs/guide/getting-started.md`](docs/guide/getting-started.md) |
| `agileplus init` | [`docs/guide/init.md`](docs/guide/init.md) |
| Workflow | [`docs/guide/workflow.md`](docs/guide/workflow.md) |
| Configuration | [`docs/guide/configuration.md`](docs/guide/configuration.md) |
| Sync (GitHub) | [`docs/guide/sync.md`](docs/guide/sync.md) |
| Triage | [`docs/guide/triage.md`](docs/guide/triage.md) |
| Local-first deployment | [`docs/guide/local-first-deployment.md`](docs/guide/local-first-deployment.md) |
| Agent governance | [`docs/agents/governance-constraints.md`](docs/agents/governance-constraints.md) |
| Work-package prompt format | [`docs/agents/prompt-format.md`](docs/agents/prompt-format.md) |
| Architecture decisions | [`docs/adr/`](docs/adr/) |
| Feature specifications | [`kitty-specs/`](kitty-specs/) and [`docs/specs/`](docs/specs/) |
| Functional requirements | [`FUNCTIONAL_REQUIREMENTS.md`](FUNCTIONAL_REQUIREMENTS.md) |
| Implementation plan | [`PLAN.md`](PLAN.md) |

## Governance

- [`GOVERNANCE.md`](GOVERNANCE.md) — project governance
- [`AGENTS.md`](AGENTS.md) — agent interaction rules
- [`CLAUDE.md`](CLAUDE.md) — Claude Code settings

## Contributing

1. Read [`docs/guide/quick-start.md`](docs/guide/quick-start.md).
2. Create a feature spec: `agileplus specify --feature <your-slug>`.
3. Open a PR referencing the spec.

## Known limitations

- A subset of crates declared in `Cargo.toml` are stubs; active work happens in `libs/` and the listed `crates/agileplus-*` directories.
- Plane.so, GitHub, and NATS adapters require external services to exercise end-to-end; smoke scripts live under `scripts/`.
- Dashboard route layering vs. `agileplus-api` was last reconciled in PR #404.

## License

MIT. See [`LICENSE`](LICENSE).
