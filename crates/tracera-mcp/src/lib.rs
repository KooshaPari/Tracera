//! # tracera-mcp
//!
//! Model Context Protocol (MCP) server for Tracera. Exposes the SWEE
//! evidence graph to MCP-aware clients (Claude Desktop, Cursor, etc.) over
//! stdio, delegating all reads/writes to the canonical
//! [`tracera_server::store::Store`] trait.
//!
//! ## Architecture
//!
//! ```text
//! ┌────────────────────────────┐   JSON-RPC / Content-Length   ┌──────────────────┐
//! │ MCP client (e.g. Claude)   │ ◄──────────────────────────► │ tracera-mcp stdio│
//! └────────────────────────────┘                                └────────┬─────────┘
//!                                                                          │  Store trait
//!                                                                          ▼
//!                                                              ┌──────────────────────┐
//!                                                              │  PgStore / SqliteStore│
//!                                                              └──────────────────────┘
//! ```
//!
//! The crate is intentionally thin: every tool is registered through
//! `rmcp`'s `#[tool]` attribute, and every method delegates to a
//! `&dyn Store`. There is **no in-process database**, no caching, and no
//! HTTP. Persistence is owned by `tracera-server`.
//!
//! ## Tools (15 total)
//!
//! | Module              | Count | Tools                                              |
//! |---------------------|-------|----------------------------------------------------|
//! | [`tools::read`]     | 5     | `read_node`, `read_edge`, `read_subgraph`, `search`, `query` |
//! | [`tools::write`]    | 4     | `create_node`, `update_node`, `create_edge`, `propose_change` |
//! | [`tools::navigate`] | 4     | `neighbors`, `path`, `impact`, `coverage`           |
//! | [`tools::propose`]  | 2     | `propose_decision`, `propose_spec_change`           |
//!
//! ## Usage
//!
//! Wire it up as an MCP server in your editor / Claude config; see the
//! `.mcp.json` / `.vscode/mcp.json` example files at the crate root.

use std::sync::Arc;

use rmcp::{
    ErrorData as McpError,
    handler::server::{router::tool::ToolRouter, tool_handler},
    model::{
        Implementation, InitializeRequestParam, InitializeResult, ProtocolVersion,
        ServerCapabilities, ServerInfo,
    },
    service::{RequestContext, RoleServer},
    transport::stdio,
    ServerHandler,
};
use thiserror::Error;
use tracing::{debug, info, instrument};

use tracera_server::store::{StoreError, StoreResult};

pub mod tools;

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

/// All errors returned by `tracera-mcp` tools.
///
/// Each variant maps cleanly onto an MCP error code:
///   - [`ToolError::InvalidInput`] → `-32602` (invalid params)
///   - [`ToolError::NotFound`]     → `-32004` (application: not found)
///   - [`ToolError::Store`]        → `-32603` (internal error)
///   - [`ToolError::Json`]         → `-32603` (serialization)
///   - [`ToolError::Unsupported`]  → `-32601` (method not found)
#[derive(Debug, Error)]
pub enum ToolError {
    /// Caller passed a value that failed schema/validation but isn't a
    /// `StoreError::Database` round-trip — e.g. unknown node type.
    #[error("invalid input: {0}")]
    InvalidInput(String),

    /// The target artifact (node / edge / project) does not exist.
    #[error("not found: {0}")]
    NotFound(String),

    /// Underlying datastore rejected the operation.
    #[error("store error: {0}")]
    Store(#[from] StoreError),

    /// `serde_json` round-trip failure when shaping an MCP response.
    #[error("json error: {0}")]
    Json(#[from] serde_json::Error),

    /// Caller asked for an operation that isn't wired up (e.g. an unknown
    /// relationship kind in the taxonomy validator).
    #[error("unsupported: {0}")]
    Unsupported(String),
}

impl From<ToolError> for McpError {
    fn from(err: ToolError) -> Self {
        let code = match &err {
            ToolError::InvalidInput { .. } => -32602,
            ToolError::NotFound { .. } => -32004,
            ToolError::Unsupported { .. } => -32601,
            ToolError::Store { .. } | ToolError::Json { .. } => -32603,
        };
        McpError::new(code, err.to_string(), None)
    }
}

/// Shorthand for `Result<T, ToolError>` inside tool bodies.
pub type ToolResult<T> = Result<T, ToolError>;

// ---------------------------------------------------------------------------
// StoreT — trait alias so tool impls can write `Arc<dyn StoreT>`
// ---------------------------------------------------------------------------

/// Trait alias for the `Store` so we don't have to repeat the trait import
/// in every tool module.
///
/// This is intentionally a tiny alias rather than a re-export so that tool
/// authors can write `store: Arc<dyn StoreT>` and have the compiler resolve
/// to the real [`tracera_server::store::Store`] trait.
pub trait StoreT: tracera_server::store::Store {}
impl<S: tracera_server::store::Store + ?Sized> StoreT for S {}

// ---------------------------------------------------------------------------
// McpServer — the wired-up server state
// ---------------------------------------------------------------------------

/// The Tracera MCP server.
///
/// Holds a single shared reference to the underlying
/// [`tracera_server::store::Store`] implementation (Postgres for hosted
/// deployments, SQLite for on-device). Every tool implementation receives
/// `&self` and reaches the trait through `self.store`.
#[derive(Clone)]
pub struct McpServer {
    /// Backing store. Shared (`Arc`) so we can clone `McpServer` cheaply and
    /// hand it to the rmcp service runtime.
    pub store: Arc<dyn StoreT>,

    /// Combined `ToolRouter` aggregating the per-module routers
    /// (`tool_router_read`, `tool_router_write`, `tool_router_navigate`,
    /// `tool_router_propose`). The `#[tool_handler]` macro reads
    /// `self.tool_router` to dispatch `tools/list` and `tools/call`.
    pub tool_router: ToolRouter<Self>,
}

impl McpServer {
    /// Construct a new server wired to `store`. Combines the per-module
    /// routers generated by `#[tool_router(router = ...)]` blocks in
    /// `tools/{read,write,navigate,propose}.rs`.
    pub fn new(store: Arc<dyn StoreT>) -> Self {
        let tool_router = tools::read::tool_router_read()
            .merge(tools::write::tool_router_write())
            .merge(tools::navigate::tool_router_navigate())
            .merge(tools::propose::tool_router_propose());
        Self {
            store,
            tool_router,
        }
    }

    /// Convenience: serve this `McpServer` over stdin/stdout using rmcp's
    /// built-in `stdio` transport. The future resolves when stdin EOFs or
    /// the underlying rmcp service shuts down.
    pub async fn serve_stdio(self) -> anyhow_lite::Result<()> {
        use rmcp::ServiceExt;
        let service = self
            .serve(stdio())
            .await
            .map_err(|e| anyhow_lite::anyhow!("failed to start stdio transport: {e}"))?;
        info!("tracera-mcp serving on stdio");
        service
            .waiting()
            .await
            .map_err(|e| anyhow_lite::anyhow!("stdio service exited with error: {e}"))?;
        Ok(())
    }
}

// ---------------------------------------------------------------------------
// Minimal `anyhow` stand-in (avoids pulling the full crate)
// ---------------------------------------------------------------------------
//
// We deliberately avoid pulling `anyhow` to keep the dependency surface
// small. This is a 30-line stand-in for `anyhow::Result` / `anyhow!` that
// satisfies exactly the calls used in [`McpServer::serve_stdio`].
pub mod anyhow_lite {
    use std::fmt;
    pub struct Error(String);
    impl fmt::Display for Error {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            f.write_str(&self.0)
        }
    }
    impl fmt::Debug for Error {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            f.write_str(&self.0)
        }
    }
    impl std::error::Error for Error {}
    pub type Result<T> = std::result::Result<T, Error>;
    pub fn anyhow<S: Into<String>>(msg: S) -> Error {
        Error(msg.into())
    }
}

// ---------------------------------------------------------------------------
// ServerHandler — protocol-level capabilities / info
// ---------------------------------------------------------------------------

/// MCP protocol version this server negotiates. Pinned to the version rmcp
/// 3.2 advertises as the current default.
const PROTOCOL_VERSION: ProtocolVersion = ProtocolVersion::V2025_06_18;

const SERVER_NAME: &str = "tracera-mcp";
const SERVER_VERSION: &str = env!("CARGO_PKG_VERSION");

/// Wire the tool router into the `ServerHandler` impl.
///
/// `#[tool_handler]` reads the `ToolRouter` from `self.tool_router` (built
/// in `McpServer::new` by merging the four per-module routers) and fills
/// in `call_tool`, `list_tools`, `get_info`, etc. — we only write the
/// protocol-level methods (`initialize`, `get_server_info`,
/// `get_protocol_version`).
#[tool_handler(router = self.tool_router)]
impl ServerHandler for McpServer {
    #[instrument(level = "debug", skip(self, _ctx), fields(method = "initialize"))]
    async fn initialize(
        &self,
        _ctx: RequestContext<RoleServer>,
        _params: InitializeRequestParam,
    ) -> Result<InitializeResult, McpError> {
        debug!("initialize: serving {} v{}", SERVER_NAME, SERVER_VERSION);
        Ok(InitializeResult {
            protocol_version: PROTOCOL_VERSION,
            capabilities: ServerCapabilities {
                // We only expose tools today; no resources / prompts / sampling.
                tools: Some(Default::default()),
                ..Default::default()
            },
            server_info: Implementation {
                name: SERVER_NAME.to_string(),
                version: SERVER_VERSION.to_string(),
                title: Some("Tracera MCP Server".to_string()),
                website_url: Some("https://github.com/KooshhaPari/Tracera".to_string()),
                icons: None,
            },
            instructions: Some(
                "Tracera MCP server. Tools operate on the SWEE evidence graph \
                 (requirements, specs, source files, tests, stories, PRs, etc.) \
                 via the Store trait. Use `read_*` and `navigate_*` tools for \
                 analysis; `create_*` / `update_*` for direct edits; \
                 `propose_*` for human-in-the-loop changes that require review."
                    .to_string(),
            ),
        })
    }

    /// Best-effort server info for legacy clients that probe `serverInfo`
    /// before fully completing `initialize`.
    fn get_server_info(&self) -> Option<ServerInfo> {
        Some(ServerInfo {
            name: SERVER_NAME.to_string(),
            version: SERVER_VERSION.to_string(),
        })
    }

    /// Pin the protocol version we negotiate.
    fn get_protocol_version(&self) -> ProtocolVersion {
        PROTOCOL_VERSION
    }
}

// ---------------------------------------------------------------------------
// Helpers shared across tool modules
// ---------------------------------------------------------------------------

/// Format a successful tool result into MCP's `CallToolResult` envelope.
pub(crate) fn ok<T: serde::Serialize>(value: T) -> Result<rmcp::model::CallToolResult, McpError> {
    let serialized = serde_json::to_string(&value).map_err(|e| {
        McpError::new(
            -32603,
            format!("response serialization failed: {e}"),
            None,
        )
    })?;
    Ok(rmcp::model::CallToolResult::success(vec![
        rmcp::model::Content::text(serialized),
    ]))
}

/// Format a structured error into a MCP `isError: true` `CallToolResult`.
///
/// We prefer returning `isError: true` *results* (not protocol errors) for
/// store / validation failures so the LLM can read the diagnostic and
/// retry. Protocol-level errors are reserved for transport failures.
pub(crate) fn ko<T: serde::Serialize>(value: T) -> Result<rmcp::model::CallToolResult, McpError> {
    let serialized = serde_json::to_string(&value).map_err(|e| {
        McpError::new(
            -32603,
            format!("error serialization failed: {e}"),
            None,
        )
    })?;
    Ok(rmcp::model::CallToolResult::error(vec![
        rmcp::model::Content::text(serialized),
    ]))
}

/// Convenience conversion so tool implementations can bubble `StoreError`
/// into the typed envelope without an explicit `?`.
pub(crate) fn store_into<T>(r: StoreResult<T>) -> ToolResult<T> {
    r.map_err(ToolError::from)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn tool_error_to_mcp_error_maps_codes() {
        let invalid = ToolError::InvalidInput("bad".into());
        let mcp: McpError = invalid.into();
        assert_eq!(mcp.code, -32602);

        let not_found = ToolError::NotFound("x".into());
        let mcp: McpError = not_found.into();
        assert_eq!(mcp.code, -32004);

        let unsupported = ToolError::Unsupported("x".into());
        let mcp: McpError = unsupported.into();
        assert_eq!(mcp.code, -32601);

        let store = ToolError::Store(StoreError::Database("oops".to_string()));
        let mcp: McpError = store.into();
        assert_eq!(mcp.code, -32603);
    }

    #[test]
    fn ok_envelope_round_trips_serializable_payload() {
        let payload = json!({ "hello": "world", "n": 42 });
        let result = ok(payload).expect("ok envelope");
        assert!(result.is_error != Some(true));
    }

    #[test]
    fn ko_envelope_round_trips_serializable_payload() {
        let payload = json!({ "error": "x", "code": "NOT_FOUND" });
        let result = ko(payload).expect("ko envelope");
        assert_eq!(result.is_error, Some(true));
    }

    #[test]
    fn server_info_constants_are_pinned() {
        assert_eq!(SERVER_NAME, "tracera-mcp");
        assert!(SERVER_VERSION.starts_with("0."));
    }
}