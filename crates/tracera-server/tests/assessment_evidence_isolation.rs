//! Acceptance regressions for issue #1098 — assessment evidence isolation.
//!
//! These tests encode the six acceptance criteria stated on
//! <https://github.com/KooshaPari/Tracera/issues/1098>:
//!
//! 1. two capabilities within one product do not contaminate each other;
//! 2. baseline-1 passing evidence cannot satisfy a baseline-2 intent;
//! 3. fresh `Unknown` / `Stale` results are never `Satisfied`;
//! 4. unrelated product evidence cannot change count, baseline or verdict;
//! 5. legacy observations without `capability_id` have an explicit
//!    compatibility contract;
//! 6. cross-product identical capability IDs are resolved by explicit
//!    product scope (with the `AcceptedIntent` identity gap documented).

use chrono::Utc;
use tracera_server::product::{
    AcceptedIntent, AssessmentEngine, AssessmentStatus, BaselineRevision, IntentKind, IntentStatus,
    Observation, ObservationKind, ObservationResult, ObservationSource, ProductId,
};

const PRODUCT: &str = "example-product";
const OTHER_PRODUCT: &str = "other-product";

fn observation_at(
    id: &str,
    product: &str,
    baseline: u64,
    capability: Option<&str>,
    result: ObservationResult,
) -> Observation {
    Observation {
        id: id.to_string(),
        product_id: ProductId::new(product),
        baseline: BaselineRevision(baseline),
        kind: ObservationKind::TestResult,
        result,
        source: ObservationSource {
            collector: "issue-1098-regression".to_string(),
            version: "1".to_string(),
            artifact_ref: None,
        },
        recorded_at: Utc::now(),
        capability_id: capability.map(str::to_string),
    }
}

fn obs(id: &str, capability: &str, result: ObservationResult) -> Observation {
    observation_at(id, PRODUCT, 1, Some(capability), result)
}

fn obs_on_baseline(
    id: &str,
    capability: &str,
    baseline: u64,
    result: ObservationResult,
) -> Observation {
    observation_at(id, PRODUCT, baseline, Some(capability), result)
}

fn capability_intent(id: &str, baseline: u64) -> AcceptedIntent {
    AcceptedIntent {
        id: id.to_string(),
        kind: IntentKind::Capability,
        title: format!("Capability {id}"),
        description: String::new(),
        status: IntentStatus::Accepted,
        baseline: BaselineRevision(baseline),
    }
}

fn finding_for<'a>(
    result: &'a tracera_server::product::AssessmentResult,
    capability_id: &str,
) -> &'a tracera_server::product::AssessmentFinding {
    result
        .findings
        .iter()
        .find(|f| f.capability_id.as_deref() == Some(capability_id))
        .unwrap_or_else(|| panic!("no finding for capability '{capability_id}'"))
}

// ---------------------------------------------------------------------------
// 1. Two capabilities within one product must not contaminate each other.
// ---------------------------------------------------------------------------

#[test]
fn two_capabilities_in_one_product_are_isolated() {
    let engine = AssessmentEngine::default_24h();
    let observations = vec![
        obs("a-pass", "cap-a", ObservationResult::Passed),
        obs("b-fail", "cap-b", ObservationResult::Failed),
    ];

    let result = engine.assess_product(PRODUCT, &observations);

    assert_eq!(
        result.findings.len(),
        2,
        "each capability needs its own finding"
    );
    assert_eq!(
        finding_for(&result, "cap-a").status,
        AssessmentStatus::Satisfied,
        "capability A passed and must not inherit B's failure"
    );
    assert_eq!(
        finding_for(&result, "cap-a").observation_ids,
        vec!["a-pass".to_string()],
        "capability A's evidence set must contain only its own observation"
    );
    assert_eq!(
        finding_for(&result, "cap-b").status,
        AssessmentStatus::Violated,
        "capability B failed"
    );
    assert_eq!(
        finding_for(&result, "cap-b").observation_ids,
        vec!["b-fail".to_string()],
        "capability B's evidence set must contain only its own observation"
    );
    assert_eq!(result.status, AssessmentStatus::Violated);
    assert_eq!(result.observation_count, 2);
}

#[test]
fn scoped_intents_keep_two_capabilities_isolated() {
    let engine = AssessmentEngine::default_24h();
    let intents = vec![capability_intent("cap-a", 1), capability_intent("cap-b", 1)];
    let observations = vec![
        obs("a-pass", "cap-a", ObservationResult::Passed),
        obs("b-fail", "cap-b", ObservationResult::Failed),
    ];

    let result =
        engine.assess_scoped_intents(PRODUCT, BaselineRevision(1), &intents, &observations);

    assert_eq!(
        finding_for(&result, "cap-a").status,
        AssessmentStatus::Satisfied
    );
    assert_eq!(
        finding_for(&result, "cap-b").status,
        AssessmentStatus::Violated
    );
    assert_eq!(result.status, AssessmentStatus::Violated);
}

// ---------------------------------------------------------------------------
// 2. Baseline-1 passing evidence cannot satisfy a baseline-2 intent.
// ---------------------------------------------------------------------------

#[test]
fn baseline_one_passing_evidence_cannot_satisfy_baseline_two_intent() {
    let engine = AssessmentEngine::default_24h();
    let intents = vec![capability_intent("cap-a", 2)];
    let observations = vec![obs_on_baseline(
        "old-pass",
        "cap-a",
        1,
        ObservationResult::Passed,
    )];

    let result =
        engine.assess_scoped_intents(PRODUCT, BaselineRevision(2), &intents, &observations);

    assert_eq!(
        result.status,
        AssessmentStatus::Unknown,
        "baseline-1 evidence must not satisfy a baseline-2 capability"
    );
    assert_eq!(result.observation_count, 0, "no observation was in scope");
    assert_eq!(result.baseline, BaselineRevision(2));
}

#[test]
fn baseline_one_passing_evidence_cannot_satisfy_baseline_two_legacy_intent() {
    let engine = AssessmentEngine::default_24h();
    let intents = vec![capability_intent("cap-a", 2)];
    let observations = vec![obs_on_baseline(
        "old-pass",
        "cap-a",
        1,
        ObservationResult::Passed,
    )];

    // Legacy entry point: the evidence key is still `Observation.product_id`
    // (legacy convention), but baseline scoping must already hold.
    let result = engine.assess_with_intents(&intents, &observations);

    assert_eq!(
        result.status,
        AssessmentStatus::Unknown,
        "legacy assessment must not reuse stale-baseline evidence"
    );
    assert!(result.findings.iter().all(|f| f.observation_ids.is_empty()));
}

#[test]
fn baseline_two_evidence_satisfies_baseline_two_intent() {
    let engine = AssessmentEngine::default_24h();
    let intents = vec![capability_intent("cap-a", 2)];
    let observations = vec![obs_on_baseline(
        "new-pass",
        "cap-a",
        2,
        ObservationResult::Passed,
    )];

    let result =
        engine.assess_scoped_intents(PRODUCT, BaselineRevision(2), &intents, &observations);
    assert_eq!(result.status, AssessmentStatus::Satisfied);
    assert_eq!(result.observation_count, 1);
}

// ---------------------------------------------------------------------------
// 3. Fresh `Unknown` and `Stale` result values must never be `Satisfied`.
// ---------------------------------------------------------------------------

#[test]
fn fresh_unknown_result_is_not_satisfied() {
    let engine = AssessmentEngine::default_24h();
    let finding =
        engine.assess_capability("cap-a", &[obs("u", "cap-a", ObservationResult::Unknown)]);
    assert_eq!(finding.status, AssessmentStatus::Unknown);
}

#[test]
fn fresh_stale_result_is_not_satisfied() {
    let engine = AssessmentEngine::default_24h();
    let finding = engine.assess_capability("cap-a", &[obs("s", "cap-a", ObservationResult::Stale)]);
    assert_eq!(finding.status, AssessmentStatus::Stale);
}

#[test]
fn passing_plus_unknown_is_not_satisfied() {
    let engine = AssessmentEngine::default_24h();
    let finding = engine.assess_capability(
        "cap-a",
        &[
            obs("p", "cap-a", ObservationResult::Passed),
            obs("u", "cap-a", ObservationResult::Unknown),
        ],
    );
    assert_eq!(finding.status, AssessmentStatus::Inconclusive);
}

#[test]
fn passing_plus_stale_result_is_not_satisfied() {
    let engine = AssessmentEngine::default_24h();
    let finding = engine.assess_capability(
        "cap-a",
        &[
            obs("p", "cap-a", ObservationResult::Passed),
            obs("s", "cap-a", ObservationResult::Stale),
        ],
    );
    assert_eq!(finding.status, AssessmentStatus::Inconclusive);
}

#[test]
fn failed_precedence_beats_unknown_and_stale() {
    let engine = AssessmentEngine::default_24h();
    let finding = engine.assess_capability(
        "cap-a",
        &[
            obs("f", "cap-a", ObservationResult::Failed),
            obs("u", "cap-a", ObservationResult::Unknown),
            obs("s", "cap-a", ObservationResult::Stale),
        ],
    );
    assert_eq!(finding.status, AssessmentStatus::Violated);
}

#[test]
fn scoped_assessment_rejects_unknown_and_stale_evidence() {
    let engine = AssessmentEngine::default_24h();
    let intents = vec![capability_intent("cap-a", 1)];
    let unknown = engine.assess_scoped_intents(
        PRODUCT,
        BaselineRevision(1),
        &intents,
        &[obs("u", "cap-a", ObservationResult::Unknown)],
    );
    assert_eq!(unknown.status, AssessmentStatus::Unknown);

    let stale = engine.assess_scoped_intents(
        PRODUCT,
        BaselineRevision(1),
        &intents,
        &[obs("s", "cap-a", ObservationResult::Stale)],
    );
    assert_eq!(stale.status, AssessmentStatus::Stale);
}

// ---------------------------------------------------------------------------
// 4. Unrelated product evidence must not change count, baseline, or verdict.
// ---------------------------------------------------------------------------

#[test]
fn unrelated_product_evidence_does_not_change_summary() {
    let engine = AssessmentEngine::default_24h();
    let own = vec![obs_on_baseline(
        "own-pass",
        "cap-a",
        2,
        ObservationResult::Passed,
    )];
    let mut with_noise = own.clone();
    with_noise.push(observation_at(
        "foreign-fail",
        OTHER_PRODUCT,
        9,
        Some("cap-a"),
        ObservationResult::Failed,
    ));

    let clean = engine.assess_product(PRODUCT, &own);
    let noisy = engine.assess_product(PRODUCT, &with_noise);

    assert_eq!(noisy.status, clean.status);
    assert_eq!(noisy.baseline, clean.baseline);
    assert_eq!(noisy.observation_count, clean.observation_count);
    assert_eq!(noisy.findings.len(), clean.findings.len());
    assert_eq!(noisy.status, AssessmentStatus::Satisfied);
    assert_eq!(noisy.baseline, BaselineRevision(2));
    assert_eq!(noisy.observation_count, 1);
}

#[test]
fn unrelated_product_only_evidence_is_unknown_not_satisfied() {
    let engine = AssessmentEngine::default_24h();
    let observations = vec![observation_at(
        "foreign-pass",
        OTHER_PRODUCT,
        1,
        Some("cap-a"),
        ObservationResult::Passed,
    )];
    let result = engine.assess_product(PRODUCT, &observations);
    assert_eq!(result.status, AssessmentStatus::Unknown);
    assert_eq!(result.observation_count, 0);
    assert!(result.findings.is_empty());
}

#[test]
fn superseded_baseline_does_not_change_current_verdict() {
    let engine = AssessmentEngine::default_24h();
    let observations = vec![
        obs_on_baseline("old-pass", "cap-a", 1, ObservationResult::Passed),
        obs_on_baseline("new-fail", "cap-a", 2, ObservationResult::Failed),
    ];
    let result = engine.assess_product(PRODUCT, &observations);
    assert_eq!(result.status, AssessmentStatus::Violated);
    assert_eq!(result.baseline, BaselineRevision(2));
    assert_eq!(result.observation_count, 1);
    assert_eq!(
        result.findings[0].observation_ids,
        vec!["new-fail".to_string()]
    );
}

// ---------------------------------------------------------------------------
// 5. Legacy observations without `capability_id`: explicit contract.
// ---------------------------------------------------------------------------
//
// Contract (documented on `AssessmentEngine::assess_product` and
// `AssessmentEngine::assess_scoped_intents`):
//
// * `assess_scoped_intents` is fail-closed: an observation with
//   `capability_id == None` can never satisfy, violate, or contaminate a
//   capability intent. It is simply excluded from the evidence set and the
//   affected capability stays `Unknown`.
// * `assess_product` is an observational summary: observations with
//   `capability_id == None` are grouped into one explicit product-level
//   bucket keyed by the product id, reported with
//   `finding.capability_id == Some(product_id)`. They are never attributed to
//   a named capability they do not claim.

#[test]
fn legacy_capabilityless_evidence_cannot_satisfy_a_scoped_capability() {
    let engine = AssessmentEngine::default_24h();
    let legacy_pass = observation_at("legacy-pass", PRODUCT, 1, None, ObservationResult::Passed);
    let result = engine.assess_scoped_intents(
        PRODUCT,
        BaselineRevision(1),
        &[capability_intent("cap-a", 1)],
        &[legacy_pass],
    );
    assert_eq!(result.status, AssessmentStatus::Unknown);
    assert_eq!(result.observation_count, 0);
    assert_eq!(result.findings.len(), 1);
    assert!(result.findings[0].observation_ids.is_empty());
}

#[test]
fn legacy_capabilityless_evidence_cannot_violate_a_scoped_capability() {
    let engine = AssessmentEngine::default_24h();
    let legacy_fail = observation_at("legacy-fail", PRODUCT, 1, None, ObservationResult::Failed);
    let result = engine.assess_scoped_intents(
        PRODUCT,
        BaselineRevision(1),
        &[capability_intent("cap-a", 1)],
        &[legacy_fail],
    );
    assert_eq!(
        result.status,
        AssessmentStatus::Unknown,
        "unattributed evidence must not be blamed on a named capability"
    );
    assert_eq!(result.observation_count, 0);
}

#[test]
fn legacy_capabilityless_evidence_uses_documented_product_level_bucket() {
    let engine = AssessmentEngine::default_24h();
    let observations = vec![
        observation_at("legacy-pass", PRODUCT, 1, None, ObservationResult::Passed),
        obs("cap-pass", "cap-a", ObservationResult::Passed),
    ];
    let result = engine.assess_product(PRODUCT, &observations);

    assert_eq!(result.findings.len(), 2, "product bucket + cap-a");
    let product_bucket = finding_for(&result, PRODUCT);
    assert_eq!(
        product_bucket.capability_id.as_deref(),
        Some(PRODUCT),
        "legacy evidence is explicitly keyed to the product, not a capability"
    );
    assert_eq!(
        product_bucket.observation_ids,
        vec!["legacy-pass".to_string()]
    );
    assert_eq!(
        finding_for(&result, "cap-a").status,
        AssessmentStatus::Satisfied
    );
    assert_eq!(result.observation_count, 2);
}

#[test]
fn legacy_capabilityless_failure_still_surfaces_in_observational_summary() {
    let engine = AssessmentEngine::default_24h();
    let observations = vec![
        observation_at("legacy-fail", PRODUCT, 1, None, ObservationResult::Failed),
        obs("cap-pass", "cap-a", ObservationResult::Passed),
    ];
    let result = engine.assess_product(PRODUCT, &observations);
    assert_eq!(
        result.status,
        AssessmentStatus::Violated,
        "a product-level failure must not be hidden by passing capabilities"
    );
}

// ---------------------------------------------------------------------------
// 6. Cross-product identical capability IDs.
// ---------------------------------------------------------------------------

#[test]
fn identical_capability_ids_across_products_are_scoped_by_explicit_product() {
    let engine = AssessmentEngine::default_24h();
    let intents = vec![capability_intent("shared-cap", 1)];
    let observations = vec![
        obs("mine-pass", "shared-cap", ObservationResult::Passed),
        observation_at(
            "theirs-fail",
            OTHER_PRODUCT,
            1,
            Some("shared-cap"),
            ObservationResult::Failed,
        ),
    ];

    let mine = engine.assess_scoped_intents(PRODUCT, BaselineRevision(1), &intents, &observations);
    let theirs =
        engine.assess_scoped_intents(OTHER_PRODUCT, BaselineRevision(1), &intents, &observations);

    assert_eq!(mine.product_id, PRODUCT);
    assert_eq!(mine.status, AssessmentStatus::Satisfied);
    assert_eq!(mine.observation_count, 1);
    assert_eq!(theirs.product_id, OTHER_PRODUCT);
    assert_eq!(theirs.status, AssessmentStatus::Violated);
    assert_eq!(theirs.observation_count, 1);
}

#[test]
fn accepted_intent_cannot_encode_product_identity() {
    // Documents the open API-design gap from the issue: `AcceptedIntent` has no
    // product field, so two intents for *different* products that share the
    // same capability id are value-identical. The engine therefore requires an
    // explicit `product_id` argument (`assess_scoped_intents`) rather than
    // inferring product identity from an intent.
    let for_product_a = capability_intent("shared-cap", 1);
    let for_product_b = capability_intent("shared-cap", 1);
    assert_eq!(
        for_product_a, for_product_b,
        "AcceptedIntent remains product-agnostic; scope must be supplied explicitly"
    );

    let encoded = serde_json::to_value(&for_product_a).expect("intent serializes");
    let keys: Vec<&str> = encoded
        .as_object()
        .expect("intent is a JSON object")
        .keys()
        .map(String::as_str)
        .collect();
    for key in ["id", "kind", "title", "description", "status", "baseline"] {
        assert!(keys.contains(&key), "expected field {key}");
    }
    assert!(
        !keys.iter().any(|k| k.contains("product")),
        "if a product field is ever added, this contract test must be updated and \
         assess_scoped_intents must validate it"
    );
}
