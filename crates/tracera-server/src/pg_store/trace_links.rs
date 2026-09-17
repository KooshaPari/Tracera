use chrono::{DateTime, Utc};
use sqlx::{PgPool, Row};

use crate::store::{StoreError, StoreResult, TraceLink};

pub(super) fn pg_row_to_trace_link(r: sqlx::postgres::PgRow) -> TraceLink {
    TraceLink {
        id: r.try_get("id").unwrap_or_default(),
        source_id: r.try_get("source_id").unwrap_or_default(),
        target_id: r.try_get("target_id").unwrap_or_default(),
        relationship: r.try_get("relationship").unwrap_or_default(),
        confidence: r.try_get("confidence").unwrap_or_default(),
        source: r.try_get("source").unwrap_or_default(),
        created_at: r.try_get("created_at").unwrap_or_else(|_| Utc::now()),
        updated_at: r.try_get("updated_at").unwrap_or_else(|_| Utc::now()),
    }
}

pub(super) async fn create_trace_link(
    pool: &PgPool,
    id: String,
    source_id: String,
    target_id: String,
    relationship: String,
    confidence: f64,
    source: String,
    now: DateTime<Utc>,
) -> StoreResult<TraceLink> {
    sqlx::query(
        "INSERT INTO trace_links \
         (id, source_id, target_id, relationship, confidence, source, created_at, updated_at) \
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
    )
    .bind(&id)
    .bind(&source_id)
    .bind(&target_id)
    .bind(&relationship)
    .bind(confidence)
    .bind(&source)
    .bind(now)
    .bind(now)
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
}

pub(super) async fn list_trace_links_for_artifact(
    pool: &PgPool,
    artifact_id: String,
) -> StoreResult<Vec<TraceLink>> {
    let rows = sqlx::query(
        "SELECT id, source_id, target_id, relationship, confidence, source, created_at, updated_at \
         FROM trace_links \
         WHERE source_id = $1 OR target_id = $1 \
         ORDER BY created_at ASC, id ASC",
    )
    .bind(&artifact_id)
    .fetch_all(pool)
    .await
    .map_err(StoreError::from)?;

    Ok(rows.into_iter().map(pg_row_to_trace_link).collect())
}
