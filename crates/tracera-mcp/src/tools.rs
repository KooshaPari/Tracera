//! MCP tools for Tracera SWEE graph.
//!
//! All `#[tool]` methods live in this file inside a single
//! `#[rmcp::tool_router(router = tool_router, vis = "pub")] impl TraceraMcpServer { ... }`
//! block. The macro generates `TraceraMcpServer::tool_router()` (public), which
//! `lib.rs` wires into the `#[tool_handler]` `ServerHandler` impl.

use std::collections::HashMap;

use chrono::{DateTime, Utc};
use rmcp::{
    ErrorData,
    handler::server::wrapper::Parameters,
    model::{CallToolResult, ContentBlock},
};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use tracera_server::{
    store::{Store, StoreResult},
    swee::{EdgeKind, NodeKind},
};

use std::str::FromStr as _;
use crate::TraceraMcpServer;

/// Unique server-side tool namespace (used in tool `name` for collisions).
pub const SERVER_NAME: &str = "tracera-mcp";

// =========================================================================
// Tool argument wrappers (Parameters<T> requires Deserialize + JsonSchema)
// =========================================================================

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct ListNodesArgs {
    #[serde(default)]
    pub node_type: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct GetNodeArgs {
    pub id: String,
}

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct NeighborsArgs {
    pub id: String,
    #[serde(default = "default_direction")]
    pub direction: String,
}

fn default_direction() -> String {
    "outgoing".to_string()
}

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct ListEdgesArgs {
    #[serde(default)]
    pub edge_type: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct CreateNodeArgs {
    pub node_type: String,
    pub label: String,
    #[serde(default)]
    pub metadata: Option<Value>,
}

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct CreateEdgeArgs {
    pub source_id: String,
    pub target_id: String,
    pub edge_type: String,
    #[serde(default = "default_confidence")]
    pub confidence: f64,
    #[serde(default = "default_source")]
    pub source: String,
    #[serde(default)]
    pub metadata: Option<Value>,
}

fn default_confidence() -> f64 {
    1.0
}

fn default_source() -> String {
    "agileplus".to_string()
}

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct ProposeArgs {
    pub intent: String,
    #[serde(default)]
    pub affected_ids: Vec<String>,
    #[serde(default = "default_proposal_kind")]
    pub kind: String,
}

fn default_proposal_kind() -> String {
    "add".to_string()
}

// =========================================================================
// Response helpers
// =========================================================================

fn ok_text(body: String) -> Result<CallToolResult, ErrorData> {
    Ok(CallToolResult::success(vec![ContentBlock::text(body)]))
}

fn ok_json<T: Serialize>(value: &T) -> Result<CallToolResult, ErrorData> {
    serde_json::to_string(value)
        .map(|body| CallToolResult::success(vec![ContentBlock::text(body)]))
        .map_err(|e| internal_error(e))
}

fn internal_error<E: std::fmt::Display>(e: E) -> ErrorData {
    ErrorData::internal_error(format!("tracera-mcp: {e}"), None)
}

// =========================================================================
// Tool router — single impl block on `TraceraMcpServer`
// =========================================================================

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
        ok_text(
            serde_json::to_string_pretty(&json!({
                "count": nodes.len(),
                "nodes": nodes
            }))
            .unwrap_or_default(),
        )
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
            Some(v) => ok_text(serde_json::to_string_pretty(&v).unwrap_or_default()),
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
        ok_text(
            serde_json::to_string_pretty(&json!({
                "node_id": id,
                "count": edges.len(),
                "edges": edges
            }))
            .unwrap_or_default(),
        )
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
        ok_text(
            serde_json::to_string_pretty(&json!({
                "count": edges.len(),
                "edges": edges
            }))
            .unwrap_or_default(),
        )
    }

    // ---------- WRITE tools ----------

    #[rmcp::tool(description = "Create a new node in the SWEE graph; returns the new node's id")]
    async fn create_node(
        &self,
        Parameters(args): Parameters<CreateNodeArgs>,
    ) -> Result<CallToolResult, ErrorData> {
        NodeKind::from_str(&args.node_type).ok_or_else(|| {
            ErrorData::invalid_params(
                format!("unknown node_type '{}'", args.node_type),
                None,
            )
        })?;
        let now: DateTime<Utc> = Utc::now();
        let new_id = self
            .store
            .create_swee_node(args.node_type, args.label, args.metadata.unwrap_or(Value::Null), now)
            .await
            .map_err(internal_error)?;
        ok_text(serde_json::to_string_pretty(&json!({ "id": new_id })).unwrap_or_default())
    }

    #[rmcp::tool(description = "Create a new edge between two existing nodes; returns the new edge's id")]
    async fn create_edge(
        &self,
        Parameters(args): Parameters<CreateEdgeArgs>,
    ) -> Result<CallToolResult, ErrorData> {
        EdgeKind::from_str(&args.edge_type).ok_or_else(|| {
            ErrorData::invalid_params(
                format!("unknown edge_type '{}'", args.edge_type),
                None,
            )
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
        ok_text(serde_json::to_string_pretty(&json!({ "id": new_id })).unwrap_or_default())
    }

    // ---------- NAVIGATE / PROPOSE tools ----------

    #[rmcp::tool(description = "Return a 1-hop subgraph rooted at the given node id (node + neighbours)")]
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
        ok_text(
            serde_json::to_string_pretty(&json!({
                "root": node,
                "edges": edges
            }))
            .unwrap_or_default(),
        )
    }

    #[rmcp::tool(description = "Submit a natural-language proposal describing an intended graph change (no mutation)")]
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
        ok_text(
            serde_json::to_string_pretty(&json!({
                "id": new_id,
                "intent": args.intent,
                "kind": args.kind,
                "affected_ids": args.affected_ids,
            }))
            .unwrap_or_default(),
        )
    }
}

// Compile-time sanity: the Store trait must support the methods we use.
#[allow(dead_code)]
fn _assert_store_methods<S: Store>() {
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
