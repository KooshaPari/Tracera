//! Product-aware observation ingestion pipeline (WP-08).
//!
//! This module provides an in-memory observation store with idempotent
//! ingestion, provenance tracking, and validation. It bridges external
//! verifier outputs (test results, measurements, findings) with the
//! product model.
//!
//! # Design
//!
//! Ingestion is **append-only** — observations are never mutated after
//! recording. Idempotency is enforced at two levels:
//!
//! 1. **Observation ID** — duplicate IDs are rejected (exact dedup).
//! 2. **Idempotency key** — a caller-supplied key that rejects an entire
//!    batch if the key was previously seen.
//!
//! Validation rejects observations with empty IDs, empty product IDs, or
//! timestamps significantly in the future.

use std::collections::HashSet;

use super::observation::Observation;

// ---------------------------------------------------------------------------
// Request / Response
// ---------------------------------------------------------------------------

/// Input for ingesting a batch of observations.
#[derive(Debug, Clone)]
pub struct ObservationIngestRequest {
    /// Observations to ingest.
    pub observations: Vec<Observation>,
    /// Optional idempotency key — if this key was previously used, the
    /// entire batch is rejected.
    pub idempotency_key: Option<String>,
}

/// Outcome of an ingestion attempt.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct IngestResult {
    /// Number of new observations accepted.
    pub accepted: usize,
    /// Number rejected (duplicates, invalid, or batch-rejected).
    pub rejected: usize,
    /// Human-readable error messages for rejected observations.
    pub errors: Vec<String>,
    /// IDs of observations that were accepted.
    pub observation_ids: Vec<String>,
}

// ---------------------------------------------------------------------------
// Validation errors
// ---------------------------------------------------------------------------

/// Reasons an individual observation may be rejected.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum IngestError {
    /// The observation has an empty ID.
    EmptyId,
    /// The observation has an empty product ID.
    EmptyProductId,
    /// The observation's `recorded_at` is more than 5 minutes in the future.
    FutureTimestamp,
    /// The observation ID already exists in the store.
    DuplicateId(String),
    /// The entire batch was rejected because the idempotency key was seen before.
    DuplicateBatch,
}

impl std::fmt::Display for IngestError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::EmptyId => write!(f, "observation has empty ID"),
            Self::EmptyProductId => write!(f, "observation has empty product ID"),
            Self::FutureTimestamp => write!(f, "observation timestamp is in the future"),
            Self::DuplicateId(id) => write!(f, "duplicate observation ID: {id}"),
            Self::DuplicateBatch => write!(f, "batch rejected: idempotency key already seen"),
        }
    }
}

// ---------------------------------------------------------------------------
// ObservationStore
// ---------------------------------------------------------------------------

/// In-memory store for product observations.
///
/// Thread-safety is left to the caller (wrap in `Arc<Mutex<…>>` or similar
/// for concurrent access).
#[derive(Debug, Default)]
pub struct ObservationStore {
    observations: Vec<Observation>,
    seen_ids: HashSet<String>,
    idempotency_keys: HashSet<String>,
}

/// Maximum allowed future skew: 5 minutes.
const MAX_FUTURE_SKEW_SECS: i64 = 300;

impl ObservationStore {
    /// Create a new empty store.
    pub fn new() -> Self {
        Self::default()
    }

    /// Ingest a batch of observations.
    ///
    /// Returns an [`IngestResult`] describing how many were accepted,
    /// rejected, and any error messages. Duplicate observation IDs and
    /// previously-seen idempotency keys cause rejection.
    pub fn ingest(&mut self, request: &ObservationIngestRequest) -> IngestResult {
        // Check batch-level idempotency
        if let Some(ref key) = request.idempotency_key {
            if self.idempotency_keys.contains(key) {
                return IngestResult {
                    accepted: 0,
                    rejected: request.observations.len(),
                    errors: vec![IngestError::DuplicateBatch.to_string()],
                    observation_ids: Vec::new(),
                };
            }
        }

        let mut accepted_ids = Vec::new();
        let mut errors = Vec::new();
        let mut accepted = 0;
        let mut rejected = 0;
        let now = chrono::Utc::now();

        for obs in &request.observations {
            match self.validate(obs, &now) {
                Ok(()) => {
                    // Check duplicate ID
                    if self.seen_ids.contains(&obs.id) {
                        errors.push(IngestError::DuplicateId(obs.id.clone()).to_string());
                        rejected += 1;
                        continue;
                    }
                    // Accept
                    self.seen_ids.insert(obs.id.clone());
                    self.observations.push(obs.clone());
                    accepted_ids.push(obs.id.clone());
                    accepted += 1;
                }
                Err(e) => {
                    errors.push(e.to_string());
                    rejected += 1;
                }
            }
        }

        // Record idempotency key only if at least one observation was accepted
        if accepted > 0 {
            if let Some(ref key) = request.idempotency_key {
                self.idempotency_keys.insert(key.clone());
            }
        }

        IngestResult {
            accepted,
            rejected,
            errors,
            observation_ids: accepted_ids,
        }
    }

    /// Retrieve all observations for a given product ID.
    pub fn get_observations_for_product(&self, product_id: &str) -> Vec<&Observation> {
        self.observations
            .iter()
            .filter(|o| o.product_id.as_str() == product_id)
            .collect()
    }

    /// Retrieve observations whose product ID matches the given capability ID.
    ///
    /// In the Tracera model, capabilities are identified by their intent ID
    /// which maps to the `product_id` field on observations.
    pub fn get_observations_for_capability(&self, capability_id: &str) -> Vec<&Observation> {
        self.observations
            .iter()
            .filter(|o| o.product_id.as_str() == capability_id)
            .collect()
    }

    /// Check if an observation ID has already been stored.
    pub fn is_duplicate(&self, observation_id: &str) -> bool {
        self.seen_ids.contains(observation_id)
    }

    /// Total number of stored observations.
    pub fn count(&self) -> usize {
        self.observations.len()
    }

    /// Validate an observation before ingestion.
    fn validate(
        &self,
        obs: &Observation,
        now: &chrono::DateTime<chrono::Utc>,
    ) -> Result<(), IngestError> {
        if obs.id.is_empty() {
            return Err(IngestError::EmptyId);
        }
        if obs.product_id.as_str().is_empty() {
            return Err(IngestError::EmptyProductId);
        }
        let skew = (obs.recorded_at - *now).num_seconds();
        if skew > MAX_FUTURE_SKEW_SECS {
            return Err(IngestError::FutureTimestamp);
        }
        Ok(())
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::product::identity::{BaselineRevision, ProductId};
    use crate::product::observation::{ObservationKind, ObservationResult, ObservationSource};

    fn ts(secs: i64) -> chrono::DateTime<chrono::Utc> {
        chrono::DateTime::from_timestamp(secs, 0).unwrap()
    }

    fn make_obs(id: &str, product: &str) -> Observation {
        Observation {
            id: id.to_string(),
            product_id: ProductId::new(product),
            baseline: BaselineRevision(1),
            kind: ObservationKind::TestResult,
            result: ObservationResult::Passed,
            source: ObservationSource {
                collector: "test".to_string(),
                version: "0.1.0".to_string(),
                artifact_ref: None,
            },
            recorded_at: ts(1_000_000),
            capability_id: None,
        }
    }

    #[test]
    fn ingest_happy_path() {
        let mut store = ObservationStore::new();
        let req = ObservationIngestRequest {
            observations: vec![make_obs("o1", "p1"), make_obs("o2", "p1")],
            idempotency_key: None,
        };
        let result = store.ingest(&req);
        assert_eq!(result.accepted, 2);
        assert_eq!(result.rejected, 0);
        assert!(result.errors.is_empty());
        assert_eq!(store.count(), 2);
    }

    #[test]
    fn duplicate_observation_id_rejected() {
        let mut store = ObservationStore::new();
        let req = ObservationIngestRequest {
            observations: vec![make_obs("o1", "p1")],
            idempotency_key: None,
        };
        store.ingest(&req);

        let req2 = ObservationIngestRequest {
            observations: vec![make_obs("o1", "p1")],
            idempotency_key: None,
        };
        let result = store.ingest(&req2);
        assert_eq!(result.accepted, 0);
        assert_eq!(result.rejected, 1);
        assert!(!result.errors.is_empty());
    }

    #[test]
    fn idempotency_key_rejects_batch() {
        let mut store = ObservationStore::new();
        let req = ObservationIngestRequest {
            observations: vec![make_obs("o1", "p1")],
            idempotency_key: Some("key-1".to_string()),
        };
        store.ingest(&req);

        let req2 = ObservationIngestRequest {
            observations: vec![make_obs("o2", "p1")],
            idempotency_key: Some("key-1".to_string()),
        };
        let result = store.ingest(&req2);
        assert_eq!(result.accepted, 0);
        assert_eq!(result.rejected, 1);
        assert!(result.errors.iter().any(|e| e.contains("idempotency")));
    }

    #[test]
    fn different_idempotency_key_accepted() {
        let mut store = ObservationStore::new();
        let req = ObservationIngestRequest {
            observations: vec![make_obs("o1", "p1")],
            idempotency_key: Some("key-1".to_string()),
        };
        store.ingest(&req);

        let req2 = ObservationIngestRequest {
            observations: vec![make_obs("o2", "p1")],
            idempotency_key: Some("key-2".to_string()),
        };
        let result = store.ingest(&req2);
        assert_eq!(result.accepted, 1);
    }

    #[test]
    fn empty_id_rejected() {
        let mut store = ObservationStore::new();
        let obs = Observation {
            id: String::new(),
            product_id: ProductId::new("p1"),
            baseline: BaselineRevision(1),
            kind: ObservationKind::TestResult,
            result: ObservationResult::Passed,
            source: ObservationSource {
                collector: "test".to_string(),
                version: "0.1.0".to_string(),
                artifact_ref: None,
            },
            recorded_at: ts(1_000_000),
            capability_id: None,
        };
        let req = ObservationIngestRequest {
            observations: vec![obs],
            idempotency_key: None,
        };
        let result = store.ingest(&req);
        assert_eq!(result.accepted, 0);
        assert_eq!(result.rejected, 1);
    }

    #[test]
    fn empty_product_id_rejected() {
        let mut store = ObservationStore::new();
        let obs = Observation {
            id: "o1".to_string(),
            product_id: ProductId::new(""),
            baseline: BaselineRevision(1),
            kind: ObservationKind::TestResult,
            result: ObservationResult::Passed,
            source: ObservationSource {
                collector: "test".to_string(),
                version: "0.1.0".to_string(),
                artifact_ref: None,
            },
            recorded_at: ts(1_000_000),
            capability_id: None,
        };
        let req = ObservationIngestRequest {
            observations: vec![obs],
            idempotency_key: None,
        };
        let result = store.ingest(&req);
        assert_eq!(result.accepted, 0);
        assert_eq!(result.rejected, 1);
    }

    #[test]
    fn future_timestamp_rejected() {
        let mut store = ObservationStore::new();
        let obs = Observation {
            id: "o1".to_string(),
            product_id: ProductId::new("p1"),
            baseline: BaselineRevision(1),
            kind: ObservationKind::TestResult,
            result: ObservationResult::Passed,
            source: ObservationSource {
                collector: "test".to_string(),
                version: "0.1.0".to_string(),
                artifact_ref: None,
            },
            // Far in the future
            recorded_at: chrono::Utc::now() + chrono::Duration::hours(1),
            capability_id: None,
        };
        let req = ObservationIngestRequest {
            observations: vec![obs],
            idempotency_key: None,
        };
        let result = store.ingest(&req);
        assert_eq!(result.accepted, 0);
        assert_eq!(result.rejected, 1);
    }

    #[test]
    fn retrieval_by_product() {
        let mut store = ObservationStore::new();
        let req = ObservationIngestRequest {
            observations: vec![
                make_obs("o1", "p1"),
                make_obs("o2", "p2"),
                make_obs("o3", "p1"),
            ],
            idempotency_key: None,
        };
        store.ingest(&req);
        assert_eq!(store.get_observations_for_product("p1").len(), 2);
        assert_eq!(store.get_observations_for_product("p2").len(), 1);
        assert!(store.get_observations_for_product("p3").is_empty());
    }

    #[test]
    fn retrieval_by_capability() {
        let mut store = ObservationStore::new();
        let req = ObservationIngestRequest {
            observations: vec![make_obs("o1", "cap-a"), make_obs("o2", "cap-b")],
            idempotency_key: None,
        };
        store.ingest(&req);
        assert_eq!(store.get_observations_for_capability("cap-a").len(), 1);
        assert!(store.get_observations_for_capability("cap-c").is_empty());
    }

    #[test]
    fn is_duplicate_works() {
        let mut store = ObservationStore::new();
        assert!(!store.is_duplicate("o1"));
        let req = ObservationIngestRequest {
            observations: vec![make_obs("o1", "p1")],
            idempotency_key: None,
        };
        store.ingest(&req);
        assert!(store.is_duplicate("o1"));
        assert!(!store.is_duplicate("o2"));
    }

    #[test]
    fn empty_batch_accepted() {
        let mut store = ObservationStore::new();
        let req = ObservationIngestRequest {
            observations: vec![],
            idempotency_key: None,
        };
        let result = store.ingest(&req);
        assert_eq!(result.accepted, 0);
        assert_eq!(result.rejected, 0);
    }

    #[test]
    fn mixed_valid_invalid_batch() {
        let mut store = ObservationStore::new();
        let good = make_obs("o-good", "p1");
        let bad = Observation {
            id: String::new(),
            product_id: ProductId::new("p1"),
            baseline: BaselineRevision(1),
            kind: ObservationKind::TestResult,
            result: ObservationResult::Passed,
            source: ObservationSource {
                collector: "test".to_string(),
                version: "0.1.0".to_string(),
                artifact_ref: None,
            },
            recorded_at: ts(1_000_000),
            capability_id: None,
        };
        let req = ObservationIngestRequest {
            observations: vec![good, bad],
            idempotency_key: None,
        };
        let result = store.ingest(&req);
        assert_eq!(result.accepted, 1);
        assert_eq!(result.rejected, 1);
    }

    #[test]
    fn rejected_batch_does_not_record_idempotency_key() {
        let mut store = ObservationStore::new();
        let bad = Observation {
            id: String::new(),
            product_id: ProductId::new("p1"),
            baseline: BaselineRevision(1),
            kind: ObservationKind::TestResult,
            result: ObservationResult::Passed,
            source: ObservationSource {
                collector: "test".to_string(),
                version: "0.1.0".to_string(),
                artifact_ref: None,
            },
            recorded_at: ts(1_000_000),
            capability_id: None,
        };
        let req = ObservationIngestRequest {
            observations: vec![bad],
            idempotency_key: Some("key-1".to_string()),
        };
        let result = store.ingest(&req);
        assert_eq!(result.accepted, 0);

        // Key should NOT be recorded since nothing was accepted
        // Re-ingest with the same key and a valid observation should succeed
        let req2 = ObservationIngestRequest {
            observations: vec![make_obs("o1", "p1")],
            idempotency_key: Some("key-1".to_string()),
        };
        let result2 = store.ingest(&req2);
        assert_eq!(result2.accepted, 1);
    }

    #[test]
    fn observation_result_roundtrip() {
        let mut store = ObservationStore::new();
        let obs = make_obs("o1", "p1");
        let req = ObservationIngestRequest {
            observations: vec![obs.clone()],
            idempotency_key: None,
        };
        store.ingest(&req);
        let retrieved = store.get_observations_for_product("p1");
        assert_eq!(retrieved[0].id, "o1");
        assert_eq!(retrieved[0].result, ObservationResult::Passed);
    }
}
