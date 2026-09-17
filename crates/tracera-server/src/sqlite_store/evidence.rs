use chrono::{DateTime, Utc};
use serde_json::Value;
use sqlx::{Row, SqlitePool};

use crate::store::{BoxFuture, EvidenceItem, StoreError, StoreResult};

use super::{str_to_ts, ts_to_str};

pub(super) fn list_evidence(pool: &SqlitePool) -> BoxFuture<'_, StoreResult<Vec<EvidenceItem>>> {
    Box::pin(async move {
        let rows = sqlx::query(
            "SELECT id, artifact_id, kind, url, metadata, created_at, updated_at
             FROM evidence ORDER BY created_at ASC",
        )
        .fetch_all(pool)
        .await
        .map_err(StoreError::from)?;

        let items = rows
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
                    created_at: str_to_ts(
                        &r.try_get::<String, _>("created_at").unwrap_or_default(),
                    ),
                    updated_at: str_to_ts(
                        &r.try_get::<String, _>("updated_at").unwrap_or_default(),
                    ),
                }
            })
            .collect();

        Ok(items)
    })
}

pub(super) fn create_evidence(
    pool: &SqlitePool,
    id: String,
    artifact_id: String,
    kind: String,
    url: String,
    metadata: Value,
    now: DateTime<Utc>,
) -> BoxFuture<'_, StoreResult<EvidenceItem>> {
    Box::pin(async move {
        let meta_str = serde_json::to_string(&metadata).unwrap_or_else(|_| "{}".to_string());
        let now_str = ts_to_str(now);

        sqlx::query(
            "INSERT INTO evidence (id, artifact_id, kind, url, metadata, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
        )
        .bind(&id)
        .bind(&artifact_id)
        .bind(&kind)
        .bind(&url)
        .bind(&meta_str)
        .bind(&now_str)
        .bind(&now_str)
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
    })
}

pub(super) fn count_evidence(pool: &SqlitePool) -> BoxFuture<'_, StoreResult<i64>> {
    Box::pin(async move {
        let row = sqlx::query("SELECT COUNT(*) as cnt FROM evidence")
            .fetch_one(pool)
            .await
            .map_err(StoreError::from)?;
        let count: i64 = row.try_get("cnt").unwrap_or(0);
        Ok(count)
    })
}
