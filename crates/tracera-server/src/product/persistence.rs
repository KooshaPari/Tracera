//! Narrow persistence contract for the mature product vertical slice.
//!
//! This deliberately does not extend the legacy broad Store trait yet.
//! VS-02/03 use this port to prove product/baseline/history semantics first.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct PersistedProduct {
    pub product_id: String,
    pub display_name: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PersistedBaseline {
    pub baseline_id: String,
    pub product_id: String,
    pub revision_number: i64,
    pub parent_baseline_id: Option<String>,
    pub accepted_at: DateTime<Utc>,
    pub metadata: Value,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PersistedEntity {
    pub entity_id: String,
    pub product_id: String,
    pub local_id: String,
    pub entity_kind: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PersistedEntityRevision {
    pub entity_revision_id: String,
    pub entity_id: String,
    pub content_revision: i64,
    pub title: String,
    pub description: String,
    pub status: String,
    pub metadata: Value,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PersistedDependencyEdge {
    pub dependency_edge_id: String,
    pub product_id: String,
    pub dependency_ref: String,
    pub dependent_ref: String,
    pub authority: String,
    pub revision: String,
    pub active: bool,
    pub recorded_at: DateTime<Utc>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PersistedObservation {
    pub observation_id: String,
    pub product_id: String,
    pub baseline_id: String,
    pub subject_entity_id: Option<String>,
    pub subject_local_id: Option<String>,
    pub candidate_ref: String,
    pub configuration: Value,
    pub result: String,
    pub verifier_id: String,
    pub verifier_version: String,
    pub recorded_at: DateTime<Utc>,
    pub raw_evidence_ref: Option<String>,
    pub metadata: Value,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EvidenceReuseDecision {
    pub reuse_decision_id: String,
    pub observation_id: String,
    pub target_baseline_id: String,
    pub target_candidate_ref: String,
    pub criterion_ref: String,
    pub applicability_state: String,
    pub compatibility_certificate_ref: Option<String>,
    pub policy_version: String,
    pub reason: String,
    pub decided_at: DateTime<Utc>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct InvalidationEvent {
    pub invalidation_id: String,
    pub product_id: String,
    pub trigger_kind: String,
    pub trigger_ref: String,
    pub target_kind: String,
    pub target_ref: String,
    pub prior_state: Option<String>,
    pub new_state: String,
    pub reason: String,
    pub occurred_at: DateTime<Utc>,
}

/// Product persistence errors remain backend-neutral at the application boundary.
#[derive(Debug, thiserror::Error)]
pub enum ProductPersistenceError {
    #[error("product persistence item not found: {0}")]
    NotFound(String),
    #[error("product persistence conflict: {0}")]
    Conflict(String),
    #[error("invalid product persistence request: {0}")]
    Invalid(String),
    #[error("product persistence backend error: {0}")]
    Backend(String),
}

/// Focused persistence port for the mature product slice.
///
/// Historical objects are append-oriented. Implementations must not silently
/// mutate an accepted baseline or overwrite an observation.
pub trait ProductPersistence: Send + Sync {
    fn create_product(
        &self,
        product: &PersistedProduct,
    ) -> impl std::future::Future<Output = Result<(), ProductPersistenceError>> + Send;

    fn get_product(
        &self,
        product_id: &str,
    ) -> impl std::future::Future<Output = Result<Option<PersistedProduct>, ProductPersistenceError>>
           + Send;

    fn accept_baseline(
        &self,
        baseline: &PersistedBaseline,
        members: &[(String, String)],
    ) -> impl std::future::Future<Output = Result<(), ProductPersistenceError>> + Send;

    fn get_baseline(
        &self,
        product_id: &str,
        baseline_id: &str,
    ) -> impl std::future::Future<Output = Result<Option<PersistedBaseline>, ProductPersistenceError>>
           + Send;

    fn create_entity(
        &self,
        entity: &PersistedEntity,
    ) -> impl std::future::Future<Output = Result<(), ProductPersistenceError>> + Send;

    fn append_entity_revision(
        &self,
        revision: &PersistedEntityRevision,
    ) -> impl std::future::Future<Output = Result<(), ProductPersistenceError>> + Send;

    fn list_baseline_entities(
        &self,
        product_id: &str,
        baseline_id: &str,
        limit: u32,
    ) -> impl std::future::Future<
        Output = Result<Vec<PersistedEntityRevision>, ProductPersistenceError>,
    > + Send;

    fn append_dependency_edge(
        &self,
        edge: &PersistedDependencyEdge,
    ) -> impl std::future::Future<Output = Result<(), ProductPersistenceError>> + Send;

    fn list_dependency_edges(
        &self,
        product_id: &str,
        revision: &str,
    ) -> impl std::future::Future<
        Output = Result<Vec<PersistedDependencyEdge>, ProductPersistenceError>,
    > + Send;

    fn append_observation(
        &self,
        observation: &PersistedObservation,
    ) -> impl std::future::Future<Output = Result<(), ProductPersistenceError>> + Send;

    fn list_observations(
        &self,
        product_id: &str,
        baseline_id: &str,
        subject_local_id: Option<&str>,
        limit: u32,
    ) -> impl std::future::Future<Output = Result<Vec<PersistedObservation>, ProductPersistenceError>>
           + Send;

    fn append_reuse_decision(
        &self,
        decision: &EvidenceReuseDecision,
    ) -> impl std::future::Future<Output = Result<(), ProductPersistenceError>> + Send;

    /// Read historical reuse decisions, not their current applicability projection.
    /// Both the observation and target baseline must belong to product_id.
    fn list_reuse_decisions_for_target(
        &self,
        product_id: &str,
        target_baseline_id: &str,
        target_candidate_ref: &str,
        limit: u32,
    ) -> impl std::future::Future<Output = Result<Vec<EvidenceReuseDecision>, ProductPersistenceError>>
           + Send;

    fn append_invalidation(
        &self,
        event: &InvalidationEvent,
    ) -> impl std::future::Future<Output = Result<(), ProductPersistenceError>> + Send;

    /// Persist an invalidation batch atomically. Exact replay is idempotent;
    /// reusing an invalidation_id for different immutable content is a conflict.
    fn append_invalidations(
        &self,
        events: &[InvalidationEvent],
    ) -> impl std::future::Future<Output = Result<(), ProductPersistenceError>> + Send;

    fn list_invalidations(
        &self,
        product_id: &str,
        target_kind: &str,
        target_ref: &str,
        limit: u32,
    ) -> impl std::future::Future<Output = Result<Vec<InvalidationEvent>, ProductPersistenceError>> + Send;
}
