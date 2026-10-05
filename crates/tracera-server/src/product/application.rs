//! Backend-neutral application boundary for product reads and baseline acceptance.

use std::{future::Future, pin::Pin, sync::Arc};

use super::{
    dependencies::{DependencyAuthority, DependencyEdge},
    invalidation_service::{execute_dependency_invalidation, PersistedInvalidationResult},
    EvidenceReuseDecision, InvalidationEvent, PersistedBaseline, PersistedDependencyEdge,
    PersistedEntityRevision, PersistedObservation, PersistedProduct, ProductPersistence,
    ProductPersistenceError,
};

pub const MAX_PRODUCT_READ_LIMIT: u32 = 1000;

pub type ProductFuture<'a, T> =
    Pin<Box<dyn Future<Output = Result<T, ProductPersistenceError>> + Send + 'a>>;

/// Object-safe application boundary. The legacy Store is deliberately separate.
pub trait ProductApplicationService: Send + Sync {
    fn get_product<'a>(
        &'a self,
        product_id: &'a str,
    ) -> ProductFuture<'a, Option<PersistedProduct>>;

    fn list_baseline_entities<'a>(
        &'a self,
        product_id: &'a str,
        baseline_id: &'a str,
        limit: u32,
    ) -> ProductFuture<'a, Vec<PersistedEntityRevision>>;

    fn list_observations<'a>(
        &'a self,
        product_id: &'a str,
        baseline_id: &'a str,
        subject_local_id: Option<&'a str>,
        limit: u32,
    ) -> ProductFuture<'a, Vec<PersistedObservation>>;

    fn list_reuse_decisions_for_target<'a>(
        &'a self,
        product_id: &'a str,
        target_baseline_id: &'a str,
        target_candidate_ref: &'a str,
        limit: u32,
    ) -> ProductFuture<'a, Vec<EvidenceReuseDecision>>;

    fn list_invalidations<'a>(
        &'a self,
        product_id: &'a str,
        target_kind: &'a str,
        target_ref: &'a str,
        limit: u32,
    ) -> ProductFuture<'a, Vec<InvalidationEvent>>;

    fn append_dependency_edge<'a>(
        &'a self,
        product_id: &'a str,
        edge: &'a PersistedDependencyEdge,
    ) -> ProductFuture<'a, ()>;

    fn execute_dependency_invalidation<'a>(
        &'a self,
        product_id: &'a str,
        changed: &'a [String],
        revision: &'a str,
        max_nodes: usize,
        trigger_ref: &'a str,
        target_kind: &'a str,
    ) -> ProductFuture<'a, PersistedInvalidationResult>;

    fn append_observation<'a>(
        &'a self,
        product_id: &'a str,
        baseline_id: &'a str,
        observation: &'a PersistedObservation,
    ) -> ProductFuture<'a, ()>;

    fn append_reuse_decision<'a>(
        &'a self,
        product_id: &'a str,
        target_baseline_id: &'a str,
        decision: &'a EvidenceReuseDecision,
    ) -> ProductFuture<'a, ()>;

    fn accept_baseline<'a>(
        &'a self,
        product_id: &'a str,
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

fn validate_limit(limit: u32) -> Result<(), ProductPersistenceError> {
    if !(1..=MAX_PRODUCT_READ_LIMIT).contains(&limit) {
        return Err(ProductPersistenceError::Invalid(format!(
            "read limit must be between 1 and {MAX_PRODUCT_READ_LIMIT}"
        )));
    }
    Ok(())
}

impl<P: ProductPersistence> ProductApplication<P> {
    async fn require_product(&self, product_id: &str) -> Result<(), ProductPersistenceError> {
        self.persistence
            .get_product(product_id)
            .await?
            .filter(|product| product.product_id == product_id)
            .ok_or_else(|| ProductPersistenceError::NotFound("product not found".into()))?;
        Ok(())
    }

    async fn require_baseline(
        &self,
        product_id: &str,
        baseline_id: &str,
    ) -> Result<(), ProductPersistenceError> {
        // An empty membership list can mean either a valid empty baseline or
        // a missing/foreign baseline. It is never an ownership certificate.
        self.persistence
            .get_baseline(product_id, baseline_id)
            .await?
            .filter(|baseline| {
                baseline.product_id == product_id && baseline.baseline_id == baseline_id
            })
            .ok_or_else(|| {
                ProductPersistenceError::NotFound("baseline not found in product scope".into())
            })?;
        Ok(())
    }
}

impl<P> ProductApplicationService for ProductApplication<P>
where
    P: ProductPersistence + 'static,
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
        limit: u32,
    ) -> ProductFuture<'a, Vec<PersistedEntityRevision>> {
        Box::pin(async move {
            validate_limit(limit)?;
            self.require_baseline(product_id, baseline_id).await?;
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
        limit: u32,
    ) -> ProductFuture<'a, Vec<PersistedObservation>> {
        Box::pin(async move {
            validate_limit(limit)?;
            self.require_baseline(product_id, baseline_id).await?;
            self.persistence
                .list_observations(product_id, baseline_id, subject_local_id, limit)
                .await
        })
    }

    fn list_reuse_decisions_for_target<'a>(
        &'a self,
        product_id: &'a str,
        target_baseline_id: &'a str,
        target_candidate_ref: &'a str,
        limit: u32,
    ) -> ProductFuture<'a, Vec<EvidenceReuseDecision>> {
        Box::pin(async move {
            validate_limit(limit)?;
            self.require_baseline(product_id, target_baseline_id)
                .await?;
            self.persistence
                .list_reuse_decisions_for_target(
                    product_id,
                    target_baseline_id,
                    target_candidate_ref,
                    limit,
                )
                .await
        })
    }

    fn list_invalidations<'a>(
        &'a self,
        product_id: &'a str,
        target_kind: &'a str,
        target_ref: &'a str,
        limit: u32,
    ) -> ProductFuture<'a, Vec<InvalidationEvent>> {
        Box::pin(async move {
            validate_limit(limit)?;
            self.require_product(product_id).await?;
            self.persistence
                .list_invalidations(product_id, target_kind, target_ref, limit)
                .await
        })
    }

    fn append_dependency_edge<'a>(
        &'a self,
        product_id: &'a str,
        edge: &'a PersistedDependencyEdge,
    ) -> ProductFuture<'a, ()> {
        Box::pin(async move {
            if edge.product_id != product_id {
                return Err(ProductPersistenceError::Invalid(
                    "dependency edge product must match request path".into(),
                ));
            }
            self.require_product(product_id).await?;
            self.persistence.append_dependency_edge(edge).await
        })
    }

    fn execute_dependency_invalidation<'a>(
        &'a self,
        product_id: &'a str,
        changed: &'a [String],
        revision: &'a str,
        max_nodes: usize,
        trigger_ref: &'a str,
        target_kind: &'a str,
    ) -> ProductFuture<'a, PersistedInvalidationResult> {
        Box::pin(async move {
            if changed.is_empty() {
                return Err(ProductPersistenceError::Invalid(
                    "dependency invalidation requires at least one changed reference".into(),
                ));
            }
            if max_nodes == 0 || max_nodes > 100_000 {
                return Err(ProductPersistenceError::Invalid(
                    "max_nodes must be between 1 and 100000".into(),
                ));
            }
            if revision.trim().is_empty() || trigger_ref.trim().is_empty() || target_kind.trim().is_empty() {
                return Err(ProductPersistenceError::Invalid(
                    "revision, trigger_ref, and target_kind are required".into(),
                ));
            }

            self.require_product(product_id).await?;
            let persisted = self
                .persistence
                .list_dependency_edges(product_id, revision)
                .await?;
            let mut edges = Vec::with_capacity(persisted.len());
            for edge in persisted {
                let authority = match edge.authority.as_str() {
                    "deterministic" => DependencyAuthority::Deterministic,
                    "accepted" => DependencyAuthority::Accepted,
                    "declared" => DependencyAuthority::Declared,
                    "inferred" => DependencyAuthority::Inferred,
                    other => {
                        return Err(ProductPersistenceError::Backend(format!(
                            "persisted dependency edge {} has unknown authority {}",
                            edge.dependency_edge_id, other
                        )));
                    }
                };
                edges.push(DependencyEdge {
                    dependency: edge.dependency_ref,
                    dependent: edge.dependent_ref,
                    authority,
                    revision: edge.revision,
                    active: edge.active,
                });
            }

            execute_dependency_invalidation(
                self.persistence.as_ref(),
                product_id,
                changed,
                &edges,
                revision,
                max_nodes,
                trigger_ref,
                target_kind,
            )
            .await
        })
    }

    fn append_observation<'a>(
        &'a self,
        product_id: &'a str,
        baseline_id: &'a str,
        observation: &'a PersistedObservation,
    ) -> ProductFuture<'a, ()> {
        Box::pin(async move {
            if observation.product_id != product_id || observation.baseline_id != baseline_id {
                return Err(ProductPersistenceError::Invalid(
                    "observation scope must match product/baseline path".into(),
                ));
            }
            self.require_baseline(product_id, baseline_id).await?;
            self.persistence.append_observation(observation).await
        })
    }

    fn append_reuse_decision<'a>(
        &'a self,
        product_id: &'a str,
        target_baseline_id: &'a str,
        decision: &'a EvidenceReuseDecision,
    ) -> ProductFuture<'a, ()> {
        Box::pin(async move {
            if decision.target_baseline_id != target_baseline_id {
                return Err(ProductPersistenceError::Invalid(
                    "reuse decision target baseline must match request path".into(),
                ));
            }
            self.require_baseline(product_id, target_baseline_id)
                .await?;
            // Persistence verifies that the source observation belongs to the
            // same product; the application boundary must not infer ownership
            // from an observation identifier.
            self.persistence.append_reuse_decision(decision).await
        })
    }

    fn accept_baseline<'a>(
        &'a self,
        product_id: &'a str,
        baseline: &'a PersistedBaseline,
        members: &'a [(String, String)],
    ) -> ProductFuture<'a, ()> {
        Box::pin(async move {
            if baseline.product_id != product_id {
                return Err(ProductPersistenceError::Invalid(
                    "baseline product must match request path".into(),
                ));
            }
            self.require_product(product_id).await?;
            self.persistence.accept_baseline(baseline, members).await
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn product_application_service_is_object_safe() {
        fn accepts(_: Arc<dyn ProductApplicationService>) {}
        let _ = accepts;
    }

    #[test]
    fn direct_application_calls_cannot_request_unbounded_reads() {
        assert!(validate_limit(0).is_err());
        assert!(validate_limit(1).is_ok());
        assert!(validate_limit(MAX_PRODUCT_READ_LIMIT).is_ok());
        assert!(validate_limit(u32::MAX).is_err());
    }
}
