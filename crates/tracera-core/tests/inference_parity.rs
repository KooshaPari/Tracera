use tracera_core::{
    ArtifactKind, CoverageState, Neo4jSchema, RequirementStatus, TraceLink, TraceLinkType,
    VerificationMethod,
};
use uuid::Uuid;

macro_rules! json_case {
    ($name:ident, $ty:ty, $value:expr, $expected:expr) => {
        #[test]
        fn $name() {
            let json = serde_json::to_string(&$value).unwrap();
            assert_eq!(json, concat!("\"", $expected, "\""));
            assert_eq!(serde_json::from_str::<$ty>(&json).unwrap(), $value);
        }
    };
}

macro_rules! trace_case {
    ($name:ident, $value:expr, $expected:expr, $core:expr) => {
        #[test]
        fn $name() {
            let project_id = Uuid::new_v4();
            let source_id = Uuid::new_v4();
            let target_id = Uuid::new_v4();
            let link = TraceLink::new(project_id, source_id, target_id, $value).unwrap();

            assert_eq!($value.as_db_str(), $expected);
            assert_eq!(Neo4jSchema::relationship_label_for($value), $expected);
            assert_eq!(
                serde_json::to_string(&$value).unwrap(),
                concat!("\"", $expected, "\"")
            );
            assert_eq!(link.is_core(), $core);
        }
    };
}

macro_rules! artifact_case {
    ($name:ident, $value:expr, $json:expr, $label:expr) => {
        #[test]
        fn $name() {
            assert_eq!(
                serde_json::to_string(&$value).unwrap(),
                concat!("\"", $json, "\"")
            );
            assert_eq!(Neo4jSchema::node_label_for($value), $label);
            assert_eq!(
                serde_json::from_str::<ArtifactKind>(concat!("\"", $json, "\"")).unwrap(),
                $value
            );
        }
    };
}

trace_case!(
    trace_infers_satisfies,
    TraceLinkType::Satisfies,
    "SATISFIES",
    true
);
trace_case!(
    trace_infers_verifies,
    TraceLinkType::Verifies,
    "VERIFIES",
    true
);
trace_case!(
    trace_infers_implements,
    TraceLinkType::Implements,
    "IMPLEMENTS",
    true
);
trace_case!(
    trace_infers_derives_from,
    TraceLinkType::DerivesFrom,
    "DERIVES_FROM",
    true
);
trace_case!(
    trace_infers_refines,
    TraceLinkType::Refines,
    "REFINES",
    false
);
trace_case!(
    trace_infers_conflicts_with,
    TraceLinkType::ConflictsWith,
    "CONFLICTS_WITH",
    false
);
trace_case!(
    trace_infers_duplicates,
    TraceLinkType::Duplicates,
    "DUPLICATES",
    false
);
trace_case!(
    trace_infers_satisfies_schema_label,
    TraceLinkType::Satisfies,
    "SATISFIES",
    true
);
trace_case!(
    trace_infers_refines_non_core,
    TraceLinkType::Refines,
    "REFINES",
    false
);
trace_case!(
    trace_infers_duplicates_non_core,
    TraceLinkType::Duplicates,
    "DUPLICATES",
    false
);

artifact_case!(
    artifact_infers_requirement,
    ArtifactKind::Requirement,
    "requirement",
    "Requirement"
);
artifact_case!(
    artifact_infers_design,
    ArtifactKind::Design,
    "design",
    "Design"
);
artifact_case!(artifact_infers_code, ArtifactKind::Code, "code", "Code");
artifact_case!(artifact_infers_test, ArtifactKind::Test, "test", "Test");
artifact_case!(
    artifact_infers_evidence,
    ArtifactKind::Evidence,
    "evidence",
    "Evidence"
);
artifact_case!(artifact_infers_risk, ArtifactKind::Risk, "risk", "Risk");
artifact_case!(
    artifact_infers_rationale,
    ArtifactKind::Rationale,
    "rationale",
    "Rationale"
);
artifact_case!(
    artifact_infers_requirement_label,
    ArtifactKind::Requirement,
    "requirement",
    "Requirement"
);
artifact_case!(
    artifact_infers_evidence_label,
    ArtifactKind::Evidence,
    "evidence",
    "Evidence"
);
artifact_case!(
    artifact_infers_rationale_label,
    ArtifactKind::Rationale,
    "rationale",
    "Rationale"
);

json_case!(
    status_infers_draft,
    RequirementStatus,
    RequirementStatus::Draft,
    "draft"
);
json_case!(
    status_infers_proposed,
    RequirementStatus,
    RequirementStatus::Proposed,
    "proposed"
);
json_case!(
    status_infers_approved,
    RequirementStatus,
    RequirementStatus::Approved,
    "approved"
);
json_case!(
    status_infers_implemented,
    RequirementStatus,
    RequirementStatus::Implemented,
    "implemented"
);
json_case!(
    status_infers_verified,
    RequirementStatus,
    RequirementStatus::Verified,
    "verified"
);
json_case!(
    status_infers_deprecated,
    RequirementStatus,
    RequirementStatus::Deprecated,
    "deprecated"
);
json_case!(
    status_infers_rejected,
    RequirementStatus,
    RequirementStatus::Rejected,
    "rejected"
);
json_case!(
    status_infers_draft_roundtrip,
    RequirementStatus,
    RequirementStatus::Draft,
    "draft"
);
json_case!(
    status_infers_verified_roundtrip,
    RequirementStatus,
    RequirementStatus::Verified,
    "verified"
);
json_case!(
    status_infers_rejected_roundtrip,
    RequirementStatus,
    RequirementStatus::Rejected,
    "rejected"
);

json_case!(
    method_infers_test,
    VerificationMethod,
    VerificationMethod::Test,
    "test"
);
json_case!(
    method_infers_analysis,
    VerificationMethod,
    VerificationMethod::Analysis,
    "analysis"
);
json_case!(
    method_infers_inspection,
    VerificationMethod,
    VerificationMethod::Inspection,
    "inspection"
);
json_case!(
    method_infers_demonstration,
    VerificationMethod,
    VerificationMethod::Demonstration,
    "demonstration"
);
json_case!(
    method_infers_review,
    VerificationMethod,
    VerificationMethod::Review,
    "review"
);
json_case!(
    method_infers_test_roundtrip,
    VerificationMethod,
    VerificationMethod::Test,
    "test"
);
json_case!(
    method_infers_analysis_roundtrip,
    VerificationMethod,
    VerificationMethod::Analysis,
    "analysis"
);
json_case!(
    method_infers_inspection_roundtrip,
    VerificationMethod,
    VerificationMethod::Inspection,
    "inspection"
);
json_case!(
    method_infers_demonstration_roundtrip,
    VerificationMethod,
    VerificationMethod::Demonstration,
    "demonstration"
);
json_case!(
    method_infers_review_roundtrip,
    VerificationMethod,
    VerificationMethod::Review,
    "review"
);

json_case!(
    coverage_infers_covered,
    CoverageState,
    CoverageState::Covered,
    "covered"
);
json_case!(
    coverage_infers_partial,
    CoverageState,
    CoverageState::Partial,
    "partial"
);
json_case!(
    coverage_infers_missing,
    CoverageState,
    CoverageState::Missing,
    "missing"
);
json_case!(
    coverage_infers_stale,
    CoverageState,
    CoverageState::Stale,
    "stale"
);
json_case!(
    coverage_infers_conflict,
    CoverageState,
    CoverageState::Conflict,
    "conflict"
);
json_case!(
    coverage_infers_covered_roundtrip,
    CoverageState,
    CoverageState::Covered,
    "covered"
);
json_case!(
    coverage_infers_partial_roundtrip,
    CoverageState,
    CoverageState::Partial,
    "partial"
);
json_case!(
    coverage_infers_missing_roundtrip,
    CoverageState,
    CoverageState::Missing,
    "missing"
);
json_case!(
    coverage_infers_stale_roundtrip,
    CoverageState,
    CoverageState::Stale,
    "stale"
);
json_case!(
    coverage_infers_conflict_roundtrip,
    CoverageState,
    CoverageState::Conflict,
    "conflict"
);
