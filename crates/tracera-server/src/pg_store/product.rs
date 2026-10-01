//! Postgres implementation of the narrow product persistence port.

use sqlx::Row;

use crate::product::persistence::{
    EvidenceReuseDecision, InvalidationEvent, PersistedBaseline, PersistedEntity,
    PersistedEntityRevision, PersistedObservation, PersistedProduct, ProductPersistence,
    ProductPersistenceError,
};

use super::PgStore;

fn backend(error: impl std::fmt::Display) -> ProductPersistenceError {
    ProductPersistenceError::Backend(error.to_string())
}

impl ProductPersistence for PgStore {
    async fn create_product(&self, p: &PersistedProduct) -> Result<(), ProductPersistenceError> {
        sqlx::query("INSERT INTO product_nodes (id,product_id,intent_kind,title,description,status,baseline_revision,created_at,updated_at) VALUES ($1,$1,'product',$2,'','accepted',0,$3,$3) ON CONFLICT (id) DO NOTHING")
            .bind(&p.product_id).bind(&p.display_name).bind(p.created_at).execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }
    async fn get_product(
        &self,
        id: &str,
    ) -> Result<Option<PersistedProduct>, ProductPersistenceError> {
        let r=sqlx::query("SELECT product_id,title,created_at FROM product_nodes WHERE id=$1 AND product_id=$1 AND intent_kind='product'")
            .bind(id).fetch_optional(&self.pool).await.map_err(backend)?;
        Ok(r.map(|r| PersistedProduct {
            product_id: r.get("product_id"),
            display_name: r.get("title"),
            created_at: r.get("created_at"),
        }))
    }
    async fn accept_baseline(
        &self,
        b: &PersistedBaseline,
        members: &[(String, String)],
    ) -> Result<(), ProductPersistenceError> {
        let mut tx = self.pool.begin().await.map_err(backend)?;
        for (entity_id, revision_id) in members {
            let valid: Option<i64> = sqlx::query_scalar(
                "SELECT 1
                 FROM product_entities_v1 e
                 JOIN product_entity_revisions_v1 r ON r.entity_id = e.entity_id
                 WHERE e.entity_id=$1 AND e.product_id=$2 AND r.entity_revision_id=$3"
            )
            .bind(entity_id)
            .bind(&b.product_id)
            .bind(revision_id)
            .fetch_optional(&mut *tx)
            .await
            .map_err(backend)?;
            if valid.is_none() {
                return Err(ProductPersistenceError::Invalid(format!(
                    "baseline {} cannot include entity {} revision {} outside product {} or with mismatched revision ownership",
                    b.baseline_id, entity_id, revision_id, b.product_id
                )));
            }
        }
        sqlx::query("INSERT INTO product_baselines_v1 (baseline_id,product_id,revision_number,parent_baseline_id,accepted_at,metadata) VALUES ($1,$2,$3,$4,$5,$6)")
            .bind(&b.baseline_id).bind(&b.product_id).bind(b.revision_number).bind(&b.parent_baseline_id).bind(b.accepted_at).bind(&b.metadata)
            .execute(&mut *tx).await.map_err(backend)?;
        for (entity_id, revision_id) in members {
            sqlx::query("INSERT INTO baseline_entity_membership_v1 (baseline_id,entity_id,entity_revision_id) VALUES ($1,$2,$3)")
                .bind(&b.baseline_id).bind(entity_id).bind(revision_id).execute(&mut *tx).await.map_err(backend)?;
        }
        tx.commit().await.map_err(backend)?;
        Ok(())
    }
    async fn get_baseline(
        &self,
        pid: &str,
        bid: &str,
    ) -> Result<Option<PersistedBaseline>, ProductPersistenceError> {
        let r=sqlx::query("SELECT baseline_id,product_id,revision_number,parent_baseline_id,accepted_at,metadata FROM product_baselines_v1 WHERE product_id=$1 AND baseline_id=$2")
            .bind(pid).bind(bid).fetch_optional(&self.pool).await.map_err(backend)?;
        Ok(r.map(|r| PersistedBaseline {
            baseline_id: r.get("baseline_id"),
            product_id: r.get("product_id"),
            revision_number: r.get("revision_number"),
            parent_baseline_id: r.get("parent_baseline_id"),
            accepted_at: r.get("accepted_at"),
            metadata: r.get("metadata"),
        }))
    }
    async fn create_entity(&self, e: &PersistedEntity) -> Result<(), ProductPersistenceError> {
        sqlx::query("INSERT INTO product_entities_v1 (entity_id,product_id,local_id,entity_kind,created_at) VALUES ($1,$2,$3,$4,$5)")
            .bind(&e.entity_id).bind(&e.product_id).bind(&e.local_id).bind(&e.entity_kind).bind(e.created_at).execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }
    async fn append_entity_revision(
        &self,
        r: &PersistedEntityRevision,
    ) -> Result<(), ProductPersistenceError> {
        sqlx::query("INSERT INTO product_entity_revisions_v1 (entity_revision_id,entity_id,content_revision,title,description,status,metadata,created_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)")
            .bind(&r.entity_revision_id).bind(&r.entity_id).bind(r.content_revision).bind(&r.title).bind(&r.description).bind(&r.status).bind(&r.metadata).bind(r.created_at)
            .execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }
    async fn list_baseline_entities(
        &self,
        pid: &str,
        bid: &str,
        limit: u32,
    ) -> Result<Vec<PersistedEntityRevision>, ProductPersistenceError> {
        let rows=sqlx::query("SELECT r.entity_revision_id,r.entity_id,r.content_revision,r.title,r.description,r.status,r.metadata,r.created_at FROM baseline_entity_membership_v1 m JOIN product_entities_v1 e ON e.entity_id=m.entity_id JOIN product_entity_revisions_v1 r ON r.entity_revision_id=m.entity_revision_id WHERE m.baseline_id=$1 AND e.product_id=$2 ORDER BY e.local_id LIMIT $3")
            .bind(bid).bind(pid).bind(i64::from(limit.min(1000))).fetch_all(&self.pool).await.map_err(backend)?;
        Ok(rows
            .into_iter()
            .map(|r| PersistedEntityRevision {
                entity_revision_id: r.get("entity_revision_id"),
                entity_id: r.get("entity_id"),
                content_revision: r.get("content_revision"),
                title: r.get("title"),
                description: r.get("description"),
                status: r.get("status"),
                metadata: r.get("metadata"),
                created_at: r.get("created_at"),
            })
            .collect())
    }
    async fn append_observation(
        &self,
        o: &PersistedObservation,
    ) -> Result<(), ProductPersistenceError> {
        sqlx::query("INSERT INTO product_observations_v1 (observation_id,product_id,baseline_id,subject_entity_id,subject_local_id,candidate_ref,configuration,result,verifier_id,verifier_version,recorded_at,raw_evidence_ref,metadata) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)")
            .bind(&o.observation_id).bind(&o.product_id).bind(&o.baseline_id).bind(&o.subject_entity_id).bind(&o.subject_local_id).bind(&o.candidate_ref).bind(&o.configuration).bind(&o.result).bind(&o.verifier_id).bind(&o.verifier_version).bind(o.recorded_at).bind(&o.raw_evidence_ref).bind(&o.metadata)
            .execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }
    async fn list_observations(
        &self,
        pid: &str,
        bid: &str,
        subject: Option<&str>,
        limit: u32,
    ) -> Result<Vec<PersistedObservation>, ProductPersistenceError> {
        let rows=sqlx::query("SELECT * FROM product_observations_v1 WHERE product_id=$1 AND baseline_id=$2 AND ($3::text IS NULL OR subject_local_id=$3) ORDER BY recorded_at,observation_id LIMIT $4")
            .bind(pid).bind(bid).bind(subject).bind(i64::from(limit.min(1000))).fetch_all(&self.pool).await.map_err(backend)?;
        Ok(rows
            .into_iter()
            .map(|r| PersistedObservation {
                observation_id: r.get("observation_id"),
                product_id: r.get("product_id"),
                baseline_id: r.get("baseline_id"),
                subject_entity_id: r.get("subject_entity_id"),
                subject_local_id: r.get("subject_local_id"),
                candidate_ref: r.get("candidate_ref"),
                configuration: r.get("configuration"),
                result: r.get("result"),
                verifier_id: r.get("verifier_id"),
                verifier_version: r.get("verifier_version"),
                recorded_at: r.get("recorded_at"),
                raw_evidence_ref: r.get("raw_evidence_ref"),
                metadata: r.get("metadata"),
            })
            .collect())
    }
    async fn append_reuse_decision(
        &self,
        d: &EvidenceReuseDecision,
    ) -> Result<(), ProductPersistenceError> {
        sqlx::query("INSERT INTO evidence_reuse_decisions_v1 (reuse_decision_id,observation_id,target_baseline_id,target_candidate_ref,criterion_ref,applicability_state,compatibility_certificate_ref,policy_version,reason,decided_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)")
            .bind(&d.reuse_decision_id).bind(&d.observation_id).bind(&d.target_baseline_id).bind(&d.target_candidate_ref).bind(&d.criterion_ref).bind(&d.applicability_state).bind(&d.compatibility_certificate_ref).bind(&d.policy_version).bind(&d.reason).bind(d.decided_at)
            .execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }
    async fn append_invalidation(
        &self,
        e: &InvalidationEvent,
    ) -> Result<(), ProductPersistenceError> {
        sqlx::query("INSERT INTO invalidation_events_v1 (invalidation_id,trigger_kind,trigger_ref,target_kind,target_ref,prior_state,new_state,reason,occurred_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)")
            .bind(&e.invalidation_id).bind(&e.trigger_kind).bind(&e.trigger_ref).bind(&e.target_kind).bind(&e.target_ref).bind(&e.prior_state).bind(&e.new_state).bind(&e.reason).bind(e.occurred_at)
            .execute(&self.pool).await.map_err(backend)?;
        Ok(())
    }
    async fn list_invalidations(
        &self,
        kind: &str,
        target: &str,
        limit: u32,
    ) -> Result<Vec<InvalidationEvent>, ProductPersistenceError> {
        let rows=sqlx::query("SELECT invalidation_id,trigger_kind,trigger_ref,target_kind,target_ref,prior_state,new_state,reason,occurred_at FROM invalidation_events_v1 WHERE target_kind=$1 AND target_ref=$2 ORDER BY occurred_at,invalidation_id LIMIT $3")
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
                occurred_at: r.get("occurred_at"),
            })
            .collect())
    }
}
