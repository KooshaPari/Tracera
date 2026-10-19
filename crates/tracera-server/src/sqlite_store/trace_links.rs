use chrono::{DateTime, Utc};
use sqlx::{Row, SqlitePool};

use crate::store::{BoxFuture, StoreError, StoreResult, TraceLink};

use super::str_to_ts;

pub(super) fn row_to_trace_link(r: sqlx::sqlite::SqliteRow) -> TraceLink {
    TraceLink {
        id: r.try_get("id").unwrap_or_default(),
        source_id: r.try_get("source_id").unwrap_or_default(),
        target_id: r.try_get("target_id").unwrap_or_default(),
        relationship: r.try_get("relationship").unwrap_or_default(),
        confidence: r.try_get("confidence").unwrap_or_default(),
        source: r.try_get("source").unwrap_or_default(),
        created_at: str_to_ts(&r.try_get::<String, _>("created_at").unwrap_or_default()),
        updated_at: str_to_ts(&r.try_get::<String, _>("updated_at").unwrap_or_default()),
    }
}

#[allow(clippy::too_many_arguments)]
pub(super) fn create_trace_link(
    pool: &SqlitePool,
    id: String,
    source_id: String,
    target_id: String,
    relationship: String,
    confidence: f64,
    source: String,
    now: DateTime<Utc>,
) -> BoxFuture<'_, StoreResult<TraceLink>> {
    Box::pin(async move {
        let now_str = super::ts_to_str(now);
        sqlx::query(
            "INSERT INTO trace_links \
             (id, source_id, target_id, relationship, confidence, source, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
        )
        .bind(&id)
        .bind(&source_id)
        .bind(&target_id)
        .bind(&relationship)
        .bind(confidence)
        .bind(&source)
        .bind(&now_str)
        .bind(&now_str)
        .execute(pool)
        .await
        .map_err(StoreError::from)?;

        Ok(TraceLink {
            id,
            source_id,
            target_id,
            relationship,
            confidence,
            source,
            created_at: now,
            updated_at: now,
        })
    })
}

pub(super) fn list_trace_links_for_artifact(
    pool: &SqlitePool,
    artifact_id: String,
) -> BoxFuture<'_, StoreResult<Vec<TraceLink>>> {
    Box::pin(async move {
        let rows = sqlx::query(
            "SELECT id, source_id, target_id, relationship, confidence, source, created_at, updated_at \
             FROM trace_links \
             WHERE source_id = ?1 OR target_id = ?1 \
             ORDER BY created_at ASC, id ASC",
        )
        .bind(&artifact_id)
        .fetch_all(pool)
        .await
        .map_err(StoreError::from)?;

        Ok(rows.into_iter().map(row_to_trace_link).collect())
    })
}
