//! NodeKind — 30 node types (ADR-SWEE-001 §Node taxonomy).

use serde::{Deserialize, Serialize};

/// Discriminator for all nodes in the SWEE evidence graph.
///
/// Stored as the `node_type` column in the `graph_nodes` / `swee_nodes` table.
/// Variants are ordered to match the SQL `CHECK` constraint exactly.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
#[allow(clippy::enum_variant_names, clippy::module_name_repetitions)]
pub enum NodeKind {
    /// Functional / non-functional requirement.
    Requirement,
    /// Design or architectural specification document.
    Specification,
    /// UI/UX design artefact.
    Design,
    /// Individual source file.
    SourceFile,
    /// Crate, package, or library boundary.
    Module,
    /// Struct, class, or trait definition.
    Class,
    /// Method, function, or closure.
    Function,
    /// Individual test case.
    Test,
    /// Test grouping (e.g. `cargo test` target).
    TestSuite,
    /// Git commit.
    Commit,
    /// GitHub / GitLab merge request.
    PullRequest,
    /// Git branch or tag.
    Branch,
    /// GitHub Issue or Jira ticket.
    Issue,
    /// Parent work-unit grouping stories.
    Epic,
    /// User story — supersedes the legacy `stories` table.
    Story,
    /// Sub-task under a story.
    Task,
    /// Defect record.
    Bug,
    /// Iteration container — supersedes the legacy `sprints` table.
    Sprint,
    /// Versioned release (semver tag).
    Release,
    /// CI/CD build execution.
    Build,
    /// Deployment event to an environment.
    Deployment,
    /// Generic evidence artefact — supersedes the legacy `evidence` table.
    Evidence,
    /// ITIL problem record — supersedes the legacy `problems` table.
    Problem,
    /// Production incident or outage.
    Incident,
    /// RFC or change advisory record.
    ChangeRequest,
    /// Contributor, author, or assignee.
    Person,
    /// Organisational team — supersedes the legacy `teams` table.
    Team,
    /// Target deployment environment.
    Environment,
    /// Generic binary or package output.
    Artifact,
    /// Observed measurement or SLO data point.
    Metric,
}

impl NodeKind {
    /// Returns the `&str` discriminant stored in the SQL `node_type` column.
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

    /// Parse a `NodeKind` from its SQL string discriminant.
    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "requirement" => Some(Self::Requirement),
            "specification" => Some(Self::Specification),
            "design" => Some(Self::Design),
            "source_file" => Some(Self::SourceFile),
            "module" => Some(Self::Module),
            "class" => Some(Self::Class),
            "function" => Some(Self::Function),
            "test" => Some(Self::Test),
            "test_suite" => Some(Self::TestSuite),
            "commit" => Some(Self::Commit),
            "pull_request" => Some(Self::PullRequest),
            "branch" => Some(Self::Branch),
            "issue" => Some(Self::Issue),
            "epic" => Some(Self::Epic),
            "story" => Some(Self::Story),
            "task" => Some(Self::Task),
            "bug" => Some(Self::Bug),
            "sprint" => Some(Self::Sprint),
            "release" => Some(Self::Release),
            "build" => Some(Self::Build),
            "deployment" => Some(Self::Deployment),
            "evidence" => Some(Self::Evidence),
            "problem" => Some(Self::Problem),
            "incident" => Some(Self::Incident),
            "change_request" => Some(Self::ChangeRequest),
            "person" => Some(Self::Person),
            "team" => Some(Self::Team),
            "environment" => Some(Self::Environment),
            "artifact" => Some(Self::Artifact),
            "metric" => Some(Self::Metric),
            _ => None,
        }
    }

    /// All variants in declaration order (useful for iteration / manifests).
    pub fn all() -> &'static [NodeKind] {
        &[
            Self::Requirement,
            Self::Specification,
            Self::Design,
            Self::SourceFile,
            Self::Module,
            Self::Class,
            Self::Function,
            Self::Test,
            Self::TestSuite,
            Self::Commit,
            Self::PullRequest,
            Self::Branch,
            Self::Issue,
            Self::Epic,
            Self::Story,
            Self::Task,
            Self::Bug,
            Self::Sprint,
            Self::Release,
            Self::Build,
            Self::Deployment,
            Self::Evidence,
            Self::Problem,
            Self::Incident,
            Self::ChangeRequest,
            Self::Person,
            Self::Team,
            Self::Environment,
            Self::Artifact,
            Self::Metric,
        ]
    }
}
