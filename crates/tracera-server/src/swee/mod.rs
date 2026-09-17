//! SWEE (Software Engineering Evidence) graph schema module.
//!
//! Defines the typed node and edge taxonomy for the unified evidence graph
//! backed by SQLite/Postgres (see `migrations/sqlite/003_swee_graph.sql` and
//! `docs/governance/ADR-SWEE-001-graph-schema-design.md`).
//!
//! # Design
//!
//! The graph uses a **single discriminator column** per table — `node_type` for
//! nodes and `edge_type` for edges — enforced by SQL `CHECK` constraints.
//! Every type in these enums must appear in the canonical schema manifest at
//! `docs/governance/schema/graph_schema.json`.

#![allow(dead_code)]

pub mod edge_kind;
pub mod node_kind;

pub use edge_kind::EdgeKind;
pub use node_kind::NodeKind;

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Domain structs — mirror the SQL table shapes
// ---------------------------------------------------------------------------

/// A node in the SWEE evidence graph.
///
/// Maps 1:1 to a row in `graph_nodes` / `swee_nodes`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SwreeNode {
    /// Primary key (TEXT UUID in the canonical schema, INTEGER in the SQLite
    /// migration variant).
    pub id: String,
    /// Discriminator — must be a valid [`NodeKind`] variant.
    pub node_type: NodeKind,
    /// Human-readable label.
    pub label: String,
    /// JSON blob for extensible properties.
    #[serde(default = "default_metadata")]
    pub metadata: serde_json::Value,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// A directed edge in the SWEE evidence graph.
///
/// Maps 1:1 to a row in `graph_edges` / `swee_edges`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SweeEdge {
    /// Primary key.
    pub id: String,
    /// Discriminator — must be a valid [`EdgeKind`] variant.
    pub edge_type: EdgeKind,
    /// Source node id.
    pub source_id: String,
    /// Target node id.
    pub target_id: String,
    /// Confidence weight (0.0–1.0) for probabilistic / inferred edges.
    #[serde(default = "default_confidence")]
    pub confidence: f64,
    /// Provenance tag (e.g. "manual", "github", "jira", "inferred").
    #[serde(default = "default_edge_source")]
    pub source: String,
    /// JSON blob for extensible properties.
    #[serde(default = "default_metadata")]
    pub metadata: serde_json::Value,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// A label/tag attached to a node for full-text search.
///
/// Maps 1:1 to a row in `swee_node_labels`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SwreeNodeLabel {
    /// Primary key.
    pub id: i64,
    /// FK → `SwreeNode.id`.
    pub node_id: String,
    /// The label text (indexed via FTS5).
    pub label: String,
    /// Namespace for scoped searches (default: "default").
    #[serde(default = "default_label_namespace")]
    pub namespace: String,
}

/// Compact node reference used in edge endpoints and graph traversals.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NodeRef {
    pub id: String,
    pub node_type: NodeKind,
    pub label: String,
}

/// A single semantic edge definition from the 35-row taxonomy.
///
/// The edge taxonomy table in ADR-SWEE-001 lists 35 rows, but the SQL
/// `CHECK` constraint stores only 32 unique type strings because
/// `contains` and `parent_of` each span multiple source→target pairs.
/// This struct captures the full 5-tuple for governance / manifest use.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EdgeDefinition {
    /// Sequential row number (1–35) in the ADR taxonomy table.
    pub ordinal: u8,
    /// Edge type string (must match an [`EdgeKind`] variant).
    pub edge_type: EdgeKind,
    /// Allowed source [`NodeKind`].
    pub source_kind: NodeKind,
    /// Allowed target [`NodeKind`].
    pub target_kind: NodeKind,
    /// Human-readable description.
    pub description: &'static str,
}

/// Returns the full 35-row edge taxonomy from ADR-SWEE-001.
///
/// Use this for schema manifest generation, CI validation, and governance
/// audits — it is the authoritative list of permitted (source, edge, target)
/// triples.
pub fn edge_taxonomy() -> &'static [EdgeDefinition] {
    use EdgeKind as E;
    use NodeKind as N;
    &[
        EdgeDefinition {
            ordinal: 1,
            edge_type: E::Implements,
            source_kind: N::Requirement,
            target_kind: N::SourceFile,
            description: "Source satisfies a requirement",
        },
        EdgeDefinition {
            ordinal: 2,
            edge_type: E::Specifies,
            source_kind: N::Specification,
            target_kind: N::Requirement,
            description: "Spec elaborates a requirement",
        },
        EdgeDefinition {
            ordinal: 3,
            edge_type: E::Designs,
            source_kind: N::Design,
            target_kind: N::Requirement,
            description: "Design covers a requirement",
        },
        EdgeDefinition {
            ordinal: 4,
            edge_type: E::Contains,
            source_kind: N::Module,
            target_kind: N::Class,
            description: "Module owns a class/trait",
        },
        EdgeDefinition {
            ordinal: 5,
            edge_type: E::Contains,
            source_kind: N::Class,
            target_kind: N::Function,
            description: "Class owns a method/function",
        },
        EdgeDefinition {
            ordinal: 6,
            edge_type: E::Contains,
            source_kind: N::Module,
            target_kind: N::Function,
            description: "Module-level free function",
        },
        EdgeDefinition {
            ordinal: 7,
            edge_type: E::DependsOn,
            source_kind: N::Module,
            target_kind: N::Module,
            description: "Crate/package dependency",
        },
        EdgeDefinition {
            ordinal: 8,
            edge_type: E::Calls,
            source_kind: N::Function,
            target_kind: N::Function,
            description: "Runtime call edge",
        },
        EdgeDefinition {
            ordinal: 9,
            edge_type: E::Extends,
            source_kind: N::Class,
            target_kind: N::Class,
            description: "Inheritance or trait impl",
        },
        EdgeDefinition {
            ordinal: 10,
            edge_type: E::Tests,
            source_kind: N::Test,
            target_kind: N::SourceFile,
            description: "Test exercises source",
        },
        EdgeDefinition {
            ordinal: 11,
            edge_type: E::Covers,
            source_kind: N::Test,
            target_kind: N::Requirement,
            description: "Test validates requirement",
        },
        EdgeDefinition {
            ordinal: 12,
            edge_type: E::BelongsTo,
            source_kind: N::Test,
            target_kind: N::TestSuite,
            description: "Test belongs to suite",
        },
        EdgeDefinition {
            ordinal: 13,
            edge_type: E::AuthoredBy,
            source_kind: N::Commit,
            target_kind: N::Person,
            description: "Commit author",
        },
        EdgeDefinition {
            ordinal: 14,
            edge_type: E::Touches,
            source_kind: N::Commit,
            target_kind: N::SourceFile,
            description: "Commit modifies file",
        },
        EdgeDefinition {
            ordinal: 15,
            edge_type: E::Targets,
            source_kind: N::PullRequest,
            target_kind: N::Branch,
            description: "PR targets branch",
        },
        EdgeDefinition {
            ordinal: 16,
            edge_type: E::MergesFrom,
            source_kind: N::PullRequest,
            target_kind: N::Branch,
            description: "PR merges feature branch",
        },
        EdgeDefinition {
            ordinal: 17,
            edge_type: E::Fixes,
            source_kind: N::PullRequest,
            target_kind: N::Issue,
            description: "PR fixes an issue",
        },
        EdgeDefinition {
            ordinal: 18,
            edge_type: E::Resolves,
            source_kind: N::PullRequest,
            target_kind: N::Bug,
            description: "PR resolves a bug",
        },
        EdgeDefinition {
            ordinal: 19,
            edge_type: E::Supersedes,
            source_kind: N::PullRequest,
            target_kind: N::PullRequest,
            description: "PR replaces earlier PR",
        },
        EdgeDefinition {
            ordinal: 20,
            edge_type: E::References,
            source_kind: N::Issue,
            target_kind: N::Commit,
            description: "Issue references commit",
        },
        EdgeDefinition {
            ordinal: 21,
            edge_type: E::Blocks,
            source_kind: N::Issue,
            target_kind: N::Issue,
            description: "Blocking dependency",
        },
        EdgeDefinition {
            ordinal: 22,
            edge_type: E::ParentOf,
            source_kind: N::Epic,
            target_kind: N::Story,
            description: "Epic contains stories",
        },
        EdgeDefinition {
            ordinal: 23,
            edge_type: E::ParentOf,
            source_kind: N::Story,
            target_kind: N::Task,
            description: "Story decomposes into tasks",
        },
        EdgeDefinition {
            ordinal: 24,
            edge_type: E::InSprint,
            source_kind: N::Story,
            target_kind: N::Sprint,
            description: "Story assigned to sprint",
        },
        EdgeDefinition {
            ordinal: 25,
            edge_type: E::OwnedBy,
            source_kind: N::Story,
            target_kind: N::Team,
            description: "Story assigned to team",
        },
        EdgeDefinition {
            ordinal: 26,
            edge_type: E::LinkedTo,
            source_kind: N::Story,
            target_kind: N::Issue,
            description: "Cross-system link",
        },
        EdgeDefinition {
            ordinal: 27,
            edge_type: E::DerivedFrom,
            source_kind: N::Evidence,
            target_kind: N::Commit,
            description: "Evidence produced by commit",
        },
        EdgeDefinition {
            ordinal: 28,
            edge_type: E::ObservedIn,
            source_kind: N::Evidence,
            target_kind: N::Deployment,
            description: "Evidence from a deployment",
        },
        EdgeDefinition {
            ordinal: 29,
            edge_type: E::TriggeredBy,
            source_kind: N::Incident,
            target_kind: N::Problem,
            description: "Incident triggers problem",
        },
        EdgeDefinition {
            ordinal: 30,
            edge_type: E::CorrelatesWith,
            source_kind: N::Problem,
            target_kind: N::Incident,
            description: "Bidirectional correlation",
        },
        EdgeDefinition {
            ordinal: 31,
            edge_type: E::Impacts,
            source_kind: N::Issue,
            target_kind: N::Requirement,
            description: "Issue threatens requirement",
        },
        EdgeDefinition {
            ordinal: 32,
            edge_type: E::ReleasedIn,
            source_kind: N::SourceFile,
            target_kind: N::Release,
            description: "File shipped in release",
        },
        EdgeDefinition {
            ordinal: 33,
            edge_type: E::DeployedTo,
            source_kind: N::Release,
            target_kind: N::Environment,
            description: "Release deployed to env",
        },
        EdgeDefinition {
            ordinal: 34,
            edge_type: E::BuiltFrom,
            source_kind: N::Build,
            target_kind: N::Commit,
            description: "Build triggered by commit",
        },
        EdgeDefinition {
            ordinal: 35,
            edge_type: E::EmittedBy,
            source_kind: N::Metric,
            target_kind: N::Build,
            description: "Metric observed during build",
        },
    ]
}

// ---------------------------------------------------------------------------
// JSON default helpers
// ---------------------------------------------------------------------------

fn default_metadata() -> serde_json::Value {
    serde_json::Value::Object(serde_json::Map::new())
}

fn default_confidence() -> f64 {
    1.0
}

fn default_edge_source() -> String {
    "manual".to_string()
}

fn default_label_namespace() -> String {
    "default".to_string()
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn node_kind_roundtrip() {
        for kind in NodeKind::all() {
            let s = kind.as_str();
            let parsed = NodeKind::from_str(s).expect("from_str should succeed");
            assert_eq!(*kind, parsed);
        }
    }

    #[test]
    fn edge_kind_roundtrip() {
        for kind in EdgeKind::all() {
            let s = kind.as_str();
            let parsed = EdgeKind::from_str(s).expect("from_str should succeed");
            assert_eq!(*kind, parsed);
        }
    }

    #[test]
    fn node_kind_count() {
        assert_eq!(NodeKind::all().len(), 30, "expected 30 node types");
    }

    #[test]
    fn edge_kind_count() {
        assert_eq!(
            EdgeKind::all().len(),
            32,
            "expected 32 unique edge type strings"
        );
    }

    #[test]
    fn edge_taxonomy_count() {
        assert_eq!(
            edge_taxonomy().len(),
            35,
            "expected 35 semantic edge definitions"
        );
    }

    #[test]
    fn edge_taxonomy_ordinals_sequential() {
        for (i, def) in edge_taxonomy().iter().enumerate() {
            assert_eq!(def.ordinal, (i + 1) as u8, "ordinal mismatch at index {i}");
        }
    }

    #[test]
    fn serde_roundtrip_node_kind() {
        let kind = NodeKind::Requirement;
        let json = serde_json::to_string(&kind).unwrap();
        assert_eq!(json, "\"requirement\"");
        let back: NodeKind = serde_json::from_str(&json).unwrap();
        assert_eq!(back, kind);
    }

    #[test]
    fn serde_roundtrip_edge_kind() {
        let kind = EdgeKind::DependsOn;
        let json = serde_json::to_string(&kind).unwrap();
        assert_eq!(json, "\"depends_on\"");
        let back: EdgeKind = serde_json::from_str(&json).unwrap();
        assert_eq!(back, kind);
    }
}
