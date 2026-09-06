# MCP Database URL Contract Design

## Goal

Make `TRACERA_DB_URL` accept only documented PostgreSQL and SQLite URL schemes,
while preserving the repaired connection, migration, and store construction
path.

## Decision

`tracera-mcp` will accept `postgres://`, `postgresql://`, `sqlite:`, and
`sqlite://` URL forms. It will reject bare filenames such as `tracera.db` with
the existing explicit configuration error. The binary will not guess a scheme
or rewrite the supplied value.

## Data Flow

```text
TRACERA_DB_URL
  -> scheme dispatch
     -> PostgreSQL factory -> migrate -> PgStore
     -> SQLite factory     -> migrate -> SqliteStore
     -> unsupported input  -> explicit configuration error
```

## Testing

HEAD already rejects a bare `.db` path through its unsupported-input fallback,
so this documentation-only reconciliation must not claim a new red-green
behavior change. Preserve the existing tests for both SQLite in-memory URL
forms and PostgreSQL connector dispatch. Then run the focused
binary/library/package checks and a configured SQLite JSON-RPC smoke exchange.

## Non-Goals

This change does not add a URL parser, file-path compatibility mode, live
PostgreSQL test infrastructure, workspace-wide formatting, or hosted CI work.
