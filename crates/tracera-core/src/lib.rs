//! `tracera-core` — canonical TraceLink entity model, FR/NFR, matrix/coverage logic.
//!
//! Phase 1 of the 2026-06-09 Tracera decouple plan. This is a 1:1 port of
//! `Tracera/src/tracertm/models/trace_link.py` and
//! `Tracera/backend/internal/traceability/types.go` to Rust.
//!
//! Status: in-progress (2026-06-10). See README.md for the full decouple plan.

use chrono::{DateTime, Utc};
use indexmap::IndexMap;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use uuid::Uuid;

pub mod ids;
pub mod workspace;

pub mod coverage;
pub mod impact;
pub mod matrix; // Phase 2 stubs — see matrix.rs; excluded from default build until Phase 2 lands.
pub mod registry;
pub mod ui_links;

pub mod cache;
pub mod health;
pub mod notification;
pub mod observability;
pub mod pagination;
pub mod rate_limit;

pub use ids::*;
pub use workspace::*;

pub use cache::*;
pub use coverage::*;
pub use health::*;
pub use impact::*;
pub use matrix::*;
pub use notification::*;
pub use observability::*;
pub use pagination::*;
pub use rate_limit::*;
pub use registry::*;
pub use ui_links::*;

// ---------------------------------------------------------------------------
// Enums (canonical vocabulary shared by SQL, Neo4j, and API layers)
// ---------------------------------------------------------------------------

/// Canonical trace-link relationship vocabulary (ISO 29148 § 5.2.6 + DO-178C Table A-3).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum TraceLinkType {
    Satisfies,
    Verifies,
    Implements,
    DerivesFrom,
    Refines,
    ConflictsWith,
    Duplicates,
}

impl TraceLinkType {
    /// Returns the SCREAMING_SNAKE string for SQL/Neo4j round-trip.
    pub fn as_db_str(&self) -> &'static str {
        match self {
            Self::Satisfies => "SATISFIES",
            Self::Verifies => "VERIFIES",
            Self::Implements => "IMPLEMENTS",
            Self::DerivesFrom => "DERIVES_FROM",
            Self::Refines => "REFINES",
            Self::ConflictsWith => "CONFLICTS_WITH",
            Self::Duplicates => "DUPLICATES",
        }
    }
}

/// Core P0 subset called out in the SOTA research brief.
pub const CORE_TRACE_LINK_TYPES: &[TraceLinkType] = &[
    TraceLinkType::Satisfies,
    TraceLinkType::Verifies,
    TraceLinkType::Implements,
    TraceLinkType::DerivesFrom,
];

/// Role of an [`Artifact`] inside the traceability graph.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ArtifactKind {
    Requirement,
    Design,
    Code,
    Test,
    Evidence,
    Risk,
    Rationale,
}

impl ArtifactKind {
    /// Returns the primary Neo4j node label for this kind.
    pub fn neo4j_label(&self) -> &'static str {
        match self {
            Self::Requirement => "Requirement",
            Self::Design => "Design",
            Self::Code => "Code",
            Self::Test => "Test",
            Self::Evidence => "Evidence",
            Self::Risk => "Risk",
            Self::Rationale => "Rationale",
        }
    }
}

/// Lifecycle states for a [`Requirement`] (ISO 29148 § 5.2.8).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RequirementStatus {
    Draft,
    Proposed,
    Approved,
    Implemented,
    Verified,
    Deprecated,
    Rejected,
}

/// DO-178C / IEEE 1012 verification methods used on VERIFIES links.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum VerificationMethod {
    Test,
    Analysis,
    Inspection,
    Demonstration,
    Review,
}

// ---------------------------------------------------------------------------
// Value objects
// ---------------------------------------------------------------------------

/// Any node in the traceability graph (super-type of [`Requirement`]).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Artifact {
    pub id: Uuid,
    pub project_id: Uuid,
    pub kind: ArtifactKind,
    pub title: String,
    pub description: Option<String>,
    pub external_id: Option<String>,
    pub metadata: BTreeMap<String, serde_json::Value>,
    pub created_at: Option<DateTime<Utc>>,
    pub updated_at: Option<DateTime<Utc>>,
}

/// A traceable requirement.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Requirement {
    #[serde(flatten)]
    pub artifact: Artifact,
    pub status: RequirementStatus,
    pub priority: Option<u8>, // 0..=5
    pub rationale: Option<String>,
    pub acceptance_criteria: Vec<String>,
    pub verification_method: Option<VerificationMethod>,
}

impl Requirement {
    /// Construct a Requirement with the right defaults (kind pinned to Requirement).
    pub fn new(artifact: Artifact) -> Result<Self, TraceLinkError> {
        if artifact.kind != ArtifactKind::Requirement {
            return Err(TraceLinkError::WrongArtifactKind {
                expected: ArtifactKind::Requirement,
                got: artifact.kind,
            });
        }
        Ok(Self {
            artifact,
            status: RequirementStatus::Draft,
            priority: None,
            rationale: None,
            acceptance_criteria: Vec::new(),
            verification_method: None,
        })
    }
}

/// A confidence-scored directed edge in the traceability graph.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TraceLink {
    pub id: Uuid,
    pub project_id: Uuid,
    pub source_artifact_id: Uuid,
    pub target_artifact_id: Uuid,
    pub from: ArtifactRef,
    pub to: ArtifactRef,
    pub link_type: TraceLinkType,
    /// 0.0..=1.0; 1.0 for human-curated links.
    pub confidence: f32,
    pub rationale: Option<String>,
    pub metadata: BTreeMap<String, serde_json::Value>,
    pub created_at: Option<DateTime<Utc>>,
    pub updated_at: Option<DateTime<Utc>>,
}

impl TraceLink {
    /// Create a new TraceLink, validating that source != target and confidence in range.
    pub fn new(
        project_id: Uuid,
        source: Uuid,
        target: Uuid,
        link_type: TraceLinkType,
    ) -> Result<Self, TraceLinkError> {
        if source == target {
            return Err(TraceLinkError::SelfLoop);
        }
        Ok(Self {
            id: Uuid::new_v4(),
            project_id,
            source_artifact_id: source,
            target_artifact_id: target,
            from: ArtifactRef::CodeEntity {
                id: source.to_string(),
                lang: "uuid".to_string(),
            },
            to: ArtifactRef::CodeEntity {
                id: target.to_string(),
                lang: "uuid".to_string(),
            },
            link_type,
            confidence: 1.0,
            rationale: None,
            metadata: BTreeMap::new(),
            created_at: Some(Utc::now()),
            updated_at: Some(Utc::now()),
        })
    }

    /// True if this link uses one of the P0 SOTA link types.
    pub fn is_core(&self) -> bool {
        CORE_TRACE_LINK_TYPES.contains(&self.link_type)
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum ArtifactRef {
    Requirement { id: RequirementId },
    NonFunctionalRequirement { id: NfrId },
    Test { id: String },
    CodeEntity { id: String, lang: String },
    Journey { id: String },
    AgentRun { id: String },
    Evidence { id: String, sha256: String },
    Document { id: String, range: Option<String> },
}

impl ArtifactRef {
    pub fn kind_str(&self) -> String {
        match self {
            Self::Requirement { .. } => "requirement",
            Self::NonFunctionalRequirement { .. } => "nfr",
            Self::Test { .. } => "test",
            Self::CodeEntity { .. } => "code",
            Self::Journey { .. } => "journey",
            Self::AgentRun { .. } => "agent",
            Self::Evidence { .. } => "evidence",
            Self::Document { .. } => "document",
        }
        .to_string()
    }
}

pub type LinkKind = TraceLinkType;

#[derive(Debug, thiserror::Error)]
pub enum TraceLinkError {
    #[error("TraceLink source_artifact_id and target_artifact_id must differ")]
    SelfLoop,
    #[error("Requirement.kind must be REQUIREMENT, got {got:?}")]
    WrongArtifactKind {
        expected: ArtifactKind,
        got: ArtifactKind,
    },
    #[error("confidence must be in 0.0..=1.0, got {0}")]
    BadConfidence(f32),
}

// ---------------------------------------------------------------------------
// Coverage state (re-exported from coverage module for convenience)
// ---------------------------------------------------------------------------

pub use crate::coverage::CoverageSummary;

/// Coverage matrix - the main output of a Tracera coverage scan.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct CoverageMatrix {
    pub cells: IndexMap<(String, String), MatrixCell>,
    pub generated_at: DateTime<Utc>,
}

/// Coverage matrix cell.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct MatrixCell {
    pub from: String,
    pub to: String,
    pub trace_links: Vec<TraceLink>,
    pub coverage: CoverageState,
}

/// Coverage state for a single cell.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CoverageState {
    Covered,
    Partial,
    Missing,
    Stale,
    Conflict,
}

// ---------------------------------------------------------------------------
// Neo4j schema (declarative DDL)
// ---------------------------------------------------------------------------

/// Neo4j relationship labels (one per [`TraceLinkType`]).
pub const NEO4J_RELATIONSHIP_TYPES: &[&str] = &[
    "SATISFIES",
    "VERIFIES",
    "IMPLEMENTS",
    "DERIVES_FROM",
    "REFINES",
    "CONFLICTS_WITH",
    "DUPLICATES",
];

/// Neo4j node labels.
pub const NEO4J_NODE_LABELS: &[&str] = &[
    "Artifact",
    "Requirement",
    "Design",
    "Code",
    "Test",
    "Evidence",
    "Risk",
    "Rationale",
    "Project",
];

/// Declarative Cypher schema for the trace-link graph projection.
pub struct Neo4jSchema;

impl Neo4jSchema {
    /// Uniqueness / existence constraints.
    pub const CONSTRAINTS: &'static [&'static str] = &[
        "CREATE CONSTRAINT artifact_id_unique IF NOT EXISTS FOR (a:Artifact) REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT requirement_id_unique IF NOT EXISTS FOR (r:Requirement) REQUIRE r.id IS UNIQUE",
        "CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
    ];

    /// Lookup / range indexes for the common RAG-side queries.
    pub const INDEXES: &'static [&'static str] = &[
        "CREATE INDEX artifact_project_kind IF NOT EXISTS FOR (a:Artifact) ON (a.project_id, a.kind)",
        "CREATE INDEX artifact_external_id IF NOT EXISTS FOR (a:Artifact) ON (a.external_id)",
        "CREATE INDEX requirement_status IF NOT EXISTS FOR (r:Requirement) ON (r.status)",
        "CREATE FULLTEXT INDEX artifact_text IF NOT EXISTS FOR (a:Artifact) ON EACH [a.title, a.description]",
    ];

    /// All DDL statements in apply order (constraints before indexes).
    pub fn all_statements() -> Vec<&'static str> {
        let mut s: Vec<&'static str> = Self::CONSTRAINTS.to_vec();
        s.extend_from_slice(Self::INDEXES);
        s
    }

    /// Return the Neo4j relationship label for a given TraceLinkType.
    pub fn relationship_label_for(link_type: TraceLinkType) -> &'static str {
        link_type.as_db_str()
    }

    /// Return the primary Neo4j node label for a given ArtifactKind.
    pub fn node_label_for(kind: ArtifactKind) -> &'static str {
        kind.neo4j_label()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn trace_link_roundtrips() {
        let link = TraceLink::new(
            Uuid::new_v4(),
            Uuid::new_v4(),
            Uuid::new_v4(),
            TraceLinkType::Verifies,
        )
        .unwrap();
        assert!(link.is_core());
        let json = serde_json::to_string(&link).unwrap();
        let parsed: TraceLink = serde_json::from_str(&json).unwrap();
        assert_eq!(link.id, parsed.id);
        assert_eq!(link.link_type, parsed.link_type);
    }

    #[test]
    fn trace_link_rejects_self_loop() {
        let id = Uuid::new_v4();
        let result = TraceLink::new(Uuid::new_v4(), id, id, TraceLinkType::Satisfies);
        assert!(matches!(result, Err(TraceLinkError::SelfLoop)));
    }

    #[test]
    fn requirement_rejects_wrong_kind() {
        let artifact = Artifact {
            id: Uuid::new_v4(),
            project_id: Uuid::new_v4(),
            kind: ArtifactKind::Code,
            title: "not a requirement".to_string(),
            description: None,
            external_id: None,
            metadata: BTreeMap::new(),
            created_at: None,
            updated_at: None,
        };
        let result = Requirement::new(artifact);
        assert!(matches!(
            result,
            Err(TraceLinkError::WrongArtifactKind { .. })
        ));
    }

    #[test]
    fn link_type_db_strings() {
        assert_eq!(TraceLinkType::Satisfies.as_db_str(), "SATISFIES");
        assert_eq!(TraceLinkType::ConflictsWith.as_db_str(), "CONFLICTS_WITH");
        assert_eq!(TraceLinkType::DerivesFrom.as_db_str(), "DERIVES_FROM");
    }

    #[test]
    fn trace_link_ui_link_navigates_from_requirement_to_test() {
        let mut link = TraceLink::new(
            Uuid::new_v4(),
            Uuid::new_v4(),
            Uuid::new_v4(),
            TraceLinkType::Verifies,
        )
        .unwrap();
        link.from = ArtifactRef::Requirement {
            id: RequirementId::from_string("FR-77"),
        };
        link.to = ArtifactRef::Test {
            id: "checkout flow/test verifies receipt".to_string(),
        };

        let ui_link = link.ui_link();

        assert_eq!(ui_link.href, format!("/trace-links/{}", link.id));
        assert_eq!(ui_link.source_href, "/requirements/FR-77");
        assert_eq!(
            ui_link.target_href,
            "/tests/checkout%20flow%2Ftest%20verifies%20receipt"
        );
        assert_eq!(ui_link.source_label, "FR-77");
        assert_eq!(ui_link.target_label, "checkout flow/test verifies receipt");
        assert_eq!(ui_link.link_type, TraceLinkType::Verifies);
    }

    #[test]
    fn neo4j_schema_statements_idempotent() {
        let stmts = Neo4jSchema::all_statements();
        assert!(stmts.len() >= 7);
        for s in &stmts {
            assert!(s.contains("IF NOT EXISTS"), "not idempotent: {}", s);
        }
    }

    #[test]
    fn neo4j_labels() {
        assert_eq!(
            Neo4jSchema::node_label_for(ArtifactKind::Requirement),
            "Requirement"
        );
        assert_eq!(
            Neo4jSchema::relationship_label_for(TraceLinkType::Verifies),
            "VERIFIES"
        );
    }
}
