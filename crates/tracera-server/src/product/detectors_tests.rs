use super::*;
use crate::product::identity::{BaselineRevision, IntentKind, IntentStatus, ProductId};
use crate::product::observation::{ObservationKind, ObservationSource};

fn ts(secs: i64) -> DateTime<Utc> {
    DateTime::from_timestamp(secs, 0).unwrap()
}

fn make_obs(id: &str, product: &str, result: ObservationResult, recorded_at: i64) -> Observation {
    Observation {
        id: id.to_string(),
        product_id: ProductId::new(product),
        baseline: BaselineRevision(1),
        kind: ObservationKind::TestResult,
        result,
        source: ObservationSource {
            collector: "test".to_string(),
            version: "0.1.0".to_string(),
            causality: None,
            artifact_ref: None,
        },
        recorded_at: ts(recorded_at),
        capability_id: Some(product.to_string()),
    }
}

fn make_obs_at_baseline(
    id: &str,
    product: &str,
    result: ObservationResult,
    recorded_at: i64,
    baseline: u64,
) -> Observation {
    Observation {
        id: id.to_string(),
        product_id: ProductId::new(product),
        baseline: BaselineRevision(baseline),
        kind: ObservationKind::TestResult,
        result,
        source: ObservationSource {
            collector: "test".to_string(),
            version: "0.1.0".to_string(),
            causality: None,
            artifact_ref: None,
        },
        recorded_at: ts(recorded_at),
        capability_id: Some(product.to_string()),
    }
}

fn make_intent(id: &str) -> AcceptedIntent {
    AcceptedIntent {
        id: id.to_string(),
        kind: IntentKind::Capability,
        title: format!("Title for {id}"),
        description: String::new(),
        status: IntentStatus::Accepted,
        baseline: BaselineRevision(1),
    }
}

// --- T07: Missing required proof is unknown ---

#[test]
fn t07_coverage_finds_unobserved_capability() {
    let det = CoverageDetector::new();
    let intents = vec![make_intent("cap-a"), make_intent("cap-b")];
    let mut proof = make_obs("o1", "product-a", ObservationResult::Passed, 1_000_000);
    proof.capability_id = Some("cap-a".into());
    let observations = vec![proof];
    let findings = det.detect(&ProductId::new("product-a"), &intents, &observations);
    assert_eq!(findings.len(), 1);
    assert_eq!(findings[0].kind, FindingKind::Coverage);
    assert_eq!(findings[0].capability_id.as_deref(), Some("cap-b"));
    assert!(findings[0].message.contains("unknown"));
}

// --- T08: Old artifact proof is stale ---

#[test]
fn t08_freshness_detects_old_observation() {
    let det = FreshnessDetector::new(100);
    let obs = vec![make_obs("o1", "cap-1", ObservationResult::Passed, 1_000)];
    // Current time is ~1.7 billion, observation is at 1000s => billions of seconds old
    let findings = det.detect(&obs);
    assert_eq!(findings.len(), 1);
    assert_eq!(findings[0].kind, FindingKind::Freshness);
    assert_eq!(findings[0].severity, FindingSeverity::Medium);
}

// --- T09: Changed expectation (different baseline) no false contradiction ---

#[test]
fn t09_different_baseline_no_contradiction() {
    let det = ContradictionDetector::new();
    let obs = vec![
        make_obs_at_baseline("o1", "cap-1", ObservationResult::Passed, 1_000_000, 1),
        make_obs_at_baseline("o2", "cap-1", ObservationResult::Failed, 2_000_000, 2),
    ];
    let findings = det.detect(&obs);
    assert_eq!(findings.len(), 0); // different baselines = different contracts
}

// --- T10: Expired result is not current ---

#[test]
fn t10_expired_result_freshness_finding() {
    let det = FreshnessDetector::new(3600); // 1 hour
    let obs = vec![make_obs("o1", "cap-1", ObservationResult::Passed, 1_000)];
    let findings = det.detect(&obs);
    assert_eq!(findings.len(), 1);
    assert!(findings[0].message.contains("seconds old"));
}

// --- T12: Conflicting same-baseline results ---

#[test]
fn t12_same_baseline_contradiction() {
    let det = ContradictionDetector::new();
    let obs = vec![
        make_obs_at_baseline("o1", "cap-1", ObservationResult::Passed, 1_000_000, 1),
        make_obs_at_baseline("o2", "cap-1", ObservationResult::Failed, 1_000_000, 1),
    ];
    let findings = det.detect(&obs);
    assert_eq!(findings.len(), 1);
    assert_eq!(findings[0].kind, FindingKind::Contradiction);
    assert_eq!(findings[0].severity, FindingSeverity::High);
    assert_eq!(findings[0].evidence.len(), 2);
}

#[test]
fn no_findings_on_clean_data() {
    let fresh_obs = Observation {
        id: "o1".to_string(),
        product_id: ProductId::new("cap-1"),
        baseline: BaselineRevision(1),
        kind: ObservationKind::TestResult,
        result: ObservationResult::Passed,
        source: ObservationSource {
            collector: "test".to_string(),
            version: "0.1.0".to_string(),
            causality: None,
            artifact_ref: None,
        },
        recorded_at: Utc::now(),
        capability_id: None,
    };
    let fd = FreshnessDetector::new(86_400);
    let cd = ContradictionDetector::new();
    // Call contradiction first (borrows), then freshness (consumes via clone avoided)
    let slice = [fresh_obs];
    assert!(fd.detect(&slice).is_empty());
    assert!(cd.detect(&slice).is_empty());
}

#[test]
fn freshness_high_for_failed_stale() {
    let det = FreshnessDetector::new(100);
    let obs = vec![make_obs("o1", "cap-1", ObservationResult::Failed, 1_000)];
    let findings = det.detect(&obs);
    assert_eq!(findings[0].severity, FindingSeverity::High);
}

#[test]
fn coverage_no_intents_no_findings() {
    let det = CoverageDetector::new();
    let findings = det.detect(&ProductId::new("product-a"), &[], &[]);
    assert!(findings.is_empty());
}

#[test]
fn detector_version_recorded() {
    let det = FreshnessDetector::new(100);
    let obs = vec![make_obs("o1", "cap-1", ObservationResult::Passed, 1_000)];
    let findings = det.detect(&obs);
    assert_eq!(findings[0].detector_version, DetectorVersion::current());
}

#[test]
fn suite_combined_results() {
    let suite = ProductDetectorSuite::new(100);
    let intents = vec![make_intent("cap-a"), make_intent("cap-b")];
    let observations = vec![
        make_obs("o1", "cap-a", ObservationResult::Passed, 1_000), // stale
    ];
    let result = suite.run(&ProductId::new("product-a"), &intents, &observations);
    // Should find: freshness (o1 is old) + coverage (cap-b has no obs)
    assert!(result.findings.len() >= 2);
    assert_eq!(result.detector_version, DetectorVersion::current());
    assert_eq!(result.capabilities_scanned, 2);
}

#[test]
fn finding_serializable() {
    let det = FreshnessDetector::new(100);
    let obs = vec![make_obs("o1", "cap-1", ObservationResult::Passed, 1_000)];
    let findings = det.detect(&obs);
    let json = serde_json::to_string(&findings[0]).unwrap();
    let roundtrip: DetectorFinding = serde_json::from_str(&json).unwrap();
    assert_eq!(roundtrip.kind, FindingKind::Freshness);
}

#[test]
fn freshness_preserves_capability_identity() {
    let mut obs = make_obs("stale", "product-a", ObservationResult::Passed, 1);
    obs.capability_id = Some("cap-a".into());
    let findings = FreshnessDetector::new(1).detect(std::slice::from_ref(&obs));
    assert_eq!(findings[0].product_id, "product-a");
    assert_eq!(findings[0].capability_id.as_deref(), Some("cap-a"));
    obs.capability_id = None;
    assert_eq!(
        FreshnessDetector::new(1).detect(&[obs])[0].capability_id,
        None
    );
}

#[test]
fn contradictions_do_not_cross_capabilities() {
    let mut passed = make_obs("pass", "product-a", ObservationResult::Passed, 1);
    passed.capability_id = Some("cap-a".into());
    let mut failed = make_obs("fail", "product-a", ObservationResult::Failed, 1);
    failed.capability_id = Some("cap-b".into());
    assert!(ContradictionDetector::new()
        .detect(&[passed, failed])
        .is_empty());
}

#[test]
fn contradiction_reports_actual_capability() {
    let mut passed = make_obs("pass", "product-a", ObservationResult::Passed, 1);
    passed.capability_id = Some("cap-a".into());
    let mut failed = make_obs("fail", "product-a", ObservationResult::Failed, 1);
    failed.capability_id = Some("cap-a".into());
    let findings = ContradictionDetector::new().detect(&[passed, failed]);
    assert_eq!(findings.len(), 1);
    assert_eq!(findings[0].product_id, "product-a");
    assert_eq!(findings[0].capability_id.as_deref(), Some("cap-a"));
}

#[test]
fn coverage_matches_capability_not_product_name() {
    let mut obs = make_obs("proof", "product-a", ObservationResult::Passed, 1);
    obs.capability_id = Some("cap-a".into());
    assert!(CoverageDetector::new()
        .detect(
            &ProductId::new("product-a"),
            &[make_intent("cap-a")],
            &[obs]
        )
        .is_empty());
}

#[test]
fn coverage_isolates_product_and_baseline() {
    let product = ProductId::new("product-a");
    let intent = make_intent("cap-a");
    let mut proof = make_obs("proof", "product-b", ObservationResult::Passed, 1);
    proof.capability_id = Some("cap-a".into());
    let detector = CoverageDetector::new();
    assert_eq!(
        detector
            .detect(
                &product,
                std::slice::from_ref(&intent),
                std::slice::from_ref(&proof)
            )
            .len(),
        1
    );
    proof.product_id = product.clone();
    proof.baseline = BaselineRevision(2);
    assert_eq!(
        detector
            .detect(
                &product,
                std::slice::from_ref(&intent),
                std::slice::from_ref(&proof)
            )
            .len(),
        1
    );
    proof.baseline = BaselineRevision(1);
    assert!(detector.detect(&product, &[intent], &[proof]).is_empty());
}

#[test]
fn contradictions_isolate_products_and_product_level_observations() {
    let mut passed = make_obs("pass", "product-a", ObservationResult::Passed, 1);
    passed.capability_id = Some("cap-a".into());
    let mut failed = passed.clone();
    failed.id = "fail".into();
    failed.result = ObservationResult::Failed;
    failed.product_id = ProductId::new("product-b");
    assert!(ContradictionDetector::new()
        .detect(&[passed.clone(), failed.clone()])
        .is_empty());
    failed.product_id = passed.product_id.clone();
    failed.capability_id = None;
    assert!(ContradictionDetector::new()
        .detect(&[passed, failed])
        .is_empty());
}
