use chrono::{DateTime, Utc};
use sqlx::{PgPool, Row};

use crate::store::{AgilePlusIngestKey, AgilePlusIngestRecord, StoreError, StoreResult};

pub(super) async fn get_agileplus_ingest_key(
    pool: &PgPool,
    idempotency_key: String,
) -> StoreResult<Option<AgilePlusIngestKey>> {
    let row = sqlx::query(
        "SELECT idempotency_key, body_fingerprint, ingestion_id \
         FROM agileplus_ingest_keys WHERE idempotency_key = $1",
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
}

pub(super) async fn record_agileplus_ingest(
    pool: &PgPool,
    record: AgilePlusIngestRecord,
    now: DateTime<Utc>,
) -> StoreResult<()> {
    let mut tx = pool.begin().await.map_err(StoreError::from)?;

    // A duplicate key must fail and roll back the revision advance.
    sqlx::query(
        "INSERT INTO agileplus_ingest_keys \
         (idempotency_key, body_fingerprint, ingestion_id, ingested_at) \
         VALUES ($1, $2, $3, $4)",
    )
    .bind(&record.idempotency_key)
    .bind(&record.body_fingerprint)
    .bind(&record.ingestion_id)
    .bind(now)
    .execute(&mut *tx)
    .await
    .map_err(StoreError::from)?;

    for revision in &record.revisions {
        sqlx::query(
            "INSERT INTO agileplus_revisions \
             (agileplus_id, entity_type, revision, node_id, updated_at) \
             VALUES ($1, $2, $3, $4, $5) \
             ON CONFLICT (agileplus_id) DO UPDATE SET \
                 entity_type = EXCLUDED.entity_type, \
                 revision = EXCLUDED.revision, \
                 node_id = EXCLUDED.node_id, \
                 updated_at = EXCLUDED.updated_at \
             WHERE EXCLUDED.revision > agileplus_revisions.revision",
        )
        .bind(&revision.agileplus_id)
        .bind(&revision.entity_type)
        .bind(revision.revision)
        .bind(&revision.node_id)
        .bind(now)
        .execute(&mut *tx)
        .await
        .map_err(StoreError::from)?;
    }

    tx.commit().await.map_err(StoreError::from)
}

pub(super) async fn get_agileplus_revision(
    pool: &PgPool,
    agileplus_id: String,
) -> StoreResult<Option<i64>> {
    let row = sqlx::query("SELECT revision FROM agileplus_revisions WHERE agileplus_id = $1")
        .bind(&agileplus_id)
        .fetch_optional(pool)
        .await
        .map_err(StoreError::from)?;

    Ok(row.map(|row| row.get::<i64, _>("revision")))
}
