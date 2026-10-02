use std::sync::Arc;

use async_trait::async_trait;

use super::{
    EvidenceReuseDecision, InvalidationEvent, PersistedBaseline, PersistedEntityRevision,
    PersistedObservation, PersistedProduct, ProductPersistence, ProductPersistenceError,
};

/// Object-safe application boundary for mature product persistence.
///
/// HTTP/MCP transports depend on this façade rather than concrete SQLite/Postgres
/// stores or the legacy monolithic Store trait.
#[async_trait]
pub trait ProductApplicationService: Send + Sync {
    async fn get_product(
        &self,
        product_id: &str,
    ) -> Result<Option<PersistedProduct>, ProductPersistenceError>;

    async fn list_baseline_entities(
        &self,
        product_id: &str,
        baseline_id: &str,
        limit: usize,
    ) -> Result<Vec<PersistedEntityRevision>, ProductPersistenceError>;

    async fn list_observations(
        &self,
        product_id: &str,
        baseline_id: &str,
        subject_local_id: Option<&str>,
        limit: usize,
    ) -> Result<Vec<PersistedObservation>, ProductPersistenceError>;

    async fn list_reuse_decisions_for_target(
        &self,
        target_baseline_id: &str,
        target_candidate_ref: &str,
        limit: usize,
    ) -> Result<Vec<EvidenceReuseDecision>, ProductPersistenceError>;

    async fn list_invalidations(
        &self,
        target_kind: &str,
        target_ref: &str,
        limit: usize,
    ) -> Result<Vec<InvalidationEvent>, ProductPersistenceError>;

    async fn accept_baseline(
        &self,
        baseline: &PersistedBaseline,
        members: &[(String, String)],
    ) -> Result<(), ProductPersistenceError>;
}

pub struct ProductApplication<P> {
    persistence: Arc<P>,
}

impl<P> ProductApplication<P> {
    pub fn new(persistence: Arc<P>) -> Self {
        Self { persistence }
    }
}

#[async_trait]
impl<P> ProductApplicationService for ProductApplication<P>
where
    P: ProductPersistence + Send + Sync + 'static,
{
    async fn get_product(
        &self,
        product_id: &str,
    ) -> Result<Option<PersistedProduct>, ProductPersistenceError> {
        self.persistence.get_product(product_id).await
    }

    async fn list_baseline_entities(
        &self,
        product_id: &str,
        baseline_id: &str,
        limit: usize,
    ) -> Result<Vec<PersistedEntityRevision>, ProductPersistenceError> {
        self.persistence
            .list_baseline_entities(product_id, baseline_id, limit)
            .await
    }

    async fn list_observations(
        &self,
        product_id: &str,
        baseline_id: &str,
        subject_local_id: Option<&str>,
        limit: usize,
    ) -> Result<Vec<PersistedObservation>, ProductPersistenceError> {
        self.persistence
            .list_observations(product_id, baseline_id, subject_local_id, limit)
            .await
    }

    async fn list_reuse_decisions_for_target(
        &self,
        target_baseline_id: &str,
        target_candidate_ref: &str,
        limit: usize,
    ) -> Result<Vec<EvidenceReuseDecision>, ProductPersistenceError> {
        self.persistence
            .list_reuse_decisions_for_target(target_baseline_id, target_candidate_ref, limit)
            .await
    }

    async fn list_invalidations(
        &self,
        target_kind: &str,
        target_ref: &str,
        limit: usize,
    ) -> Result<Vec<InvalidationEvent>, ProductPersistenceError> {
        self.persistence
            .list_invalidations(target_kind, target_ref, limit)
            .await
    }

    async fn accept_baseline(
        &self,
        baseline: &PersistedBaseline,
        members: &[(String, String)],
    ) -> Result<(), ProductPersistenceError> {
        self.persistence.accept_baseline(baseline, members).await
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn assert_object_safe(_: Arc<dyn ProductApplicationService>) {}

    #[test]
    fn product_application_service_is_object_safe() {
        fn accepts(_: &dyn ProductApplicationService) {}
        let _ = accepts;
        let _ = assert_object_safe;
    }
}
