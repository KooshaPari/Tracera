#![allow(dead_code)]

//! Observation types — measurements, test results, and findings that are
//! anchored to a specific product baseline.
//!
//! Observations are the evidence layer of the product model. Each
//! observation references a [`ProductId`](super::identity::ProductId) and
//! [`BaselineRevision`](super::identity::BaselineRevision) so that
//! historical results are always compared against the correct contract
//! snapshot.
//!
//! Part of WP-02 (Adopt stable identity, revision and portable contract
//! boundary) — specifically:
//!
//! - **R02** — Observations must reference a stable product identity.
//! - **R04** — Observations must pin to a specific baseline revision.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use super::identity::{BaselineRevision, ProductId};

// ---------------------------------------------------------------------------
// Observation
// ---------------------------------------------------------------------------

/// The category of an observation.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ObservationKind {
    /// Automated test result (unit, integration, e2e).
    TestResult,
    /// Quantitative measurement (performance, coverage, size).
    Measurement,
    /// Qualitative finding (security review, audit note).
    Finding,
    /// High-level assessment (readiness, maturity score).
    Assessment,
}

/// Outcome of an observation.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ObservationResult {
    /// The observation passed / met expectations.
    Passed,
    /// The observation failed / did not meet expectations.
    Failed,
    /// The data is older than the staleness threshold.
    Stale,
    /// No data available yet.
    Unknown,
    /// Result is ambiguous or partially satisfied.
    Inconclusive,
}

/// Provenance metadata for an observation.
///
/// Records which collector produced the observation, its version, and an
/// optional reference to the source artifact (e.g. a test report URL or
/// build log).
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct ObservationSource {
    /// Name of the collector (e.g. "cargo-test", "lighthouse-ci", "manual").
    pub collector: String,
    /// Semver of the collector that produced this observation.
    pub version: String,
    /// Optional reference to the source artifact.
    pub artifact_ref: Option<String>,
}

/// A single observation anchored to a product baseline.
///
/// Observations are **append-only** — once recorded they are never mutated.
/// Staleness is computed at query time by comparing `recorded_at` against
/// the current time and a configurable threshold.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Observation {
    /// Unique identifier for this observation.
    pub id: String,
    /// Which product this observation pertains to (R02).
    pub product_id: ProductId,
    /// Which baseline revision was active when this observation was recorded (R04).
    pub baseline: BaselineRevision,
    /// Category of the observation.
    pub kind: ObservationKind,
    /// Outcome of the observation.
    pub result: ObservationResult,
    /// Provenance / source metadata.
    pub source: ObservationSource,
    /// UTC timestamp when this observation was recorded.
    pub recorded_at: DateTime<Utc>,
    /// Optional capability this observation is associated with.
    #[serde(default)]
    pub capability_id: Option<String>,
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_observation() -> Observation {
        Observation {
            id: "obs-001".to_string(),
            product_id: ProductId::new("tracera"),
            baseline: BaselineRevision(1),
            kind: ObservationKind::TestResult,
            result: ObservationResult::Passed,
            source: ObservationSource {
                collector: "cargo-test".to_string(),
                version: "0.1.0".to_string(),
                artifact_ref: Some("https://ci.example.com/build/42".to_string()),
            },
            recorded_at: chrono::DateTime::parse_from_rfc3339("2026-09-17T12:00:00Z")
                .unwrap()
                .to_utc(),
            capability_id: Some("cap-storage".to_string()),
        }
    }

    #[test]
    fn observation_construction() {
        let obs = sample_observation();
        assert_eq!(obs.product_id.as_str(), "tracera");
        assert_eq!(obs.baseline, BaselineRevision(1));
        assert_eq!(obs.kind, ObservationKind::TestResult);
        assert_eq!(obs.result, ObservationResult::Passed);
    }

    #[test]
    fn observation_serialization_roundtrip() {
        let obs = sample_observation();
        let json = serde_json::to_string(&obs).unwrap();
        let roundtrip: Observation = serde_json::from_str(&json).unwrap();
        assert_eq!(roundtrip.id, obs.id);
        assert_eq!(roundtrip.result, obs.result);
        assert_eq!(roundtrip.source.collector, "cargo-test");
    }

    #[test]
    fn observation_source_without_artifact() {
        let source = ObservationSource {
            collector: "manual".to_string(),
            version: "1.0.0".to_string(),
            artifact_ref: None,
        };
        let json = serde_json::to_string(&source).unwrap();
        let roundtrip: ObservationSource = serde_json::from_str(&json).unwrap();
        assert!(roundtrip.artifact_ref.is_none());
    }

    #[test]
    fn observation_kind_all_variants() {
        let kinds = vec![
            ObservationKind::TestResult,
            ObservationKind::Measurement,
            ObservationKind::Finding,
            ObservationKind::Assessment,
        ];
        for kind in &kinds {
            let json = serde_json::to_string(kind).unwrap();
            let roundtrip: ObservationKind = serde_json::from_str(&json).unwrap();
            assert_eq!(*kind, roundtrip);
        }
    }

    #[test]
    fn observation_result_all_variants() {
        let results = vec![
            ObservationResult::Passed,
            ObservationResult::Failed,
            ObservationResult::Stale,
            ObservationResult::Unknown,
            ObservationResult::Inconclusive,
        ];
        for result in &results {
            let json = serde_json::to_string(result).unwrap();
            let roundtrip: ObservationResult = serde_json::from_str(&json).unwrap();
            assert_eq!(*result, roundtrip);
        }
    }
}
