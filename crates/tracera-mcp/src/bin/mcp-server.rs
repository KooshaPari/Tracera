//! `tracera-mcp` — stdio MCP server binary.
//!
//! This is a thin entry point that:
//! 1. Initializes `tracing` based on the `RUST_LOG` env var (default
//!    `info`).
//! 2. Constructs the [`tracera_server::store::Store`] implementation
//!    based on the `TRACERA_DB_URL` env var.
//! 3. Builds a [`tracera_mcp::McpServer`] and serves it over stdio using
//!    rmcp's `transport-io` feature.
//!
//! ## Environment variables
//!
//! | Variable          | Default        | Purpose                                       |
//! |-------------------|----------------|-----------------------------------------------|
//! | `TRACERA_DB_URL`  | (none)         | Database connection URL. `postgres://…` for PgStore, `sqlite://…` for SqliteStore. Required unless `--demo` is passed. |
//! | `RUST_LOG`        | `info`         | `tracing` log level filter.                   |
//! | `TRACERA_DEMO`    | (unset)        | If set to `1`, use an in-memory stub store (for local dev). |
//!
//! ## Usage
//!
//! ```bash
//! TRACERA_DB_URL=sqlite://./tracera.db \
//!   cargo run -p tracera-mcp --bin tracera-mcp
//! ```
//!
//! Then point your MCP client (Claude Desktop, Cursor, etc.) at the
//! `tracera-mcp` binary — see `.mcp.json` / `.vscode/mcp.json` at the
//! crate root for example configs.

use std::sync::Arc;

use rmcp::ServiceExt;
use tracing_subscriber::EnvFilter;

use tracera_mcp::McpServer;
use tracera_server::store::Store;

#[tokio::main(flavor = "multi_thread", worker_threads = 2)]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // -- 1) Logging ---------------------------------------------------------
    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info,tracera_mcp=info,rmcp=info"));
    tracing_subscriber::fmt()
        .with_env_filter(filter)
        .with_target(false)
        .with_writer(std::io::stderr) // MCP stdio protocol uses stdout
        .init();

    // -- 2) Banner ----------------------------------------------------------
    eprintln!(
        "tracera-mcp {} starting (pid={}, stdio transport)",
        env!("CARGO_PKG_VERSION"),
        std::process::id()
    );

    // -- 3) Build the store -----------------------------------------------
    let store: Arc<dyn Store> = match build_store().await {
        Ok(s) => s,
        Err(e) => {
            eprintln!("fatal: failed to construct store: {e}");
            std::process::exit(2);
        }
    };

    // -- 4) Run ------------------------------------------------------------
    let server = McpServer::new(store);
    // rmcp 3.2 removed `serve_stdio()`. Use `ServiceExt::serve(...)` with
    // an explicit `(AsyncRead, AsyncWrite)` transport tuple from
    // `tokio::io::{stdin, stdout}`. The `IntoTransport` impl lives in
    // `rmcp::transport::async_rw` and is auto-selected by type inference.
    let transport = (tokio::io::stdin(), tokio::io::stdout());
    if let Err(e) = server.serve(transport).await {
        eprintln!("fatal: stdio server exited with error: {e}");
        std::process::exit(1);
    }
    Ok(())
}

/// Build the [`tracera_mcp::Store`] implementation from environment.
///
/// Resolution order:
/// 1. `TRACERA_DEMO=1`  → in-memory stub (for local dev / smoke tests).
/// 2. `TRACERA_DB_URL`  → `postgres://…` or `sqlite://…`.
/// 3. Otherwise          → error.
async fn build_store() -> Result<Arc<dyn Store>, String> {
    if std::env::var("TRACERA_DEMO").as_deref() == Ok("1") {
        eprintln!("tracera-mcp: using in-memory demo store (TRACERA_DEMO=1)");
        return Ok(Arc::new(DemoStore));
    }
    let url = std::env::var("TRACERA_DB_URL")
        .map_err(|_| "TRACERA_DB_URL is not set (and TRACERA_DEMO != 1)".to_string())?;
    build_store_from_url(&url).await
}

/// Construct a store from a URL.
///
/// We dispatch on the scheme prefix:
///   - `postgres://` or `postgresql://` → `PgStore`
///   - `sqlite://`                      → `SqliteStore`
///   - anything else                    → error
async fn build_store_from_url(url: &str) -> Result<Arc<dyn Store>, String> {
    // We re-export the concrete types through `tracera_mcp::stores::*`
    // when wired in a follow-up. For now the dispatcher is feature-gated
    // and returns a friendly error so the binary still compiles.
    #[cfg(feature = "postgres")]
    {
        if url.starts_with("postgres://") || url.starts_with("postgresql://") {
            return tracera_mcp::stores::pg::PgStore::connect(url)
                .await
                .map(|s| Arc::new(s) as Arc<dyn Store>)
                .map_err(|e| format!("PgStore::connect: {e}"));
        }
    }
    #[cfg(feature = "sqlite")]
    {
        if let Some(path) = url.strip_prefix("sqlite://") {
            return tracera_mcp::stores::sqlite::SqliteStore::connect(path)
                .await
                .map(|s| Arc::new(s) as Arc<dyn Store>)
                .map_err(|e| format!("SqliteStore::connect: {e}"));
        }
    }
    Err(format!(
        "unrecognized TRACERA_DB_URL scheme `{url}`; \
         expected `postgres://…` or `sqlite://…` (or set TRACERA_DEMO=1)"
    ))
}

// ---------------------------------------------------------------------------
// In-memory demo store — used when TRACERA_DEMO=1.
// ---------------------------------------------------------------------------
//
// This is a minimal stub of [`tracera_server::store::Store`] that returns
// empty collections for every read and errors for every write. It exists
// so a developer can launch the binary without configuring a database:
//
//   $ TRACERA_DEMO=1 cargo run -p tracera-mcp --bin tracera-mcp
//
// The `tools/list` and `tools/call` round-trip will succeed; calls into
// the store will return empty results.
//
// We deliberately do not implement the full trait here — the canonical
// `PgStore` / `SqliteStore` implementations live in `tracera-server`. This
// stub is only a placeholder for the demo binary path.

mod demo {
    use std::future::Future;
    use std::pin::Pin;

    use chrono::{DateTime, Utc};
    use serde_json::Value;
    use tracera_server::store::{
        BoxFuture, EvidenceItem, ListParams, Problem, Store, StoreError, StoreResult,
    };

    /// Compile-time check: `DemoStore` only exists for the demo path.
    /// When the `postgres` / `sqlite` features are off, this is the only
    /// `Store` impl available to the binary.
    pub struct DemoStore;

    impl Store for DemoStore {
        fn list_evidence(&self) -> BoxFuture<'_, StoreResult<Vec<EvidenceItem>>> {
            Box::pin(async { Ok(vec![]) })
        }
        fn create_evidence(
            &self,
            _id: String,
            _artifact_id: String,
            _kind: String,
            _url: String,
            _metadata: Value,
            _now: DateTime<Utc>,
        ) -> BoxFuture<'_, StoreResult<EvidenceItem>> {
            Box::pin(async {
                Err(StoreError::Database(
                    "DemoStore is read-only; configure TRACERA_DB_URL for writes".into(),
                ))
            })
        }
        fn list_sprints(
            &self,
        ) -> BoxFuture<'_, StoreResult<Vec<tracera_server::store::Sprint>>> {
            Box::pin(async { Ok(vec![]) })
        }
        fn create_sprint(
            &self,
            _id: String,
            _name: String,
            _goal: String,
            _start: DateTime<Utc>,
            _end: DateTime<Utc>,
            _now: DateTime<Utc>,
        ) -> BoxFuture<'_, StoreResult<tracera_server::store::Sprint>> {
            Box::pin(async {
                Err(StoreError::Database(
                    "DemoStore is read-only; configure TRACERA_DB_URL for writes".into(),
                ))
            })
        }
        fn list_stories(
            &self,
        ) -> BoxFuture<'_, StoreResult<Vec<tracera_server::store::Story>>> {
            Box::pin(async { Ok(vec![]) })
        }
        fn create_story(
            &self,
            _id: String,
            _sprint: Option<String>,
            _t: String,
            _d: String,
            _s: String,
            _p: Option<i64>,
            _now: DateTime<Utc>,
        ) -> BoxFuture<'_, StoreResult<tracera_server::store::Story>> {
            Box::pin(async {
                Err(StoreError::Database(
                    "DemoStore is read-only; configure TRACERA_DB_URL for writes".into(),
                ))
            })
        }
        fn create_trace_link(
            &self,
            _id: String,
            _s: String,
            _t: String,
            _rel: String,
            _c: f64,
            _src: String,
            _now: DateTime<Utc>,
        ) -> BoxFuture<'_, StoreResult<tracera_server::store::TraceLink>> {
            Box::pin(async {
                Err(StoreError::Database(
                    "DemoStore is read-only; configure TRACERA_DB_URL for writes".into(),
                ))
            })
        }
        fn list_trace_links_for_artifact(
            &self,
            _id: String,
        ) -> BoxFuture<'_, StoreResult<Vec<tracera_server::store::TraceLink>>> {
            Box::pin(async { Ok(vec![]) })
        }
        fn list_teams(&self) -> BoxFuture<'_, StoreResult<Vec<tracera_server::store::TeamRow>>> {
            Box::pin(async { Ok(vec![]) })
        }
        fn list_projects(
            &self,
            _p: ListParams,
        ) -> BoxFuture<'_, StoreResult<Vec<tracera_server::store::ProjectSummary>>> {
            Box::pin(async { Ok(vec![]) })
        }
        fn count_projects(&self) -> BoxFuture<'_, StoreResult<i64>> {
            Box::pin(async { Ok(0) })
        }
        fn get_project(
            &self,
            _id: String,
        ) -> BoxFuture<'_, StoreResult<Option<tracera_server::store::ProjectSummary>>>
        {
            Box::pin(async { Ok(None) })
        }
        fn count_evidence(&self) -> BoxFuture<'_, StoreResult<i64>> {
            Box::pin(async { Ok(0) })
        }
        fn check_readiness(&self) -> BoxFuture<'_, StoreResult<()>> {
            Box::pin(async { Ok(()) })
        }
        fn list_problems(
            &self,
            _p: String,
            _s: Option<String>,
            _lp: ListParams,
        ) -> BoxFuture<'_, StoreResult<Vec<Problem>>> {
            Box::pin(async { Ok(vec![]) })
        }
        fn create_problem(
            &self,
            _id: String,
            _p: String,
            _n: String,
            _t: String,
            _d: Option<String>,
            _s: String,
            _r: Option<String>,
            _c: Option<String>,
            _sc: Option<String>,
            _tags: Option<Value>,
            _il: String,
            _u: String,
            _pr: String,
            _rca: bool,
            _rci: bool,
            _wa: bool,
            _pfa: bool,
            _at: Option<String>,
            _team: Option<String>,
            _owner: Option<String>,
            _k: Option<String>,
            _now: DateTime<Utc>,
        ) -> BoxFuture<'_, StoreResult<Problem>> {
            Box::pin(async {
                Err(StoreError::Database(
                    "DemoStore is read-only; configure TRACERA_DB_URL for writes".into(),
                ))
            })
        }
        fn count_problems(&self, _p: String) -> BoxFuture<'_, StoreResult<i64>> {
            Box::pin(async { Ok(0) })
        }
        fn count_problems_filtered(
            &self,
            _p: String,
            _s: Option<String>,
        ) -> BoxFuture<'_, StoreResult<i64>> {
            Box::pin(async { Ok(0) })
        }
        fn create_swee_node(
            &self,
            _t: String,
            _l: String,
            _m: Value,
            _now: DateTime<Utc>,
        ) -> BoxFuture<'_, StoreResult<String>> {
            Box::pin(async {
                Err(StoreError::Database(
                    "DemoStore is read-only; configure TRACERA_DB_URL for writes".into(),
                ))
            })
        }
        fn create_swee_edge(
            &self,
            _t: String,
            _s: String,
            _t2: String,
            _c: f64,
            _src: String,
            _m: Value,
            _now: DateTime<Utc>,
        ) -> BoxFuture<'_, StoreResult<String>> {
            Box::pin(async {
                Err(StoreError::Database(
                    "DemoStore is read-only; configure TRACERA_DB_URL for writes".into(),
                ))
            })
        }
        fn list_swee_nodes(
            &self,
            _t: Option<String>,
        ) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
            Box::pin(async { Ok(vec![]) })
        }
        fn list_swee_edges(
            &self,
            _t: Option<String>,
        ) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
            Box::pin(async { Ok(vec![]) })
        }
        fn get_swee_node(
            &self,
            _id: String,
        ) -> BoxFuture<'_, StoreResult<Option<Value>>> {
            Box::pin(async { Ok(None) })
        }
        fn get_swee_neighbors(
            &self,
            _id: String,
            _d: String,
        ) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
            Box::pin(async { Ok(vec![]) })
        }
    }
}

use demo::DemoStore;
