use chrono::{DateTime, Utc};
use serde_json::Value;
use sqlx::{Row, SqlitePool};

use crate::store::{
    AgilePlusEdgeWrite, AgilePlusIngestOutcome, AgilePlusIngestRecord, AgilePlusNodeWrite,
    StoreError, StoreResult,
};

use super::ts_to_str;

/// Apply a native AgilePlus ingest as one SQLite transaction.
///
/// Nodes and edges are inserted first so their staged indices can be resolved
/// to database ids. Any error drops the transaction, rolling back every graph
/// row, revision row, and the idempotency receipt.
pub(super) async fn ingest(
    pool: &SqlitePool,
    nodes: Vec<AgilePlusNodeWrite>,
    edges: Vec<AgilePlusEdgeWrite>,
    mut record: AgilePlusIngestRecord,
    now: DateTime<Utc>,
) -> StoreResult<AgilePlusIngestOutcome> {
    let now_str = ts_to_str(now);
    let mut tx = pool.begin().await.map_err(StoreError::from)?;

    let mut node_ids = Vec::with_capacity(nodes.len());
    for node in nodes {
        let metadata = json_string(&node.metadata);
        let result = sqlx::query(
            "INSERT INTO swee_nodes (type, name, metadata, created_at, updated_at) \
             VALUES (?1, ?2, ?3, ?4, ?4) RETURNING id",
        )
        .bind(&node.node_type)
        .bind(&node.label)
        .bind(&metadata)
        .bind(&now_str)
        .fetch_one(&mut *tx)
        .await
        .map_err(classify_sqlite_error)?;
        node_ids.push(result.get::<i64, _>("id"));
    }

    let mut edges_created = 0usize;
    for edge in edges {
        let (Some(source_id), Some(target_id)) = (
            node_ids.get(edge.source_node_index).copied(),
            node_ids.get(edge.target_node_index).copied(),
        ) else {
            return Err(StoreError::Conflict(
                "edge references an unknown staged node".into(),
            ));
        };
        let metadata = json_string(&edge.metadata);
        let result = sqlx::query(
            "INSERT INTO swee_edges \
             (source_id, target_id, type, weight, metadata, created_at) \
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
        )
        .bind(source_id)
        .bind(target_id)
        .bind(&edge.edge_type)
        .bind(edge.confidence)
        .bind(&metadata)
        .bind(&now_str)
        .execute(&mut *tx)
        .await
        .map_err(classify_sqlite_error)?;
        if result.rows_affected() != 1 {
            return Err(StoreError::Conflict("duplicate edge".into()));
        }
        edges_created += 1;
    }

    let mut revisions_written = 0usize;
    for revision in &mut record.revisions {
        let staged_index = revision
            .node_id
            .strip_prefix("index:")
            .and_then(|value| value.parse::<usize>().ok());
        if let Some(index) = staged_index {
            let Some(node_id) = node_ids.get(index) else {
                return Err(StoreError::Conflict(
                    "revision references an unknown staged node".into(),
                ));
            };
            revision.node_id = node_id.to_string();
        }
        let result = sqlx::query(
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
        .map_err(classify_sqlite_error)?;
        revisions_written += result.rows_affected() as usize;
    }

    let result = sqlx::query(
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
    .map_err(classify_sqlite_error)?;
    if result.rows_affected() != 1 {
        return Err(StoreError::Conflict(
            "idempotency key already consumed".into(),
        ));
    }

    tx.commit().await.map_err(StoreError::from)?;
    Ok(AgilePlusIngestOutcome {
        nodes_created: node_ids.len(),
        edges_created,
        revisions_written,
    })
}

fn classify_sqlite_error(error: sqlx::Error) -> StoreError {
    match error {
        sqlx::Error::Database(database)
            if database.is_unique_violation()
                || database.code().as_deref() == Some("2067")
                || database.code().as_deref() == Some("1555") =>
        {
            StoreError::Conflict(database.message().to_owned())
        }
        error => StoreError::from(error),
    }
}

fn json_string(value: &Value) -> String {
    serde_json::to_string(value).unwrap_or_else(|_| "{}".to_string())
}
