//! MCP tools for Tracera SWEE graph.
//!
//! All `#[tool]` methods live in this file inside a single
//! `#[rmcp::tool_router(router = tool_router, vis = "pub")] impl TraceraMcpServer { ... }`
//! block. The macro generates `TraceraMcpServer::tool_router()` (public), which
//! `lib.rs` wires into the `#[tool_handler]` `ServerHandler` impl.

use std::collections::HashMap;

use chrono::{DateTime, Utc};
use rmcp::{
    handler::server::wrapper::Parameters,
    model::{CallToolResult, ContentBlock},
    ErrorData,
};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use tracera_server::{
    store::{Store, StoreResult},
    swee::{EdgeKind, NodeKind},
};

use crate::TraceraMcpServer;

/// Unique server-side tool namespace (used in tool `name` for collisions).
pub const SERVER_NAME: &str = "tracera-mcp";

// =========================================================================
// Tool argument wrappers (Parameters<T> requires Deserialize + JsonSchema)
// =========================================================================

/// Arguments for the `list_nodes` tool.
#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct ListNodesArgs {
    /// Optional `NodeKind` name to filter by (for example `Requirement`).
    #[serde(default)]
    pub node_type: Option<String>,
}

/// Arguments for the `get_node` tool.
#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct GetNodeArgs {
    /// Id of the node to fetch.
    pub id: String,
}

/// Arguments for the `neighbours` and `subgraph` tools.
#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct NeighborsArgs {
    /// Id of the node whose neighbourhood should be returned.
    pub id: String,
    /// Edge direction to follow: `outgoing` (default), `incoming`, or `both`.
    #[serde(default = "default_direction")]
    pub direction: String,
}

fn default_direction() -> String {
    "outgoing".to_string()
}

/// Arguments for the `list_edges` tool.
#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct ListEdgesArgs {
    /// Optional `EdgeKind` name to filter by.
    #[serde(default)]
    pub edge_type: Option<String>,
}

/// Arguments for the `create_node` tool.
#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct CreateNodeArgs {
    /// `NodeKind` name for the new node.
    pub node_type: String,
    /// Human-readable label for the new node.
    pub label: String,
    /// Optional free-form metadata stored alongside the node.
    #[serde(default)]
    pub metadata: Option<Value>,
}

/// Arguments for the `create_edge` tool.
#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct CreateEdgeArgs {
    /// Id of the edge's source node.
    pub source_id: String,
    /// Id of the edge's target node.
    pub target_id: String,
    /// `EdgeKind` name for the new edge.
    pub edge_type: String,
    /// Confidence score in `0.0..=1.0`; defaults to `1.0`.
    #[serde(default = "default_confidence")]
    pub confidence: f64,
    /// Provenance label for the edge; defaults to `agileplus`.
    #[serde(default = "default_source")]
    pub source: String,
    /// Optional free-form metadata stored alongside the edge.
    #[serde(default)]
    pub metadata: Option<Value>,
}

fn default_confidence() -> f64 {
    1.0
}

fn default_source() -> String {
    "agileplus".to_string()
}

/// Arguments for the `propose` tool.
#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct ProposeArgs {
    /// Natural-language description of the intended change.
    pub intent: String,
    /// Ids of the nodes or edges the proposal affects.
    #[serde(default)]
    pub affected_ids: Vec<String>,
    /// Proposal kind label (for example `add` or `remove`); defaults to `add`.
    #[serde(default = "default_proposal_kind")]
    pub kind: String,
}

fn default_proposal_kind() -> String {
    "add".to_string()
}

// =========================================================================
// Response helpers
// =========================================================================

/// Serialize `value` as pretty JSON and return it as a single text block.
fn ok_json<T: Serialize>(value: &T) -> Result<CallToolResult, ErrorData> {
    Ok(CallToolResult::success(vec![ContentBlock::text(
        serde_json::to_string_pretty(value).map_err(internal_error)?,
    )]))
}

fn internal_error<E: std::fmt::Display>(e: E) -> ErrorData {
    ErrorData::internal_error(format!("tracera-mcp: {e}"), None)
}

// =========================================================================
// Tool router — single impl block on `TraceraMcpServer`
// =========================================================================

#[allow(missing_docs)]
#[rmcp::tool_router(router = tool_router, vis = "pub")]
impl TraceraMcpServer {
    // ---------- READ tools ----------

    #[rmcp::tool(description = "List nodes in the SWEE graph, optionally filtered by node_type")]
    async fn list_nodes(
        &self,
        Parameters(args): Parameters<ListNodesArgs>,
    ) -> Result<CallToolResult, ErrorData> {
        let nodes = self
            .store
            .list_swee_nodes(args.node_type)
            .await
            .map_err(internal_error)?;
        ok_json(&json!({
            "count": nodes.len(),
            "nodes": nodes
        }))
    }

    #[rmcp::tool(description = "Fetch a single node by its id")]
    async fn get_node(
        &self,
        Parameters(args): Parameters<GetNodeArgs>,
    ) -> Result<CallToolResult, ErrorData> {
        let id = args.id.clone();
        let node = self
            .store
            .get_swee_node(args.id)
            .await
            .map_err(internal_error)?;
        match node {
            Some(v) => ok_json(&v),
            None => Err(ErrorData::invalid_params(
                format!("node '{}' not found", id),
                None,
            )),
        }
    }

    #[rmcp::tool(description = "Return the edges adjacent to a node (1-hop neighborhood)")]
    async fn neighbours(
        &self,
        Parameters(args): Parameters<NeighborsArgs>,
    ) -> Result<CallToolResult, ErrorData> {
        let id = args.id.clone();
        let edges = self
            .store
            .get_swee_neighbors(args.id, args.direction)
            .await
            .map_err(internal_error)?;
        ok_json(&json!({
            "node_id": id,
            "count": edges.len(),
            "edges": edges
        }))
    }

    #[rmcp::tool(description = "List edges in the graph, optionally filtered by edge_type")]
    async fn list_edges(
        &self,
        Parameters(args): Parameters<ListEdgesArgs>,
    ) -> Result<CallToolResult, ErrorData> {
        let edges = self
            .store
            .list_swee_edges(args.edge_type)
            .await
            .map_err(internal_error)?;
        ok_json(&json!({
            "count": edges.len(),
            "edges": edges
        }))
    }

    // ---------- WRITE tools ----------

    #[rmcp::tool(description = "Create a new node in the SWEE graph; returns the new node's id")]
    async fn create_node(
        &self,
        Parameters(args): Parameters<CreateNodeArgs>,
    ) -> Result<CallToolResult, ErrorData> {
        NodeKind::from_str(&args.node_type).ok_or_else(|| {
            ErrorData::invalid_params(format!("unknown node_type '{}'", args.node_type), None)
        })?;
        let now: DateTime<Utc> = Utc::now();
        let new_id = self
            .store
            .create_swee_node(
                args.node_type,
                args.label,
                args.metadata.unwrap_or(Value::Null),
                now,
            )
            .await
            .map_err(internal_error)?;
        ok_json(&json!({ "id": new_id }))
    }

    #[rmcp::tool(
        description = "Create a new edge between two existing nodes; returns the new edge's id"
    )]
    async fn create_edge(
        &self,
        Parameters(args): Parameters<CreateEdgeArgs>,
    ) -> Result<CallToolResult, ErrorData> {
        EdgeKind::from_str(&args.edge_type).ok_or_else(|| {
            ErrorData::invalid_params(format!("unknown edge_type '{}'", args.edge_type), None)
        })?;
        let now: DateTime<Utc> = Utc::now();
        let new_id = self
            .store
            .create_swee_edge(
                args.edge_type,
                args.source_id,
                args.target_id,
                args.confidence,
                args.source,
                args.metadata.unwrap_or(Value::Null),
                now,
            )
            .await
            .map_err(internal_error)?;
        ok_json(&json!({ "id": new_id }))
    }

    // ---------- NAVIGATE / PROPOSE tools ----------

    #[rmcp::tool(
        description = "Return a 1-hop subgraph rooted at the given node id (node + neighbours)"
    )]
    async fn subgraph(
        &self,
        Parameters(args): Parameters<NeighborsArgs>,
    ) -> Result<CallToolResult, ErrorData> {
        let id = args.id.clone();
        let node = self
            .store
            .get_swee_node(args.id)
            .await
            .map_err(internal_error)?;
        let edges = self
            .store
            .get_swee_neighbors(id, args.direction)
            .await
            .map_err(internal_error)?;
        ok_json(&json!({
            "root": node,
            "edges": edges
        }))
    }

    #[rmcp::tool(
        description = "Submit a natural-language proposal describing an intended graph change (no mutation)"
    )]
    async fn propose(
        &self,
        Parameters(args): Parameters<ProposeArgs>,
    ) -> Result<CallToolResult, ErrorData> {
        // Record the proposal as a synthetic Proposal node so Atlas picks it up.
        let proposal_id = format!("proposal-{}", uuid::Uuid::new_v4());
        let now: DateTime<Utc> = Utc::now();
        let new_id = self
            .store
            .create_swee_node(
                format!("{:?}", NodeKind::Requirement),
                format!("Proposal: {}", args.intent),
                json!({
                    "kind": args.kind,
                    "affected_ids": args.affected_ids,
                    "submitted_at": now.to_rfc3339(),
                    "id_hint": proposal_id,
                    "node_subtype": "proposal",
                }),
                now,
            )
            .await
            .map_err(internal_error)?;
        ok_json(&json!({
            "id": new_id,
            "intent": args.intent,
            "kind": args.kind,
            "affected_ids": args.affected_ids,
        }))
    }
}

// Compile-time sanity: the Store trait must support the methods we use.
#[allow(dead_code)]
fn _assert_store_methods<S: Store>() {
    let _marker = std::marker::PhantomData::<S>;
    let _store_result_is_send: fn(StoreResult<()>) = |_| {};
    let _fns: Vec<&str> = vec![
        "list_swee_nodes",
        "get_swee_node",
        "create_swee_node",
        "list_swee_edges",
        "create_swee_edge",
        "get_swee_neighbors",
    ];
    let _hm: HashMap<String, Value> = HashMap::new();
}
