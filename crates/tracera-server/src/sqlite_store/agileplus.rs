use chrono::{DateTime, Utc};
use sqlx::{Row, SqlitePool};

use crate::store::{AgilePlusIngestKey, AgilePlusIngestRecord, BoxFuture, StoreError, StoreResult};

use super::ts_to_str;

pub(super) fn get_agileplus_ingest_key(
    pool: &SqlitePool,
    idempotency_key: String,
) -> BoxFuture<'_, StoreResult<Option<AgilePlusIngestKey>>> {
    Box::pin(async move {
        let row = sqlx::query(
            "SELECT idempotency_key, body_fingerprint, ingestion_id \
             FROM agileplus_ingest_keys WHERE idempotency_key = ?1",
        )
        .bind(&idempotency_key)
        .fetch_optional(pool)
        .await
        .map_err(StoreError::from)?;

        Ok(row.map(|row| AgilePlusIngestKey {
            idempotency_key: row.get("idempotency_key"),
            body_fingerprint: row.get("body_fingerprint"),
            ingestion_id: row.get("ingestion_id"),
        }))
    })
}

pub(super) fn record_agileplus_ingest(
    pool: &SqlitePool,
    record: AgilePlusIngestRecord,
    now: DateTime<Utc>,
) -> BoxFuture<'_, StoreResult<()>> {
    Box::pin(async move {
        let now_str = ts_to_str(now);
        let mut tx = pool.begin().await.map_err(StoreError::from)?;

        // A duplicate key must fail: the PRIMARY KEY makes the whole
        // transaction roll back, including any revision advancement.
        sqlx::query(
            "INSERT INTO agileplus_ingest_keys \
             (idempotency_key, body_fingerprint, ingestion_id, ingested_at) \
             VALUES (?1, ?2, ?3, ?4)",
        )
        .bind(&record.idempotency_key)
        .bind(&record.body_fingerprint)
        .bind(&record.ingestion_id)
        .bind(&now_str)
        .execute(&mut *tx)
        .await
        .map_err(StoreError::from)?;

        for revision in &record.revisions {
            sqlx::query(
                "INSERT INTO agileplus_revisions \
                 (agileplus_id, entity_type, revision, node_id, updated_at) \
                 VALUES (?1, ?2, ?3, ?4, ?5) \
                 ON CONFLICT(agileplus_id) DO UPDATE SET \
                     entity_type = excluded.entity_type, \
                     revision = excluded.revision, \
                     node_id = excluded.node_id, \
                     updated_at = excluded.updated_at \
                 WHERE excluded.revision > agileplus_revisions.revision",
            )
            .bind(&revision.agileplus_id)
            .bind(&revision.entity_type)
            .bind(revision.revision)
            .bind(&revision.node_id)
            .bind(&now_str)
            .execute(&mut *tx)
            .await
            .map_err(StoreError::from)?;
        }

        tx.commit().await.map_err(StoreError::from)
    })
}

pub(super) fn get_agileplus_revision(
    pool: &SqlitePool,
    agileplus_id: String,
) -> BoxFuture<'_, StoreResult<Option<i64>>> {
    Box::pin(async move {
        let row = sqlx::query("SELECT revision FROM agileplus_revisions WHERE agileplus_id = ?1")
            .bind(&agileplus_id)
            .fetch_optional(pool)
            .await
            .map_err(StoreError::from)?;

        Ok(row.map(|row| row.get::<i64, _>("revision")))
    })
}
