use std::{future::Future, pin::Pin, sync::Arc};

use super::{
    EvidenceReuseDecision, InvalidationEvent, PersistedBaseline, PersistedEntityRevision,
    PersistedObservation, PersistedProduct, ProductPersistence, ProductPersistenceError,
};

type ProductFuture<'a, T> =
    Pin<Box<dyn Future<Output = Result<T, ProductPersistenceError>> + Send + 'a>>;

/// Object-safe application boundary for mature product persistence.
///
/// HTTP/MCP transports depend on this façade rather than concrete SQLite/Postgres
/// stores or the legacy monolithic Store trait.
pub trait ProductApplicationService: Send + Sync {
    fn get_product<'a>(&'a self, product_id: &'a str)
        -> ProductFuture<'a, Option<PersistedProduct>>;

    fn list_baseline_entities<'a>(
        &'a self,
        product_id: &'a str,
        baseline_id: &'a str,
        limit: usize,
    ) -> ProductFuture<'a, Vec<PersistedEntityRevision>>;

    fn list_observations<'a>(
        &'a self,
        product_id: &'a str,
        baseline_id: &'a str,
        subject_local_id: Option<&'a str>,
        limit: usize,
    ) -> ProductFuture<'a, Vec<PersistedObservation>>;

    fn list_reuse_decisions_for_target<'a>(
        &'a self,
        target_baseline_id: &'a str,
        target_candidate_ref: &'a str,
        limit: usize,
    ) -> ProductFuture<'a, Vec<EvidenceReuseDecision>>;

    fn list_invalidations<'a>(
        &'a self,
        target_kind: &'a str,
        target_ref: &'a str,
        limit: usize,
    ) -> ProductFuture<'a, Vec<InvalidationEvent>>;

    fn accept_baseline<'a>(
        &'a self,
        baseline: &'a PersistedBaseline,
        members: &'a [(String, String)],
    ) -> ProductFuture<'a, ()>;
}

pub struct ProductApplication<P> {
    persistence: Arc<P>,
}

impl<P> ProductApplication<P> {
    pub fn new(persistence: Arc<P>) -> Self {
        Self { persistence }
    }
}

impl<P> ProductApplicationService for ProductApplication<P>
where
    P: ProductPersistence + Send + Sync + 'static,
{
    fn get_product<'a>(
        &'a self,
        product_id: &'a str,
    ) -> ProductFuture<'a, Option<PersistedProduct>> {
        Box::pin(async move { self.persistence.get_product(product_id).await })
    }

    fn list_baseline_entities<'a>(
        &'a self,
        product_id: &'a str,
        baseline_id: &'a str,
        limit: usize,
    ) -> ProductFuture<'a, Vec<PersistedEntityRevision>> {
        Box::pin(async move {
            self.persistence
                .list_baseline_entities(product_id, baseline_id, limit)
                .await
        })
    }

    fn list_observations<'a>(
        &'a self,
        product_id: &'a str,
        baseline_id: &'a str,
        subject_local_id: Option<&'a str>,
        limit: usize,
    ) -> ProductFuture<'a, Vec<PersistedObservation>> {
        Box::pin(async move {
            self.persistence
                .list_observations(product_id, baseline_id, subject_local_id, limit)
                .await
        })
    }

    fn list_reuse_decisions_for_target<'a>(
        &'a self,
        target_baseline_id: &'a str,
        target_candidate_ref: &'a str,
        limit: usize,
    ) -> ProductFuture<'a, Vec<EvidenceReuseDecision>> {
        Box::pin(async move {
            self.persistence
                .list_reuse_decisions_for_target(
                    target_baseline_id,
                    target_candidate_ref,
                    limit,
                )
                .await
        })
    }

    fn list_invalidations<'a>(
        &'a self,
        target_kind: &'a str,
        target_ref: &'a str,
        limit: usize,
    ) -> ProductFuture<'a, Vec<InvalidationEvent>> {
        Box::pin(async move {
            self.persistence
                .list_invalidations(target_kind, target_ref, limit)
                .await
        })
    }

    fn accept_baseline<'a>(
        &'a self,
        baseline: &'a PersistedBaseline,
        members: &'a [(String, String)],
    ) -> ProductFuture<'a, ()> {
        Box::pin(async move { self.persistence.accept_baseline(baseline, members).await })
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
