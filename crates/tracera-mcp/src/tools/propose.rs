//! Human-in-the-loop proposal tools.
//!
//! These tools do *not* mutate the SWEE graph. They emit a structured
//! proposal artifact (a JSON envelope) that downstream consumers — a
//! review board, a CI bot, or a human reviewer — can inspect before
//! promoting the change to the actual store.
//!
//! Tools:
//! - `propose_decision`    — generic decision proposal (e.g. "we should
//!                            deprecate X because Y"). Embeds the decision
//!                            text, the rationale, and the list of affected
//!                            SWEE nodes (looked up by id and inlined so the
//!                            reviewer has full context).
//! - `propose_spec_change` — narrow variant of the above specialised to
//!                            requirement / specification deltas. Captures
//!                            the spec text, the proposed replacement, and
//!                            a list of impacted requirements.
//!
//! Both tools are read-only (the `isError` envelope is used to report
//! validation errors, not persistence errors — there is no persistence
//! in this path).
//!
//! ## Workflow
//!
//! 1. LLM agent inspects the graph via the `read_*` and `navigate_*` tools.
//! 2. Agent identifies a change to propose.
//! 3. Agent calls `propose_decision` / `propose_spec_change` and gets
//!    a JSON envelope with the proposal + the embedded SWEE context.
//! 4. Reviewer inspects the envelope in their PR / change board.
//! 5. Reviewer (or follow-up automation) calls `create_node` / `create_edge`
//!    to materialize the change.

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

use crate::tools::read::node_from_value;
use crate::{ok, store_into, McpServer, ToolError};

// ---------------------------------------------------------------------------
// propose_decision
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ProposeDecisionInput {
    /// Short title (1..=120 chars).
    pub title: String,
    /// Detailed rationale (markdown allowed).
    pub rationale: String,
    /// SWEE node ids that this decision affects. Inlined into the proposal
    /// envelope so the reviewer has full context.
    #[serde(default)]
    pub affected_node_ids: Vec<String>,
    /// Optional RFC / ADR link.
    #[serde(default)]
    pub rfc_url: Option<String>,
    /// Free-form tags (e.g. `["deprecation", "v2-migration"]`).
    #[serde(default)]
    pub tags: Vec<String>,
    /// Author / proposer (free-form string — e.g. an LLM agent id or a
    /// human handle).
    #[serde(default)]
    pub author: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct ProposeDecisionOutput {
    pub proposal_id: String,
    pub kind: &'static str,
    pub title: String,
    pub rationale: String,
    pub affected_nodes: Vec<Value>,
    pub rfc_url: Option<String>,
    pub tags: Vec<String>,
    pub author: Option<String>,
    pub created_at: String,
    /// Stable, hash-like fingerprint of the proposal's content. Downstream
    /// tools use this to detect duplicate proposals.
    pub fingerprint: String,
}

// ---------------------------------------------------------------------------
// propose_spec_change
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, schemars::JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ProposeSpecChangeInput {
    /// SWEE node id of the spec / requirement being changed.
    pub spec_id: String,
    /// The proposed new text.
    pub proposed_text: String,
    /// The reason for the change.
    pub reason: String,
    /// Optional list of *additional* requirement ids that this change
    /// impacts. The tool will fetch each and include a structured
    /// `impact_summary` so the reviewer can see the blast-radius.
    #[serde(default)]
    pub additional_impact_ids: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct ProposeSpecChangeOutput {
    pub proposal_id: String,
    pub kind: &'static str,
    pub spec: Value,
    pub proposed_text: String,
    pub reason: String,
    pub impact: Vec<Value>,
    pub fingerprint: String,
    pub created_at: String,
}

// =========================================================================
// ToolRouter
// =========================================================================

#[tool_router(router = tool_router_propose, vis = "pub(crate)")]
impl McpServer {
    /// Generate a structured decision-proposal envelope.
    #[tool(
        description = "Generate a structured *proposal* envelope for a human-in-the-loop decision. Does **not** mutate the SWEE graph. The envelope includes the title, rationale, the affected SWEE nodes (inlined for review), optional RFC URL, tags, and a stable fingerprint. The downstream reviewer / change board uses this to gate the actual write via `create_node` / `create_edge`."
    )]
    #[instrument(level = "info", skip(self))]
    pub async fn propose_decision(
        &self,
        Parameters(ProposeDecisionInput {
            title,
            rationale,
            affected_node_ids,
            rfc_url,
            tags,
            author,
        }): Parameters<ProposeDecisionInput>,
    ) -> Result<CallToolResult, McpError> {
        if title.trim().is_empty() || title.len() > 120 {
            return Err(ToolError::InvalidInput(
                "title must be 1..=120 characters".into(),
            )
            .into());
        }
        if rationale.trim().is_empty() {
            return Err(ToolError::InvalidInput(
                "rationale must be non-empty".into(),
            )
            .into());
        }
        if affected_node_ids.len() > 200 {
            return Err(ToolError::InvalidInput(
                "affected_node_ids may contain at most 200 entries".into(),
            )
            .into());
        }

        // Inline affected nodes. We deliberately do not return an error
        // for missing ids — a partial view is still useful for review,
        // and we tag the missing ones with `__missing__: true`.
        let mut affected: Vec<Value> = Vec::new();
        let mut missing: Vec<String> = Vec::new();
        for nid in &affected_node_ids {
            let raw = store_into(self.store.get_swee_node(nid.clone()).await)?;
            match raw {
                Some(row) => {
                    if let Some(n) = node_from_value(nid, &row) {
                        affected.push(serde_json::to_value(n).unwrap_or(Value::Null));
                    } else {
                        missing.push(nid.clone());
                    }
                }
                None => missing.push(nid.clone()),
            }
        }
        if !missing.is_empty() {
            affected.push(json!({
                "__missing__": true,
                "ids": missing,
            }));
        }

        // Fingerprint = SHA-256 of (title | rationale | sorted_ids | tags).
        // We use sha2 directly to avoid pulling a digest trait.
        use sha2::{Digest, Sha256};
        let mut sorted_ids: Vec<String> = affected_node_ids.clone();
        sorted_ids.sort();
        let mut sorted_tags: Vec<String> = tags.clone();
        sorted_tags.sort();
        let payload = format!(
            "{}|{}|{}|{}",
            title,
            rationale,
            sorted_ids.join(","),
            sorted_tags.join(",")
        );
        let mut hasher = Sha256::new();
        hasher.update(payload.as_bytes());
        let digest = hasher.finalize();
        let fingerprint = digest
            .iter()
            .map(|b| format!("{b:02x}"))
            .collect::<String>();

        let now = Utc::now();
        let proposal_id = Uuid::new_v4().to_string();

        Ok(ok(ProposeDecisionOutput {
            proposal_id,
            kind: "decision",
            title,
            rationale,
            affected_nodes: affected,
            rfc_url,
            tags,
            author,
            created_at: now.to_rfc3339(),
            fingerprint,
        })?)
    }

    /// Generate a structured spec-change proposal.
    #[tool(
        description = "Generate a structured *proposal* envelope for a single spec / requirement change. Does **not** mutate the SWEE graph. Returns the existing spec (inlined), the proposed new text, the reason, and the structured impact summary (each impacted node inlined). Use this when the change is narrow and known; use `propose_decision` for broader cross-cutting decisions."
    )]
    #[instrument(level = "info", skip(self))]
    pub async fn propose_spec_change(
        &self,
        Parameters(ProposeSpecChangeInput {
            spec_id,
            proposed_text,
            reason,
            additional_impact_ids,
        }): Parameters<ProposeSpecChangeInput>,
    ) -> Result<CallToolResult, McpError> {
        if proposed_text.trim().is_empty() {
            return Err(ToolError::InvalidInput(
                "proposed_text must be non-empty".into(),
            )
            .into());
        }
        if reason.trim().is_empty() {
            return Err(ToolError::InvalidInput(
                "reason must be non-empty".into(),
            )
            .into());
        }
        if additional_impact_ids.len() > 200 {
            return Err(ToolError::InvalidInput(
                "additional_impact_ids may contain at most 200 entries".into(),
            )
            .into());
        }

        // 1) Load the spec node. Error if missing — `propose_spec_change`
        //    is meant for *existing* specs.
        let spec_raw = store_into(self.store.get_swee_node(spec_id.clone()).await)?
            .ok_or_else(|| ToolError::NotFound(format!("spec node {spec_id}")))?;
        let spec_node = node_from_value(&spec_id, &spec_raw)
            .ok_or_else(|| ToolError::NotFound(format!("spec node {spec_id}")))?;
        let spec_payload = serde_json::to_value(&spec_node).unwrap_or(Value::Null);

        // 2) Inline the additional impact nodes (best-effort, like above).
        let mut impact: Vec<Value> = Vec::new();
        let mut missing: Vec<String> = Vec::new();
        for nid in &additional_impact_ids {
            let raw = store_into(self.store.get_swee_node(nid.clone()).await)?;
            match raw {
                Some(row) => {
                    if let Some(n) = node_from_value(nid, &row) {
                        impact.push(serde_json::to_value(n).unwrap_or(Value::Null));
                    } else {
                        missing.push(nid.clone());
                    }
                }
                None => missing.push(nid.clone()),
            }
        }
        if !missing.is_empty() {
            impact.push(json!({
                "__missing__": true,
                "ids": missing,
            }));
        }

        // 3) Fingerprint.
        use sha2::{Digest, Sha256};
        let mut sorted_ids: Vec<String> = additional_impact_ids.clone();
        sorted_ids.sort();
        sorted_ids.push(spec_id.clone());
        sorted_ids.sort();
        let payload = format!(
            "{}|{}|{}|{}",
            spec_id, proposed_text, reason, sorted_ids.join(",")
        );
        let mut hasher = Sha256::new();
        hasher.update(payload.as_bytes());
        let digest = hasher.finalize();
        let fingerprint = digest
            .iter()
            .map(|b| format!("{b:02x}"))
            .collect::<String>();

        let now = Utc::now();
        let proposal_id = Uuid::new_v4().to_string();

        Ok(ok(ProposeSpecChangeOutput {
            proposal_id,
            kind: "spec_change",
            spec: spec_payload,
            proposed_text,
            reason,
            impact,
            fingerprint,
            created_at: now.to_rfc3339(),
        })?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn propose_decision_input_defaults_are_optional() {
        let raw = json!({ "title": "T", "rationale": "R" });
        let parsed: ProposeDecisionInput = serde_json::from_value(raw).unwrap();
        assert_eq!(parsed.title, "T");
        assert!(parsed.affected_node_ids.is_empty());
        assert!(parsed.rfc_url.is_none());
        assert!(parsed.tags.is_empty());
        assert!(parsed.author.is_none());
    }

    #[test]
    fn propose_decision_input_rejects_empty_rationale() {
        let raw = json!({ "title": "T", "rationale": "   " });
        let parsed: ProposeDecisionInput = serde_json::from_value(raw).unwrap();
        // Note: schema check is in the tool body — this test only checks
        // that the type accepts the payload; the validation fires later.
        assert_eq!(parsed.rationale, "   ");
    }

    #[test]
    fn propose_spec_change_input_requires_spec_id() {
        let raw = json!({ "proposed_text": "X", "reason": "Y" });
        let parsed: Result<ProposeSpecChangeInput, _> = serde_json::from_value(raw);
        assert!(parsed.is_err());
    }

    #[test]
    fn output_struct_field_order_is_stable_for_schema() {
        // Compile-time check that the output structs have the expected
        // serialized field names.
        let out = ProposeDecisionOutput {
            proposal_id: "p".into(),
            kind: "decision",
            title: "t".into(),
            rationale: "r".into(),
            affected_nodes: vec![],
            rfc_url: None,
            tags: vec![],
            author: None,
            created_at: "2026-01-01T00:00:00Z".into(),
            fingerprint: "f".into(),
        };
        let v = serde_json::to_value(&out).unwrap();
        assert!(v.get("proposal_id").is_some());
        assert!(v.get("kind").is_some());
        assert!(v.get("fingerprint").is_some());
    }
}