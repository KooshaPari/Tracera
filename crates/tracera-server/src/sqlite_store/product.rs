//! SQLite implementation of the narrow product persistence port.

use sqlx::Row;

use crate::product::persistence::{
    PersistedBaseline, PersistedEntity, PersistedEntityRevision, PersistedObservation,
    PersistedProduct, ProductPersistence, ProductPersistenceError, EvidenceReuseDecision, InvalidationEvent,
};

use super::{str_to_ts, ts_to_str, SqliteStore};

fn backend(error: impl std::fmt::Display) -> ProductPersistenceError {
    ProductPersistenceError::Backend(error.to_string())
}

impl ProductPersistence for SqliteStore {
    async fn create_product(&self, product: &PersistedProduct) -> Result<(), ProductPersistenceError> {
        // v1 deliberately reuses product_baselines/entities as product ownership
        // storage until a dedicated product registry table is justified.
        // A product with no baseline/entity has no persisted row yet.
        sqlx::query(
            "INSERT OR IGNORE INTO product_nodes
             (id, product_id, intent_kind, title, description, status, baseline_revision, metadata, created_at, updated_at)
             VALUES (?1, ?1, 'product', ?2, '', 'accepted', 0, '{}', ?3, ?3)"
        )
        .bind(&product.product_id)
        .bind(&product.display_name)
        .bind(ts_to_str(product.created_at))
        .execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }

    async fn get_product(&self, product_id: &str) -> Result<Option<PersistedProduct>, ProductPersistenceError> {
        let row = sqlx::query(
            "SELECT product_id, title, created_at FROM product_nodes
             WHERE id=?1 AND product_id=?1 AND intent_kind='product'"
        ).bind(product_id).fetch_optional(&self.pool).await.map_err(backend)?;
        Ok(row.map(|r| PersistedProduct {
            product_id: r.get("product_id"),
            display_name: r.get("title"),
            created_at: str_to_ts(&r.get::<String,_>("created_at")),
        }))
    }

    async fn accept_baseline(&self, baseline: &PersistedBaseline, members: &[(String, String)]) -> Result<(), ProductPersistenceError> {
        let mut tx = self.pool.begin().await.map_err(backend)?;
        sqlx::query(
            "INSERT INTO product_baselines_v1
             (baseline_id, product_id, revision_number, parent_baseline_id, accepted_at, metadata)
             VALUES (?1,?2,?3,?4,?5,?6)"
        )
        .bind(&baseline.baseline_id).bind(&baseline.product_id).bind(baseline.revision_number)
        .bind(&baseline.parent_baseline_id).bind(ts_to_str(baseline.accepted_at))
        .bind(baseline.metadata.to_string()).execute(&mut *tx).await.map_err(backend)?;

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

    async fn get_baseline(&self, product_id: &str, baseline_id: &str) -> Result<Option<PersistedBaseline>, ProductPersistenceError> {
        let row = sqlx::query(
            "SELECT baseline_id, product_id, revision_number, parent_baseline_id, accepted_at, metadata
             FROM product_baselines_v1 WHERE product_id=?1 AND baseline_id=?2"
        ).bind(product_id).bind(baseline_id).fetch_optional(&self.pool).await.map_err(backend)?;
        Ok(row.map(|r| PersistedBaseline {
            baseline_id:r.get("baseline_id"), product_id:r.get("product_id"),
            revision_number:r.get("revision_number"), parent_baseline_id:r.get("parent_baseline_id"),
            accepted_at:str_to_ts(&r.get::<String,_>("accepted_at")),
            metadata:serde_json::from_str(&r.get::<String,_>("metadata")).unwrap_or_default(),
        }))
    }

    async fn create_entity(&self, entity: &PersistedEntity) -> Result<(), ProductPersistenceError> {
        sqlx::query(
            "INSERT INTO product_entities_v1 (entity_id, product_id, local_id, entity_kind, created_at)
             VALUES (?1,?2,?3,?4,?5)"
        ).bind(&entity.entity_id).bind(&entity.product_id).bind(&entity.local_id)
          .bind(&entity.entity_kind).bind(ts_to_str(entity.created_at))
          .execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }

    async fn append_entity_revision(&self, revision: &PersistedEntityRevision) -> Result<(), ProductPersistenceError> {
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

    async fn list_baseline_entities(&self, product_id: &str, baseline_id: &str, limit: u32) -> Result<Vec<PersistedEntityRevision>, ProductPersistenceError> {
        let rows=sqlx::query(
            "SELECT r.entity_revision_id,r.entity_id,r.content_revision,r.title,r.description,r.status,r.metadata,r.created_at
             FROM baseline_entity_membership_v1 m
             JOIN product_entities_v1 e ON e.entity_id=m.entity_id
             JOIN product_entity_revisions_v1 r ON r.entity_revision_id=m.entity_revision_id
             WHERE m.baseline_id=?1 AND e.product_id=?2 ORDER BY e.local_id LIMIT ?3"
        ).bind(baseline_id).bind(product_id).bind(i64::from(limit.min(1000)))
          .fetch_all(&self.pool).await.map_err(backend)?;
        Ok(rows.into_iter().map(|r| PersistedEntityRevision {
            entity_revision_id:r.get("entity_revision_id"),entity_id:r.get("entity_id"),
            content_revision:r.get("content_revision"),title:r.get("title"),description:r.get("description"),
            status:r.get("status"),metadata:serde_json::from_str(&r.get::<String,_>("metadata")).unwrap_or_default(),
            created_at:str_to_ts(&r.get::<String,_>("created_at")),
        }).collect())
    }

    async fn append_observation(&self, o: &PersistedObservation) -> Result<(), ProductPersistenceError> {
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

    async fn list_observations(&self, product_id: &str, baseline_id: &str, subject_local_id: Option<&str>, limit: u32) -> Result<Vec<PersistedObservation>, ProductPersistenceError> {
        let rows=sqlx::query(
            "SELECT * FROM product_observations_v1
             WHERE product_id=?1 AND baseline_id=?2 AND (?3 IS NULL OR subject_local_id=?3)
             ORDER BY recorded_at, observation_id LIMIT ?4"
        ).bind(product_id).bind(baseline_id).bind(subject_local_id).bind(i64::from(limit.min(1000)))
          .fetch_all(&self.pool).await.map_err(backend)?;
        Ok(rows.into_iter().map(|r| PersistedObservation {
            observation_id:r.get("observation_id"),product_id:r.get("product_id"),baseline_id:r.get("baseline_id"),
            subject_entity_id:r.get("subject_entity_id"),subject_local_id:r.get("subject_local_id"),
            candidate_ref:r.get("candidate_ref"),configuration:serde_json::from_str(&r.get::<String,_>("configuration")).unwrap_or_default(),
            result:r.get("result"),verifier_id:r.get("verifier_id"),verifier_version:r.get("verifier_version"),
            recorded_at:str_to_ts(&r.get::<String,_>("recorded_at")),raw_evidence_ref:r.get("raw_evidence_ref"),
            metadata:serde_json::from_str(&r.get::<String,_>("metadata")).unwrap_or_default(),
        }).collect())
    }
    async fn append_reuse_decision(&self,d:&EvidenceReuseDecision)->Result<(),ProductPersistenceError>{
        sqlx::query("INSERT INTO evidence_reuse_decisions_v1 (reuse_decision_id,observation_id,target_baseline_id,target_candidate_ref,criterion_ref,applicability_state,compatibility_certificate_ref,policy_version,reason,decided_at) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10)")
            .bind(&d.reuse_decision_id).bind(&d.observation_id).bind(&d.target_baseline_id).bind(&d.target_candidate_ref).bind(&d.criterion_ref).bind(&d.applicability_state).bind(&d.compatibility_certificate_ref).bind(&d.policy_version).bind(&d.reason).bind(ts_to_str(d.decided_at))
            .execute(&self.pool).await.map_err(backend)?;Ok(())
    }

    async fn append_invalidation(&self,e:&InvalidationEvent)->Result<(),ProductPersistenceError>{
        sqlx::query("INSERT INTO invalidation_events_v1 (invalidation_id,trigger_kind,trigger_ref,target_kind,target_ref,prior_state,new_state,reason,occurred_at) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9)")
            .bind(&e.invalidation_id).bind(&e.trigger_kind).bind(&e.trigger_ref).bind(&e.target_kind).bind(&e.target_ref).bind(&e.prior_state).bind(&e.new_state).bind(&e.reason).bind(ts_to_str(e.occurred_at))
            .execute(&self.pool).await.map_err(backend)?;Ok(())
    }

    async fn list_invalidations(&self,kind:&str,target:&str,limit:u32)->Result<Vec<InvalidationEvent>,ProductPersistenceError>{
        let rows=sqlx::query("SELECT invalidation_id,trigger_kind,trigger_ref,target_kind,target_ref,prior_state,new_state,reason,occurred_at FROM invalidation_events_v1 WHERE target_kind=?1 AND target_ref=?2 ORDER BY occurred_at,invalidation_id LIMIT ?3")
            .bind(kind).bind(target).bind(i64::from(limit.min(1000))).fetch_all(&self.pool).await.map_err(backend)?;
        Ok(rows.into_iter().map(|r|InvalidationEvent{invalidation_id:r.get("invalidation_id"),trigger_kind:r.get("trigger_kind"),trigger_ref:r.get("trigger_ref"),target_kind:r.get("target_kind"),target_ref:r.get("target_ref"),prior_state:r.get("prior_state"),new_state:r.get("new_state"),reason:r.get("reason"),occurred_at:str_to_ts(&r.get::<String,_>("occurred_at"))}).collect())
    }

}
