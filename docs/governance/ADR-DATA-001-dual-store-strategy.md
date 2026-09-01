# ADR-DATA-001: Dual-Store Strategy (PostgreSQL for Production, SQLite for Development/Testing)

| Field         | Value                    |
| ------------- | ------------------------ |
| **Status**    | Accepted                 |
| **Date**      | 2026-08-30               |
| **Authors**   | Tracera Data Engineering |
| **Reviewers** | Platform Team, SRE       |

## Context

Tracera's data layer must serve two very different operational profiles simultaneously.

**Production** needs a hardened, concurrent, network-accessible RDBMS that can survive node
failures, support point-in-time recovery, and scale horizontally behind a connection pool.
PostgreSQL 16+ satisfies all of these requirements and is already the team's primary
operational database.

**Development and CI** need the opposite: instant startup, zero external dependencies, and
fast teardown. Provisioning a PostgreSQL instance for every local developer, every feature
branch in CI, or every integration-test run adds minutes of setup time, increases flake
rates from network/timeout issues, and creates friction that discourages frequent testing.

SQLite is the most widely deployed embedded database on the planet. It requires no server
process, stores its entire state in a single file, and executes most Tracera query patterns
in single-digit milliseconds on a developer laptop. Its limitations (limited concurrent
writers, no network access, no row-level locking) are acceptable in non-production contexts
where a single process exclusively owns the database file.

Previous attempts to share a single PostgreSQL instance across all CI jobs caused connection
exhaustion, flaky test suites, and expensive pre-test setup scripts. A dedicated PostgreSQL
container per CI job solved correctness but tripled CI wall-clock time.

## Decision

We adopt a **dual-store strategy**: PostgreSQL is the production and staging database;
SQLite is the exclusive database for local development, unit tests, and single-tenant CI
pipelines.

### Feature Parity Requirements

1. **Schema parity.** A single canonical schema definition (managed by SQLx migrations) is
   applied to both engines. Engine-specific DDL (e.g., PostgreSQL's `GENERATED ALWAYS AS`
   vs. SQLite triggers) is abstracted behind the migration layer so that each target
   receives equivalent semantics.

2. **Query parity.** All repository modules must pass their test suites against both
   backends. A shared integration-test harness runs the same test matrix against SQLite
   and a throwaway PostgreSQL container (via `testcontainers-rs`) on every merge to
   `main`.

3. **ORM / query-builder parity.** The application uses SQLx directly with compile-time
   checked queries. Any query that uses PostgreSQL-specific syntax (e.g., `ILIKE`,
   `jsonb` operators) must have a tested SQLite-compatible alternative path, gated at
   runtime by a `DatabaseBackend` enum.

4. **Migration testing.** Every migration file must include forward **and** downgrade
   paths for both engines. The CI pipeline runs `migrate up && migrate down && migrate up`
   on both SQLite and PostgreSQL to verify idempotency.

### Runtime Selection

```rust
pub enum DatabaseBackend {
    Postgres,
    Sqlite,
}

impl DatabaseBackend {
    /// Returns the backend from the `DATABASE_BACKEND` env var,
    /// defaulting to Postgres in production builds and SQLite in
    /// test/debug builds.
    pub fn from_env() -> Self { /* ... */ }
}
```

The selected backend is resolved once at application startup and propagated through the
dependency-injection container. Connection-pool settings, statement timeouts, and
transaction isolation levels are tuned independently per backend.

### Data Migration / Seed Parity

- Seed scripts are idempotent SQL that execute identically on both engines.
- A `tracera-cli seed` command re-seeds the database regardless of backend, ensuring
  developers and CI always start from a known-good state.

## Alternatives Considered

| Alternative                       | Rejection Reason                                                         |
| --------------------------------- | ------------------------------------------------------------------------ |
| PostgreSQL everywhere             | CI wall-clock time too high; local setup too heavy for new contributors. |
| SQLite everywhere                 | Cannot meet production concurrency, replication, or backup requirements. |
| Docker Compose with Postgres only | Flake rates from container orchestration in CI; slow cold starts.        |
| In-memory database (e.g., r2d2)   | No persistence across test runs; diverges from production storage.       |

## Consequences

### Positive

- **Faster local iteration.** Developers go from `git clone` to a running server in
  under two seconds with no Docker daemon required.
- **Cheaper CI.** SQLite-backed CI jobs use ~40 % fewer compute seconds and eliminate
  network-related flakes, reducing CI costs and improving merge velocity.
- **Correctness safety net.** The shared migration and query-parity tests catch
  engine-specific regressions before they reach staging.
- **Lower barrier to entry.** New contributors can run the full test suite on Windows,
  macOS, or Linux without installing PostgreSQL.

### Negative

- **Increased migration complexity.** Every migration must be authored with both engines
  in mind. PostgreSQL-specific features (full-text search, materialized views, logical
  replication) require explicit fallback paths or feature-gating.
- **Dual test matrix.** CI runs the integration suite twice, adding ~30 seconds per
  pipeline (a worthwhile trade-off against the minutes saved by avoiding PostgreSQL
  containers).
- **Potential behavioral drift.** Edge cases around transaction isolation, `NULL`
  ordering, and type casting differ between engines. The parity test harness mitigates
  but cannot eliminate this risk entirely.
- **Maintenance burden.** The `DatabaseBackend` abstraction and engine-specific shims
  require ongoing maintenance as new queries are added.

### Risks and Mitigations

| Risk                                   | Mitigation                                                  |
| -------------------------------------- | ----------------------------------------------------------- |
| SQLite silently allows invalid syntax  | SQLx compile-time checks enforce both backends in CI.       |
| Postgres-only features creep into prod | Feature-gate macro flags non-portable queries at review.    |
| Developer SQLite file conflicts        | `.gitignore` excludes `*.db`; `cargo test` uses temp files. |

## References

- [SQLite Documentation — When to Use SQLite](https://www.sqlite.org/whentouse.html)
- [PostgreSQL 16 Release Notes](https://www.postgresql.org/docs/16/release-16.html)
- [SQLx — Compile-Time Checked Queries](https://docs.rs/sqlx/latest/sqlx/)
- [Testcontainers for Rust](https://docs.rs/testcontainers/)
