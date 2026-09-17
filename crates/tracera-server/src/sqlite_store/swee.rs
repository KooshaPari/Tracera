use chrono::{DateTime, Utc};
use serde_json::Value;
use sqlx::{Row, SqlitePool};

use crate::store::{BoxFuture, StoreError, StoreResult};

use super::ts_to_str;

pub(super) fn create_swee_node(
    pool: &SqlitePool,
    node_type: String,
    label: String,
    metadata: Value,
    now: DateTime<Utc>,
) -> BoxFuture<'_, StoreResult<String>> {
    Box::pin(async move {
        let meta_str = serde_json::to_string(&metadata).unwrap_or_else(|_| "{}".to_string());
        let now_str = ts_to_str(now);

        let result = sqlx::query(
            "INSERT INTO swee_nodes (type, name, metadata, created_at, updated_at) \
             VALUES (?1, ?2, ?3, ?4, ?5)",
        )
        .bind(&node_type)
        .bind(&label)
        .bind(&meta_str)
        .bind(&now_str)
        .bind(&now_str)
        .execute(pool)
        .await
        .map_err(StoreError::from)?;

        Ok(result.last_insert_rowid().to_string())
    })
}

#[allow(clippy::too_many_arguments)]
pub(super) fn create_swee_edge(
    pool: &SqlitePool,
    edge_type: String,
    source_id: String,
    target_id: String,
    confidence: f64,
    _source: String,
    metadata: Value,
    now: DateTime<Utc>,
) -> BoxFuture<'_, StoreResult<String>> {
    Box::pin(async move {
        let meta_str = serde_json::to_string(&metadata).unwrap_or_else(|_| "{}".to_string());
        let now_str = ts_to_str(now);

        let result = sqlx::query(
            "INSERT INTO swee_edges (source_id, target_id, type, weight, metadata, created_at) \
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
        )
        .bind(source_id.parse::<i64>().unwrap_or(0))
        .bind(target_id.parse::<i64>().unwrap_or(0))
        .bind(&edge_type)
        .bind(confidence)
        .bind(&meta_str)
        .bind(&now_str)
        .execute(pool)
        .await
        .map_err(StoreError::from)?;

        Ok(result.last_insert_rowid().to_string())
    })
}

pub(super) fn list_swee_nodes(
    pool: &SqlitePool,
    node_type: Option<String>,
) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
    Box::pin(async move {
        let rows = match node_type {
            Some(ref nt) => sqlx::query(
                "SELECT id, type, name, metadata, created_at, updated_at \
                     FROM swee_nodes WHERE type = ?1 ORDER BY created_at DESC",
            )
            .bind(nt)
            .fetch_all(pool)
            .await
            .map_err(StoreError::from)?,
            None => sqlx::query(
                "SELECT id, type, name, metadata, created_at, updated_at \
                     FROM swee_nodes ORDER BY created_at DESC",
            )
            .fetch_all(pool)
            .await
            .map_err(StoreError::from)?,
        };

        Ok(rows
            .into_iter()
            .map(|r| {
                let meta_str: String = r.try_get("metadata").unwrap_or_default();
                let metadata: Value =
                    serde_json::from_str(&meta_str).unwrap_or(Value::Object(Default::default()));
                let id: i64 = r.try_get("id").unwrap_or_default();
                serde_json::json!({
                    "id": id.to_string(),
                    "node_type": r.try_get::<String, _>("type").unwrap_or_default(),
                    "label": r.try_get::<String, _>("name").unwrap_or_default(),
                    "metadata": metadata,
                    "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
                    "updated_at": r.try_get::<String, _>("updated_at").unwrap_or_default(),
                })
            })
            .collect())
    })
}

pub(super) fn list_swee_edges(
    pool: &SqlitePool,
    edge_type: Option<String>,
) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
    Box::pin(async move {
        let rows = match edge_type {
            Some(ref et) => sqlx::query(
                "SELECT id, source_id, target_id, type, weight, metadata, created_at \
                     FROM swee_edges WHERE type = ?1 ORDER BY created_at DESC",
            )
            .bind(et)
            .fetch_all(pool)
            .await
            .map_err(StoreError::from)?,
            None => sqlx::query(
                "SELECT id, source_id, target_id, type, weight, metadata, created_at \
                     FROM swee_edges ORDER BY created_at DESC",
            )
            .fetch_all(pool)
            .await
            .map_err(StoreError::from)?,
        };

        Ok(rows
            .into_iter()
            .map(|r| {
                let meta_str: String = r.try_get("metadata").unwrap_or_default();
                let metadata: Value =
                    serde_json::from_str(&meta_str).unwrap_or(Value::Object(Default::default()));
                let id: i64 = r.try_get("id").unwrap_or_default();
                let src_id: i64 = r.try_get("source_id").unwrap_or_default();
                let tgt_id: i64 = r.try_get("target_id").unwrap_or_default();
                serde_json::json!({
                    "id": id.to_string(),
                    "source_id": src_id.to_string(),
                    "target_id": tgt_id.to_string(),
                    "edge_type": r.try_get::<String, _>("type").unwrap_or_default(),
                    "weight": r.try_get::<f64, _>("weight").unwrap_or(1.0),
                    "metadata": metadata,
                    "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
                })
            })
            .collect())
    })
}

pub(super) fn get_swee_node(
    pool: &SqlitePool,
    id: String,
) -> BoxFuture<'_, StoreResult<Option<Value>>> {
    Box::pin(async move {
        let row = sqlx::query(
            "SELECT id, type, name, metadata, created_at, updated_at \
             FROM swee_nodes WHERE id = ?1",
        )
        .bind(&id)
        .fetch_optional(pool)
        .await
        .map_err(StoreError::from)?;

        Ok(row.map(|r| {
            let meta_str: String = r.try_get("metadata").unwrap_or_default();
            let metadata: Value =
                serde_json::from_str(&meta_str).unwrap_or(Value::Object(Default::default()));
            let db_id: i64 = r.try_get("id").unwrap_or_default();
            serde_json::json!({
                "id": db_id.to_string(),
                "node_type": r.try_get::<String, _>("type").unwrap_or_default(),
                "label": r.try_get::<String, _>("name").unwrap_or_default(),
                "metadata": metadata,
                "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
                "updated_at": r.try_get::<String, _>("updated_at").unwrap_or_default(),
            })
        }))
    })
}

pub(super) fn get_swee_neighbors(
    pool: &SqlitePool,
    id: String,
    direction: String,
) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
    Box::pin(async move {
        let rows = match direction.as_str() {
            "forward" => {
                sqlx::query(
                    "SELECT e.id, e.source_id, e.target_id, e.type, e.weight, e.metadata, e.created_at \
                     FROM swee_edges e WHERE e.source_id = ?1 ORDER BY e.created_at DESC",
                )
                .bind(&id)
                .fetch_all(pool)
                .await
                .map_err(StoreError::from)?
            }
            "reverse" => {
                sqlx::query(
                    "SELECT e.id, e.source_id, e.target_id, e.type, e.weight, e.metadata, e.created_at \
                     FROM swee_edges e WHERE e.target_id = ?1 ORDER BY e.created_at DESC",
                )
                .bind(&id)
                .fetch_all(pool)
                .await
                .map_err(StoreError::from)?
            }
            _ => {
                sqlx::query(
                    "SELECT e.id, e.source_id, e.target_id, e.type, e.weight, e.metadata, e.created_at \
                     FROM swee_edges e WHERE e.source_id = ?1 OR e.target_id = ?1 ORDER BY e.created_at DESC",
                )
                .bind(&id)
                .fetch_all(pool)
                .await
                .map_err(StoreError::from)?
            }
        };

        Ok(rows
            .into_iter()
            .map(|r| {
                let meta_str: String = r.try_get("metadata").unwrap_or_default();
                let metadata: Value =
                    serde_json::from_str(&meta_str).unwrap_or(Value::Object(Default::default()));
                let eid: i64 = r.try_get("id").unwrap_or_default();
                let src_id: i64 = r.try_get("source_id").unwrap_or_default();
                let tgt_id: i64 = r.try_get("target_id").unwrap_or_default();
                serde_json::json!({
                    "id": eid.to_string(),
                    "source_id": src_id.to_string(),
                    "target_id": tgt_id.to_string(),
                    "edge_type": r.try_get::<String, _>("type").unwrap_or_default(),
                    "weight": r.try_get::<f64, _>("weight").unwrap_or(1.0),
                    "metadata": metadata,
                    "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
                })
            })
            .collect())
    })
}
