//! SQLite implementation of the narrow product persistence port.

use sqlx::Row;

use crate::product::persistence::{
    EvidenceReuseDecision, InvalidationEvent, PersistedBaseline, PersistedEntity,
    PersistedEntityRevision, PersistedObservation, PersistedProduct, ProductPersistence,
    ProductPersistenceError,
};

use super::{str_to_ts, ts_to_str, SqliteStore};

fn backend(error: impl std::fmt::Display) -> ProductPersistenceError {
    ProductPersistenceError::Backend(error.to_string())
}

impl ProductPersistence for SqliteStore {
    async fn create_product(
        &self,
        product: &PersistedProduct,
    ) -> Result<(), ProductPersistenceError> {
        // Product registry identity remains in the additive compatibility table.
        sqlx::query(
            "INSERT OR IGNORE INTO product_nodes
             (id, product_id, intent_kind, title, description, status, baseline_revision, created_at, updated_at)
             VALUES (?1, ?1, 'product', ?2, '', 'accepted', 0, ?3, ?3)"
        )
        .bind(&product.product_id)
        .bind(&product.display_name)
        .bind(ts_to_str(product.created_at))
        .execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }

    async fn get_product(
        &self,
        product_id: &str,
    ) -> Result<Option<PersistedProduct>, ProductPersistenceError> {
        let row = sqlx::query(
            "SELECT product_id, title, created_at FROM product_nodes
             WHERE id=?1 AND product_id=?1 AND intent_kind='product'",
        )
        .bind(product_id)
        .fetch_optional(&self.pool)
        .await
        .map_err(backend)?;
        Ok(row.map(|r| PersistedProduct {
            product_id: r.get("product_id"),
            display_name: r.get("title"),
            created_at: str_to_ts(&r.get::<String, _>("created_at")),
        }))
    }

    async fn accept_baseline(
        &self,
        baseline: &PersistedBaseline,
        members: &[(String, String)],
    ) -> Result<(), ProductPersistenceError> {
        let mut tx = self.pool.begin().await.map_err(backend)?;
        let product_exists: Option<i64> = sqlx::query_scalar(
            "SELECT 1 FROM product_nodes
             WHERE id=?1 AND product_id=?1 AND intent_kind='product'",
        )
        .bind(&baseline.product_id)
        .fetch_optional(&mut *tx)
        .await
        .map_err(backend)?;
        if product_exists.is_none() {
            return Err(ProductPersistenceError::Invalid(format!(
                "baseline {} references unknown product {}",
                baseline.baseline_id, baseline.product_id
            )));
        }
        if let Some(parent_id) = &baseline.parent_baseline_id {
            let parent_product: Option<String> = sqlx::query_scalar(
                "SELECT product_id FROM product_baselines_v1 WHERE baseline_id=?1",
            )
            .bind(parent_id)
            .fetch_optional(&mut *tx)
            .await
            .map_err(backend)?;
            match parent_product {
                Some(parent_product) if parent_product == baseline.product_id => {}
                Some(parent_product) => {
                    return Err(ProductPersistenceError::Invalid(format!(
                        "baseline {} for product {} cannot parent baseline {} from product {}",
                        baseline.baseline_id, baseline.product_id, parent_id, parent_product
                    )));
                }
                None => {
                    return Err(ProductPersistenceError::Invalid(format!(
                        "baseline {} references missing parent baseline {}",
                        baseline.baseline_id, parent_id
                    )));
                }
            }
        }
        for (entity_id, revision_id) in members {
            let valid: Option<i64> = sqlx::query_scalar(
                "SELECT 1
                 FROM product_entities_v1 e
                 JOIN product_entity_revisions_v1 r ON r.entity_id = e.entity_id
                 WHERE e.entity_id=?1 AND e.product_id=?2 AND r.entity_revision_id=?3",
            )
            .bind(entity_id)
            .bind(&baseline.product_id)
            .bind(revision_id)
            .fetch_optional(&mut *tx)
            .await
            .map_err(backend)?;
            if valid.is_none() {
                return Err(ProductPersistenceError::Invalid(format!(
                    "baseline {} cannot include entity {} revision {} outside product {} or with mismatched revision ownership",
                    baseline.baseline_id, entity_id, revision_id, baseline.product_id
                )));
            }
        }
        sqlx::query(
            "INSERT INTO product_baselines_v1
             (baseline_id, product_id, revision_number, parent_baseline_id, accepted_at, metadata)
             VALUES (?1,?2,?3,?4,?5,?6)",
        )
        .bind(&baseline.baseline_id)
        .bind(&baseline.product_id)
        .bind(baseline.revision_number)
        .bind(&baseline.parent_baseline_id)
        .bind(ts_to_str(baseline.accepted_at))
        .bind(baseline.metadata.to_string())
        .execute(&mut *tx)
        .await
        .map_err(backend)?;
        for (entity_id, revision_id) in members {
            sqlx::query(
                "INSERT INTO baseline_entity_membership_v1 (baseline_id, entity_id, entity_revision_id)
                 VALUES (?1,?2,?3)"
            ).bind(&baseline.baseline_id).bind(entity_id).bind(revision_id)
             .execute(&mut *tx).await.map_err(backend)?;
        }
        tx.commit().await.map_err(backend)?;
        Ok(())
    }

    async fn get_baseline(
        &self,
        product_id: &str,
        baseline_id: &str,
    ) -> Result<Option<PersistedBaseline>, ProductPersistenceError> {
        let row = sqlx::query(
            "SELECT baseline_id, product_id, revision_number, parent_baseline_id, accepted_at, metadata
             FROM product_baselines_v1 WHERE product_id=?1 AND baseline_id=?2"
        ).bind(product_id).bind(baseline_id).fetch_optional(&self.pool).await.map_err(backend)?;
        Ok(row.map(|r| PersistedBaseline {
            baseline_id: r.get("baseline_id"),
            product_id: r.get("product_id"),
            revision_number: r.get("revision_number"),
            parent_baseline_id: r.get("parent_baseline_id"),
            accepted_at: str_to_ts(&r.get::<String, _>("accepted_at")),
            metadata: serde_json::from_str(&r.get::<String, _>("metadata")).unwrap_or_default(),
        }))
    }

    async fn create_entity(&self, entity: &PersistedEntity) -> Result<(), ProductPersistenceError> {
        let product_exists: Option<i64> = sqlx::query_scalar(
            "SELECT 1 FROM product_nodes
             WHERE id=?1 AND product_id=?1 AND intent_kind='product'",
        )
        .bind(&entity.product_id)
        .fetch_optional(&self.pool)
        .await
        .map_err(backend)?;
        if product_exists.is_none() {
            return Err(ProductPersistenceError::Invalid(format!(
                "entity {} references unknown product {}",
                entity.entity_id, entity.product_id
            )));
        }
        sqlx::query(
            "INSERT INTO product_entities_v1 (entity_id, product_id, local_id, entity_kind, created_at)
             VALUES (?1,?2,?3,?4,?5)"
        ).bind(&entity.entity_id).bind(&entity.product_id).bind(&entity.local_id)
          .bind(&entity.entity_kind).bind(ts_to_str(entity.created_at))
          .execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }

    async fn append_entity_revision(
        &self,
        revision: &PersistedEntityRevision,
    ) -> Result<(), ProductPersistenceError> {
        sqlx::query(
            "INSERT INTO product_entity_revisions_v1
             (entity_revision_id, entity_id, content_revision, title, description, status, metadata, created_at)
             VALUES (?1,?2,?3,?4,?5,?6,?7,?8)"
        ).bind(&revision.entity_revision_id).bind(&revision.entity_id).bind(revision.content_revision)
          .bind(&revision.title).bind(&revision.description).bind(&revision.status)
          .bind(revision.metadata.to_string()).bind(ts_to_str(revision.created_at))
          .execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }

    async fn list_baseline_entities(
        &self,
        product_id: &str,
        baseline_id: &str,
        limit: u32,
    ) -> Result<Vec<PersistedEntityRevision>, ProductPersistenceError> {
        let rows=sqlx::query(
            "SELECT r.entity_revision_id,r.entity_id,r.content_revision,r.title,r.description,r.status,r.metadata,r.created_at
             FROM baseline_entity_membership_v1 m
             JOIN product_entities_v1 e ON e.entity_id=m.entity_id
             JOIN product_entity_revisions_v1 r ON r.entity_revision_id=m.entity_revision_id
             WHERE m.baseline_id=?1 AND e.product_id=?2 ORDER BY e.local_id LIMIT ?3"
        ).bind(baseline_id).bind(product_id).bind(i64::from(limit.min(1000)))
          .fetch_all(&self.pool).await.map_err(backend)?;
        Ok(rows
            .into_iter()
            .map(|r| PersistedEntityRevision {
                entity_revision_id: r.get("entity_revision_id"),
                entity_id: r.get("entity_id"),
                content_revision: r.get("content_revision"),
                title: r.get("title"),
                description: r.get("description"),
                status: r.get("status"),
                metadata: serde_json::from_str(&r.get::<String, _>("metadata")).unwrap_or_default(),
                created_at: str_to_ts(&r.get::<String, _>("created_at")),
            })
            .collect())
    }

    async fn append_observation(
        &self,
        o: &PersistedObservation,
    ) -> Result<(), ProductPersistenceError> {
        let baseline_product: Option<String> =
            sqlx::query_scalar("SELECT product_id FROM product_baselines_v1 WHERE baseline_id=?1")
                .bind(&o.baseline_id)
                .fetch_optional(&self.pool)
                .await
                .map_err(backend)?;
        match baseline_product {
            Some(product_id) if product_id == o.product_id => {}
            Some(product_id) => {
                return Err(ProductPersistenceError::Invalid(format!(
                    "observation {} claims product {} but baseline {} belongs to {}",
                    o.observation_id, o.product_id, o.baseline_id, product_id
                )));
            }
            None => {
                return Err(ProductPersistenceError::Invalid(format!(
                    "observation {} references missing baseline {}",
                    o.observation_id, o.baseline_id
                )));
            }
        }
        if let Some(subject_entity_id) = &o.subject_entity_id {
            let subject_product: Option<String> =
                sqlx::query_scalar("SELECT product_id FROM product_entities_v1 WHERE entity_id=?1")
                    .bind(subject_entity_id)
                    .fetch_optional(&self.pool)
                    .await
                    .map_err(backend)?;
            if subject_product.as_deref() != Some(o.product_id.as_str()) {
                return Err(ProductPersistenceError::Invalid(format!(
                    "observation {} subject entity {} is missing or outside product {}",
                    o.observation_id, subject_entity_id, o.product_id
                )));
            }
        }
        sqlx::query(
            "INSERT INTO product_observations_v1
             (observation_id,product_id,baseline_id,subject_entity_id,subject_local_id,candidate_ref,configuration,result,verifier_id,verifier_version,recorded_at,raw_evidence_ref,metadata)
             VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13)"
        ).bind(&o.observation_id).bind(&o.product_id).bind(&o.baseline_id).bind(&o.subject_entity_id)
          .bind(&o.subject_local_id).bind(&o.candidate_ref).bind(o.configuration.to_string()).bind(&o.result)
          .bind(&o.verifier_id).bind(&o.verifier_version).bind(ts_to_str(o.recorded_at))
          .bind(&o.raw_evidence_ref).bind(o.metadata.to_string()).execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }

    async fn list_observations(
        &self,
        product_id: &str,
        baseline_id: &str,
        subject_local_id: Option<&str>,
        limit: u32,
    ) -> Result<Vec<PersistedObservation>, ProductPersistenceError> {
        let rows = sqlx::query(
            "SELECT * FROM product_observations_v1
             WHERE product_id=?1 AND baseline_id=?2 AND (?3 IS NULL OR subject_local_id=?3)
             ORDER BY recorded_at, observation_id LIMIT ?4",
        )
        .bind(product_id)
        .bind(baseline_id)
        .bind(subject_local_id)
        .bind(i64::from(limit.min(1000)))
        .fetch_all(&self.pool)
        .await
        .map_err(backend)?;
        Ok(rows
            .into_iter()
            .map(|r| PersistedObservation {
                observation_id: r.get("observation_id"),
                product_id: r.get("product_id"),
                baseline_id: r.get("baseline_id"),
                subject_entity_id: r.get("subject_entity_id"),
                subject_local_id: r.get("subject_local_id"),
                candidate_ref: r.get("candidate_ref"),
                configuration: serde_json::from_str(&r.get::<String, _>("configuration"))
                    .unwrap_or_default(),
                result: r.get("result"),
                verifier_id: r.get("verifier_id"),
                verifier_version: r.get("verifier_version"),
                recorded_at: str_to_ts(&r.get::<String, _>("recorded_at")),
                raw_evidence_ref: r.get("raw_evidence_ref"),
                metadata: serde_json::from_str(&r.get::<String, _>("metadata")).unwrap_or_default(),
            })
            .collect())
    }

    async fn list_reuse_decisions_for_target(
        &self,
        product_id: &str,
        target_baseline_id: &str,
        target_candidate_ref: &str,
        limit: u32,
    ) -> Result<Vec<EvidenceReuseDecision>, ProductPersistenceError> {
        if self
            .get_baseline(product_id, target_baseline_id)
            .await?
            .is_none()
        {
            return Err(ProductPersistenceError::NotFound(
                "baseline not found in product scope".into(),
            ));
        }
        let rows = sqlx::query(include_str!("../product/sql/reuse_for_target.sqlite.sql"))
            .bind(product_id)
            .bind(target_baseline_id)
            .bind(target_candidate_ref)
            .bind(i64::from(limit.min(1000)))
            .fetch_all(&self.pool)
            .await
            .map_err(backend)?;
        Ok(rows
            .into_iter()
            .map(|r| EvidenceReuseDecision {
                reuse_decision_id: r.get("reuse_decision_id"),
                observation_id: r.get("observation_id"),
                target_baseline_id: r.get("target_baseline_id"),
                target_candidate_ref: r.get("target_candidate_ref"),
                criterion_ref: r.get("criterion_ref"),
                applicability_state: r.get("applicability_state"),
                compatibility_certificate_ref: r.get("compatibility_certificate_ref"),
                policy_version: r.get("policy_version"),
                reason: r.get("reason"),
                decided_at: str_to_ts(&r.get::<String, _>("decided_at")),
            })
            .collect())
    }

    async fn append_reuse_decision(
        &self,
        d: &EvidenceReuseDecision,
    ) -> Result<(), ProductPersistenceError> {
        let scopes: Option<(String, String)> = sqlx::query_as(
            "SELECT o.product_id, b.product_id
             FROM product_observations_v1 o
             JOIN product_baselines_v1 b ON b.baseline_id=?2
             WHERE o.observation_id=?1",
        )
        .bind(&d.observation_id)
        .bind(&d.target_baseline_id)
        .fetch_optional(&self.pool)
        .await
        .map_err(backend)?;
        match scopes {
            Some((observation_product, target_product))
                if observation_product == target_product => {}
            Some((observation_product, target_product)) => {
                return Err(ProductPersistenceError::Invalid(format!(
                    "reuse decision {} cannot bind observation {} from product {} to baseline {} from product {}",
                    d.reuse_decision_id, d.observation_id, observation_product,
                    d.target_baseline_id, target_product
                )));
            }
            None => {
                return Err(ProductPersistenceError::Invalid(format!(
                    "reuse decision {} references missing observation {} or target baseline {}",
                    d.reuse_decision_id, d.observation_id, d.target_baseline_id
                )));
            }
        }
        sqlx::query("INSERT INTO evidence_reuse_decisions_v1 (reuse_decision_id,observation_id,target_baseline_id,target_candidate_ref,criterion_ref,applicability_state,compatibility_certificate_ref,policy_version,reason,decided_at) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10)")
            .bind(&d.reuse_decision_id).bind(&d.observation_id).bind(&d.target_baseline_id).bind(&d.target_candidate_ref).bind(&d.criterion_ref).bind(&d.applicability_state).bind(&d.compatibility_certificate_ref).bind(&d.policy_version).bind(&d.reason).bind(ts_to_str(d.decided_at))
            .execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }

    async fn append_invalidation(
        &self,
        e: &InvalidationEvent,
    ) -> Result<(), ProductPersistenceError> {
        self.append_invalidations(std::slice::from_ref(e)).await
    }

    async fn append_invalidations(
        &self,
        events: &[InvalidationEvent],
    ) -> Result<(), ProductPersistenceError> {
        let mut tx = self.pool.begin().await.map_err(backend)?;
        for e in events {
            let inserted = sqlx::query(
                "INSERT OR IGNORE INTO invalidation_events_v1
                 (invalidation_id,trigger_kind,trigger_ref,target_kind,target_ref,prior_state,new_state,reason,occurred_at)
                 VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9)",
            )
            .bind(&e.invalidation_id)
            .bind(&e.trigger_kind)
            .bind(&e.trigger_ref)
            .bind(&e.target_kind)
            .bind(&e.target_ref)
            .bind(&e.prior_state)
            .bind(&e.new_state)
            .bind(&e.reason)
            .bind(ts_to_str(e.occurred_at))
            .execute(&mut *tx)
            .await
            .map_err(backend)?;
            if inserted.rows_affected() == 0 {
                let row = sqlx::query(
                    "SELECT invalidation_id,trigger_kind,trigger_ref,target_kind,target_ref,prior_state,new_state,reason,occurred_at
                     FROM invalidation_events_v1 WHERE invalidation_id=?1",
                )
                .bind(&e.invalidation_id)
                .fetch_one(&mut *tx)
                .await
                .map_err(backend)?;
                let existing = InvalidationEvent {
                    invalidation_id: row.get("invalidation_id"),
                    trigger_kind: row.get("trigger_kind"),
                    trigger_ref: row.get("trigger_ref"),
                    target_kind: row.get("target_kind"),
                    target_ref: row.get("target_ref"),
                    prior_state: row.get("prior_state"),
                    new_state: row.get("new_state"),
                    reason: row.get("reason"),
                    occurred_at: str_to_ts(&row.get::<String, _>("occurred_at")),
                };
                if existing != *e {
                    return Err(ProductPersistenceError::Conflict(format!(
                        "invalidation {} already exists with different immutable content",
                        e.invalidation_id
                    )));
                }
            }
        }
        tx.commit().await.map_err(backend)?;
        Ok(())
    }

    async fn list_invalidations(
        &self,
        kind: &str,
        target: &str,
        limit: u32,
    ) -> Result<Vec<InvalidationEvent>, ProductPersistenceError> {
        let rows=sqlx::query("SELECT invalidation_id,trigger_kind,trigger_ref,target_kind,target_ref,prior_state,new_state,reason,occurred_at FROM invalidation_events_v1 WHERE target_kind=?1 AND target_ref=?2 ORDER BY occurred_at,invalidation_id LIMIT ?3")
            .bind(kind).bind(target).bind(i64::from(limit.min(1000))).fetch_all(&self.pool).await.map_err(backend)?;
        Ok(rows
            .into_iter()
            .map(|r| InvalidationEvent {
                invalidation_id: r.get("invalidation_id"),
                trigger_kind: r.get("trigger_kind"),
                trigger_ref: r.get("trigger_ref"),
                target_kind: r.get("target_kind"),
                target_ref: r.get("target_ref"),
                prior_state: r.get("prior_state"),
                new_state: r.get("new_state"),
                reason: r.get("reason"),
                occurred_at: str_to_ts(&r.get::<String, _>("occurred_at")),
            })
            .collect())
    }
}
