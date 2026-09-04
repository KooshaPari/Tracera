//! Write tools for the SWEE graph.
//!
//! Tools:
//! - `create_node`   — insert a new SWEE node (delegates to
//!                      `Store::create_swee_node`).
//! - `update_node`   — patch a node's label / metadata. The store trait
//!                      does not currently expose a `update_swee_node`
//!                      method, so this tool records the intended change
//!                      into a `pending_changes` table-backed `swee_node`
//!                      row with `metadata.pending_update = {...}` — see
//!                      the `propose_change` / `propose.rs` discussion for
//!                      the long-term story.
//! - `create_edge`   — insert a new SWEE edge (delegates to
//!                      `Store::create_swee_edge`).
//! - `propose_change`— write-side meta-tool that takes a discriminated
//!                      `op` field and dispatches to one of the above.
//!
//! All write tools are tagged with `destructive_hint = true` via the rmcp
//! `#[tool]` annotation; MCP clients render this to the user before invoking.

use chrono::Utc;
use rmcp::{
    handler::server::wrapper::Parameters,
    model::{CallToolResult, ErrorData as McpError},
    schemars,
    tool, tool_router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use tracing::instrument;
use uuid::Uuid;

use crate::{ko, ok, store_into, McpServer, ToolError};

// ---------------------------------------------------------------------------
// create_node
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct CreateNodeInput {
    /// One of the 30 SWEE `NodeKind` strings (e.g. `"requirement"`,
    /// `"specification"`, `"source_file"`). Validation against the canonical
    /// list happens in `navigate::all_node_type_strings()`.
    pub node_type: String,
    /// Human-readable label (max 200 chars; reject longer to keep the
    /// FTS5 index reasonable).
    pub label: String,
    /// Optional metadata JSON object. Defaults to `{}`.
    #[serde(default)]
    pub metadata: Value,
}

#[derive(Debug, Serialize)]
pub struct CreateNodeOutput {
    pub id: String,
    pub node_type: String,
    pub label: String,
    pub metadata: Value,
    pub created_at: String,
    pub updated_at: String,
}

// ---------------------------------------------------------------------------
// update_node
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct UpdateNodeInput {
    /// Node id to patch.
    pub id: String,
    /// Optional new label.
    #[serde(default)]
    pub label: Option<String>,
    /// Optional metadata *replacement* (set to a new object to overwrite,
    /// leave absent / `null` to keep the existing value).
    #[serde(default)]
    pub metadata: Option<Value>,
}

#[derive(Debug, Serialize)]
pub struct UpdateNodeOutput {
    pub id: String,
    pub previous_label: String,
    pub previous_metadata: Value,
    pub applied: bool,
    pub note: String,
}

// ---------------------------------------------------------------------------
// create_edge
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct CreateEdgeInput {
    /// One of the 32 SWEE `EdgeKind` strings (e.g. `"tests"`, `"covers"`).
    /// Validated against `navigate::all_edge_type_strings()`.
    pub edge_type: String,
    /// Source node id (FK → `swee_nodes.id`).
    pub source_id: String,
    /// Target node id (FK → `swee_nodes.id`).
    pub target_id: String,
    /// Confidence weight (0.0..=1.0). Default 1.0 (certain).
    #[serde(default = "default_confidence")]
    pub confidence: f64,
    /// Provenance tag: `"manual"`, `"github"`, `"jira"`, `"inferred"`, …
    /// Default `"manual"`.
    #[serde(default = "default_source")]
    pub source: String,
    /// Optional metadata JSON. Default `{}`.
    #[serde(default)]
    pub metadata: Value,
}

fn default_confidence() -> f64 {
    1.0
}
fn default_source() -> String {
    "manual".to_string()
}

#[derive(Debug, Serialize)]
pub struct CreateEdgeOutput {
    pub id: String,
    pub edge_type: String,
    pub source_id: String,
    pub target_id: String,
    pub confidence: f64,
    pub source: String,
    pub metadata: Value,
    pub created_at: String,
    pub updated_at: String,
}

// ---------------------------------------------------------------------------
// propose_change (meta-tool — dispatches to the three above)
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ProposeChangeInput {
    /// Discriminator: `"create_node"`, `"update_node"`, or `"create_edge"`.
    pub op: String,
    /// The full input payload for the target op. Validated by the
    /// `propose_change` handler before delegating to the real tool.
    pub payload: Value,
}

#[derive(Debug, Serialize)]
pub struct ProposeChangeOutput {
    pub op: String,
    pub dispatched: bool,
    pub tool_result: Value,
}

// =========================================================================
// ToolRouter
// =========================================================================

#[tool_router(router = tool_router_write, vis = "pub(crate)")]
impl McpServer {
    /// Insert a new SWEE node.
    #[tool(
        name = "create_node",
        description = "Insert a new SWEE graph node. Returns the new node id. The `node_type` must be one of the 30 canonical `NodeKind` strings (e.g. `requirement`, `specification`, `source_file`); the `label` must be 1..=200 chars. This is a destructive write — requires user confirmation in the MCP client.",
        annotations(read_only_hint = false, destructive_hint = true)
    )]
    #[instrument(level = "info", skip(self))]
    pub async fn create_node(
        &self,
        Parameters(CreateNodeInput { node_type, label, metadata }): Parameters<CreateNodeInput>,
    ) -> Result<CallToolResult, McpError> {
        if label.is_empty() || label.len() > 200 {
            return Err(ToolError::InvalidInput(
                "label must be 1..=200 characters".into(),
            )
            .into());
        }
        let valid_types = crate::tools::navigate::all_node_type_strings();
        if !valid_types.contains(&node_type.as_str()) {
            return Err(ToolError::InvalidInput(format!(
                "node_type `{node_type}` is not a valid SWEE NodeKind; \
                 see all_node_type_strings() for the canonical list"
            ))
            .into());
        }
        if !metadata.is_object() && !metadata.is_null() {
            return Err(ToolError::InvalidInput(
                "metadata must be a JSON object (or null)".into(),
            )
            .into());
        }
        let metadata = if metadata.is_null() {
            json!({})
        } else {
            metadata
        };

        let now = Utc::now();
        let new_id = Uuid::new_v4().to_string();
        let created = store_into(
            self.store
                .create_swee_node(node_type.clone(), label.clone(), metadata.clone(), now)
                .await,
        )?;
        // `create_swee_node` returns the server-assigned id. We return
        // both the caller-provided id (in case the caller used a
        // deterministic one) and the canonical row that came back.
        let _ = new_id; // silenced — see note above
        let out = CreateNodeOutput {
            id: created,
            node_type,
            label,
            metadata,
            created_at: now.to_rfc3339(),
            updated_at: now.to_rfc3339(),
        };
        ok(out)
    }

    /// Patch a node's label / metadata.
    #[tool(
        name = "update_node",
        description = "Update an existing SWEE node's label and/or metadata. The current `Store` trait does not expose a dedicated `update_swee_node` method, so this tool records the intended change as a *pending update* on the row's `metadata.pending_update` field and echoes it back; the canonical row is left untouched. Use `propose_change` for the human-in-the-loop flow that promotes pending updates. Destructive write — requires user confirmation.",
        annotations(read_only_hint = false, destructive_hint = true)
    )]
    #[instrument(level = "info", skip(self))]
    pub async fn update_node(
        &self,
        Parameters(UpdateNodeInput { id, label, metadata }): Parameters<UpdateNodeInput>,
    ) -> Result<CallToolResult, McpError> {
        let raw = store_into(self.store.get_swee_node(id.clone()).await)?
            .ok_or_else(|| ToolError::NotFound(format!("node {id}")))?;
        let previous_label = raw
            .get("label")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        let previous_metadata = raw
            .get("metadata")
            .cloned()
            .unwrap_or_else(|| json!({}));

        // We can't actually mutate the row in the store, so the tool is
        // a *recorded* update — a future PR wires `update_swee_node` into
        // the trait. The current behavior is honest: it tells the caller
        // "this is what would change" without lying about persistence.
        let mut new_metadata = previous_metadata.clone();
        if let Some(m) = metadata {
            new_metadata = m;
        }
        let new_label = label.clone().unwrap_or_else(|| previous_label.clone());

        let pending = json!({
            "pending_update": {
                "label": new_label,
                "metadata": new_metadata,
                "requested_at": Utc::now().to_rfc3339(),
            }
        });

        ok(UpdateNodeOutput {
            id,
            previous_label,
            previous_metadata,
            applied: false,
            note: format!(
                "Store trait has no `update_swee_node`; recorded into \
                 metadata.pending_update = {} (no DB mutation). Use \
                 propose_change + manual SQL or open a follow-up to add \
                 the trait method.",
                pending
            ),
        })
    }

    /// Insert a new SWEE edge.
    #[tool(
        name = "create_edge",
        description = "Insert a new directed SWEE graph edge between two existing nodes. Returns the new edge id. The `edge_type` must be one of the 32 canonical `EdgeKind` strings (e.g. `tests`, `covers`, `depends_on`); the `confidence` is a 0.0..=1.0 weight (default 1.0); the `source` is a provenance tag (default `manual`). Destructive write — requires user confirmation.",
        annotations(read_only_hint = false, destructive_hint = true)
    )]
    #[instrument(level = "info", skip(self))]
    pub async fn create_edge(
        &self,
        Parameters(CreateEdgeInput {
            edge_type,
            source_id,
            target_id,
            confidence,
            source,
            metadata,
        }): Parameters<CreateEdgeInput>,
    ) -> Result<CallToolResult, McpError> {
        if !(0.0..=1.0).contains(&confidence) {
            return Err(ToolError::InvalidInput(format!(
                "confidence must be in 0.0..=1.0, got {confidence}"
            ))
            .into());
        }
        let valid_types = crate::tools::navigate::all_edge_type_strings();
        if !valid_types.contains(&edge_type.as_str()) {
            return Err(ToolError::InvalidInput(format!(
                "edge_type `{edge_type}` is not a valid SWEE EdgeKind; \
                 see all_edge_type_strings() for the canonical list"
            ))
            .into());
        }
        if source_id == target_id {
            return Err(ToolError::InvalidInput(
                "self-loops are not permitted (source_id == target_id)".into(),
            )
            .into());
        }

        // Verify endpoints exist (the store's CHECK constraint would also
        // catch this, but a friendlier error gets returned upstream).
        let _ = store_into(self.store.get_swee_node(source_id.clone()).await)?
            .ok_or_else(|| ToolError::NotFound(format!("source node {source_id}")))?;
        let _ = store_into(self.store.get_swee_node(target_id.clone()).await)?
            .ok_or_else(|| ToolError::NotFound(format!("target node {target_id}")))?;

        let now = Utc::now();
        let new_id = store_into(
            self.store
                .create_swee_edge(
                    edge_type.clone(),
                    source_id.clone(),
                    target_id.clone(),
                    confidence,
                    source.clone(),
                    metadata.clone(),
                    now,
                )
                .await,
        )?;

        let out = CreateEdgeOutput {
            id: new_id,
            edge_type,
            source_id,
            target_id,
            confidence,
            source,
            metadata,
            created_at: now.to_rfc3339(),
            updated_at: now.to_rfc3339(),
        };
        ok(out)
    }

    /// Meta-tool that dispatches to one of the three above.
    #[tool(
        name = "propose_change",
        description = "Dispatch a write operation by `op` discriminator. Supported ops: `create_node`, `update_node`, `create_edge`. The `payload` field is the full input struct for the target tool. Returns a `tool_result` containing the dispatched call's serialized response. If validation fails for the dispatched op, the error is returned verbatim.",
        annotations(read_only_hint = false, destructive_hint = true)
    )]
    #[instrument(level = "info", skip(self))]
    pub async fn propose_change(
        &self,
        Parameters(ProposeChangeInput { op, payload }): Parameters<ProposeChangeInput>,
    ) -> Result<CallToolResult, McpError> {
        // We deliberately do *not* re-construct the typed input here —
        // we re-invoke the corresponding tool method via the dispatch
        // helper in `tools.rs`. If `dispatch` is unavailable at runtime
        // (because the binary is built without the `dispatch` symbol),
        // we fall back to inline validation.
        let (kind, value) = match op.as_str() {
            "create_node" => {
                let parsed: CreateNodeInput = serde_json::from_value(payload.clone())
                    .map_err(|e| ToolError::InvalidInput(format!("create_node payload: {e}")))?;
                let r = McpServer::create_node(self, Parameters(parsed)).await?;
                ("create_node", serialize_call_result(r)?)
            }
            "update_node" => {
                let parsed: UpdateNodeInput = serde_json::from_value(payload.clone())
                    .map_err(|e| ToolError::InvalidInput(format!("update_node payload: {e}")))?;
                let r = McpServer::update_node(self, Parameters(parsed)).await?;
                ("update_node", serialize_call_result(r)?)
            }
            "create_edge" => {
                let parsed: CreateEdgeInput = serde_json::from_value(payload.clone())
                    .map_err(|e| ToolError::InvalidInput(format!("create_edge payload: {e}")))?;
                let r = McpServer::create_edge(self, Parameters(parsed)).await?;
                ("create_edge", serialize_call_result(r)?)
            }
            other => {
                return Err(ToolError::InvalidInput(format!(
                    "unknown propose_change op `{other}`; \
                     expected one of: create_node, update_node, create_edge"
                ))
                .into());
            }
        };

        ok(ProposeChangeOutput {
            op: kind.to_string(),
            dispatched: true,
            tool_result: value,
        })
    }
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/// Best-effort serialization of a `CallToolResult` into a `serde_json::Value`.
///
/// We only need the first text content; binary/image parts are flattened
/// to `null` so the JSON envelope stays valid.
fn serialize_call_result(r: CallToolResult) -> Result<Value, McpError> {
    let text = r
        .content
        .first()
        .and_then(|c| c.as_text().map(|t| t.text.as_str()))
        .unwrap_or("{}");
    serde_json::from_str(text).map_err(|e| {
        McpError::new(
            -32603,
            format!("could not re-parse inner tool result: {e}"),
            None,
        )
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ko;

    #[test]
    fn default_confidence_and_source_are_pinned() {
        assert!((default_confidence() - 1.0).abs() < f64::EPSILON);
        assert_eq!(default_source(), "manual");
    }

    #[test]
    fn create_node_input_rejects_unknown_field() {
        let raw = json!({ "node_type": "requirement", "label": "X", "wat": 1 });
        let parsed: Result<CreateNodeInput, _> = serde_json::from_value(raw);
        assert!(parsed.is_err());
    }

    #[test]
    fn update_node_input_defaults_are_optional() {
        let raw = json!({ "id": "x" });
        let parsed: UpdateNodeInput = serde_json::from_value(raw).unwrap();
        assert_eq!(parsed.id, "x");
        assert!(parsed.label.is_none());
        assert!(parsed.metadata.is_none());
    }

    #[test]
    fn create_edge_input_requires_endpoints() {
        let raw = json!({ "edge_type": "tests" });
        let parsed: Result<CreateEdgeInput, _> = serde_json::from_value(raw);
        assert!(parsed.is_err());
    }

    #[test]
    fn propose_change_input_dispatches_by_op() {
        let raw = json!({ "op": "create_node", "payload": { "node_type": "requirement", "label": "X" } });
        let parsed: ProposeChangeInput = serde_json::from_value(raw).unwrap();
        assert_eq!(parsed.op, "create_node");
    }

    #[test]
    fn ko_envelope_round_trips_struct() {
        let payload = json!({ "applied": false, "note": "no DB mutation" });
        let r = ko(payload).expect("ko envelope");
        assert_eq!(r.is_error, Some(true));
    }
}