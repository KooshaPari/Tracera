//! WorkOS Audit Log ingest → graph events.
//!
//! WorkOS's audit log (`audit.log.created`) carries actor, action, target and
//! context metadata. We normalize it into the same shape as
//! [`crate::sync::ProvisionOutcome`] but tagged as `event` nodes so they're
//! easy to filter out of long-lived graph queries.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::error::WorkOSResult;
use crate::sync::{GraphEdge, GraphNode, ProvisionOutcome};
use crate::webhooks::WebhookEnvelope;

/// Node-kind string for an audit event node.
pub const NODE_KIND_AUDIT_EVENT: &str = "incident"; // SWEE schema reuse — see rationale below
/// Edge-kind linking an audit event to the actor that triggered it.
pub const EDGE_KIND_AUDIT_BY: &str = "authored_by";
/// Edge-kind linking an audit event to the target it acted on.
pub const EDGE_KIND_AUDIT_ABOUT: &str = "derived_from";

/// Payload of a `audit.log.created` event (WorkOS Audit Logs API).
///
/// Only the fields we actually use are strongly-typed — the rest of the
/// payload is preserved verbatim under `metadata`.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AuditLogEvent {
    pub id: String,
    /// ISO-8601 timestamp string from WorkOS.
    pub created_at: String,
    /// Action verb (e.g. `"user.created"`, `"role.assigned"`).
    pub action: String,
    /// Actor that performed the action.
    #[serde(default)]
    pub actor: Option<AuditActor>,
    /// Target resource the action was performed on.
    #[serde(default)]
    pub target: Option<AuditTarget>,
    /// Free-form context (request id, IP, user agent, etc.).
    #[serde(default)]
    pub context: Value,
    /// Free-form metadata blob.
    #[serde(default)]
    pub metadata: Value,
    #[serde(default)]
    pub organization_id: Option<String>,
}

/// `actor` block on an audit log entry.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AuditActor {
    pub id: String,
    #[serde(rename = "type")]
    pub actor_type: String,
    #[serde(default)]
    pub name: Option<String>,
}

/// `target` block on an audit log entry.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AuditTarget {
    pub id: String,
    #[serde(rename = "type")]
    pub target_type: String,
    #[serde(default)]
    pub name: Option<String>,
}

/// What the tracera-server should do with this event.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AuditOutcome {
    pub event: GraphNode,
    pub edges: Vec<GraphEdge>,
    pub summary: String,
}

/// Convert a `audit.log.created` envelope into a graph event + edges.
pub fn ingest(envelope: &WebhookEnvelope, received_at: DateTime<Utc>) -> WorkOSResult<AuditOutcome> {
    let event: AuditLogEvent = serde_json::from_value(envelope.data.clone())?;
    let node_id = format!("workos-audit-{}", event.id);

    let mut metadata = serde_json::Map::new();
    metadata.insert("workos_id".into(), Value::String(event.id.clone()));
    metadata.insert("source".into(), Value::String("workos.audit".into()));
    metadata.insert("action".into(), Value::String(event.action.clone()));
    metadata.insert("created_at".into(), Value::String(event.created_at.clone()));
    metadata.insert(
        "received_at".into(),
        Value::String(received_at.to_rfc3339()),
    );
    if let Some(org_id) = &event.organization_id {
        metadata.insert("organization_id".into(), Value::String(org_id.clone()));
    }
    if !event.context.is_null() {
        metadata.insert("context".into(), event.context.clone());
    }
    if !event.metadata.is_null() {
        metadata.insert("payload".into(), event.metadata.clone());
    }
    let label = if let Some(target) = &event.target {
        format!("{} on {}", event.action, target.name.clone().unwrap_or_else(|| target.id.clone()))
    } else {
        event.action.clone()
    };

    let node = GraphNode {
        id: node_id.clone(),
        // SWEE doesn't have a dedicated `event` or `audit` kind; `incident` is
        // the closest semantic fit (a record of something that happened) and
        // lets us query audit events alongside real incidents in one pass.
        node_type: NODE_KIND_AUDIT_EVENT.to_string(),
        label,
        metadata: Value::Object(metadata),
        tombstone: false,
    };

    let mut edges = Vec::new();
    if let Some(actor) = &event.actor {
        edges.push(GraphEdge {
            edge_type: EDGE_KIND_AUDIT_BY.to_string(),
            source_id: node_id.clone(),
            target_id: format!("workos-{}-{}", singularize_kind(&actor.actor_type), actor.id),
            confidence: 1.0,
            source: "workos.audit".into(),
            metadata: Value::Object({
                let mut m = serde_json::Map::new();
                m.insert("actor_type".into(), Value::String(actor.actor_type.clone()));
                m
            }),
        });
    }
    if let Some(target) = &event.target {
        edges.push(GraphEdge {
            edge_type: EDGE_KIND_AUDIT_ABOUT.to_string(),
            source_id: node_id.clone(),
            target_id: format!("workos-{}-{}", singularize_kind(&target.target_type), target.id),
            confidence: 1.0,
            source: "workos.audit".into(),
            metadata: Value::Object({
                let mut m = serde_json::Map::new();
                m.insert("target_type".into(), Value::String(target.target_type.clone()));
                m
            }),
        });
    }

    let summary = format!(
        "audit {} actor={} target={}",
        event.id,
        event
            .actor
            .as_ref()
            .map(|a| a.id.as_str())
            .unwrap_or("<unknown>"),
        event
            .target
            .as_ref()
            .map(|t| t.id.as_str())
            .unwrap_or("<unknown>"),
    );

    Ok(AuditOutcome {
        event: node,
        edges,
        summary,
    })
}

/// Lower-case + singularize a WorkOS resource type for use in node ids.
///
/// Examples:
///   `"users"`    → `"user"`
///   `"User"`     → `"user"`
///   `"roles"`    → `"role"`
fn singularize_kind(kind: &str) -> String {
    let lower = kind.to_ascii_lowercase();
    if let Some(stripped) = lower.strip_suffix('s') {
        stripped.to_string()
    } else {
        lower
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::webhooks::WebhookEnvelope;
    use serde_json::json;

    fn envelope(data: Value) -> WebhookEnvelope {
        WebhookEnvelope {
            id: "evt_audit_01".into(),
            event_type: "audit.log.created".into(),
            created_at: Some("2026-09-03T12:00:00Z".parse().unwrap()),
            data,
            organization_id: Some("org_01".into()),
        }
    }

    #[test]
    fn audit_event_minimal_produces_node_no_edges() {
        let env = envelope(json!({
            "id": "audit_1",
            "created_at": "2026-09-03T12:00:00Z",
            "action": "session.created"
        }));
        let outcome = ingest(&env, Utc::now()).unwrap();
        assert_eq!(outcome.event.id, "workos-audit-audit_1");
        assert_eq!(outcome.event.node_type, NODE_KIND_AUDIT_EVENT);
        assert!(outcome.edges.is_empty());
    }

    #[test]
    fn audit_event_with_actor_and_target_links_both() {
        let env = envelope(json!({
            "id": "audit_1",
            "created_at": "2026-09-03T12:00:00Z",
            "action": "role.assigned",
            "actor": {"id": "user_1", "type": "user", "name": "Ada"},
            "target": {"id": "role_admin", "type": "role", "name": "Admin"},
            "organization_id": "org_01",
            "context": {"ip": "1.2.3.4"},
            "metadata": {"granted_by": "user_99"}
        }));
        let outcome = ingest(&env, Utc::now()).unwrap();
        assert_eq!(outcome.edges.len(), 2);
        let by = outcome
            .edges
            .iter()
            .find(|e| e.edge_type == EDGE_KIND_AUDIT_BY)
            .unwrap();
        assert_eq!(by.target_id, "workos-user-user_1");
        let about = outcome
            .edges
            .iter()
            .find(|e| e.edge_type == EDGE_KIND_AUDIT_ABOUT)
            .unwrap();
        assert_eq!(about.target_id, "workos-role-role_admin");
        assert_eq!(outcome.event.metadata["context"]["ip"], "1.2.3.4");
        assert_eq!(outcome.event.metadata["payload"]["granted_by"], "user_99");
    }

    #[test]
    fn singularize_kind_strips_trailing_s() {
        assert_eq!(singularize_kind("users"), "user");
        assert_eq!(singularize_kind("User"), "user");
        assert_eq!(singularize_kind("role"), "role");
        assert_eq!(singularize_kind("ORGANIZATIONS"), "organization");
    }

    #[test]
    fn audit_event_label_includes_target_when_present() {
        let env = envelope(json!({
            "id": "audit_1",
            "created_at": "2026-09-03T12:00:00Z",
            "action": "user.suspended",
            "target": {"id": "user_99", "type": "user", "name": "Ada"}
        }));
        let outcome = ingest(&env, Utc::now()).unwrap();
        assert_eq!(outcome.event.label, "user.suspended on Ada");
    }

    #[test]
    fn audit_event_with_action_only_uses_action_as_label() {
        let env = envelope(json!({
            "id": "audit_1",
            "created_at": "2026-09-03T12:00:00Z",
            "action": "system.check"
        }));
        let outcome = ingest(&env, Utc::now()).unwrap();
        assert_eq!(outcome.event.label, "system.check");
    }

    #[test]
    fn provision_outcome_is_serializable() {
        let env = envelope(json!({
            "id": "audit_1",
            "created_at": "2026-09-03T12:00:00Z",
            "action": "x.y"
        }));
        let outcome = ingest(&env, Utc::now()).unwrap();
        let wrapped = ProvisionOutcome {
            nodes: vec![outcome.event],
            edges: outcome.edges,
            summary: outcome.summary,
        };
        let serialized = serde_json::to_string(&wrapped).unwrap();
        assert!(serialized.contains("workos-audit-audit_1"));
    }
}
