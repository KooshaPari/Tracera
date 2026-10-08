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

#[test]
fn product_assessment_excludes_other_product_and_baseline() {
    let engine = AssessmentEngine::default_24h();
    let own = observation("own", ObservationResult::Passed);
    let mut unrelated = observation("unrelated", ObservationResult::Failed);
    unrelated.product_id = ProductId::new("other-product");
    unrelated.baseline = BaselineRevision(9);
    let result = engine.assess_product("example-product", &[own, unrelated]);
    assert_eq!(result.status, AssessmentStatus::Satisfied);
    assert_eq!(result.baseline, BaselineRevision(1));
    assert_eq!(result.observation_count, 1);
    assert_eq!(result.findings.len(), 1);
}

#[test]
fn product_assessment_separates_capabilities() {
    let engine = AssessmentEngine::default_24h();
    let a = observation("a", ObservationResult::Passed);
    let mut b = observation("b", ObservationResult::Failed);
    b.capability_id = Some("cap-b".to_string());
    let result = engine.assess_product("example-product", &[a, b]);
    assert_eq!(result.status, AssessmentStatus::Violated);
    assert_eq!(result.findings.len(), 2);
    assert_eq!(result.observation_count, 2);
}

#[test]
fn product_assessment_ignores_superseded_baseline() {
    let engine = AssessmentEngine::default_24h();
    let old = observation("old", ObservationResult::Passed);
    let mut current = observation("current", ObservationResult::Failed);
    current.baseline = BaselineRevision(2);
    let result = engine.assess_product("example-product", &[old, current]);
    assert_eq!(result.status, AssessmentStatus::Violated);
    assert_eq!(result.baseline, BaselineRevision(2));
    assert_eq!(result.observation_count, 1);
    assert_eq!(result.findings[0].observation_ids, vec!["current".to_string()]);
}
