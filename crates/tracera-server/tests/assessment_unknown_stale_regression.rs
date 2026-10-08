//! Regression tests for source issue #1098: non-passing observation values.
use chrono::Utc;
use tracera_server::product::{
    AssessmentEngine, AssessmentStatus, BaselineRevision, Observation, ObservationKind,
    ObservationResult, ObservationSource, ProductId,
};

fn observation(id: &str, result: ObservationResult) -> Observation {
    Observation {
        id: id.to_string(),
        product_id: ProductId::new("example-product"),
        baseline: BaselineRevision(1),
        kind: ObservationKind::TestResult,
        result,
        source: ObservationSource {
            collector: "regression-test".to_string(),
            version: "1".to_string(),
            artifact_ref: None,
        },
        recorded_at: Utc::now(),
        capability_id: Some("cap-a".to_string()),
    }
}

#[test]
fn fresh_unknown_is_not_satisfied() {
    let e = AssessmentEngine::default_24h();
    let result = e.assess_capability("cap-a", &[observation("u", ObservationResult::Unknown)]);
    assert_eq!(result.status, AssessmentStatus::Unknown);
}

#[test]
fn fresh_stale_result_is_not_satisfied() {
    let e = AssessmentEngine::default_24h();
    let result = e.assess_capability("cap-a", &[observation("s", ObservationResult::Stale)]);
    assert_eq!(result.status, AssessmentStatus::Stale);
}

#[test]
fn passing_and_unknown_evidence_is_inconclusive() {
    let e = AssessmentEngine::default_24h();
    let result = e.assess_capability("cap-a", &[
        observation("p", ObservationResult::Passed),
        observation("u", ObservationResult::Unknown),
    ]);
    assert_eq!(result.status, AssessmentStatus::Inconclusive);
}

#[test]
fn passing_only_evidence_remains_satisfied() {
    let e = AssessmentEngine::default_24h();
    let result = e.assess_capability("cap-a", &[observation("p", ObservationResult::Passed)]);
    assert_eq!(result.status, AssessmentStatus::Satisfied);
}
