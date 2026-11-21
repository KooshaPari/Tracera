use sqlx::{Row, SqlitePool};

use crate::store::{AgilePlusIngestKey, BoxFuture, StoreError, StoreResult};

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
