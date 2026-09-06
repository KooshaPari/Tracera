//! Tracera MCP (Model Context Protocol) server library.
//!
//! Exposes the Tracera SWEE graph — nodes, edges, neighbours, and change
//! proposals — as a small, agent-friendly MCP tool surface. The canonical
//! transport is stdio (one JSON-RPC 2.0 frame per line, Content-Length
//! framed). Every tool delegates into the `tracera_server::Store` trait, so
//! the same graph that's persisted by the HTTP server is the graph any MCP
//! client (Claude, Cursor, IDE agent, custom agent runtime) reads & writes.
//!
//! # Tool surface (rmcp 3.2)
//!
//! ## Read
//! - `list_nodes` — list SWEE nodes, optionally filtered by `node_type`
//! - `get_node`   — fetch one node by id
//! - `neighbours` — list edges touching a node (both directions)
//!
//! ## Write (these *do* mutate the graph and emit a `trace_link_changed` event)
//! - `create_node` — insert a node (delegates to `Store::create_swee_node`)
//! - `create_edge` — insert an edge between two existing nodes
//!
//! ## Propose (never mutates; returns a `ChangeRequest` a human reviewer can apply)
//! - `propose_change` — produces a `ChangeRequest` from a diff payload
//!
//! All tools return a `Result<serde_json::Value, rmcp::model::ErrorData>` so the
//! macro can shape the wire response consistently.

#![forbid(unsafe_code)]
#![warn(missing_docs)]
// Relaxed for MCP arg structs (rmcp derives schemars docs from the field names).

pub mod tools;

use std::sync::Arc;

use rmcp::handler::server::router::tool::ToolRouter;
use rmcp::handler::server::ServerHandler;
use rmcp::model::InitializeResult;
use rmcp::ErrorData as McpError;
// rmcp 3.2 re-exports the macros when feature="macros" is enabled.
use rmcp::{tool_handler, tool_router};
use tracera_server::store::Store;

/// A type alias for our JSON tool output. The macro serializes whatever this
/// `serde_json::Value` is back to the MCP client.
pub type ToolResult<T = serde_json::Value> = Result<T, McpError>;

/// Shorter alias preserved from the original v0.1 public API — downstream
/// binaries (and tests) refer to the server as `McpServer`.
pub type McpServer = TraceraMcpServer;

/// The central MCP server. Wraps an `Arc<dyn Store>` and exposes tool routers.
///
/// All four tool routers (`read`, `write`, `navigate`, `propose`) are wired in
/// at construction time and merged into the `ServerHandler` impl via the
/// `#[tool_handler]` macro.
#[derive(Clone)]
pub struct TraceraMcpServer {
    /// Backing store. Always `Arc<dyn Store + Send + Sync>` — the HTTP server,
    /// the desktop tray, and any future agent runtime can all share the same
    /// instance behind an `Arc`.
    pub store: Arc<dyn Store>,
    /// All tools registered against this server. Auto-populated by the
    /// `#[tool_handler]` macro using the routers attached to each sub-module.
    pub tool_router: ToolRouter<Self>,
}

impl TraceraMcpServer {
    /// Build a new MCP server wrapping the given store.
    pub fn new(store: Arc<dyn Store>) -> Self {
        Self {
            store,
            tool_router: Self::tool_router(),
        }
    }

    /// Convenience: the standard info advertised during `initialize`. The MCP
    /// spec uses `ServerInfo` as a type alias for `InitializeResult` in rmcp 3.2.
    pub fn server_info() -> InitializeResult {
        use rmcp::model::{Implementation, ServerCapabilities, ServerInfo};
        ServerInfo::new(ServerCapabilities::default()).with_server_info(Implementation::new(
            "tracera-mcp",
            env!("CARGO_PKG_VERSION"),
        ))
    }
}

// ---------------------------------------------------------------------------
// ServerHandler impl — auto-generates `tool_router()` and the JSON-RPC methods
// from the `#[tool_router]` impls attached to this type by sub-modules.
// ---------------------------------------------------------------------------

#[tool_handler]
impl ServerHandler for TraceraMcpServer {
    /// Returns the static info advertised during `initialize`.
    fn get_info(&self) -> InitializeResult {
        Self::server_info()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The `TraceraMcpServer` must be `Send + Sync` so the tokio task hosting
    /// the stdio transport can share it across awaits.
    #[test]
    fn server_is_send_and_sync() {
        fn assert_send_sync<T: Send + Sync>() {}
        assert_send_sync::<TraceraMcpServer>();
    }

    /// `server_info` must always succeed and produce a valid info.
    #[test]
    fn server_info_is_well_formed() {
        let info = TraceraMcpServer::server_info();
        assert_eq!(info.server_info.name, "tracera-mcp");
        assert!(!info.server_info.version.is_empty());
    }
}
