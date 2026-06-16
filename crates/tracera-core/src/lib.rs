//! `tracera-core` — thin Tracera live-service crate on [`traceability_core`].
//!
//! Shared domain types (`Artifact`, `Requirement`, `TraceLink`, coverage matrix,
//! impact analysis, ids) are re-exported from `traceability-core` so there is
//! ONE model across phenotype-pm-core and Tracera. This crate keeps Tracera-only
//! service glue: UI link navigation, coverage summaries, registry, and ops helpers.

pub mod cache;
pub mod config;
pub mod coverage;
pub mod health;
pub mod ids;
pub mod impact;
pub mod matrix;
pub mod notification;
pub mod observability;
pub mod pagination;
pub mod rate_limit;
pub mod registry;
pub mod ui_links;
pub mod workspace;

// ---------------------------------------------------------------------------
// Shared core re-exports (ONE model)
// ---------------------------------------------------------------------------

pub use traceability_core::{
    build_from_pairs, build_matrix, classify_cell, neighbors,
    Artifact, ArtifactKind, ArtifactRef, BlastNode, BuildResult, CoverageMatrix, CoverageState,
    CORE_TRACE_LINK_TYPES, ImpactConfig, ImpactReport, LinkKind, MatrixCell, NfrId,
    NEO4J_NODE_LABELS, NEO4J_RELATIONSHIP_TYPES, Neo4jSchema, Requirement, RequirementId,
    RequirementStatus, TraceLink, TraceLinkError, TraceLinkType, VerificationMethod,
    compute_impact, conflicts_only, is_core_link_type, top_affected,
};
pub use traceability_core::matrix::{added, changed, removed};

pub use coverage::CoverageSummary;
pub use cache::*;
pub use health::*;
pub use notification::*;
pub use observability::*;
pub use pagination::*;
pub use rate_limit::*;
pub use registry::*;
pub use ui_links::*;
pub use workspace::*;

#[cfg(test)]
mod tests {
    use super::*;
    use traceability_core::ids::RequirementId;

    #[test]
    fn trace_link_roundtrips_via_shared_core() {
        let link = TraceLink::new(
            uuid::Uuid::new_v4(),
            uuid::Uuid::new_v4(),
            uuid::Uuid::new_v4(),
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
    fn trace_link_ui_link_navigates_from_requirement_to_test() {
        let mut link = TraceLink::new(
            uuid::Uuid::new_v4(),
            uuid::Uuid::new_v4(),
            uuid::Uuid::new_v4(),
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
    fn neo4j_schema_reexported_from_shared_core() {
        let stmts = Neo4jSchema::all_statements();
        assert!(stmts.len() >= 7);
        for s in &stmts {
            assert!(s.contains("IF NOT EXISTS"), "not idempotent: {s}");
        }
        assert_eq!(
            Neo4jSchema::node_label_for(ArtifactKind::Requirement),
            "Requirement"
        );
        assert_eq!(
            Neo4jSchema::relationship_label_for(TraceLinkType::Verifies),
            "VERIFIES"
        );
    }

    #[test]
    fn trace_link_rejects_self_loop() {
        let id = uuid::Uuid::new_v4();
        let result = TraceLink::new(uuid::Uuid::new_v4(), id, id, TraceLinkType::Satisfies);
        assert!(matches!(result, Err(TraceLinkError::SelfLoop)));
    }

    #[test]
    fn requirement_rejects_wrong_kind() {
        use std::collections::BTreeMap;
        let artifact = Artifact {
            id: uuid::Uuid::new_v4(),
            project_id: uuid::Uuid::new_v4(),
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
}
