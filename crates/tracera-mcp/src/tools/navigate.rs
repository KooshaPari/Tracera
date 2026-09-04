//! Navigation / traversal MCP tools for the SWEE graph.
//!
//! Tools:
//! - `neighbors` — 1-hop neighborhood of a node (with edge-type filter)
//! - `path`      — BFS shortest path between two nodes
//! - `impact`    — 2-hop downstream / upstream blast-radius from a node
//! - `coverage`  — for a set of test nodes, return the requirement /
//!                  specification nodes they cover
//!
//! The navigation graph is delegated to `Store::get_swee_neighbors`; the
//! store returns pairs of `{edge, other_node}` that we walk in-memory to
//! compute paths, impact, and coverage. All results are bounded by a
//! configurable `max_nodes` cap to keep memory under control.

use std::collections::{HashMap, HashSet, VecDeque};

use rmcp::{
    handler::server::wrapper::Parameters,
    model::{CallToolResult, ErrorData as McpError},
    schemars,
    tool, tool_router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use tracing::instrument;

use crate::tools::read::node_from_value;
use crate::{ok, store_into, McpServer, ToolError};

use super::read::normalize_direction;

// ---------------------------------------------------------------------------
// Canonical type enumerations (re-exported to other tool modules)
// ---------------------------------------------------------------------------

/// Every valid `NodeKind` string, in declaration order.
///
/// Mirrors the 30-variant enum in `tracera-server/src/swee.rs`; we keep a
/// local copy so the MCP layer doesn't have to take a hard dep on the
/// server crate's private types.
pub fn all_node_type_strings() -> &'static [&'static str] {
    &[
        "requirement",
        "specification",
        "design",
        "source_file",
        "module",
        "class",
        "function",
        "test",
        "test_suite",
        "commit",
        "pull_request",
        "branch",
        "issue",
        "epic",
        "story",
        "task",
        "bug",
        "sprint",
        "release",
        "build",
        "deployment",
        "evidence",
        "problem",
        "incident",
        "change_request",
        "person",
        "team",
        "environment",
        "artifact",
        "metric",
    ]
}

/// Every valid `EdgeKind` string, in declaration order.
pub fn all_edge_type_strings() -> &'static [&'static str] {
    &[
        "implements",
        "specifies",
        "designs",
        "contains",
        "depends_on",
        "calls",
        "extends",
        "tests",
        "covers",
        "belongs_to",
        "authored_by",
        "touches",
        "targets",
        "merges_from",
        "fixes",
        "resolves",
        "supersedes",
        "references",
        "blocks",
        "parent_of",
        "in_sprint",
        "owned_by",
        "linked_to",
        "derived_from",
        "observed_in",
        "triggered_by",
        "correlates_with",
        "impacts",
        "released_in",
        "deployed_to",
        "built_from",
        "emitted_by",
    ]
}

// ---------------------------------------------------------------------------
// neighbors
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct NeighborsInput {
    /// Center node id.
    pub id: String,
    /// Edge direction filter. One of `"in"`, `"out"`, `"both"` (or the
    /// natural-language aliases `incoming`, `outgoing`, `undirected`).
    #[serde(default = "default_neighbors_direction")]
    pub direction: String,
    /// Optional edge-type whitelist.
    #[serde(default)]
    pub edge_types: Vec<String>,
    /// Cap on the number of neighbor rows returned. Default 100, hard cap 500.
    #[serde(default = "default_neighbors_limit")]
    pub limit: u32,
}

fn default_neighbors_direction() -> String {
    "both".to_string()
}
fn default_neighbors_limit() -> u32 {
    100
}

#[derive(Debug, Serialize)]
pub struct NeighborsOutput {
    pub id: String,
    pub direction: String,
    pub count: usize,
    pub truncated: bool,
    pub neighbors: Vec<NeighborRow>,
}

#[derive(Debug, Serialize)]
pub struct NeighborRow {
    pub edge: Value,
    pub other_node: Value,
}

// ---------------------------------------------------------------------------
// path
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct PathInput {
    /// Source node id.
    pub from: String,
    /// Target node id.
    pub to: String,
    /// Edge direction: `"out"` (forward from `from` to `to`),
    /// `"in"` (backward), or `"both"` (undirected). Default `"out"`.
    #[serde(default = "default_path_direction")]
    pub direction: String,
    /// Hard cap on BFS depth. Default 6, max 12.
    #[serde(default = "default_path_max_depth")]
    pub max_depth: u8,
    /// Optional edge-type whitelist (e.g. `["depends_on"]`).
    #[serde(default)]
    pub edge_types: Vec<String>,
}

fn default_path_direction() -> String {
    "out".to_string()
}
fn default_path_max_depth() -> u8 {
    6
}

#[derive(Debug, Serialize)]
pub struct PathOutput {
    pub from: String,
    pub to: String,
    pub found: bool,
    pub length: usize,
    pub nodes: Vec<Value>,
    pub edges: Vec<Value>,
    pub explored: usize,
}

// ---------------------------------------------------------------------------
// impact
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ImpactInput {
    /// Center node id.
    pub id: String,
    /// Direction: `"upstream"` (what depends on this), `"downstream"`
    /// (what this depends on), or `"both"`. Default `"downstream"`.
    #[serde(default = "default_impact_direction")]
    pub direction: String,
    /// BFS depth. Default 2, max 3.
    #[serde(default = "default_impact_depth")]
    pub depth: u8,
    /// Hard cap on returned nodes. Default 200, max 500.
    #[serde(default = "default_impact_limit")]
    pub max_nodes: u32,
}

fn default_impact_direction() -> String {
    "downstream".to_string()
}
fn default_impact_depth() -> u8 {
    2
}
fn default_impact_limit() -> u32 {
    200
}

#[derive(Debug, Serialize)]
pub struct ImpactOutput {
    pub id: String,
    pub direction: String,
    pub depth: u8,
    pub reached: usize,
    pub truncated: bool,
    pub nodes: Vec<Value>,
    pub edges: Vec<Value>,
}

// ---------------------------------------------------------------------------
// coverage
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct CoverageInput {
    /// Test node ids to evaluate.
    pub test_ids: Vec<String>,
    /// Max BFS depth from each test. Default 4, max 6.
    #[serde(default = "default_coverage_depth")]
    pub max_depth: u8,
    /// Hard cap on returned covered nodes. Default 200, max 500.
    #[serde(default = "default_coverage_limit")]
    pub max_nodes: u32,
}

fn default_coverage_depth() -> u8 {
    4
}
fn default_coverage_limit() -> u32 {
    200
}

#[derive(Debug, Serialize)]
pub struct CoverageOutput {
    pub test_ids: Vec<String>,
    pub covered_requirements: Vec<Value>,
    pub covered_specifications: Vec<Value>,
    pub uncovered_requirements: Vec<Value>,
    pub total_edges_walked: usize,
    pub truncated: bool,
}

// =========================================================================
// ToolRouter
// =========================================================================

#[tool_router(router = tool_router_navigate, vis = "pub(crate)")]
impl McpServer {
    /// 1-hop neighborhood of a node.
    #[tool(
        description = "Return the 1-hop neighborhood of a SWEE node. Each row is a `{edge, other_node}` pair so you can see both the connecting edge and the opposite endpoint. Filter by `direction` (`in`, `out`, `both`) and optionally restrict to a whitelist of `edge_types`."
    )]
    #[instrument(level = "debug", skip(self))]
    pub async fn neighbors(
        &self,
        Parameters(NeighborsInput {
            id,
            direction,
            edge_types,
            limit,
        }): Parameters<NeighborsInput>,
    ) -> Result<CallToolResult, McpError> {
        if limit == 0 || limit > 500 {
            return Err(ToolError::InvalidInput(format!(
                "limit must be between 1 and 500, got {limit}"
            ))
            .into());
        }
        let dir = normalize_direction(&direction);

        // Verify the center exists — otherwise the caller mistyped the id.
        let _ = store_into(self.store.get_swee_node(id.clone()).await)?
            .ok_or_else(|| ToolError::NotFound(format!("node {id}")))?;

        let rows = store_into(self.store.get_swee_neighbors(id.clone(), dir.clone()).await)?;
        let mut out: Vec<NeighborRow> = Vec::new();
        let mut truncated = false;
        for entry in rows {
            let edge = entry.get("edge").cloned().unwrap_or(Value::Null);
            if !edge_types.is_empty() {
                let et = edge
                    .get("edge_type")
                    .and_then(|v| v.as_str())
                    .unwrap_or("");
                if !edge_types.iter().any(|t| t == et) {
                    continue;
                }
            }
            if out.len() >= limit as usize {
                truncated = true;
                break;
            }
            out.push(NeighborRow {
                edge,
                other_node: entry.get("other_node").cloned().unwrap_or(Value::Null),
            });
        }

        let count = out.len();
        Ok(ok(NeighborsOutput {
            id,
            direction: dir,
            count,
            truncated,
            neighbors: out,
        })?)
    }

    /// BFS shortest path between two nodes.
    #[tool(
        description = "BFS shortest-path search between two SWEE nodes. Returns the ordered list of nodes + edges along the path. `direction` controls whether the search follows outgoing edges (`out`, default), incoming edges (`in`), or both (`both`). `max_depth` caps the BFS depth (default 6, max 12). Returns `found: false` if no path exists within the depth cap."
    )]
    #[instrument(level = "debug", skip(self))]
    pub async fn path(
        &self,
        Parameters(PathInput {
            from,
            to,
            direction,
            max_depth,
            edge_types,
        }): Parameters<PathInput>,
    ) -> Result<CallToolResult, McpError> {
        if max_depth == 0 || max_depth > 12 {
            return Err(ToolError::InvalidInput(
                "max_depth must be 1..=12".into(),
            )
            .into());
        }
        if from == to {
            return Ok(ok(PathOutput {
                from,
                to,
                found: true,
                length: 0,
                nodes: vec![],
                edges: vec![],
                explored: 1,
            })?);
        }
        let dir = normalize_direction(&direction);
        let max_nodes_explored: usize = 5_000;

        // Standard BFS over the (possibly directed) graph; we keep the
        // predecessor map so we can reconstruct the path.
        let mut visited: HashSet<String> = HashSet::new();
        let mut parent: HashMap<String, (String, Value)> = HashMap::new();
        let mut queue: VecDeque<(String, u8)> = VecDeque::new();
        visited.insert(from.clone());
        queue.push_back((from.clone(), 0));
        let mut found = false;
        let mut explored = 0usize;
        let max_d = max_depth;

        while let Some((node, depth)) = queue.pop_front() {
            explored += 1;
            if explored > max_nodes_explored {
                break;
            }
            if depth >= max_d {
                continue;
            }
            let neighbors = store_into(
                self.store
                    .get_swee_neighbors(node.clone(), dir.clone())
                    .await,
            )?;
            for entry in neighbors {
                let edge = entry.get("edge").cloned().unwrap_or(Value::Null);
                if !edge_types.is_empty() {
                    let et = edge
                        .get("edge_type")
                        .and_then(|v| v.as_str())
                        .unwrap_or("");
                    if !edge_types.iter().any(|t| t == et) {
                        continue;
                    }
                }
                let other_id = match entry
                    .pointer("/other_node/id")
                    .and_then(|v| v.as_str())
                {
                    Some(s) => s.to_string(),
                    None => continue,
                };
                if visited.contains(&other_id) {
                    continue;
                }
                visited.insert(other_id.clone());
                parent.insert(other_id.clone(), (node.clone(), edge));
                if other_id == to {
                    found = true;
                    break;
                }
                queue.push_back((other_id, depth + 1));
            }
            if found {
                break;
            }
        }

        if !found {
            return Ok(ok(PathOutput {
                from,
                to,
                found: false,
                length: 0,
                nodes: vec![],
                edges: vec![],
                explored,
            })?);
        }

        // Reconstruct path by walking `parent` from `to` back to `from`.
        let mut rev_nodes: Vec<String> = vec![to.clone()];
        let mut rev_edges: Vec<Value> = Vec::new();
        let mut cur = to.clone();
        while let Some((prev, edge)) = parent.get(&cur).cloned() {
            rev_nodes.push(prev.clone());
            rev_edges.push(edge);
            if prev == from {
                break;
            }
            cur = prev;
        }
        rev_nodes.reverse();
        rev_edges.reverse();

        // Hydrate each node on the path.
        let mut node_payloads: Vec<Value> = Vec::with_capacity(rev_nodes.len());
        for nid in &rev_nodes {
            let raw = store_into(self.store.get_swee_node(nid.clone()).await)?;
            node_payloads.push(raw.unwrap_or_else(|| json!({ "id": nid })));
        }

        Ok(ok(PathOutput {
            from,
            to,
            found: true,
            length: rev_edges.len(),
            nodes: node_payloads,
            edges: rev_edges,
            explored,
        })?)
    }

    /// Blast-radius from a node.
    #[tool(
        description = "Compute the blast-radius from a SWEE node. `direction` is `downstream` (default — what this node transitively affects), `upstream` (what affects this), or `both`. Returns the set of reached nodes and the connecting edges. `depth` is capped at 3 to avoid exponential blow-ups."
    )]
    #[instrument(level = "debug", skip(self))]
    pub async fn impact(
        &self,
        Parameters(ImpactInput {
            id,
            direction,
            depth,
            max_nodes,
        }): Parameters<ImpactInput>,
    ) -> Result<CallToolResult, McpError> {
        if depth == 0 || depth > 3 {
            return Err(ToolError::InvalidInput("depth must be 1..=3".into()).into());
        }
        if max_nodes == 0 || max_nodes > 500 {
            return Err(ToolError::InvalidInput(format!(
                "max_nodes must be 1..=500, got {max_nodes}"
            ))
            .into());
        }
        let dir = match direction.as_str() {
            "upstream" => "in".to_string(),
            "downstream" => "out".to_string(),
            "both" => "both".to_string(),
            other => {
                return Err(ToolError::InvalidInput(format!(
                    "direction must be upstream|downstream|both, got `{other}`"
                ))
                .into());
            }
        };

        let _ = store_into(self.store.get_swee_node(id.clone()).await)?
            .ok_or_else(|| ToolError::NotFound(format!("node {id}")))?;

        let mut visited: HashSet<String> = HashSet::new();
        visited.insert(id.clone());
        let mut frontier: Vec<String> = vec![id.clone()];
        let mut edges_out: Vec<Value> = Vec::new();
        let mut truncated = false;

        for _ in 0..depth {
            if visited.len() >= max_nodes as usize {
                truncated = true;
                break;
            }
            let mut next: Vec<String> = Vec::new();
            for node in &frontier {
                let neighbors =
                    store_into(self.store.get_swee_neighbors(node.clone(), dir.clone()).await)?;
                for entry in neighbors {
                    let edge = entry.get("edge").cloned().unwrap_or(Value::Null);
                    edges_out.push(edge);
                    if let Some(other_id) = entry
                        .pointer("/other_node/id")
                        .and_then(|v| v.as_str())
                        .map(String::from)
                    {
                        if !visited.contains(&other_id) {
                            visited.insert(other_id.clone());
                            next.push(other_id);
                            if visited.len() >= max_nodes as usize {
                                truncated = true;
                            }
                        }
                    }
                }
            }
            if next.is_empty() {
                break;
            }
            frontier = next;
        }

        // Hydrate reached nodes (excluding the center).
        let mut node_payloads: Vec<Value> = Vec::new();
        for nid in visited.iter() {
            if nid == &id {
                continue;
            }
            let raw = store_into(self.store.get_swee_node(nid.clone()).await)?;
            node_payloads.push(raw.unwrap_or_else(|| json!({ "id": nid })));
        }

        Ok(ok(ImpactOutput {
            id,
            direction,
            depth,
            reached: node_payloads.len(),
            truncated,
            nodes: node_payloads,
            edges: edges_out,
        })?)
    }

    /// Coverage analysis: what do these tests cover?
    #[tool(
        description = "Coverage analysis: for the given `test_ids`, BFS-walk the graph in the `in` direction and bucket reached nodes by type. Returns the lists of covered requirements and specifications, plus a list of *uncovered* requirements (gap analysis). Destructive hint: false (read-only)."
    )]
    #[instrument(level = "debug", skip(self))]
    pub async fn coverage(
        &self,
        Parameters(CoverageInput {
            test_ids,
            max_depth,
            max_nodes,
        }): Parameters<CoverageInput>,
    ) -> Result<CallToolResult, McpError> {
        if max_depth == 0 || max_depth > 6 {
            return Err(ToolError::InvalidInput(
                "max_depth must be 1..=6".into(),
            )
            .into());
        }
        if max_nodes == 0 || max_nodes > 500 {
            return Err(ToolError::InvalidInput(format!(
                "max_nodes must be 1..=500, got {max_nodes}"
            ))
            .into());
        }
        if test_ids.is_empty() {
            return Err(ToolError::InvalidInput(
                "test_ids must contain at least one id".into(),
            )
            .into());
        }

        let mut covered_reqs: HashSet<String> = HashSet::new();
        let mut covered_specs: HashSet<String> = HashSet::new();
        let mut total_edges = 0usize;
        let mut truncated = false;

        for test_id in &test_ids {
            // Verify each test exists.
            let _ = store_into(self.store.get_swee_node(test_id.clone()).await)?
                .ok_or_else(|| ToolError::NotFound(format!("test node {test_id}")))?;

            let mut visited: HashSet<String> = HashSet::new();
            visited.insert(test_id.clone());
            let mut frontier: Vec<String> = vec![test_id.clone()];
            for _ in 0..max_depth {
                if covered_reqs.len() + covered_specs.len() >= max_nodes as usize {
                    truncated = true;
                    break;
                }
                let mut next: Vec<String> = Vec::new();
                for node in &frontier {
                    let neighbors = store_into(
                        self.store
                            .get_swee_neighbors(node.clone(), "in".to_string())
                            .await,
                    )?;
                    for entry in neighbors {
                        total_edges += 1;
                        let other_id = match entry
                            .pointer("/other_node/id")
                            .and_then(|v| v.as_str())
                        {
                            Some(s) => s.to_string(),
                            None => continue,
                        };
                        let other_type = entry
                            .pointer("/other_node/node_type")
                            .and_then(|v| v.as_str())
                            .unwrap_or("");
                        match other_type {
                            "requirement" => {
                                covered_reqs.insert(other_id.clone());
                            }
                            "specification" => {
                                covered_specs.insert(other_id.clone());
                            }
                            _ => {}
                        }
                        if !visited.contains(&other_id) {
                            visited.insert(other_id.clone());
                            next.push(other_id);
                            if covered_reqs.len() + covered_specs.len()
                                >= max_nodes as usize
                            {
                                truncated = true;
                            }
                        }
                    }
                }
                if next.is_empty() {
                    break;
                }
                frontier = next;
            }
        }

        // Hydrate the IDs into full nodes.
        let mut covered_req_nodes: Vec<Value> = Vec::new();
        for id in &covered_reqs {
            let raw = store_into(self.store.get_swee_node(id.clone()).await)?;
            covered_req_nodes.push(raw.unwrap_or_else(|| json!({ "id": id })));
        }
        let mut covered_spec_nodes: Vec<Value> = Vec::new();
        for id in &covered_specs {
            let raw = store_into(self.store.get_swee_node(id.clone()).await)?;
            covered_spec_nodes.push(raw.unwrap_or_else(|| json!({ "id": id })));
        }

        // Compute uncovered requirements: every requirement, minus the
        // ones we covered. This is a generous BFS so we don't need to
        // trust the caller's test set.
        let all_requirements =
            store_into(self.store.list_swee_nodes(Some("requirement".to_string())).await)?;
        let mut uncovered: Vec<Value> = Vec::new();
        for row in all_requirements {
            if let Some(id) = row.get("id").and_then(|v| v.as_str()) {
                if !covered_reqs.contains(id) {
                    uncovered.push(node_from_value(id, &row).map(|n| {
                        serde_json::to_value(n).unwrap_or(Value::Null)
                    })
                    .unwrap_or(Value::Null));
                }
            }
        }

        Ok(ok(CoverageOutput {
            test_ids,
            covered_requirements: covered_req_nodes,
            covered_specifications: covered_spec_nodes,
            uncovered_requirements: uncovered,
            total_edges_walked: total_edges,
            truncated,
        })?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn node_type_strings_have_30_entries() {
        assert_eq!(all_node_type_strings().len(), 30);
    }

    #[test]
    fn edge_type_strings_have_32_entries() {
        assert_eq!(all_edge_type_strings().len(), 32);
    }

    #[test]
    fn node_type_strings_are_unique() {
        let v = all_node_type_strings();
        let unique: HashSet<_> = v.iter().copied().collect();
        assert_eq!(unique.len(), v.len());
    }

    #[test]
    fn edge_type_strings_are_unique() {
        let v = all_edge_type_strings();
        let unique: HashSet<_> = v.iter().copied().collect();
        assert_eq!(unique.len(), v.len());
    }

    #[test]
    fn canonical_lists_match_well_known_types() {
        assert!(all_node_type_strings().contains(&"requirement"));
        assert!(all_node_type_strings().contains(&"specification"));
        assert!(all_node_type_strings().contains(&"source_file"));
        assert!(all_edge_type_strings().contains(&"tests"));
        assert!(all_edge_type_strings().contains(&"covers"));
        assert!(all_edge_type_strings().contains(&"depends_on"));
    }

    #[test]
    fn direction_defaults_are_stable() {
        assert_eq!(default_neighbors_direction(), "both");
        assert_eq!(default_path_direction(), "out");
        assert_eq!(default_impact_direction(), "downstream");
        assert_eq!(default_neighbors_limit(), 100);
        assert_eq!(default_path_max_depth(), 6);
        assert_eq!(default_impact_depth(), 2);
        assert_eq!(default_impact_limit(), 200);
        assert_eq!(default_coverage_depth(), 4);
        assert_eq!(default_coverage_limit(), 200);
    }
}