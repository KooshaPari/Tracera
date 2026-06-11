//! `tracera-core` — canonical TraceLink entity model, FR/NFR, matrix/coverage logic.
//!
//! Status: scaffold (2026-06-10). See README.md for the full decouple plan.

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use indexmap::IndexMap;

pub mod ids;
pub mod matrix;
pub mod impact;
pub mod coverage;

pub use ids::*;
pub use matrix::*;
pub use coverage::*;

/// Status of a requirement.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RequirementStatus {
    Draft,
    Proposed,
    Accepted,
    Implemented,
    Verified,
    Deprecated,
}

/// Link from a requirement to an evidence artifact (test, code, journey, agent run, etc.).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TraceLink {
    pub id: TraceLinkId,
    pub from: ArtifactRef,
    pub to: ArtifactRef,
    pub kind: LinkKind,
    pub confidence: f32,
    pub created_at: DateTime<Utc>,
    pub created_by: String,
}

/// Type of artifact (requirement, test, code entity, journey, agent run, etc.).
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case", tag = "kind")]
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

/// Link kind.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LinkKind {
    Satisfies,
    Verifies,
    Refines,
    Conflicts,
    Depends,
    Supersedes,
    Derives,
}

/// Coverage matrix cell.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct MatrixCell {
    pub from: ArtifactRef,
    pub to: ArtifactRef,
    pub trace_links: Vec<TraceLink>,
    pub coverage: CoverageState,
}

/// Coverage state.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CoverageState {
    Covered,
    Partial,
    Missing,
    Stale,
    Conflict,
}

/// Coverage matrix.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct CoverageMatrix {
    pub cells: IndexMap<(String, String), MatrixCell>,
    pub generated_at: DateTime<Utc>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn trace_link_roundtrips() {
        let link = TraceLink {
            id: TraceLinkId::new(),
            from: ArtifactRef::Requirement { id: RequirementId::new() },
            to: ArtifactRef::Test { id: "T-001".to_string() },
            kind: LinkKind::Verifies,
            confidence: 0.95,
            created_at: Utc::now(),
            created_by: "test".to_string(),
        };
        let json = serde_json::to_string(&link).unwrap();
        let parsed: TraceLink = serde_json::from_str(&json).unwrap();
        assert_eq!(link, parsed);
    }
}
