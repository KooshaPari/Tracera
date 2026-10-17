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

use super::identity::{AcceptedIntent, IntentKind, IntentStatus, ProductId};
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
        Self("1.1.0".to_string())
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
                    capability_id: obs.capability_id.clone(),
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

impl Default for CoverageDetector {
    fn default() -> Self {
        Self
    }
}

impl CoverageDetector {
    /// Create a new coverage detector.
    pub fn new() -> Self {
        Self
    }

    /// Find capabilities with no observations.
    pub fn detect(
        &self,
        product_id: &ProductId,
        intents: &[AcceptedIntent],
        observations: &[Observation],
    ) -> Vec<DetectorFinding> {
        let now = Utc::now();
        let version = DetectorVersion::current();
        let mut findings = Vec::new();

        for intent in intents.iter().filter(|intent| {
            intent.kind == IntentKind::Capability && intent.status == IntentStatus::Accepted
        }) {
            let cap_id = &intent.id;
            let has_obs = observations.iter().any(|obs| {
                obs.product_id == *product_id
                    && obs.capability_id.as_deref() == Some(cap_id.as_str())
                    && obs.baseline == intent.baseline
            });
            if !has_obs {
                findings.push(DetectorFinding {
                    kind: FindingKind::Coverage,
                    product_id: product_id.as_str().to_string(),
                    capability_id: Some(cap_id.clone()),
                    message: format!(
                        "Capability '{cap_id}' has no observations at baseline {}. \
                         This is unknown status, not an absence of capability.",
                        intent.baseline.number()
                    ),
                    evidence: vec![cap_id.clone()],
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

impl Default for ContradictionDetector {
    fn default() -> Self {
        Self
    }
}

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

        // Independent sources may disagree; isolate product, capability and baseline.
        let mut groups: std::collections::HashMap<
            (String, Option<String>, u64),
            Vec<&Observation>,
        > = std::collections::HashMap::new();
        for obs in observations {
            let key = (
                obs.product_id.as_str().to_string(),
                obs.capability_id.clone(),
                obs.baseline.0,
            );
            groups.entry(key).or_default().push(obs);
        }

        for ((product_id, capability_id, baseline), group) in &groups {
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
                    capability_id: capability_id.clone(),
                    message: format!(
                        "Product '{product_id}', {}, has both passing and failing \
                         observations at baseline {baseline}. Resolution is required.",
                        capability_id
                            .as_ref()
                            .map(|id| format!("capability '{id}'"))
                            .unwrap_or_else(|| "product-level observations".into())
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
    pub fn run(
        &self,
        product_id: &ProductId,
        intents: &[AcceptedIntent],
        observations: &[Observation],
    ) -> DetectorResult {
        let mut findings = Vec::new();
        findings.extend(self.freshness.detect(observations));
        findings.extend(self.coverage.detect(product_id, intents, observations));
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
#[path = "detectors_tests.rs"]
mod tests;
