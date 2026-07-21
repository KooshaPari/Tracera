# Bounded SQLx Pool Initialization

## Goal

Make production database startup use explicit, bounded connection policy for both
Postgres and SQLite, while preserving the existing backend selection and migration
contracts.

## Design

Add small, typed connection builders beside the server startup path. The builders
configure SQLx pool limits and timeouts before connecting. SQLite initialization
also applies the existing WAL, synchronous, busy-timeout, and foreign-key policy
through one shared path; in-memory SQLite continues to skip WAL.

Production startup will call the builders instead of raw `PgPool::connect` and
`SqlitePool::connect`. Test-only in-memory fixtures may keep their local setup when
they intentionally exercise a specific store fixture.

## Defaults and invariants

- Maximum connections are finite and explicit for both backends.
- Acquisition and idle timeouts are finite to prevent indefinite request waits.
- SQLite keeps `busy_timeout = 5000`, `foreign_keys = ON`, and WAL for file-backed
  databases.
- Existing `DATABASE_URL` scheme selection and migration ordering remain unchanged.
- Connection failures continue to produce the current fatal startup diagnostics.

## Testing

Add focused tests for SQLite pragmas and pool limits. Exercise the production
initialization helpers with an in-memory SQLite URL and assert that readiness still
uses the initialized pool. Run formatting, clippy with warnings denied, and the
targeted server tests.

## Non-goals

This slice does not change schemas, API responses, deployment topology, or the
existing queue-specific lifecycle helpers.
