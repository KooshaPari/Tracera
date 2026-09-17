#![allow(dead_code)]

//! Product-aware observation ingestion pipeline (WP-08).
//!
//! This module provides the write-side ingestion pipeline for [`Observation`]
//! values into the product model.  It validates each incoming observation,
//! enforces idempotency at both the observation-ID and batch-key level, and
//! stores accepted observations in an in-memory [`ObservationStore`] that will
//! be wired to a persistent backend in a future work package.
//!
//! Part of WP-08 (Product-aware observation ingestion pipeline):
//!
//! - **R15** — Ingestion must be idempotent: re-submitting the same batch
//!   (identified by an optional idempotency key) must not create duplicates.
//! - **R16** — Observations with empty IDs or product IDs must be rejected.
//! - **R17** — Observations with timestamps in the far future must be rejected.
//! - **R18** — The store must support lookup by product ID and capability ID.

use std::collections::HashSet;

use chrono::{Duration, Utc};

use super::observation::Observation;

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/// Maximum number of minutes into the future a `recorded_at` timestamp may be
/// before the observation is rejected as implausible (R17).
const FUTURE_TOLERANCE_MINUTES: i64 = 5;

// ---------------------------------------------------------------------------
// ObservationIngestRequest
// ---------------------------------------------------------------------------

/// Input payload for the observation ingestion pipeline.
///
/// Contains a batch of [`Observation`] values and an optional idempotency key.
/// If the key matches a previously accepted batch, the entire batch is
/// rejected (R15).
#[derive(Debug, Clone)]
pub struct ObservationIngestRequest {
    /// The observations to ingest.
    pub observations: Vec<Observation>,
    /// Optional idempotency key for batch-level deduplication.
    pub idempotency_key: Option<String>,
}

// ---------------------------------------------------------------------------
// IngestResult
// ---------------------------------------------------------------------------

/// Outcome of a single ingestion call.
///
/// Reports how many observations were accepted, how many were rejected, and
/// which observation IDs were stored.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct IngestResult {
    /// Number of new observations accepted and stored.
    pub accepted: usize,
    /// Number of observations rejected (duplicates, invalid, or batch-level
    /// idempotency failure).
    pub rejected: usize,
    /// Human-readable error messages for each rejected observation.
    pub errors: Vec<String>,
    /// IDs of the observations that were accepted.
    pub observation_ids: Vec<String>,
}

// ---------------------------------------------------------------------------
// ObservationStore
// ---------------------------------------------------------------------------

/// In-memory store for validated observations.
///
/// Provides idempotent ingestion, validation, and lookup by product or
/// capability.  The store will be backed by a persistent database in a
/// future work package.
#[derive(Debug, Default)]
pub struct ObservationStore {
    /// All stored observations, keyed by their unique ID.
    observations: Vec<Observation>,
    /// Set of observation IDs already stored (fast duplicate check).
    id_index: HashSet<String>,
    /// Set of idempotency keys already consumed.
    idempotency_keys: HashSet<String>,
}

impl ObservationStore {
    /// Create an empty store.
    pub fn new() -> Self {
        Self::default()
    }

    /// Ingest a batch of observations from the given [`ObservationIngestRequest`].
    ///
    /// Each observation is individually validated:
    ///
    /// - Empty `id` → rejected.
    /// - Empty `product_id` → rejected.
    /// - Duplicate `id` (already stored) → rejected.
    /// - `recorded_at` more than 5 minutes in the future → rejected.
    ///
    /// If the request carries an `idempotency_key` that was seen in a
    /// previous ingest call, **all** observations in the batch are rejected.
    pub fn ingest(&mut self, request: &ObservationIngestRequest) -> IngestResult {
        let mut accepted = 0usize;
        let mut rejected = 0usize;
        let mut errors = Vec::new();
        let mut observation_ids = Vec::new();

        // --- Batch-level idempotency check (R15) ---
        if let Some(ref key) = request.idempotency_key {
            if self.idempotency_keys.contains(key.as_str()) {
                let count = request.observations.len();
                rejected += count;
                errors.push(format!(
                    "Batch idempotency key '{}' was already consumed; \
                     all {count} observation(s) rejected.",
                    key
                ));
                return IngestResult {
                    accepted,
                    rejected,
                    errors,
                    observation_ids,
                };
            }
        }

        let now = Utc::now();
        let tolerance = Duration::minutes(FUTURE_TOLERANCE_MINUTES);

        for obs in &request.observations {
            // R16 — Empty ID.
            if obs.id.is_empty() {
                rejected += 1;
                errors.push("Observation has an empty ID and was rejected.".to_string());
                continue;
            }

            // R16 — Empty product_id.
            if obs.product_id.as_str().is_empty() {
                rejected += 1;
                errors.push(format!(
                    "Observation '{}' has an empty product_id and was rejected.",
                    obs.id
                ));
                continue;
            }

            // Duplicate detection (R15 — observation-level).
            if self.id_index.contains(obs.id.as_str()) {
                rejected += 1;
                errors.push(format!(
                    "Observation '{}' is a duplicate and was rejected.",
                    obs.id
                ));
                continue;
            }

            // R17 — Future timestamp.
            if obs.recorded_at > now + tolerance {
                rejected += 1;
                errors.push(format!(
                    "Observation '{}' has a recorded_at timestamp in the \
                     future (beyond {}-minute tolerance) and was rejected.",
                    obs.id, FUTURE_TOLERANCE_MINUTES
                ));
                continue;
            }

            // All checks passed — store the observation.
            observation_ids.push(obs.id.clone());
            self.id_index.insert(obs.id.clone());
            self.observations.push(obs.clone());
            accepted += 1;
        }

        // Record the idempotency key only if at least one observation was
        // accepted (otherwise a fully-rejected batch does not "consume" the key).
        if accepted > 0 {
            if let Some(ref key) = request.idempotency_key {
                self.idempotency_keys.insert(key.clone());
            }
        }

        IngestResult {
            accepted,
            rejected,
            errors,
            observation_ids,
        }
    }

    /// Retrieve all observations for a given product ID.
    pub fn get_observations_for_product(&self, product_id: &str) -> Vec<&Observation> {
        self.observations
            .iter()
            .filter(|o| o.product_id.as_str() == product_id)
            .collect()
    }

    /// Retrieve all observations associated with a given capability ID.
    pub fn get_observations_for_capability(&self, capability_id: &str) -> Vec<&Observation> {
        self.observations
            .iter()
            .filter(|o| o.capability_id.as_deref() == Some(capability_id))
            .collect()
    }

    /// Returns `true` if the given observation ID is already stored.
    pub fn is_duplicate(&self, observation_id: &str) -> bool {
        self.id_index.contains(observation_id)
    }

    /// Total number of stored observations.
    pub fn count(&self) -> usize {
        self.observations.len()
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

    /// Helper to build a valid observation with sensible defaults.
    fn make_obs(id: &str, product_id: &str) -> Observation {
        Observation {
            id: id.to_string(),
            product_id: ProductId::new(product_id),
            baseline: BaselineRevision(1),
            kind: ObservationKind::TestResult,
            result: ObservationResult::Passed,
            source: ObservationSource {
                collector: "cargo-test".to_string(),
                version: "0.1.0".to_string(),
                artifact_ref: None,
            },
            recorded_at: Utc::now(),
            capability_id: None,
        }
    }

    /// Build a request with no idempotency key.
    fn simple_request(observations: Vec<Observation>) -> ObservationIngestRequest {
        ObservationIngestRequest {
            observations,
            idempotency_key: None,
        }
    }

    // ----- Happy path -----

    #[test]
    fn ingest_single_valid_observation() {
        let mut store = ObservationStore::new();
        let req = simple_request(vec![make_obs("obs-1", "prod-a")]);
        let result = store.ingest(&req);

        assert_eq!(result.accepted, 1);
        assert_eq!(result.rejected, 0);
        assert!(result.errors.is_empty());
        assert_eq!(result.observation_ids, vec!["obs-1"]);
        assert_eq!(store.count(), 1);
    }

    #[test]
    fn ingest_multiple_valid_observations() {
        let mut store = ObservationStore::new();
        let req = simple_request(vec![
            make_obs("obs-1", "prod-a"),
            make_obs("obs-2", "prod-a"),
            make_obs("obs-3", "prod-b"),
        ]);
        let result = store.ingest(&req);

        assert_eq!(result.accepted, 3);
        assert_eq!(result.rejected, 0);
        assert!(result.errors.is_empty());
        assert_eq!(store.count(), 3);
    }

    // ----- Duplicate detection -----

    #[test]
    fn duplicate_observation_id_rejected() {
        let mut store = ObservationStore::new();
        let req1 = simple_request(vec![make_obs("obs-1", "prod-a")]);
        store.ingest(&req1);

        let req2 = simple_request(vec![make_obs("obs-1", "prod-a")]);
        let result = store.ingest(&req2);

        assert_eq!(result.accepted, 0);
        assert_eq!(result.rejected, 1);
        assert_eq!(result.errors.len(), 1);
        assert!(result.errors[0].contains("duplicate"));
        assert_eq!(store.count(), 1);
    }

    #[test]
    fn is_duplicate_returns_true_for_stored_obs() {
        let mut store = ObservationStore::new();
        assert!(!store.is_duplicate("obs-1"));

        let req = simple_request(vec![make_obs("obs-1", "prod-a")]);
        store.ingest(&req);

        assert!(store.is_duplicate("obs-1"));
        assert!(!store.is_duplicate("obs-2"));
    }

    // ----- Idempotency key -----

    #[test]
    fn same_idempotency_key_rejects_batch() {
        let mut store = ObservationStore::new();

        let req1 = ObservationIngestRequest {
            observations: vec![make_obs("obs-1", "prod-a")],
            idempotency_key: Some("key-abc".to_string()),
        };
        let result1 = store.ingest(&req1);
        assert_eq!(result1.accepted, 1);

        // Re-submit with the same key — all observations should be rejected.
        let req2 = ObservationIngestRequest {
            observations: vec![make_obs("obs-2", "prod-a")],
            idempotency_key: Some("key-abc".to_string()),
        };
        let result2 = store.ingest(&req2);
        assert_eq!(result2.accepted, 0);
        assert_eq!(result2.rejected, 1);
        assert!(result2.errors[0].contains("key-abc"));
        assert_eq!(store.count(), 1);
    }

    #[test]
    fn different_idempotency_key_accepted() {
        let mut store = ObservationStore::new();

        let req1 = ObservationIngestRequest {
            observations: vec![make_obs("obs-1", "prod-a")],
            idempotency_key: Some("key-1".to_string()),
        };
        store.ingest(&req1);

        let req2 = ObservationIngestRequest {
            observations: vec![make_obs("obs-2", "prod-a")],
            idempotency_key: Some("key-2".to_string()),
        };
        let result2 = store.ingest(&req2);
        assert_eq!(result2.accepted, 1);
        assert_eq!(store.count(), 2);
    }

    #[test]
    fn no_idempotency_key_allows_reingest_of_different_obs() {
        let mut store = ObservationStore::new();
        let req1 = simple_request(vec![make_obs("obs-1", "prod-a")]);
        store.ingest(&req1);

        let req2 = simple_request(vec![make_obs("obs-2", "prod-a")]);
        let result = store.ingest(&req2);
        assert_eq!(result.accepted, 1);
    }

    // ----- Validation: empty ID -----

    #[test]
    fn empty_observation_id_rejected() {
        let mut store = ObservationStore::new();
        let obs = make_obs("", "prod-a");
        let req = simple_request(vec![obs]);
        let result = store.ingest(&req);

        assert_eq!(result.accepted, 0);
        assert_eq!(result.rejected, 1);
        assert!(result.errors[0].contains("empty ID"));
    }

    // ----- Validation: empty product_id -----

    #[test]
    fn empty_product_id_rejected() {
        let mut store = ObservationStore::new();
        let obs = make_obs("obs-1", "");
        let req = simple_request(vec![obs]);
        let result = store.ingest(&req);

        assert_eq!(result.accepted, 0);
        assert_eq!(result.rejected, 1);
        assert!(result.errors[0].contains("empty product_id"));
    }

    // ----- Validation: future timestamp -----

    #[test]
    fn future_timestamp_rejected() {
        let mut store = ObservationStore::new();
        let mut obs = make_obs("obs-future", "prod-a");
        obs.recorded_at = Utc::now() + Duration::minutes(10);
        let req = simple_request(vec![obs]);
        let result = store.ingest(&req);

        assert_eq!(result.accepted, 0);
        assert_eq!(result.rejected, 1);
        assert!(result.errors[0].contains("future"));
    }

    #[test]
    fn timestamp_within_tolerance_accepted() {
        let mut store = ObservationStore::new();
        let mut obs = make_obs("obs-ok", "prod-a");
        obs.recorded_at = Utc::now() + Duration::minutes(3);
        let req = simple_request(vec![obs]);
        let result = store.ingest(&req);

        assert_eq!(result.accepted, 1);
        assert_eq!(result.rejected, 0);
    }

    // ----- Retrieval: by product -----

    #[test]
    fn get_observations_for_product() {
        let mut store = ObservationStore::new();
        let req = simple_request(vec![
            make_obs("obs-1", "prod-a"),
            make_obs("obs-2", "prod-a"),
            make_obs("obs-3", "prod-b"),
        ]);
        store.ingest(&req);

        let a = store.get_observations_for_product("prod-a");
        assert_eq!(a.len(), 2);

        let b = store.get_observations_for_product("prod-b");
        assert_eq!(b.len(), 1);

        let c = store.get_observations_for_product("prod-c");
        assert!(c.is_empty());
    }

    // ----- Retrieval: by capability -----

    #[test]
    fn get_observations_for_capability() {
        let mut store = ObservationStore::new();

        let mut obs1 = make_obs("obs-1", "prod-a");
        obs1.capability_id = Some("cap-storage".to_string());
        let mut obs2 = make_obs("obs-2", "prod-a");
        obs2.capability_id = Some("cap-storage".to_string());
        let mut obs3 = make_obs("obs-3", "prod-a");
        obs3.capability_id = Some("cap-auth".to_string());
        let obs4 = make_obs("obs-4", "prod-a"); // no capability

        let req = simple_request(vec![obs1, obs2, obs3, obs4]);
        store.ingest(&req);

        let storage = store.get_observations_for_capability("cap-storage");
        assert_eq!(storage.len(), 2);

        let auth = store.get_observations_for_capability("cap-auth");
        assert_eq!(auth.len(), 1);

        let unknown = store.get_observations_for_capability("cap-missing");
        assert!(unknown.is_empty());
    }

    // ----- Roundtrip: ingest then query -----

    #[test]
    fn roundtrip_ingest_then_query_by_product() {
        let mut store = ObservationStore::new();
        let mut obs = make_obs("obs-roundtrip", "prod-x");
        obs.kind = ObservationKind::Measurement;
        obs.result = ObservationResult::Failed;
        obs.capability_id = Some("cap-perf".to_string());

        let req = simple_request(vec![obs]);
        let result = store.ingest(&req);
        assert_eq!(result.accepted, 1);

        let stored = store.get_observations_for_product("prod-x");
        assert_eq!(stored.len(), 1);
        assert_eq!(stored[0].kind, ObservationKind::Measurement);
        assert_eq!(stored[0].result, ObservationResult::Failed);
        assert_eq!(stored[0].capability_id.as_deref(), Some("cap-perf"));
    }

    // ----- Mixed batch: some valid, some invalid -----

    #[test]
    fn mixed_valid_and_invalid_batch() {
        let mut store = ObservationStore::new();

        let valid = make_obs("obs-valid", "prod-a");
        let mut invalid_future = make_obs("obs-future", "prod-a");
        invalid_future.recorded_at = Utc::now() + Duration::minutes(20);

        let req = simple_request(vec![valid, invalid_future]);
        let result = store.ingest(&req);

        assert_eq!(result.accepted, 1);
        assert_eq!(result.rejected, 1);
        assert_eq!(result.observation_ids, vec!["obs-valid"]);
        assert_eq!(store.count(), 1);
    }

    // ----- Empty batch -----

    #[test]
    fn empty_batch_accepted_with_no_counts() {
        let mut store = ObservationStore::new();
        let req = simple_request(vec![]);
        let result = store.ingest(&req);

        assert_eq!(result.accepted, 0);
        assert_eq!(result.rejected, 0);
        assert!(result.errors.is_empty());
        assert!(result.observation_ids.is_empty());
    }

    // ----- Idempotency key not consumed on full rejection -----

    #[test]
    fn idempotency_key_not_consumed_on_full_rejection() {
        let mut store = ObservationStore::new();

        // First batch — all observations are invalid (empty ID).
        let req1 = ObservationIngestRequest {
            observations: vec![make_obs("", "prod-a")],
            idempotency_key: Some("key-reject".to_string()),
        };
        let result1 = store.ingest(&req1);
        assert_eq!(result1.accepted, 0);
        assert_eq!(result1.rejected, 1);

        // Second batch with same key but valid observation — should succeed
        // because the key was never "consumed" (no accepts in first batch).
        let req2 = ObservationIngestRequest {
            observations: vec![make_obs("obs-ok", "prod-a")],
            idempotency_key: Some("key-reject".to_string()),
        };
        let result2 = store.ingest(&req2);
        assert_eq!(result2.accepted, 1);
    }
}
