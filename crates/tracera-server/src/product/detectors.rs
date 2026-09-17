//! Freshness, coverage, and contradiction detectors (WP-11).
//!
//! Versioned detectors that identify product health issues from
//! observations and accepted intent. Each detector is independently
//! versioned and produces explainable findings.
//!
//! # Detectors
//!
//! - **FreshnessDetector** — finds observations older than a threshold.
//! - **CoverageDetector** — finds capabilities with zero observations.
//! - **ContradictionDetector** — finds capabilities with conflicting
//!   (Passed + Failed) observations at the same baseline.
//!
//! All detectors are pure functions with no side effects.

use chrono::{DateTime, Utc};

use super::identity::AcceptedIntent;
use super::observation::{Observation, ObservationResult};

// ---------------------------------------------------------------------------
// Version
// ---------------------------------------------------------------------------

/// Semantic version for detector logic.
#[derive(Debug, Clone, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub struct DetectorVersion(pub String);

impl DetectorVersion {
    /// Current version of all detectors.
    pub fn current() -> Self {
        Self("1.0.0".to_string())
    }
}

// ---------------------------------------------------------------------------
// Finding kind
// ---------------------------------------------------------------------------

/// Severity of a detector finding — re-exported from the assessment module
/// to avoid duplicate enum definitions.
pub use super::assessment::FindingSeverity;

/// Which detector produced this finding.
#[derive(Debug, Clone, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub enum FindingKind {
    Freshness,
    Coverage,
    Contradiction,
}

// ---------------------------------------------------------------------------
// Finding
// ---------------------------------------------------------------------------

/// A single explainable detector finding.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct DetectorFinding {
    /// Which detector produced this finding.
    pub kind: FindingKind,
    /// Product this finding pertains to.
    pub product_id: String,
    /// Capability this finding pertains to (None = product-level).
    pub capability_id: Option<String>,
    /// Human-readable explanation.
    pub message: String,
    /// Observation IDs or other evidence references.
    pub evidence: Vec<String>,
    /// Version of the detector that produced this finding.
    pub detector_version: DetectorVersion,
    /// When this finding was detected.
    pub detected_at: DateTime<Utc>,
    /// Severity of the finding.
    pub severity: FindingSeverity,
}

// ---------------------------------------------------------------------------
// Detector result
// ---------------------------------------------------------------------------

/// Aggregate result from running all detectors.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct DetectorResult {
    /// All findings from all detectors.
    pub findings: Vec<DetectorFinding>,
    /// Number of products scanned.
    pub products_scanned: usize,
    /// Number of capabilities scanned.
    pub capabilities_scanned: usize,
    /// Version of the detectors that ran.
    pub detector_version: DetectorVersion,
    /// When the detectors ran.
    pub ran_at: DateTime<Utc>,
}

// ---------------------------------------------------------------------------
// FreshnessDetector
// ---------------------------------------------------------------------------

/// Detects observations that are older than a configured maximum age.
#[derive(Debug, Clone)]
pub struct FreshnessDetector {
    /// Maximum age in seconds before an observation is considered stale.
    max_age_secs: i64,
}

impl FreshnessDetector {
    /// Create a new freshness detector with the given threshold.
    pub fn new(max_age_secs: i64) -> Self {
        Self { max_age_secs }
    }

    /// Find stale observations in the given set.
    pub fn detect(&self, observations: &[Observation]) -> Vec<DetectorFinding> {
        let now = Utc::now();
        let version = DetectorVersion::current();
        let mut findings = Vec::new();

        for obs in observations {
            let age = (now - obs.recorded_at).num_seconds();
            if age > self.max_age_secs {
                let severity = if obs.result == ObservationResult::Failed {
                    FindingSeverity::High
                } else {
                    FindingSeverity::Medium
                };
                findings.push(DetectorFinding {
                    kind: FindingKind::Freshness,
                    product_id: obs.product_id.as_str().to_string(),
                    capability_id: Some(obs.product_id.as_str().to_string()),
                    message: format!(
                        "Observation '{}' is {} seconds old (max: {}s). \
                         The result may no longer be current.",
                        obs.id, age, self.max_age_secs,
                    ),
                    evidence: vec![obs.id.clone()],
                    detector_version: version.clone(),
                    detected_at: now,
                    severity,
                });
            }
        }

        findings
    }
}

// ---------------------------------------------------------------------------
// CoverageDetector
// ---------------------------------------------------------------------------

/// Detects capabilities that have zero observations.
#[derive(Debug, Clone)]
pub struct CoverageDetector;

impl CoverageDetector {
    /// Create a new coverage detector.
    pub fn new() -> Self {
        Self
    }

    /// Find capabilities with no observations.
    pub fn detect(
        &self,
        intents: &[AcceptedIntent],
        observations: &[Observation],
    ) -> Vec<DetectorFinding> {
        let now = Utc::now();
        let version = DetectorVersion::current();
        let mut findings = Vec::new();

        // Collect all capability intent IDs
        let capability_ids: Vec<&str> = intents
            .iter()
            .filter(|i| i.kind == super::identity::IntentKind::Capability)
            .map(|i| i.id.as_str())
            .collect();

        for cap_id in &capability_ids {
            let has_obs = observations
                .iter()
                .any(|o| o.product_id.as_str() == *cap_id);
            if !has_obs {
                findings.push(DetectorFinding {
                    kind: FindingKind::Coverage,
                    product_id: (*cap_id).to_string(),
                    capability_id: Some(cap_id.to_string()),
                    message: format!(
                        "Capability '{cap_id}' has no observations. \
                         This is unknown status, not an absence of capability."
                    ),
                    evidence: vec![cap_id.to_string()],
                    detector_version: version.clone(),
                    detected_at: now,
                    severity: FindingSeverity::Medium,
                });
            }
        }

        findings
    }
}

// ---------------------------------------------------------------------------
// ContradictionDetector
// ---------------------------------------------------------------------------

/// Detects capabilities where Passed and Failed observations coexist
/// at the same baseline revision.
#[derive(Debug, Clone)]
pub struct ContradictionDetector;

impl ContradictionDetector {
    /// Create a new contradiction detector.
    pub fn new() -> Self {
        Self
    }

    /// Find capabilities with contradictory observations.
    pub fn detect(&self, observations: &[Observation]) -> Vec<DetectorFinding> {
        let now = Utc::now();
        let version = DetectorVersion::current();
        let mut findings = Vec::new();

        // Group by product_id + baseline
        let mut groups: std::collections::HashMap<(String, u64), Vec<&Observation>> =
            std::collections::HashMap::new();
        for obs in observations {
            let key = (obs.product_id.as_str().to_string(), obs.baseline.0);
            groups.entry(key).or_default().push(obs);
        }

        for ((product_id, _baseline), group) in &groups {
            let has_passed = group.iter().any(|o| o.result == ObservationResult::Passed);
            let has_failed = group.iter().any(|o| o.result == ObservationResult::Failed);

            if has_passed && has_failed {
                let evidence: Vec<String> = group
                    .iter()
                    .filter(|o| {
                        o.result == ObservationResult::Passed
                            || o.result == ObservationResult::Failed
                    })
                    .map(|o| o.id.clone())
                    .collect();

                findings.push(DetectorFinding {
                    kind: FindingKind::Contradiction,
                    product_id: product_id.clone(),
                    capability_id: Some(product_id.clone()),
                    message: format!(
                        "Capability '{product_id}' has both passing and failing \
                         observations at the same baseline. Resolution is required."
                    ),
                    evidence,
                    detector_version: version.clone(),
                    detected_at: now,
                    severity: FindingSeverity::High,
                });
            }
        }

        findings
    }
}

// ---------------------------------------------------------------------------
// Suite
// ---------------------------------------------------------------------------

/// Runs all detectors as a suite.
#[derive(Debug, Clone)]
pub struct ProductDetectorSuite {
    freshness: FreshnessDetector,
    coverage: CoverageDetector,
    contradiction: ContradictionDetector,
}

impl ProductDetectorSuite {
    /// Create a suite with all three detectors.
    pub fn new(freshness_max_age_secs: i64) -> Self {
        Self {
            freshness: FreshnessDetector::new(freshness_max_age_secs),
            coverage: CoverageDetector::new(),
            contradiction: ContradictionDetector::new(),
        }
    }

    /// Run all detectors and return combined results.
    pub fn run(&self, intents: &[AcceptedIntent], observations: &[Observation]) -> DetectorResult {
        let mut findings = Vec::new();
        findings.extend(self.freshness.detect(observations));
        findings.extend(self.coverage.detect(intents, observations));
        findings.extend(self.contradiction.detect(observations));

        let products_scanned: std::collections::HashSet<&str> =
            observations.iter().map(|o| o.product_id.as_str()).collect();

        let capabilities_scanned: usize = intents
            .iter()
            .filter(|i| i.kind == super::identity::IntentKind::Capability)
            .count();

        DetectorResult {
            findings,
            products_scanned: products_scanned.len(),
            capabilities_scanned,
            detector_version: DetectorVersion::current(),
            ran_at: Utc::now(),
        }
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::product::identity::{BaselineRevision, IntentKind, IntentStatus, ProductId};
    use crate::product::observation::{ObservationKind, ObservationSource};

    fn ts(secs: i64) -> DateTime<Utc> {
        DateTime::from_timestamp(secs, 0).unwrap()
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
                artifact_ref: None,
            },
            recorded_at: ts(recorded_at),
            capability_id: None,
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
        let observations = vec![make_obs(
            "o1",
            "cap-a",
            ObservationResult::Passed,
            1_000_000,
        )];
        let findings = det.detect(&intents, &observations);
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
                artifact_ref: None,
            },
            recorded_at: Utc::now(),
            capability_id: None,
        };
        let fd = FreshnessDetector::new(86_400);
        let cd = ContradictionDetector::new();
        assert!(fd.detect(&[fresh_obs.clone()]).is_empty());
        assert!(cd.detect(&[fresh_obs]).is_empty());
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
        let findings = det.detect(&[], &[]);
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
        let result = suite.run(&intents, &observations);
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
}
