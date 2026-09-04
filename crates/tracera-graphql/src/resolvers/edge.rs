//! GraphQL resolvers for SWEE graph edges.
//!
//! Mirrors `/api/v1/graph/edges` and the legacy trace-link endpoints
//! (`/api/v1/trace`, `/api/v1/trace/{artifact_id}/links`,
//! `/api/v1/trace/{direction}/{artifact_id}`).
//!
//! The 32 [`EdgeKind`] variants match the `swee_edges.edge_type` CHECK
//! constraint (ADR-SWEE-001). Persisted trace-links (legacy `trace_links`
//! table) are exposed through the same `GraphEdge` shape so a REST client
//! reading `/api/v1/trace/{id}/links` sees the same fields as a GraphQL
//! client reading `node(id).incidentLinks`.

use async_graphql::{Enum, InputObject, SimpleObject};
use chrono::{DateTime, Utc};
use serde_json::Value as JsonValue;

use super::node::NodeRef;

// ---------------------------------------------------------------------------
// EdgeKind — 32 unique discriminants (35 semantic definitions).
// ---------------------------------------------------------------------------

#[derive(Enum, Copy, Clone, Eq, PartialEq, Debug, Hash)]
#[graphql(rename_items = "snake_case")]
pub enum EdgeKind {
    Implements,
    Specifies,
    Designs,
    Contains,
    DependsOn,
    Calls,
    Extends,
    Tests,
    Covers,
    BelongsTo,
    AuthoredBy,
    Touches,
    Targets,
    MergesFrom,
    Fixes,
    Resolves,
    Supersedes,
    References,
    Blocks,
    ParentOf,
    InSprint,
    OwnedBy,
    LinkedTo,
    DerivedFrom,
    ObservedIn,
    TriggeredBy,
    CorrelatesWith,
    Impacts,
    ReleasedIn,
    DeployedTo,
    BuiltFrom,
    EmittedBy,
}

impl EdgeKind {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Implements => "implements",
            Self::Specifies => "specifies",
            Self::Designs => "designs",
            Self::Contains => "contains",
            Self::DependsOn => "depends_on",
            Self::Calls => "calls",
            Self::Extends => "extends",
            Self::Tests => "tests",
            Self::Covers => "covers",
            Self::BelongsTo => "belongs_to",
            Self::AuthoredBy => "authored_by",
            Self::Touches => "touches",
            Self::Targets => "targets",
            Self::MergesFrom => "merges_from",
            Self::Fixes => "fixes",
            Self::Resolves => "resolves",
            Self::Supersedes => "supersedes",
            Self::References => "references",
            Self::Blocks => "blocks",
            Self::ParentOf => "parent_of",
            Self::InSprint => "in_sprint",
            Self::OwnedBy => "owned_by",
            Self::LinkedTo => "linked_to",
            Self::DerivedFrom => "derived_from",
            Self::ObservedIn => "observed_in",
            Self::TriggeredBy => "triggered_by",
            Self::CorrelatesWith => "correlates_with",
            Self::Impacts => "impacts",
            Self::ReleasedIn => "released_in",
            Self::DeployedTo => "deployed_to",
            Self::BuiltFrom => "built_from",
            Self::EmittedBy => "emitted_by",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        Some(match s {
            "implements" => Self::Implements,
            "specifies" => Self::Specifies,
            "designs" => Self::Designs,
            "contains" => Self::Contains,
            "depends_on" => Self::DependsOn,
            "calls" => Self::Calls,
            "extends" => Self::Extends,
            "tests" => Self::Tests,
            "covers" => Self::Covers,
            "belongs_to" => Self::BelongsTo,
            "authored_by" => Self::AuthoredBy,
            "touches" => Self::Touches,
            "targets" => Self::Targets,
            "merges_from" => Self::MergesFrom,
            "fixes" => Self::Fixes,
            "resolves" => Self::Resolves,
            "supersedes" => Self::Supersedes,
            "references" => Self::References,
            "blocks" => Self::Blocks,
            "parent_of" => Self::ParentOf,
            "in_sprint" => Self::InSprint,
            "owned_by" => Self::OwnedBy,
            "linked_to" => Self::LinkedTo,
            "derived_from" => Self::DerivedFrom,
            "observed_in" => Self::ObservedIn,
            "triggered_by" => Self::TriggeredBy,
            "correlates_with" => Self::CorrelatesWith,
            "impacts" => Self::Impacts,
            "released_in" => Self::ReleasedIn,
            "deployed_to" => Self::DeployedTo,
            "built_from" => Self::BuiltFrom,
            "emitted_by" => Self::EmittedBy,
            _ => return None,
        })
    }
}

/// Direction of an incident link relative to an artifact.
///
/// REST parity: `/api/v1/trace/forward/{id}` returns `"forward"`,
/// `/api/v1/trace/reverse/{id}` returns `"reverse"`.
#[derive(Enum, Copy, Clone, Eq, PartialEq, Debug)]
#[graphql(name = "TraceDirection", rename_items = "snake_case")]
pub enum TraceDirection {
    Forward,
    Reverse,
}

impl TraceDirection {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Forward => "forward",
            Self::Reverse => "reverse",
        }
    }
}

// ---------------------------------------------------------------------------
// GraphEdge — output type for both SWEE edges and persisted trace-links.
// ---------------------------------------------------------------------------

#[derive(SimpleObject, Clone, Debug)]
pub struct GraphEdge {
    pub id: String,
    pub edge_type: EdgeKind,
    pub source_id: String,
    pub target_id: String,
    pub confidence: f64,
    /// Provenance: `"manual"`, `"github"`, `"jira"`, `"inferred"`, `"api"`.
    pub source: String,
    pub metadata: JsonValue,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// Compact edge view embedded inside neighbour responses.
#[derive(SimpleObject, Clone, Debug)]
pub struct EdgeSummary {
    pub id: String,
    pub edge_type: EdgeKind,
    pub source_id: String,
    pub target_id: String,
    pub confidence: f64,
}

/// Legacy trace-link response shape used by `/api/v1/trace/...`.
#[derive(SimpleObject, Clone, Debug)]
pub struct PersistedTraceLink {
    pub id: String,
    pub source_id: String,
    pub target_id: String,
    pub relationship: String,
    pub confidence: f64,
    pub source: String,
    pub direction: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(SimpleObject, Clone, Debug)]
pub struct TraceNeighbors {
    pub artifact_id: String,
    pub direction: String,
    pub neighbors: Vec<NodeRef>,
}

// ---------------------------------------------------------------------------
// Inputs
// ---------------------------------------------------------------------------

#[derive(InputObject, Clone, Debug)]
pub struct EdgeCreateInput {
    pub edge_type: EdgeKind,
    pub source_id: String,
    pub target_id: String,
    /// Optional — defaults to 1.0 (mirrors `confidence` column default).
    #[graphql(default)]
    pub confidence: Option<f64>,
    /// Provenance tag. Defaults to `"manual"`.
    #[graphql(default)]
    pub source: Option<String>,
    #[graphql(default)]
    pub metadata: JsonValue,
}

#[derive(InputObject, Clone, Debug, Default)]
pub struct EdgeListFilter {
    #[graphql(default)]
    pub edge_type: Option<EdgeKind>,
    #[graphql(default)]
    pub source_id: Option<String>,
    #[graphql(default)]
    pub target_id: Option<String>,
    #[graphql(default)]
    pub limit: Option<i32>,
}

impl EdgeListFilter {
    pub fn validated_limit(&self) -> i32 {
        match self.limit {
            None => 50,
            Some(n) if n < 1 => 1,
            Some(n) if n > 500 => 500,
            Some(n) => n,
        }
    }
}

#[derive(InputObject, Clone, Debug)]
pub struct TraceLinkCreateInput {
    pub source_id: String,
    pub target_id: String,
    pub relationship: String,
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn edge_kind_roundtrip() {
        let kinds = [
            EdgeKind::Implements,
            EdgeKind::Contains,
            EdgeKind::DependsOn,
            EdgeKind::ParentOf,
            EdgeKind::EmittedBy,
        ];
        for kind in kinds {
            let s = kind.as_str();
            let parsed = EdgeKind::parse(s).expect("must parse");
            assert_eq!(parsed, kind);
        }
    }

    #[test]
    fn edge_kind_count_is_32() {
        let all = [
            EdgeKind::Implements,
            EdgeKind::Specifies,
            EdgeKind::Designs,
            EdgeKind::Contains,
            EdgeKind::DependsOn,
            EdgeKind::Calls,
            EdgeKind::Extends,
            EdgeKind::Tests,
            EdgeKind::Covers,
            EdgeKind::BelongsTo,
            EdgeKind::AuthoredBy,
            EdgeKind::Touches,
            EdgeKind::Targets,
            EdgeKind::MergesFrom,
            EdgeKind::Fixes,
            EdgeKind::Resolves,
            EdgeKind::Supersedes,
            EdgeKind::References,
            EdgeKind::Blocks,
            EdgeKind::ParentOf,
            EdgeKind::InSprint,
            EdgeKind::OwnedBy,
            EdgeKind::LinkedTo,
            EdgeKind::DerivedFrom,
            EdgeKind::ObservedIn,
            EdgeKind::TriggeredBy,
            EdgeKind::CorrelatesWith,
            EdgeKind::Impacts,
            EdgeKind::ReleasedIn,
            EdgeKind::DeployedTo,
            EdgeKind::BuiltFrom,
            EdgeKind::EmittedBy,
        ];
        assert_eq!(all.len(), 32, "expected 32 unique edge discriminants");
    }

    #[test]
    fn direction_strings_match_rest() {
        assert_eq!(TraceDirection::Forward.as_str(), "forward");
        assert_eq!(TraceDirection::Reverse.as_str(), "reverse");
    }
}
