//! GraphQL resolvers for SWEE graph nodes.
//!
//! Mirrors the REST surface at `/api/v1/graph/nodes` and `/api/v1/graph/nodes/{id}`.
//! The 30 [`NodeKind`] variants come straight from `tracera-server::swee::NodeKind`
//! (ADR-SWEE-001). This file deliberately does not depend on `tracera-server`
//! so the gateway can be deployed standalone — the `Store` abstraction is
//! injected by the binary.

use async_graphql::{Enum, InputObject, SimpleObject};
use chrono::{DateTime, Utc};
use serde_json::Value as JsonValue;

// ---------------------------------------------------------------------------
// NodeKind — 30 discriminants matching ADR-SWEE-001 §Node taxonomy.
// Serialised as snake_case so the GraphQL strings match the SQL CHECK column.
// ---------------------------------------------------------------------------

/// The 30 SWEE node kinds (ADR-SWEE-001).
///
/// Kept as a separate enum from the server crate so the gateway stays
/// deployable without dragging in the entire server dependency tree.
/// The wire format (`requirement`, `source_file`, ...) is identical.
#[derive(Enum, Copy, Clone, Eq, PartialEq, Debug, Hash)]
#[graphql(rename_items = "snake_case")]
pub enum NodeKind {
    Requirement,
    Specification,
    Design,
    SourceFile,
    Module,
    Class,
    Function,
    Test,
    TestSuite,
    Commit,
    PullRequest,
    Branch,
    Issue,
    Epic,
    Story,
    Task,
    Bug,
    Sprint,
    Release,
    Build,
    Deployment,
    Evidence,
    Problem,
    Incident,
    ChangeRequest,
    Person,
    Team,
    Environment,
    Artifact,
    Metric,
}

impl NodeKind {
    /// Returns the SQL-compatible discriminant.
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Requirement => "requirement",
            Self::Specification => "specification",
            Self::Design => "design",
            Self::SourceFile => "source_file",
            Self::Module => "module",
            Self::Class => "class",
            Self::Function => "function",
            Self::Test => "test",
            Self::TestSuite => "test_suite",
            Self::Commit => "commit",
            Self::PullRequest => "pull_request",
            Self::Branch => "branch",
            Self::Issue => "issue",
            Self::Epic => "epic",
            Self::Story => "story",
            Self::Task => "task",
            Self::Bug => "bug",
            Self::Sprint => "sprint",
            Self::Release => "release",
            Self::Build => "build",
            Self::Deployment => "deployment",
            Self::Evidence => "evidence",
            Self::Problem => "problem",
            Self::Incident => "incident",
            Self::ChangeRequest => "change_request",
            Self::Person => "person",
            Self::Team => "team",
            Self::Environment => "environment",
            Self::Artifact => "artifact",
            Self::Metric => "metric",
        }
    }

    /// Parses from the SQL discriminant. Mirrors the server-side `from_str`.
    pub fn parse(s: &str) -> Option<Self> {
        Some(match s {
            "requirement" => Self::Requirement,
            "specification" => Self::Specification,
            "design" => Self::Design,
            "source_file" => Self::SourceFile,
            "module" => Self::Module,
            "class" => Self::Class,
            "function" => Self::Function,
            "test" => Self::Test,
            "test_suite" => Self::TestSuite,
            "commit" => Self::Commit,
            "pull_request" => Self::PullRequest,
            "branch" => Self::Branch,
            "issue" => Self::Issue,
            "epic" => Self::Epic,
            "story" => Self::Story,
            "task" => Self::Task,
            "bug" => Self::Bug,
            "sprint" => Self::Sprint,
            "release" => Self::Release,
            "build" => Self::Build,
            "deployment" => Self::Deployment,
            "evidence" => Self::Evidence,
            "problem" => Self::Problem,
            "incident" => Self::Incident,
            "change_request" => Self::ChangeRequest,
            "person" => Self::Person,
            "team" => Self::Team,
            "environment" => Self::Environment,
            "artifact" => Self::Artifact,
            "metric" => Self::Metric,
            _ => return None,
        })
    }
}

// ---------------------------------------------------------------------------
// GraphNode — GraphQL view of a SWEE node row.
// ---------------------------------------------------------------------------

/// A node in the SWEE evidence graph. Maps 1:1 to a row in `swee_nodes`.
#[derive(SimpleObject, Clone, Debug)]
pub struct GraphNode {
    pub id: String,
    pub node_type: NodeKind,
    pub label: String,
    /// JSON blob — kept as opaque scalar so the gateway does not need to know
    /// the shape ahead of time (matches the REST contract).
    pub metadata: JsonValue,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// Lightweight reference returned by neighbour queries and edge endpoints.
#[derive(SimpleObject, Clone, Debug)]
pub struct NodeRef {
    pub id: String,
    pub node_type: NodeKind,
    pub label: String,
}

// ---------------------------------------------------------------------------
// Inputs — match the REST POST bodies for `/api/v1/graph/nodes`.
// ---------------------------------------------------------------------------

#[derive(InputObject, Clone, Debug)]
pub struct NodeCreateInput {
    pub node_type: NodeKind,
    pub label: String,
    /// Optional metadata. Defaults to `{}` on the server.
    #[graphql(default)]
    pub metadata: JsonValue,
}

/// Filters used by the listing endpoint, mirroring the REST query string.
#[derive(InputObject, Clone, Debug, Default)]
pub struct NodeListFilter {
    /// Restrict to a single node kind. `None` ⇒ all kinds.
    #[graphql(default)]
    pub node_type: Option<NodeKind>,
    /// Case-insensitive substring filter on the label.
    #[graphql(default)]
    pub label_contains: Option<String>,
    /// Maximum rows to return (matches the REST `page_size` semantics).
    #[graphql(default)]
    pub limit: Option<i32>,
}

impl NodeListFilter {
    /// REST parity: clamp `limit` to the same 1..=500 range the server enforces.
    pub fn validated_limit(&self) -> i32 {
        match self.limit {
            None => 50,
            Some(n) if n < 1 => 1,
            Some(n) if n > 500 => 500,
            Some(n) => n,
        }
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn node_kind_roundtrip() {
        let kinds = [
            NodeKind::Requirement,
            NodeKind::SourceFile,
            NodeKind::TestSuite,
            NodeKind::ChangeRequest,
            NodeKind::Metric,
        ];
        for kind in kinds {
            let s = kind.as_str();
            let parsed = NodeKind::parse(s).expect("must parse");
            assert_eq!(parsed, kind);
        }
    }

    #[test]
    fn node_kind_parse_rejects_unknown() {
        assert!(NodeKind::parse("not_a_kind").is_none());
    }

    #[test]
    fn list_filter_default_limit_is_50() {
        assert_eq!(NodeListFilter::default().validated_limit(), 50);
    }

    #[test]
    fn list_filter_clamps_out_of_range() {
        assert_eq!(
            NodeListFilter {
                limit: Some(0),
                ..Default::default()
            }
            .validated_limit(),
            1
        );
        assert_eq!(
            NodeListFilter {
                limit: Some(10_000),
                ..Default::default()
            }
            .validated_limit(),
            500
        );
        assert_eq!(
            NodeListFilter {
                limit: Some(123),
                ..Default::default()
            }
            .validated_limit(),
            123
        );
    }
}
