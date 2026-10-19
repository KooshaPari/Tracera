//! EdgeKind — 32 unique edge types mapping to 35 semantic edge definitions
//! (ADR-SWEE-001 §Edge taxonomy).
//!
//! Some edge type strings appear in multiple semantic relationships:
//!   - "contains"   → (module→class), (class→function), (module→function)
//!   - "parent_of"  → (epic→story), (story→task)
//!
//! The CHECK constraint stores only the unique string; the source/target node
//! pair constrains which semantic meaning applies at the DB level.

use serde::{Deserialize, Serialize};

/// Discriminator for all directed edges in the SWEE evidence graph.
///
/// Stored as the `edge_type` column in the `graph_edges` / `swee_edges` table.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
#[allow(clippy::enum_variant_names, clippy::module_name_repetitions)]
pub enum EdgeKind {
    /// Source satisfies a requirement (requirement → source_file).
    Implements,
    /// Spec elaborates a requirement (specification → requirement).
    Specifies,
    /// Design covers a requirement (design → requirement).
    Designs,
    /// Parent owns a child (module→class, class→function, module→function).
    Contains,
    /// Crate / package dependency (module → module).
    DependsOn,
    /// Runtime call edge (function → function).
    Calls,
    /// Inheritance or trait implementation (class → class).
    Extends,
    /// Test exercises source (test → source_file).
    Tests,
    /// Test validates requirement (test → requirement).
    Covers,
    /// Test belongs to suite (test → test_suite).
    BelongsTo,
    /// Commit author (commit → person).
    AuthoredBy,
    /// Commit modifies file (commit → source_file).
    Touches,
    /// PR targets branch (pull_request → branch).
    Targets,
    /// PR merges feature branch (pull_request → branch).
    MergesFrom,
    /// PR fixes an issue (pull_request → issue).
    Fixes,
    /// PR resolves a bug (pull_request → bug).
    Resolves,
    /// PR replaces earlier PR (pull_request → pull_request).
    Supersedes,
    /// Issue references commit (issue → commit).
    References,
    /// Blocking dependency (issue → issue).
    Blocks,
    /// Hierarchical containment (epic→story, story→task).
    ParentOf,
    /// Story assigned to sprint (story → sprint).
    InSprint,
    /// Story assigned to team (story → team).
    OwnedBy,
    /// Cross-system link (story → issue).
    LinkedTo,
    /// Evidence produced by commit (evidence → commit).
    DerivedFrom,
    /// Evidence from a deployment (evidence → deployment).
    ObservedIn,
    /// Incident triggers problem (incident → problem).
    TriggeredBy,
    /// Bidirectional correlation (problem → incident).
    CorrelatesWith,
    /// Issue threatens requirement (issue → requirement).
    Impacts,
    /// File shipped in release (source_file → release).
    ReleasedIn,
    /// Release deployed to env (release → environment).
    DeployedTo,
    /// Build triggered by commit (build → commit).
    BuiltFrom,
    /// Metric observed during build (metric → build).
    EmittedBy,
}

impl EdgeKind {
    /// Returns the `&str` discriminant stored in the SQL `edge_type` column.
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

    #[allow(clippy::should_implement_trait)]
    /// Parse an `EdgeKind` from its SQL string discriminant.
    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "implements" => Some(Self::Implements),
            "specifies" => Some(Self::Specifies),
            "designs" => Some(Self::Designs),
            "contains" => Some(Self::Contains),
            "depends_on" => Some(Self::DependsOn),
            "calls" => Some(Self::Calls),
            "extends" => Some(Self::Extends),
            "tests" => Some(Self::Tests),
            "covers" => Some(Self::Covers),
            "belongs_to" => Some(Self::BelongsTo),
            "authored_by" => Some(Self::AuthoredBy),
            "touches" => Some(Self::Touches),
            "targets" => Some(Self::Targets),
            "merges_from" => Some(Self::MergesFrom),
            "fixes" => Some(Self::Fixes),
            "resolves" => Some(Self::Resolves),
            "supersedes" => Some(Self::Supersedes),
            "references" => Some(Self::References),
            "blocks" => Some(Self::Blocks),
            "parent_of" => Some(Self::ParentOf),
            "in_sprint" => Some(Self::InSprint),
            "owned_by" => Some(Self::OwnedBy),
            "linked_to" => Some(Self::LinkedTo),
            "derived_from" => Some(Self::DerivedFrom),
            "observed_in" => Some(Self::ObservedIn),
            "triggered_by" => Some(Self::TriggeredBy),
            "correlates_with" => Some(Self::CorrelatesWith),
            "impacts" => Some(Self::Impacts),
            "released_in" => Some(Self::ReleasedIn),
            "deployed_to" => Some(Self::DeployedTo),
            "built_from" => Some(Self::BuiltFrom),
            "emitted_by" => Some(Self::EmittedBy),
            _ => None,
        }
    }

    /// All variants in declaration order.
    pub fn all() -> &'static [EdgeKind] {
        &[
            Self::Implements,
            Self::Specifies,
            Self::Designs,
            Self::Contains,
            Self::DependsOn,
            Self::Calls,
            Self::Extends,
            Self::Tests,
            Self::Covers,
            Self::BelongsTo,
            Self::AuthoredBy,
            Self::Touches,
            Self::Targets,
            Self::MergesFrom,
            Self::Fixes,
            Self::Resolves,
            Self::Supersedes,
            Self::References,
            Self::Blocks,
            Self::ParentOf,
            Self::InSprint,
            Self::OwnedBy,
            Self::LinkedTo,
            Self::DerivedFrom,
            Self::ObservedIn,
            Self::TriggeredBy,
            Self::CorrelatesWith,
            Self::Impacts,
            Self::ReleasedIn,
            Self::DeployedTo,
            Self::BuiltFrom,
            Self::EmittedBy,
        ]
    }
}
