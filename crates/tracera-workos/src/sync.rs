//! Directory Sync: convert WorkOS `dsync.*` webhook payloads into graph nodes.
//!
//! Mapping:
//!
//! | WorkOS resource        | Tracera graph node            | Node kind  |
//! |------------------------|-------------------------------|------------|
//! | `dsync.user.*`         | `Agent` (id: `workos-user-*`)| `agent`    |
//! | `dsync.group.*`        | `Team` (id: `workos-team-*`)  | `team`     |
//! | `dsync.organization.*` | `Organization`                | `team`*    |
//!
//! *Organizations are also stored as `Team` nodes since the SWEE schema doesn't
//!  have an `organization` kind; we tag them via metadata.
//!
//! This module is deliberately pure — it produces `GraphNode` records but does
//! not write them anywhere. The tracera-server's webhook handler calls
//! [`provision`] and then passes the returned `Vec<GraphNode>` to the SWEE
//! `create_swee_node` / `create_swee_edge` store methods.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::error::{WorkOSError, WorkOSResult};
use crate::webhooks::WebhookEnvelope;

/// Stable node-kind strings used by the SWEE schema.
pub const NODE_KIND_AGENT: &str = "agent";
pub const NODE_KIND_TEAM: &str = "team";
pub const NODE_KIND_PERSON: &str = "person";
pub const NODE_KIND_ORGANIZATION: &str = "team"; // alias for metadata tagging

/// Edge-kind strings used to link directory resources.
pub const EDGE_KIND_MEMBER_OF: &str = "belongs_to";
pub const EDGE_KIND_OWNS_TEAM: &str = "owns_team";
pub const EDGE_KIND_REPORTS_TO: &str = "reports_to";

/// Action implied by the event type suffix.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum SyncAction {
    Created,
    Updated,
    Deleted,
    Added,
    Removed,
}

impl SyncAction {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Created => "created",
            Self::Updated => "updated",
            Self::Deleted => "deleted",
            Self::Added => "added",
            Self::Removed => "removed",
        }
    }
}

/// A graph node produced by [`provision`]. The `metadata` blob is passed
/// straight through to `create_swee_node`.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GraphNode {
    /// Tracera node id — namespaced so we never collide with other ingest
    /// sources. Format: `workos-<resource>-<workos_id>`.
    pub id: String,
    pub node_type: String,
    pub label: String,
    pub metadata: Value,
    /// True when this node should be tombstoned on the receiving side rather
    /// than upserted (set for `*.deleted` events).
    pub tombstone: bool,
}

/// A directed graph edge produced by [`provision`].
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GraphEdge {
    pub edge_type: String,
    pub source_id: String,
    pub target_id: String,
    pub confidence: f64,
    pub source: String,
    pub metadata: Value,
}

/// What the tracera-server should do with this event.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ProvisionOutcome {
    pub nodes: Vec<GraphNode>,
    pub edges: Vec<GraphEdge>,
    /// Short human-readable summary suitable for a log line.
    pub summary: String,
}

// ---------------------------------------------------------------------------
// Resource payloads (subset we care about)
// ---------------------------------------------------------------------------

/// `dsync.user.*` payload — see WorkOS Directory Sync schema.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DirectoryUser {
    pub id: String,
    #[serde(default)]
    pub email: Option<String>,
    #[serde(default)]
    pub first_name: Option<String>,
    #[serde(default)]
    pub last_name: Option<String>,
    #[serde(default)]
    pub state: Option<String>, // "active" | "inactive" | "suspended"
    #[serde(default)]
    pub organization_id: Option<String>,
    #[serde(default)]
    pub groups: Vec<DirectoryGroupRef>,
    #[serde(default)]
    pub custom_attributes: Value,
}

/// `dsync.group.*` payload (embedded inside user payloads as a reference,
/// or top-level for group events).
#[derive(Clone, Debug, Serialize, Deserialize, Clone)]
pub struct DirectoryGroupRef {
    pub id: String,
    #[serde(default)]
    pub name: Option<String>,
}

/// `dsync.group.*` top-level payload.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DirectoryGroup {
    pub id: String,
    #[serde(default)]
    pub name: Option<String>,
    #[serde(default)]
    pub organization_id: Option<String>,
}

/// `dsync.organization.*` payload.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DirectoryOrganization {
    pub id: String,
    #[serde(default)]
    pub name: Option<String>,
    #[serde(default)]
    pub domains: Vec<DirectoryDomain>,
}

/// `domains[]` element on `DirectoryOrganization`.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DirectoryDomain {
    pub id: String,
    pub domain: String,
}

/// Convert a webhook envelope into Tracera graph nodes/edges.
///
/// Returns [`WorkOSError::UnsupportedDirectoryEvent`] if the event type is in
/// the `dsync.*` family but not one we recognise.
pub fn provision(envelope: &WebhookEnvelope, received_at: DateTime<Utc>) -> WorkOSResult<ProvisionOutcome> {
    let (action, family) = parse_action(&envelope.event_type)?;
    let data = envelope.data.clone();
    match family {
        "user" => provision_user(&data, action, &envelope.id, received_at),
        "group" => provision_group(&data, action, &envelope.id, received_at),
        "organization" => provision_organization(&data, action, &envelope.id, received_at),
        _ => Err(WorkOSError::UnsupportedDirectoryEvent(format!(
            "unsupported dsync resource family {:?}",
            family
        ))),
    }
}

fn parse_action(event_type: &str) -> WorkOSResult<(SyncAction, &'static str)> {
    let rest = event_type.strip_prefix("dsync.").ok_or_else(|| {
        WorkOSError::UnsupportedDirectoryEvent(format!(
            "{event_type:?} is not a dsync.* event"
        ))
    })?;
    let (resource, suffix) = rest.split_once('.').ok_or_else(|| {
        WorkOSError::UnsupportedDirectoryEvent(format!(
            "missing suffix in dsync event {event_type:?}"
        ))
    })?;
    let resource: &'static str = match resource {
        "user" => "user",
        "group" => "group",
        "organization" => "organization",
        _ => {
            return Err(WorkOSError::UnsupportedDirectoryEvent(format!(
                "unknown dsync resource {resource:?}"
            )));
        }
    };
    let action = match suffix {
        "created" => SyncAction::Created,
        "updated" => SyncAction::Updated,
        "deleted" => SyncAction::Deleted,
        "user_added" => SyncAction::Added,
        "user_removed" => SyncAction::Removed,
        _ => {
            return Err(WorkOSError::UnsupportedDirectoryEvent(format!(
                "unknown dsync suffix {suffix:?}"
            )));
        }
    };
    Ok((action, resource))
}

fn provision_user(
    data: &Value,
    action: SyncAction,
    event_id: &str,
    received_at: DateTime<Utc>,
) -> WorkOSResult<ProvisionOutcome> {
    let user: DirectoryUser = serde_json::from_value(data.clone())?;
    let node_id = format!("workos-user-{}", user.id);
    let label = user
        .email
        .clone()
        .unwrap_or_else(|| format!("User {}", user.id));
    let mut metadata = serde_json::Map::new();
    metadata.insert("workos_id".into(), Value::String(user.id.clone()));
    metadata.insert("source".into(), Value::String("workos.directory_sync".into()));
    metadata.insert("event_id".into(), Value::String(event_id.into()));
    if let Some(email) = &user.email {
        metadata.insert("email".into(), Value::String(email.clone()));
    }
    if let Some(first) = &user.first_name {
        metadata.insert("first_name".into(), Value::String(first.clone()));
    }
    if let Some(last) = &user.last_name {
        metadata.insert("last_name".into(), Value::String(last.clone()));
    }
    if let Some(state) = &user.state {
        metadata.insert("state".into(), Value::String(state.clone()));
    }
    metadata.insert(
        "received_at".into(),
        Value::String(received_at.to_rfc3339()),
    );
    if let Some(org_id) = &user.organization_id {
        metadata.insert(
            "organization_id".into(),
            Value::String(org_id.clone()),
        );
    }
    if !user.custom_attributes.is_null() {
        metadata.insert("custom_attributes".into(), user.custom_attributes.clone());
    }

    let tombstone = action == SyncAction::Deleted;
    let node = GraphNode {
        id: node_id.clone(),
        node_type: NODE_KIND_AGENT.to_string(),
        label,
        metadata: Value::Object(metadata.clone()),
        tombstone,
    };

    let mut edges = Vec::new();
    if !tombstone {
        // Group memberships → `belongs_to` edges (team → person, or per the
        // SWEE schema, person → team).
        for group in &user.groups {
            edges.push(GraphEdge {
                edge_type: EDGE_KIND_MEMBER_OF.to_string(),
                source_id: node_id.clone(),
                target_id: format!("workos-team-{}", group.id),
                confidence: 1.0,
                source: "workos.directory_sync".into(),
                metadata: Value::Object({
                    let mut m = serde_json::Map::new();
                    m.insert("event_id".into(), Value::String(event_id.into()));
                    m
                }),
            });
        }
        // Org ownership → `belongs_to` (agent → org-as-team).
        if let Some(org_id) = &user.organization_id {
            edges.push(GraphEdge {
                edge_type: EDGE_KIND_MEMBER_OF.to_string(),
                source_id: node_id.clone(),
                target_id: format!("workos-org-{org_id}"),
                confidence: 1.0,
                source: "workos.directory_sync".into(),
                metadata: Value::Object({
                    let mut m = serde_json::Map::new();
                    m.insert("event_id".into(), Value::String(event_id.into()));
                    m.insert("via".into(), Value::String("organization_id".into()));
                    m
                }),
            });
        }
    }

    let summary = format!(
        "user {} {} -> {} node, {} edges",
        user.id,
        action.as_str(),
        node_id,
        edges.len()
    );
    Ok(ProvisionOutcome {
        nodes: vec![node],
        edges,
        summary,
    })
}

fn provision_group(
    data: &Value,
    action: SyncAction,
    event_id: &str,
    received_at: DateTime<Utc>,
) -> WorkOSResult<ProvisionOutcome> {
    let group: DirectoryGroup = serde_json::from_value(data.clone())?;
    let node_id = format!("workos-team-{}", group.id);
    let label = group.name.clone().unwrap_or_else(|| format!("Group {}", group.id));
    let mut metadata = serde_json::Map::new();
    metadata.insert("workos_id".into(), Value::String(group.id.clone()));
    metadata.insert("source".into(), Value::String("workos.directory_sync".into()));
    metadata.insert("event_id".into(), Value::String(event_id.into()));
    metadata.insert(
        "received_at".into(),
        Value::String(received_at.to_rfc3339()),
    );
    if let Some(org_id) = &group.organization_id {
        metadata.insert("organization_id".into(), Value::String(org_id.clone()));
    }
    let tombstone = action == SyncAction::Deleted;
    let node = GraphNode {
        id: node_id.clone(),
        node_type: NODE_KIND_TEAM.to_string(),
        label,
        metadata: Value::Object(metadata),
        tombstone,
    };
    let summary = format!("group {} {} -> {}", group.id, action.as_str(), node_id);
    Ok(ProvisionOutcome {
        nodes: vec![node],
        edges: vec![],
        summary,
    })
}

fn provision_organization(
    data: &Value,
    action: SyncAction,
    event_id: &str,
    received_at: DateTime<Utc>,
) -> WorkOSResult<ProvisionOutcome> {
    let org: DirectoryOrganization = serde_json::from_value(data.clone())?;
    let node_id = format!("workos-org-{}", org.id);
    let label = org.name.clone().unwrap_or_else(|| format!("Org {}", org.id));
    let mut metadata = serde_json::Map::new();
    metadata.insert("workos_id".into(), Value::String(org.id.clone()));
    metadata.insert("source".into(), Value::String("workos.directory_sync".into()));
    metadata.insert("event_id".into(), Value::String(event_id.into()));
    metadata.insert(
        "received_at".into(),
        Value::String(received_at.to_rfc3339()),
    );
    metadata.insert("is_organization".into(), Value::Bool(true));
    metadata.insert(
        "domains".into(),
        Value::Array(
            org.domains
                .iter()
                .map(|d| Value::String(d.domain.clone()))
                .collect(),
        ),
    );
    let tombstone = action == SyncAction::Deleted;
    let node = GraphNode {
        id: node_id.clone(),
        node_type: NODE_KIND_ORGANIZATION.to_string(),
        label,
        metadata: Value::Object(metadata),
        tombstone,
    };
    let summary = format!(
        "organization {} {} -> {}",
        org.id,
        action.as_str(),
        node_id
    );
    Ok(ProvisionOutcome {
        nodes: vec![node],
        edges: vec![],
        summary,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::webhooks::WebhookEnvelope;
    use serde_json::json;

    fn envelope(event_type: &str, data: Value) -> WebhookEnvelope {
        WebhookEnvelope {
            id: "evt_test".into(),
            event_type: event_type.into(),
            created_at: None,
            data,
            organization_id: Some("org_01".into()),
        }
    }

    #[test]
    fn user_created_produces_agent_node_and_belongs_to_edges() {
        let env = envelope(
            "dsync.user.created",
            json!({
                "id": "user_1",
                "email": "ada@example.com",
                "first_name": "Ada",
                "last_name": "Lovelace",
                "state": "active",
                "organization_id": "org_01",
                "groups": [
                    {"id": "group_eng", "name": "Engineering"},
                    {"id": "group_arch", "name": "Architecture"}
                ],
                "custom_attributes": {"department": "R&D"}
            }),
        );
        let outcome = provision(&env, Utc::now()).unwrap();
        assert_eq!(outcome.nodes.len(), 1);
        let node = &outcome.nodes[0];
        assert_eq!(node.id, "workos-user-user_1");
        assert_eq!(node.node_type, NODE_KIND_AGENT);
        assert_eq!(node.label, "ada@example.com");
        assert!(!node.tombstone);
        assert_eq!(node.metadata["email"], "ada@example.com");
        assert_eq!(node.metadata["state"], "active");
        assert_eq!(node.metadata["custom_attributes"]["department"], "R&D");

        // 2 group edges + 1 org edge = 3 total
        assert_eq!(outcome.edges.len(), 3);
        let targets: Vec<&str> = outcome
            .edges
            .iter()
            .map(|e| e.target_id.as_str())
            .collect();
        assert!(targets.contains(&"workos-team-group_eng"));
        assert!(targets.contains(&"workos-team-group_arch"));
        assert!(targets.contains(&"workos-org-org_01"));
    }

    #[test]
    fn user_deleted_is_tombstone_only_no_edges() {
        let env = envelope(
            "dsync.user.deleted",
            json!({
                "id": "user_1",
                "email": "ada@example.com",
                "groups": [{"id": "group_eng"}]
            }),
        );
        let outcome = provision(&env, Utc::now()).unwrap();
        assert!(outcome.nodes[0].tombstone);
        assert!(outcome.edges.is_empty());
    }

    #[test]
    fn user_updated_overwrites_metadata_not_tombstone() {
        let env = envelope(
            "dsync.user.updated",
            json!({
                "id": "user_1",
                "email": "ada-new@example.com",
                "state": "inactive"
            }),
        );
        let outcome = provision(&env, Utc::now()).unwrap();
        assert!(!outcome.nodes[0].tombstone);
        assert_eq!(
            outcome.nodes[0].metadata["email"],
            "ada-new@example.com"
        );
        assert_eq!(outcome.nodes[0].metadata["state"], "inactive");
    }

    #[test]
    fn group_created_produces_team_node() {
        let env = envelope(
            "dsync.group.created",
            json!({"id": "group_1", "name": "Platform", "organization_id": "org_01"}),
        );
        let outcome = provision(&env, Utc::now()).unwrap();
        assert_eq!(outcome.nodes[0].node_type, NODE_KIND_TEAM);
        assert_eq!(outcome.nodes[0].id, "workos-team-group_1");
        assert_eq!(outcome.nodes[0].label, "Platform");
        assert!(outcome.edges.is_empty());
    }

    #[test]
    fn organization_created_tags_metadata_with_domains() {
        let env = envelope(
            "dsync.organization.created",
            json!({
                "id": "org_1",
                "name": "Acme",
                "domains": [
                    {"id": "dom_1", "domain": "acme.example.com"}
                ]
            }),
        );
        let outcome = provision(&env, Utc::now()).unwrap();
        assert_eq!(outcome.nodes[0].node_type, NODE_KIND_ORGANIZATION);
        assert_eq!(outcome.nodes[0].metadata["is_organization"], true);
        assert_eq!(
            outcome.nodes[0].metadata["domains"][0],
            "acme.example.com"
        );
    }

    #[test]
    fn unknown_suffix_yields_unsupported_error() {
        let env = envelope(
            "dsync.user.archived",
            json!({"id": "user_1"}),
        );
        let err = provision(&env, Utc::now()).unwrap_err();
        assert!(matches!(err, WorkOSError::UnsupportedDirectoryEvent(_)));
    }

    #[test]
    fn non_dsync_event_yields_unsupported_error() {
        let env = envelope(
            "audit.log.created",
            json!({"id": "evt_1"}),
        );
        let err = provision(&env, Utc::now()).unwrap_err();
        assert!(matches!(err, WorkOSError::UnsupportedDirectoryEvent(_)));
    }

    #[test]
    fn parse_action_extracts_resource_and_suffix() {
        let (action, resource) = parse_action("dsync.user.created").unwrap();
        assert_eq!(action, SyncAction::Created);
        assert_eq!(resource, "user");
        let (action, resource) = parse_action("dsync.group.user_added").unwrap();
        assert_eq!(action, SyncAction::Added);
        assert_eq!(resource, "group");
    }
}
