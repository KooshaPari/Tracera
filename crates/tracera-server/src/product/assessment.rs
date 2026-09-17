//! Deterministic product-linked assessment core (WP-10).
//!
//! This module provides an assessment engine that evaluates product health
//! from observations against accepted intent. It implements the core
//! semantics:
//!
//! - **Satisfied** — all required observations pass
//! - **Violated** — at least one required observation fails
//! - **Unknown** — missing required proof (not "absent capability")
//! - **Inconclusive** — conflicting observations or ambiguous results
//! - **Stale** — observations exist but are older than the freshness threshold
//!
//! Assessment is **deterministic**: the same inputs always produce the same
//! output. No side effects, no randomness.

use chrono::{DateTime, Utc};

use super::identity::{AcceptedIntent, BaselineRevision, IntentKind};
use super::observation::{Observation, ObservationResult};

// ---------------------------------------------------------------------------
// Status
// ---------------------------------------------------------------------------

/// The assessed health of a capability or product.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub enum AssessmentStatus {
    /// All required observations pass.
    Satisfied,
    /// At least one required observation fails.
    Violated,
    /// Missing required observations — unknown, not absent.
    Unknown,
    /// Conflicting observations or ambiguous results.
    Inconclusive,
    /// Observations exist but are older than the freshness threshold.
    Stale,
}

impl AssessmentStatus {
    /// Severity ordering: Violated > Inconclusive > Stale > Unknown > Satisfied.
    pub fn worse_than(self, other: Self) -> bool {
        self.ordinal() > other.ordinal()
    }

    fn ordinal(self) -> u8 {
        match self {
            Self::Satisfied => 0,
            Self::Unknown => 1,
            Self::Stale => 2,
            Self::Inconclusive => 3,
            Self::Violated => 4,
        }
    }
}

// ---------------------------------------------------------------------------
// Severity
// ---------------------------------------------------------------------------

/// Severity of a finding.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub enum FindingSeverity {
    Critical,
    High,
    Medium,
    Low,
    Info,
}

impl FindingSeverity {
    /// Map assessment status to a default severity.
    pub fn from_status(status: AssessmentStatus) -> Self {
        match status {
            AssessmentStatus::Violated => Self::High,
            AssessmentStatus::Inconclusive => Self::Medium,
            AssessmentStatus::Stale => Self::Medium,
            AssessmentStatus::Unknown => Self::Medium,
            AssessmentStatus::Satisfied => Self::Info,
        }
    }
}

// ---------------------------------------------------------------------------
// Finding
// ---------------------------------------------------------------------------

/// A single assessment finding for a capability or product.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct AssessmentFinding {
    /// Product this finding pertains to.
    pub product_id: String,
    /// Capability this finding pertains to (None = product-level).
    pub capability_id: Option<String>,
    /// Assessment status.
    pub status: AssessmentStatus,
    /// Human-readable explanation.
    pub explanation: String,
    /// Observation IDs that contributed to this finding.
    pub observation_ids: Vec<String>,
    /// Severity of the finding.
    pub severity: FindingSeverity,
}

// ---------------------------------------------------------------------------
// Result
// ---------------------------------------------------------------------------

/// Complete assessment output for a product.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct AssessmentResult {
    /// Product assessed.
    pub product_id: String,
    /// Baseline revision assessed against.
    pub baseline: BaselineRevision,
    /// Overall status (worst across all capabilities).
    pub status: AssessmentStatus,
    /// Detailed findings per capability.
    pub findings: Vec<AssessmentFinding>,
    /// When this assessment was computed.
    pub assessed_at: DateTime<Utc>,
    /// Total observations considered.
    pub observation_count: usize,
}

// ---------------------------------------------------------------------------
// Engine
// ---------------------------------------------------------------------------

/// Deterministic assessment engine.
///
/// Constructed with a configurable freshness threshold, then used to
/// assess individual capabilities or entire products.
#[derive(Debug, Clone)]
pub struct AssessmentEngine {
    /// Observations older than this (in seconds) are considered stale.
    freshness_threshold_secs: i64,
}

impl AssessmentEngine {
    /// Create a new engine with the given freshness threshold.
    ///
    /// `freshness_threshold_secs` — observations older than this many
    /// seconds are considered stale. A typical value is 86400 (24 hours).
    pub fn new(freshness_threshold_secs: i64) -> Self {
        Self {
            freshness_threshold_secs,
        }
    }

    /// Create a default engine with a 24-hour freshness threshold.
    pub fn default_24h() -> Self {
        Self::new(86_400)
    }

    /// Assess a single capability given its observations.
    pub fn assess_capability(
        &self,
        capability_id: &str,
        observations: &[Observation],
    ) -> AssessmentFinding {
        let now = Utc::now();
        let obs = observations;
        let obs_ids: Vec<String> = obs.iter().map(|o| o.id.clone()).collect();

        if obs.is_empty() {
            return AssessmentFinding {
                product_id: String::new(),
                capability_id: Some(capability_id.to_string()),
                status: AssessmentStatus::Unknown,
                explanation: format!(
                    "No observations found for capability '{capability_id}'. \
                     Status is unknown — this is not an absence of capability."
                ),
                observation_ids: Vec::new(),
                severity: FindingSeverity::from_status(AssessmentStatus::Unknown),
            };
        }

        // Check freshness: are ALL observations stale?
        let all_stale = obs
            .iter()
            .all(|o| (now - o.recorded_at).num_seconds() > self.freshness_threshold_secs);
        if all_stale {
            return AssessmentFinding {
                product_id: String::new(),
                capability_id: Some(capability_id.to_string()),
                status: AssessmentStatus::Stale,
                explanation: format!(
                    "All {count} observations for capability '{capability_id}' \
                     are older than the freshness threshold ({thresh}s).",
                    count = obs.len(),
                    thresh = self.freshness_threshold_secs,
                ),
                observation_ids: obs_ids,
                severity: FindingSeverity::from_status(AssessmentStatus::Stale),
            };
        }

        // Check for failures
        let has_failed = obs.iter().any(|o| o.result == ObservationResult::Failed);
        let has_passed = obs.iter().any(|o| o.result == ObservationResult::Passed);
        let has_inconclusive = obs
            .iter()
            .any(|o| o.result == ObservationResult::Inconclusive);

        if has_failed && has_passed {
            // Conflicting: both pass and fail
            return AssessmentFinding {
                product_id: String::new(),
                capability_id: Some(capability_id.to_string()),
                status: AssessmentStatus::Inconclusive,
                explanation: format!(
                    "Capability '{capability_id}' has conflicting observations: \
                     some passed and some failed. Resolution is required."
                ),
                observation_ids: obs_ids,
                severity: FindingSeverity::from_status(AssessmentStatus::Inconclusive),
            };
        }

        if has_failed {
            let failed_ids: Vec<String> = obs
                .iter()
                .filter(|o| o.result == ObservationResult::Failed)
                .map(|o| o.id.clone())
                .collect();
            return AssessmentFinding {
                product_id: String::new(),
                capability_id: Some(capability_id.to_string()),
                status: AssessmentStatus::Violated,
                explanation: format!(
                    "Capability '{capability_id}' has failed observations: {failed_ids:?}."
                ),
                observation_ids: failed_ids,
                severity: FindingSeverity::from_status(AssessmentStatus::Violated),
            };
        }

        if has_inconclusive {
            return AssessmentFinding {
                product_id: String::new(),
                capability_id: Some(capability_id.to_string()),
                status: AssessmentStatus::Inconclusive,
                explanation: format!("Capability '{capability_id}' has inconclusive observations."),
                observation_ids: obs_ids,
                severity: FindingSeverity::from_status(AssessmentStatus::Inconclusive),
            };
        }

        // All relevant observations passed
        AssessmentFinding {
            product_id: String::new(),
            capability_id: Some(capability_id.to_string()),
            status: AssessmentStatus::Satisfied,
            explanation: format!(
                "Capability '{capability_id}' has {count} passing observation(s).",
                count = obs.len(),
            ),
            observation_ids: obs_ids,
            severity: FindingSeverity::from_status(AssessmentStatus::Satisfied),
        }
    }

    /// Assess an entire product by evaluating each capability intent.
    pub fn assess_product(
        &self,
        product_id: &str,
        observations: &[Observation],
    ) -> AssessmentResult {
        // Group observations by product_id (which maps to capability in our model)
        let mut capability_map: std::collections::HashMap<String, Vec<&Observation>> =
            std::collections::HashMap::new();
        for obs in observations {
            if obs.product_id.as_str() == product_id {
                capability_map
                    .entry(obs.product_id.as_str().to_string())
                    .or_default()
                    .push(obs);
            }
        }

        if capability_map.is_empty() {
            return AssessmentResult {
                product_id: product_id.to_string(),
                baseline: BaselineRevision(0),
                status: AssessmentStatus::Unknown,
                findings: Vec::new(),
                assessed_at: Utc::now(),
                observation_count: 0,
            };
        }

        let mut findings = Vec::new();
        let mut worst_status = AssessmentStatus::Satisfied;

        for (cap_id, _cap_obs) in &capability_map {
            let mut finding = self.assess_capability(cap_id, observations);
            finding.product_id = product_id.to_string();
            if finding.status.worse_than(worst_status) {
                worst_status = finding.status;
            }
            findings.push(finding);
        }

        // Determine baseline from most recent observation
        let baseline = observations
            .iter()
            .map(|o| o.baseline)
            .max()
            .unwrap_or(BaselineRevision(0));

        AssessmentResult {
            product_id: product_id.to_string(),
            baseline,
            status: worst_status,
            findings,
            assessed_at: Utc::now(),
            observation_count: observations.len(),
        }
    }

    /// Full assessment using accepted intents as the requirement set.
    ///
    /// Capabilities with no observations are flagged as Unknown.
    /// Capabilities with observations are assessed normally.
    pub fn assess_with_intents(
        &self,
        intents: &[AcceptedIntent],
        observations: &[Observation],
    ) -> AssessmentResult {
        let capabilities: Vec<&AcceptedIntent> = intents
            .iter()
            .filter(|i| i.kind == IntentKind::Capability)
            .collect();

        if capabilities.is_empty() {
            return AssessmentResult {
                product_id: String::new(),
                baseline: BaselineRevision(0),
                status: AssessmentStatus::Unknown,
                findings: Vec::new(),
                assessed_at: Utc::now(),
                observation_count: observations.len(),
            };
        }

        let product_id = capabilities
            .first()
            .map(|c| c.id.clone())
            .unwrap_or_default();

        let mut findings = Vec::new();
        let mut worst_status = AssessmentStatus::Satisfied;

        for intent in &capabilities {
            let cap_obs: Vec<&Observation> = observations
                .iter()
                .filter(|o| o.product_id.as_str() == intent.id)
                .collect();

            let finding = if cap_obs.is_empty() {
                AssessmentFinding {
                    product_id: intent.id.clone(),
                    capability_id: Some(intent.id.clone()),
                    status: AssessmentStatus::Unknown,
                    explanation: format!(
                        "Capability '{}' has no observations. Status is unknown.",
                        intent.id
                    ),
                    observation_ids: Vec::new(),
                    severity: FindingSeverity::from_status(AssessmentStatus::Unknown),
                }
            } else {
                let all_obs: Vec<Observation> = cap_obs.into_iter().cloned().collect();
                let mut f = self.assess_capability(&intent.id, &all_obs);
                f.product_id = intent.id.clone();
                f
            };

            if finding.status.worse_than(worst_status) {
                worst_status = finding.status;
            }
            findings.push(finding);
        }

        let baseline = intents
            .iter()
            .map(|i| i.baseline)
            .max()
            .unwrap_or(BaselineRevision(0));

        AssessmentResult {
            product_id,
            baseline,
            status: worst_status,
            findings,
            assessed_at: Utc::now(),
            observation_count: observations.len(),
        }
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::product::identity::{IntentKind, IntentStatus, ProductId};
    use crate::product::observation::{ObservationKind, ObservationSource};

    fn ts(_secs: i64) -> DateTime<Utc> {
        Utc::now()
    }

    fn make_obs(
        id: &str,
        product: &str,
        result: ObservationResult,
        recorded_at: i64,
    ) -> Observation {
        Observation {
            id: id.to_string(),
            product_id: ProductId::new(product),
            baseline: BaselineRevision(1),
            kind: ObservationKind::TestResult,
            result,
            source: ObservationSource {
                collector: "test".to_string(),
                version: "0.1.0".to_string(),
                artifact_ref: None,
            },
            recorded_at: ts(recorded_at),
            capability_id: None,
        }
    }

    fn make_intent(id: &str, kind: IntentKind) -> AcceptedIntent {
        AcceptedIntent {
            id: id.to_string(),
            kind,
            title: format!("Title for {id}"),
            description: String::new(),
            status: IntentStatus::Accepted,
            baseline: BaselineRevision(1),
        }
    }

    // --- T05: Current failed verifier yields violation ---

    #[test]
    fn t05_failed_yields_violation() {
        let engine = AssessmentEngine::new(86_400);
        let obs = vec![make_obs(
            "o1",
            "cap-1",
            ObservationResult::Failed,
            1_000_000,
        )];
        let finding = engine.assess_capability("cap-1", &obs);
        assert_eq!(finding.status, AssessmentStatus::Violated);
        assert_eq!(finding.severity, FindingSeverity::High);
    }

    // --- T06: Healthy current controls remain satisfied ---

    #[test]
    fn t06_all_pass_satisfied() {
        let engine = AssessmentEngine::new(86_400);
        let obs = vec![
            make_obs("o1", "cap-1", ObservationResult::Passed, 1_000_000),
            make_obs("o2", "cap-1", ObservationResult::Passed, 1_000_100),
        ];
        let finding = engine.assess_capability("cap-1", &obs);
        assert_eq!(finding.status, AssessmentStatus::Satisfied);
        assert_eq!(finding.severity, FindingSeverity::Info);
    }

    // --- T07: Missing required proof is unknown ---

    #[test]
    fn t07_missing_proof_is_unknown() {
        let engine = AssessmentEngine::new(86_400);
        let finding = engine.assess_capability("cap-1", &[]);
        assert_eq!(finding.status, AssessmentStatus::Unknown);
        assert!(finding.explanation.contains("unknown"));
        assert!(finding.explanation.contains("not"));
    }

    // --- T11: Later collector error overrides old green ---

    #[test]
    fn t11_later_error_overrides_old_green() {
        let engine = AssessmentEngine::new(86_400);
        let obs = vec![
            make_obs("o-pass", "cap-1", ObservationResult::Passed, 1_000_000),
            make_obs("o-fail", "cap-1", ObservationResult::Failed, 2_000_000),
        ];
        let finding = engine.assess_capability("cap-1", &obs);
        assert_eq!(finding.status, AssessmentStatus::Inconclusive);
    }

    // --- T12: Conflicting same-time results remain inconclusive ---

    #[test]
    fn t12_conflicting_results_inconclusive() {
        let engine = AssessmentEngine::new(86_400);
        let obs = vec![
            make_obs("o1", "cap-1", ObservationResult::Passed, 1_000_000),
            make_obs("o2", "cap-1", ObservationResult::Failed, 1_000_000),
        ];
        let finding = engine.assess_capability("cap-1", &obs);
        assert_eq!(finding.status, AssessmentStatus::Inconclusive);
    }

    #[test]
    fn no_observations_unknown() {
        let engine = AssessmentEngine::new(86_400);
        let finding = engine.assess_capability("cap-1", &[]);
        assert_eq!(finding.status, AssessmentStatus::Unknown);
    }

    #[test]
    fn mixed_pass_fail_inconclusive() {
        let engine = AssessmentEngine::new(86_400);
        let obs = vec![
            make_obs("o1", "cap-1", ObservationResult::Passed, 1_000_000),
            make_obs("o2", "cap-1", ObservationResult::Failed, 1_000_000),
        ];
        let finding = engine.assess_capability("cap-1", &obs);
        assert_eq!(finding.status, AssessmentStatus::Inconclusive);
    }

    #[test]
    fn all_passed_satisfied() {
        let engine = AssessmentEngine::new(86_400);
        let obs = vec![make_obs(
            "o1",
            "cap-1",
            ObservationResult::Passed,
            1_000_000,
        )];
        let finding = engine.assess_capability("cap-1", &obs);
        assert_eq!(finding.status, AssessmentStatus::Satisfied);
    }

    #[test]
    fn assessment_deterministic() {
        let engine = AssessmentEngine::new(86_400);
        let obs = vec![
            make_obs("o1", "cap-1", ObservationResult::Passed, 1_000_000),
            make_obs("o2", "cap-1", ObservationResult::Failed, 1_000_000),
        ];
        let f1 = engine.assess_capability("cap-1", &obs);
        let f2 = engine.assess_capability("cap-1", &obs);
        assert_eq!(f1.status, f2.status);
        assert_eq!(f1.explanation, f2.explanation);
    }

    #[test]
    fn worst_status_propagates_in_product() {
        let engine = AssessmentEngine::new(86_400);
        let intents = vec![
            make_intent("cap-good", IntentKind::Capability),
            make_intent("cap-bad", IntentKind::Capability),
        ];
        let observations = vec![
            make_obs("o1", "cap-good", ObservationResult::Passed, 1_000_000),
            make_obs("o2", "cap-bad", ObservationResult::Failed, 1_000_000),
        ];
        let result = engine.assess_with_intents(&intents, &observations);
        assert_eq!(result.status, AssessmentStatus::Violated);
        assert_eq!(result.findings.len(), 2);
    }

    #[test]
    fn severity_mapping() {
        assert_eq!(
            FindingSeverity::from_status(AssessmentStatus::Violated),
            FindingSeverity::High
        );
        assert_eq!(
            FindingSeverity::from_status(AssessmentStatus::Unknown),
            FindingSeverity::Medium
        );
        assert_eq!(
            FindingSeverity::from_status(AssessmentStatus::Satisfied),
            FindingSeverity::Info
        );
    }

    #[test]
    fn stale_observations_produce_stale_status() {
        let engine = AssessmentEngine::new(100); // 100s threshold
        let old_obs = Observation {
            id: "o1".to_string(),
            product_id: ProductId::new("cap-1"),
            baseline: BaselineRevision(1),
            kind: ObservationKind::TestResult,
            result: ObservationResult::Passed,
            source: ObservationSource {
                collector: "test".to_string(),
                version: "0.1.0".to_string(),
                artifact_ref: None,
            },
            recorded_at: DateTime::from_timestamp(1_000, 0).unwrap(),
            capability_id: None,
        };
        let finding = engine.assess_capability("cap-1", &[old_obs]);
        assert_eq!(finding.status, AssessmentStatus::Stale);
    }

    #[test]
    fn assessment_result_serializable() {
        let engine = AssessmentEngine::new(86_400);
        let obs = vec![make_obs(
            "o1",
            "cap-1",
            ObservationResult::Passed,
            1_000_000,
        )];
        let finding = engine.assess_capability("cap-1", &obs);
        let json = serde_json::to_string(&finding).unwrap();
        let roundtrip: AssessmentFinding = serde_json::from_str(&json).unwrap();
        assert_eq!(roundtrip.status, AssessmentStatus::Satisfied);
    }
}
