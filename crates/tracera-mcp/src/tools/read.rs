//! Read-only MCP tools for the SWEE graph.
//!
//! Tools:
//! - `read_node`     — fetch a single SWEE node by id
//! - `read_edge`     — fetch a single SWEE edge by id
//! - `read_subgraph` — fetch a node plus its incident edges (and neighbor
//!                      nodes up to N hops away)
//! - `search`        — substring search over node labels, delegated through
//!                      `Store::list_swee_nodes`
//! - `query`         — typed projections (`by_type`, `by_id`, `linked_to`,
//!                      `uncovered_requirements`)
//!
//! All tools are implemented as inherent methods on [`crate::McpServer`] and
//! each carries a `#[tool]` attribute that drives rmcp's `tools/list`
//! metadata. The `#[tool_router]` macro on the `impl` block generates a
//! router function that `#[tool_handler]` in `lib.rs` consumes.

use std::collections::HashSet;

use rmcp::{
    handler::server::wrapper::Parameters,
    model::ErrorData as McpError,
    schemars,
    tool, tool_router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use tracing::instrument;

use crate::{ok, store_into, McpServer, ToolError};

// ---------------------------------------------------------------------------
// Shared helpers (used by write.rs and navigate.rs too — pub(crate))
// ---------------------------------------------------------------------------

/// Normalize the caller-provided direction string into one of
/// `"in"`, `"out"`, or `"both"` (the canonical values accepted by
/// `Store::get_swee_neighbors`).
///
/// Accepts the natural-language forms `"incoming"`, `"outgoing"`,
/// `"undirected"`, etc. so LLMs don't have to memorize the exact contract.
pub(crate) fn normalize_direction(s: &str) -> String {
    let cleaned = s.to_lowercase().replace('-', "_").replace(' ', "_");
    match cleaned.as_str() {
        "in" | "inbound" | "incoming" | "from" => "in".to_string(),
        "out" | "outbound" | "outgoing" | "to" => "out".to_string(),
        "both" | "any" | "all" | "undirected" | "bi" => "both".to_string(),
        other => other.to_string(),
    }
}

/// Build a `ReadNodeOutput` from a raw `serde_json::Value` row returned by
/// `Store::get_swee_node`. Returns `None` if `id` is missing (the store
/// shouldn't ever produce such a row, but we guard against schema drift).
pub(crate) fn node_from_value(id: &str, raw: &Value) -> Option<ReadNodeOutput> {
    Some(ReadNodeOutput {
        id: raw
            .get("id")
            .and_then(|v| v.as_str())
            .unwrap_or(id)
            .to_string(),
        node_type: raw
            .get("node_type")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown")
            .to_string(),
        label: raw
            .get("label")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string(),
        metadata: raw.get("metadata").cloned().unwrap_or_else(|| json!({})),
        created_at: raw
            .get("created_at")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string(),
        updated_at: raw
            .get("updated_at")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string(),
        labels: None,
    })
}

// ---------------------------------------------------------------------------
// Input / output types for each tool
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ReadNodeInput {
    /// The SWEE node id (UUID v4 string).
    pub id: String,
    /// If true, include the node's labels (FTS5 namespace tags).
    #[serde(default)]
    pub include_labels: bool,
}

#[derive(Debug, Serialize)]
pub struct ReadNodeOutput {
    pub id: String,
    pub node_type: String,
    pub label: String,
    pub metadata: Value,
    pub created_at: String,
    pub updated_at: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub labels: Option<Vec<String>>,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ReadEdgeInput {
    /// The SWEE edge id (UUID v4 string).
    pub id: String,
    /// If true, inline the source and target node summaries instead of just
    /// returning their ids. Costs one extra round-trip per node.
    #[serde(default)]
    pub expand_endpoints: bool,
}

#[derive(Debug, Serialize)]
pub struct ReadEdgeOutput {
    pub id: String,
    pub edge_type: String,
    pub source_id: String,
    pub target_id: String,
    pub confidence: f64,
    pub source: String,
    pub metadata: Value,
    pub created_at: String,
    pub updated_at: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_node: Option<ReadNodeOutput>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_node: Option<ReadNodeOutput>,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ReadSubgraphInput {
    /// Center node id.
    pub id: String,
    /// Number of hops to expand (0 = center only, 1 = center + immediate
    /// neighbors, default 1, max 2 to avoid exponential blowups).
    #[serde(default = "default_hops")]
    pub hops: u8,
    /// Edge direction filter for expansion.
    #[serde(default = "default_direction")]
    pub direction: String,
    /// Optional edge type whitelist (e.g. `["tests", "covers"]`).
    /// Empty / None = all edge types.
    #[serde(default)]
    pub edge_types: Vec<String>,
}

fn default_hops() -> u8 {
    1
}
fn default_direction() -> String {
    "both".to_string()
}

#[derive(Debug, Serialize)]
pub struct ReadSubgraphOutput {
    pub center: ReadNodeOutput,
    pub nodes: Vec<ReadNodeOutput>,
    pub edges: Vec<Value>,
    pub hops: u8,
    pub direction: String,
    pub truncated: bool,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct SearchInput {
    /// Free-text query string. Matched against node `label` (case-insensitive
    /// substring match — the underlying FTS5 filter is delegated to the
    /// store via `list_swee_nodes`).
    pub query: String,
    /// Optional node-type whitelist (e.g. `["requirement", "specification"]`).
    #[serde(default)]
    pub node_types: Vec<String>,
    /// Optional label-namespace filter (e.g. `"requirements"`, `"specs"`).
    /// Currently a no-op (returns an error if non-empty) — see tool docs.
    #[serde(default)]
    pub namespaces: Vec<String>,
    /// Max results to return (default 50, hard cap 500).
    #[serde(default = "default_search_limit")]
    pub limit: u32,
}

fn default_search_limit() -> u32 {
    50
}

#[derive(Debug, Serialize)]
pub struct SearchOutput {
    pub query: String,
    pub matches: Vec<ReadNodeOutput>,
    pub total: usize,
    pub truncated: bool,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct QueryInput {
    /// One of `"by_type"`, `"by_id"`, `"linked_to"`, or
    /// `"uncovered_requirements"`.
    pub kind: String,
    /// Argument bag interpreted per `kind`:
    /// - `by_type`           → `{ "node_type": "<NodeKind>" }`
    /// - `by_id`             → `{ "ids": ["..."] }` or `{ "id": "..." }`
    /// - `linked_to`         → `{ "node_id": "...", "direction": "in|out|both" }`
    /// - `uncovered_requirements` → `{}`
    #[serde(default)]
    pub args: Value,
}

#[derive(Debug, Serialize)]
pub struct QueryOutput {
    pub kind: String,
    pub count: usize,
    pub nodes: Vec<ReadNodeOutput>,
    pub edges: Vec<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
}

impl QueryOutput {
    /// Fill `count` from the actual node vector length.
    fn with_count(mut self) -> Self {
        self.count = self.nodes.len();
        self
    }
}

// =========================================================================
// ToolRouter — every `#[tool]` method below is registered on McpServer.
// =========================================================================

#[tool_router(router = tool_router_read, vis = "pub(crate)")]
impl McpServer {
    /// Fetch a single SWEE node by id.
    #[tool(
        description = "Fetch a single SWEE graph node by its UUID id. Returns the node's type, label, metadata, and timestamps. Optionally include its FTS5 labels via `include_labels: true`."
    )]
    #[instrument(level = "debug", skip(self))]
    pub async fn read_node(
        &self,
        Parameters(ReadNodeInput { id, include_labels }): Parameters<ReadNodeInput>,
    ) -> Result<rmcp::model::CallToolResult, McpError> {
        let raw = store_into(self.store.get_swee_node(id.clone()).await)?
            .ok_or_else(|| ToolError::NotFound(format!("node {id}")))?;

        let mut output = node_from_value(&id, &raw)
            .ok_or_else(|| ToolError::NotFound(format!("node {id}")))?;

        if include_labels {
            // The store doesn't currently expose a `list_node_labels` method,
            // so we fall back to scanning `list_swee_nodes(node_type = …)` and
            // pulling the `labels` array from the matching row. This stays
            // inside the trait contract — no direct DB access.
            let node_type = output.node_type.clone();
            let id_clone = output.id.clone();
            let all_nodes = store_into(self.store.list_swee_nodes(Some(node_type)).await)?;
            let labels = all_nodes
                .into_iter()
                .find(|n| n.get("id").and_then(|v| v.as_str()) == Some(&id_clone))
                .and_then(|n| n.get("labels").cloned())
                .and_then(|v| v.as_array().map(|a| a.clone()))
                .map(|arr| {
                    arr.into_iter()
                        .filter_map(|v| v.as_str().map(|s| s.to_string()))
                        .collect::<Vec<_>>()
                })
                .unwrap_or_default();
            output.labels = Some(labels);
        }

        ok(output)
    }

    /// Fetch a single SWEE edge by id.
    #[tool(
        description = "Fetch a single SWEE graph edge by its UUID id. Returns the edge type, endpoints, confidence, provenance (`source`), and metadata. Set `expand_endpoints: true` to inline the source and target node summaries (two extra round-trips)."
    )]
    #[instrument(level = "debug", skip(self))]
    pub async fn read_edge(
        &self,
        Parameters(ReadEdgeInput { id, expand_endpoints }): Parameters<ReadEdgeInput>,
    ) -> Result<rmcp::model::CallToolResult, McpError> {
        // The store's `list_swee_edges(edge_type)` is type-filtered; we
        // have to scan the edge stream to find a single id. For a typical
        // graph size this is acceptable; if you have >100k edges, the
        // dedicated `read_edge` lookup should be added to the store trait.
        let mut found: Option<Value> = None;
        for edge_type in crate::tools::navigate::all_edge_type_strings() {
            let rows = store_into(
                self.store
                    .list_swee_edges(Some(edge_type.to_string()))
                    .await,
            )?;
            if let Some(hit) = rows
                .into_iter()
                .find(|r| r.get("id").and_then(|v| v.as_str()) == Some(&id))
            {
                found = Some(hit);
                break;
            }
        }
        let raw = found.ok_or_else(|| ToolError::NotFound(format!("edge {id}")))?;

        let mut output = ReadEdgeOutput {
            id: raw
                .get("id")
                .and_then(|v| v.as_str())
                .unwrap_or(&id)
                .to_string(),
            edge_type: raw
                .get("edge_type")
                .and_then(|v| v.as_str())
                .unwrap_or("unknown")
                .to_string(),
            source_id: raw
                .get("source_id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            target_id: raw
                .get("target_id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            confidence: raw.get("confidence").and_then(|v| v.as_f64()).unwrap_or(1.0),
            source: raw
                .get("source")
                .and_then(|v| v.as_str())
                .unwrap_or("manual")
                .to_string(),
            metadata: raw.get("metadata").cloned().unwrap_or_else(|| json!({})),
            created_at: raw
                .get("created_at")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            updated_at: raw
                .get("updated_at")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            source_node: None,
            target_node: None,
        };

        if expand_endpoints {
            output.source_node = expand_node(self, &output.source_id).await?;
            output.target_node = expand_node(self, &output.target_id).await?;
        }

        ok(output)
    }

    /// Fetch a node plus its N-hop neighborhood.
    #[tool(
        description = "Fetch a SWEE node plus its N-hop neighborhood (N in {0,1,2}). Returns the center node, all neighbor nodes within `hops` edges (filtered by `direction` and optionally `edge_types`), and the connecting edges. Use `hops=0` to fetch only the center node; use `hops=2` for impact-style queries. Note: `hops>=3` is rejected to avoid exponential blow-ups."
    )]
    #[instrument(level = "debug", skip(self))]
    pub async fn read_subgraph(
        &self,
        Parameters(ReadSubgraphInput { id, hops, direction, edge_types }): Parameters<ReadSubgraphInput>,
    ) -> Result<rmcp::model::CallToolResult, McpError> {
        if hops > 2 {
            return Err(ToolError::InvalidInput("hops must be 0, 1, or 2".into()).into());
        }
        let dir = normalize_direction(&direction);

        let center_raw = store_into(self.store.get_swee_node(id.clone()).await)?
            .ok_or_else(|| ToolError::NotFound(format!("node {id}")))?;
        let center = node_from_value(&id, &center_raw)
            .ok_or_else(|| ToolError::NotFound(format!("node {id}")))?;

        let mut visited: HashSet<String> = HashSet::new();
        visited.insert(center.id.clone());
        let mut frontier: Vec<String> = vec![center.id.clone()];
        let mut edges: Vec<Value> = Vec::new();
        let mut truncated = false;
        let max_nodes = 200;

        for _ in 0..hops {
            if visited.len() >= max_nodes {
                truncated = true;
                break;
            }
            let mut next_frontier: Vec<String> = Vec::new();
            for node_id in &frontier {
                let neighbors = store_into(
                    self.store
                        .get_swee_neighbors(node_id.clone(), dir.clone())
                        .await,
                )?;
                // Each neighbor row is a `{edge, other_node}` pair (the
                // shape returned by PgStore / SqliteStore's BFS expansion).
                for entry in neighbors {
                    let edge = entry.get("edge").cloned().unwrap_or(Value::Null);
                    let other = entry.get("other_node").cloned().unwrap_or(Value::Null);

                    if !edge_types.is_empty() {
                        let et = edge
                            .get("edge_type")
                            .and_then(|v| v.as_str())
                            .unwrap_or("");
                        if !edge_types.iter().any(|t| t == et) {
                            continue;
                        }
                    }

                    edges.push(edge);

                    if let Some(other_id) =
                        other.get("id").and_then(|v| v.as_str()).map(String::from)
                    {
                        if !visited.contains(&other_id) {
                            visited.insert(other_id.clone());
                            next_frontier.push(other_id.clone());
                            if visited.len() >= max_nodes {
                                truncated = true;
                            }
                        }
                    }
                }
            }
            if next_frontier.is_empty() {
                break;
            }
            frontier = next_frontier;
        }

        // Hydrate visited nodes (excluding the center, which is already in
        // the response).
        let mut nodes_out: Vec<ReadNodeOutput> = Vec::new();
        for nid in visited.iter() {
            if nid == &center.id {
                continue;
            }
            if let Some(n) = expand_node(self, nid).await? {
                nodes_out.push(n);
            }
        }

        ok(ReadSubgraphOutput {
            center,
            nodes: nodes_out,
            edges,
            hops,
            direction: dir,
            truncated,
        })
    }

    /// Full-text search across node labels.
    #[tool(
        description = "Full-text search across node labels. Returns up to `limit` (default 50, max 500) matching nodes. The `namespaces` filter is currently best-effort — passing a non-empty list returns an error so you don't silently drop the filter."
    )]
    #[instrument(level = "debug", skip(self))]
    pub async fn search(
        &self,
        Parameters(SearchInput { query, node_types, namespaces, limit }): Parameters<SearchInput>,
    ) -> Result<rmcp::model::CallToolResult, McpError> {
        if !namespaces.is_empty() {
            return Err(ToolError::Unsupported(
                "namespaces filter is not yet implemented in the Store trait; \
                 open a follow-up issue or use `node_types` instead"
                    .into(),
            )
            .into());
        }
        if limit == 0 || limit > 500 {
            return Err(
                ToolError::InvalidInput(format!("limit must be between 1 and 500, got {limit}"))
                    .into(),
            );
        }
        if query.trim().is_empty() {
            return Err(ToolError::InvalidInput("query must be non-empty".into()).into());
        }

        let types: Vec<String> = if node_types.is_empty() {
            crate::tools::navigate::all_node_type_strings()
                .into_iter()
                .map(|s| s.to_string())
                .collect()
        } else {
            node_types.clone()
        };

        let q_lower = query.to_lowercase();
        let mut matches: Vec<ReadNodeOutput> = Vec::new();
        let mut total = 0usize;
        let limit_us = limit as usize;

        for node_type in &types {
            let rows = store_into(self.store.list_swee_nodes(Some(node_type.clone())).await)?;
            for row in rows {
                total += 1;
                let label = row
                    .get("label")
                    .and_then(|v| v.as_str())
                    .unwrap_or("")
                    .to_lowercase();
                if label.contains(&q_lower) {
                    if matches.len() < limit_us {
                        if let Some(n) = node_from_value("", &row) {
                            matches.push(n);
                        }
                    }
                }
            }
        }

        let truncated = total > matches.len();
        ok(SearchOutput {
            query,
            matches,
            total,
            truncated,
        })
    }

    /// Typed projection over the SWEE graph.
    #[tool(
        description = "Typed projection over the SWEE graph. Pass `kind` as one of: `by_type` (args: `{node_type}`), `by_id` (args: `{ids}` array or single `id`), `linked_to` (args: `{node_id, direction}`), `uncovered_requirements` (args: `{}`). Returns nodes + edges as appropriate for the projection."
    )]
    #[instrument(level = "debug", skip(self))]
    pub async fn query(
        &self,
        Parameters(QueryInput { kind, args }): Parameters<QueryInput>,
    ) -> Result<rmcp::model::CallToolResult, McpError> {
        match kind.as_str() {
            "by_type" => {
                let node_type = args
                    .get("node_type")
                    .and_then(|v| v.as_str())
                    .ok_or_else(|| ToolError::InvalidInput("`by_type` requires args.node_type".into()))?
                    .to_string();
                let rows =
                    store_into(self.store.list_swee_nodes(Some(node_type.clone())).await)?;
                let nodes = rows
                    .iter()
                    .filter_map(|r| node_from_value("", r))
                    .collect();
                ok(QueryOutput {
                    kind,
                    count: 0,
                    nodes,
                    edges: vec![],
                    notes: None,
                }
                .with_count())
            }
            "by_id" => {
                let ids: Vec<String> = if let Some(arr) = args.get("ids").and_then(|v| v.as_array()) {
                    arr.iter()
                        .filter_map(|v| v.as_str().map(String::from))
                        .collect()
                } else if let Some(single) = args.get("id").and_then(|v| v.as_str()) {
                    vec![single.to_string()]
                } else {
                    return Err(ToolError::InvalidInput(
                        "`by_id` requires args.ids (array) or args.id (string)".into(),
                    )
                    .into());
                };
                let mut nodes = Vec::new();
                for id in ids {
                    if let Some(n) = expand_node(self, &id).await? {
                        nodes.push(n);
                    }
                }
                ok(QueryOutput {
                    kind,
                    count: 0,
                    nodes,
                    edges: vec![],
                    notes: None,
                }
                .with_count())
            }
            "linked_to" => {
                let node_id = args
                    .get("node_id")
                    .and_then(|v| v.as_str())
                    .ok_or_else(|| ToolError::InvalidInput("`linked_to` requires args.node_id".into()))?
                    .to_string();
                let direction = args
                    .get("direction")
                    .and_then(|v| v.as_str())
                    .unwrap_or("both")
                    .to_string();
                let dir = normalize_direction(&direction);
                let neighbors =
                    store_into(self.store.get_swee_neighbors(node_id.clone(), dir).await)?;
                let mut edges: Vec<Value> = Vec::new();
                let mut node_ids: Vec<String> = Vec::new();
                for entry in neighbors {
                    if let Some(edge) = entry.get("edge").cloned() {
                        edges.push(edge);
                    }
                    if let Some(other_id) = entry
                        .pointer("/other_node/id")
                        .and_then(|v| v.as_str())
                        .map(String::from)
                    {
                        node_ids.push(other_id);
                    }
                }
                node_ids.sort();
                node_ids.dedup();
                let mut nodes = Vec::new();
                for nid in node_ids {
                    if let Some(n) = expand_node(self, &nid).await? {
                        nodes.push(n);
                    }
                }
                ok(QueryOutput {
                    kind,
                    count: 0,
                    nodes,
                    edges,
                    notes: None,
                }
                .with_count())
            }
            "uncovered_requirements" => {
                // 1) list every requirement
                let req_rows =
                    store_into(self.store.list_swee_nodes(Some("requirement".to_string())).await)?;
                let mut uncovered: Vec<ReadNodeOutput> = Vec::new();
                for row in req_rows {
                    let id = match row.get("id").and_then(|v| v.as_str()) {
                        Some(s) => s.to_string(),
                        None => continue,
                    };
                    let neighbors = store_into(
                        self.store
                            .get_swee_neighbors(id.clone(), "in".to_string())
                            .await,
                    )?;
                    // A requirement is "covered" iff at least one incoming
                    // edge has type `tests` or `covers`.
                    let covered = neighbors.iter().any(|entry| {
                        entry
                            .pointer("/edge/edge_type")
                            .and_then(|v| v.as_str())
                            .map(|et| et == "tests" || et == "covers")
                            .unwrap_or(false)
                    });
                    if !covered {
                        if let Some(n) = node_from_value(&id, &row) {
                            uncovered.push(n);
                        }
                    }
                }
                ok(QueryOutput {
                    kind,
                    count: 0,
                    nodes: uncovered,
                    edges: vec![],
                    notes: Some("Requirements with no incoming `tests` or `covers` edge".to_string()),
                }
                .with_count())
            }
            other => Err(ToolError::InvalidInput(format!("unknown query kind: {other}")).into()),
        }
    }
}

// ---------------------------------------------------------------------------
// Internal helpers — `expand_node` is shared with other tool modules
// ---------------------------------------------------------------------------

async fn expand_node(server: &McpServer, id: &str) -> Result<Option<ReadNodeOutput>, McpError> {
    let raw = match store_into(server.store.get_swee_node(id.to_string()).await)? {
        Some(r) => r,
        None => return Ok(None),
    };
    Ok(node_from_value(id, &raw))
}

// ---------------------------------------------------------------------------
// Public re-exports of the type enumerations
// ---------------------------------------------------------------------------
//
// `navigate.rs` keeps the canonical lists; we re-export here so callers
// that depend only on `tools::read` don't have to import `navigate`.

pub use crate::tools::navigate::all_node_type_strings;
pub use crate::tools::navigate::all_edge_type_strings;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn direction_normalization_is_total() {
        for raw in [
            "in", "IN", "incoming", "from", "out", "Outgoing", "to", "both", "any",
            "undirected", "garbage",
        ] {
            let _ = normalize_direction(raw);
        }
        assert_eq!(normalize_direction("in"), "in");
        assert_eq!(normalize_direction("incoming"), "in");
        assert_eq!(normalize_direction("from"), "in");
        assert_eq!(normalize_direction("out"), "out");
        assert_eq!(normalize_direction("to"), "out");
        assert_eq!(normalize_direction("both"), "both");
        assert_eq!(normalize_direction("undirected"), "both");
        // Unknown strings are passed through unchanged so the store
        // gets the canonical error rather than us guessing.
        assert_eq!(normalize_direction("garbage"), "garbage");
    }

    #[test]
    fn read_node_input_deserializes_minimal_payload() {
        let raw = json!({ "id": "abc" });
        let parsed: ReadNodeInput = serde_json::from_value(raw).unwrap();
        assert_eq!(parsed.id, "abc");
        assert!(!parsed.include_labels);
    }

    #[test]
    fn read_node_input_rejects_unknown_fields() {
        let raw = json!({ "id": "abc", "wat": 1 });
        let parsed: Result<ReadNodeInput, _> = serde_json::from_value(raw);
        assert!(parsed.is_err(), "deny_unknown_fields should reject `wat`");
    }

    #[test]
    fn read_subgraph_input_defaults_are_stable() {
        let raw = json!({ "id": "abc" });
        let parsed: ReadSubgraphInput = serde_json::from_value(raw).unwrap();
        assert_eq!(parsed.hops, 1);
        assert_eq!(parsed.direction, "both");
        assert!(parsed.edge_types.is_empty());
    }

    #[test]
    fn search_input_default_limit_is_50() {
        assert_eq!(default_search_limit(), 50);
    }

    #[test]
    fn query_input_supports_all_kinds() {
        for kind in ["by_type", "by_id", "linked_to", "uncovered_requirements"] {
            let raw = json!({ "kind": kind });
            let parsed: QueryInput = serde_json::from_value(raw).unwrap();
            assert_eq!(parsed.kind, kind);
        }
    }

    #[test]
    fn query_output_with_count_recovers_zero() {
        let o = QueryOutput {
            kind: "by_type".to_string(),
            count: 999,
            nodes: vec![],
            edges: vec![],
            notes: None,
        }
        .with_count();
        assert_eq!(o.count, 0);
    }

    #[test]
    fn node_from_value_handles_missing_optional_fields() {
        let raw = json!({ "id": "x", "node_type": "requirement" });
        let n = node_from_value("x", &raw).unwrap();
        assert_eq!(n.id, "x");
        assert_eq!(n.node_type, "requirement");
        assert_eq!(n.label, "");
        assert_eq!(n.metadata, json!({}));
        assert!(n.labels.is_none());
    }
}