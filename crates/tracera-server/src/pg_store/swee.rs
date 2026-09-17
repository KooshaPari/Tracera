use chrono::{DateTime, Utc};
use serde_json::Value;
use sqlx::{PgPool, Row};

use crate::store::{StoreError, StoreResult};

pub(super) async fn create_swee_node(
    pool: &PgPool,
    node_type: String,
    label: String,
    metadata: Value,
    now: DateTime<Utc>,
) -> StoreResult<String> {
    let row: (i64,) = sqlx::query_as(
        "INSERT INTO swee_nodes (node_type, label, metadata, created_at, updated_at) \
         VALUES ($1, $2, $3::jsonb, $4, $5) \
         RETURNING id",
    )
    .bind(&node_type)
    .bind(&label)
    .bind(&metadata)
    .bind(now)
    .bind(now)
    .fetch_one(pool)
    .await
    .map_err(StoreError::from)?;

    Ok(row.0.to_string())
}

#[allow(clippy::too_many_arguments)]
pub(super) async fn create_swee_edge(
    pool: &PgPool,
    edge_type: String,
    source_id: String,
    target_id: String,
    confidence: f64,
    _source: String,
    metadata: Value,
    now: DateTime<Utc>,
) -> StoreResult<String> {
    let src_id: i64 = source_id.parse().unwrap_or(0);
    let tgt_id: i64 = target_id.parse().unwrap_or(0);

    let row: (i64,) = sqlx::query_as(
        "INSERT INTO swee_edges (source_id, target_id, edge_type, confidence, metadata, created_at) \
         VALUES ($1, $2, $3, $4, $5::jsonb, $6) \
         RETURNING id",
    )
    .bind(src_id)
    .bind(tgt_id)
    .bind(&edge_type)
    .bind(confidence)
    .bind(&metadata)
    .bind(now)
    .fetch_one(pool)
    .await
    .map_err(StoreError::from)?;

    Ok(row.0.to_string())
}

pub(super) async fn list_swee_nodes(
    pool: &PgPool,
    node_type: Option<String>,
) -> StoreResult<Vec<Value>> {
    let rows = match node_type {
        Some(ref nt) => sqlx::query(
            "SELECT id, node_type, label, metadata::text, created_at, updated_at \
                 FROM swee_nodes WHERE node_type = $1 ORDER BY created_at DESC",
        )
        .bind(nt)
        .fetch_all(pool)
        .await
        .map_err(StoreError::from)?,
        None => sqlx::query(
            "SELECT id, node_type, label, metadata::text, created_at, updated_at \
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
            let metadata: Value = serde_json::from_str(&meta_str)
                .unwrap_or(Value::Object(Default::default()));
            let id: i64 = r.try_get("id").unwrap_or_default();
            serde_json::json!({
                "id": id.to_string(),
                "node_type": r.try_get::<String, _>("node_type").unwrap_or_default(),
                "label": r.try_get::<String, _>("label").unwrap_or_default(),
                "metadata": metadata,
                "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
                "updated_at": r.try_get::<String, _>("updated_at").unwrap_or_default(),
            })
        })
        .collect())
}

pub(super) async fn list_swee_edges(
    pool: &PgPool,
    edge_type: Option<String>,
) -> StoreResult<Vec<Value>> {
    let rows = match edge_type {
        Some(ref et) => {
            sqlx::query(
                "SELECT id, source_id, target_id, edge_type, confidence, metadata::text, created_at \
                 FROM swee_edges WHERE edge_type = $1 ORDER BY created_at DESC",
            )
            .bind(et)
            .fetch_all(pool)
            .await
            .map_err(StoreError::from)?
        }
        None => {
            sqlx::query(
                "SELECT id, source_id, target_id, edge_type, confidence, metadata::text, created_at \
                 FROM swee_edges ORDER BY created_at DESC",
            )
            .fetch_all(pool)
            .await
            .map_err(StoreError::from)?
        }
    };

    Ok(rows
        .into_iter()
        .map(|r| {
            let meta_str: String = r.try_get("metadata").unwrap_or_default();
            let metadata: Value = serde_json::from_str(&meta_str)
                .unwrap_or(Value::Object(Default::default()));
            let id: i64 = r.try_get("id").unwrap_or_default();
            let src_id: i64 = r.try_get("source_id").unwrap_or_default();
            let tgt_id: i64 = r.try_get("target_id").unwrap_or_default();
            serde_json::json!({
                "id": id.to_string(),
                "source_id": src_id.to_string(),
                "target_id": tgt_id.to_string(),
                "edge_type": r.try_get::<String, _>("edge_type").unwrap_or_default(),
                "weight": r.try_get::<f64, _>("confidence").unwrap_or(1.0),
                "metadata": metadata,
                "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
            })
        })
        .collect())
}

pub(super) async fn get_swee_node(
    pool: &PgPool,
    id: String,
) -> StoreResult<Option<Value>> {
    let row = sqlx::query(
        "SELECT id, node_type, label, metadata::text, created_at, updated_at \
         FROM swee_nodes WHERE id = $1",
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
            "node_type": r.try_get::<String, _>("node_type").unwrap_or_default(),
            "label": r.try_get::<String, _>("label").unwrap_or_default(),
            "metadata": metadata,
            "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
            "updated_at": r.try_get::<String, _>("updated_at").unwrap_or_default(),
        })
    }))
}

pub(super) async fn get_swee_neighbors(
    pool: &PgPool,
    id: String,
    direction: String,
) -> StoreResult<Vec<Value>> {
    let rows = match direction.as_str() {
        "forward" => {
            sqlx::query(
                "SELECT e.id, e.source_id, e.target_id, e.edge_type, e.confidence, e.metadata::text, e.created_at \
                 FROM swee_edges e WHERE e.source_id = $1::bigint ORDER BY e.created_at DESC",
            )
            .bind(&id)
            .fetch_all(pool)
            .await
            .map_err(StoreError::from)?
        }
        "reverse" => {
            sqlx::query(
                "SELECT e.id, e.source_id, e.target_id, e.edge_type, e.confidence, e.metadata::text, e.created_at \
                 FROM swee_edges e WHERE e.target_id = $1::bigint ORDER BY e.created_at DESC",
            )
            .bind(&id)
            .fetch_all(pool)
            .await
            .map_err(StoreError::from)?
        }
        _ => {
            // "both" or any other value
            sqlx::query(
                "SELECT e.id, e.source_id, e.target_id, e.edge_type, e.confidence, e.metadata::text, e.created_at \
                 FROM swee_edges e WHERE e.source_id = $1::bigint OR e.target_id = $1::bigint ORDER BY e.created_at DESC",
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
            let metadata: Value = serde_json::from_str(&meta_str)
                .unwrap_or(Value::Object(Default::default()));
            let eid: i64 = r.try_get("id").unwrap_or_default();
            let src_id: i64 = r.try_get("source_id").unwrap_or_default();
            let tgt_id: i64 = r.try_get("target_id").unwrap_or_default();
            serde_json::json!({
                "id": eid.to_string(),
                "source_id": src_id.to_string(),
                "target_id": tgt_id.to_string(),
                "edge_type": r.try_get::<String, _>("edge_type").unwrap_or_default(),
                "weight": r.try_get::<f64, _>("confidence").unwrap_or(1.0),
                "metadata": metadata,
                "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
            })
        })
        .collect())
}
