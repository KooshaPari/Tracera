use chrono::{DateTime, Utc};
use serde_json::Value;
use sqlx::{PgPool, Row};

use crate::store::{EvidenceItem, StoreError, StoreResult};

pub(super) async fn list_evidence(pool: &PgPool) -> StoreResult<Vec<EvidenceItem>> {
    let rows = sqlx::query(
        "SELECT id, artifact_id, kind, url, metadata::text, \
         created_at, updated_at \
         FROM evidence ORDER BY created_at ASC",
    )
    .fetch_all(pool)
    .await
    .map_err(StoreError::from)?;

    Ok(rows
        .into_iter()
        .map(|r| {
            let meta_str: String = r.try_get("metadata").unwrap_or_default();
            let metadata: Value = serde_json::from_str(&meta_str)
                .unwrap_or(Value::Object(Default::default()));
            EvidenceItem {
                id: r.try_get("id").unwrap_or_default(),
                artifact_id: r.try_get("artifact_id").unwrap_or_default(),
                kind: r.try_get("kind").unwrap_or_default(),
                url: r.try_get("url").unwrap_or_default(),
                metadata,
                created_at: r.try_get("created_at").unwrap_or_else(|_| Utc::now()),
                updated_at: r.try_get("updated_at").unwrap_or_else(|_| Utc::now()),
            }
        })
        .collect())
}

pub(super) async fn create_evidence(
    pool: &PgPool,
    id: String,
    artifact_id: String,
    kind: String,
    url: String,
    metadata: Value,
    now: DateTime<Utc>,
) -> StoreResult<EvidenceItem> {
    let meta_str = serde_json::to_string(&metadata).unwrap_or_else(|_| "{}".to_string());
    sqlx::query(
        "INSERT INTO evidence \
         (id, artifact_id, kind, url, metadata, created_at, updated_at) \
         VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7)",
    )
    .bind(&id)
    .bind(&artifact_id)
    .bind(&kind)
    .bind(&url)
    .bind(&meta_str)
    .bind(now)
    .bind(now)
    .execute(pool)
    .await
    .map_err(StoreError::from)?;

    Ok(EvidenceItem {
        id,
        artifact_id,
        kind,
        url,
        metadata,
        created_at: now,
        updated_at: now,
    })
}

pub(super) async fn count_evidence(pool: &PgPool) -> StoreResult<i64> {
    let row = sqlx::query("SELECT COUNT(*) AS cnt FROM evidence")
        .fetch_one(pool)
        .await
        .map_err(StoreError::from)?;
    let count: i64 = row.try_get("cnt").unwrap_or(0);
    Ok(count)
}
