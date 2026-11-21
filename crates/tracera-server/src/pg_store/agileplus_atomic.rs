use chrono::{DateTime, Utc};
use sqlx::{PgPool, Row};

use crate::store::{
    AgilePlusEdgeWrite, AgilePlusIngestOutcome, AgilePlusIngestRecord, AgilePlusNodeWrite,
    StoreError, StoreResult,
};

/// Apply a native AgilePlus ingest as one PostgreSQL transaction.
pub(super) async fn ingest(
    pool: &PgPool,
    nodes: Vec<AgilePlusNodeWrite>,
    edges: Vec<AgilePlusEdgeWrite>,
    mut record: AgilePlusIngestRecord,
    now: DateTime<Utc>,
) -> StoreResult<AgilePlusIngestOutcome> {
    let mut tx = pool.begin().await.map_err(StoreError::from)?;
    let mut node_ids = Vec::with_capacity(nodes.len());

    for node in nodes {
        let row = sqlx::query(
            "INSERT INTO swee_nodes (node_type, label, metadata, created_at, updated_at) \
             VALUES ($1, $2, $3, $4, $4) RETURNING id",
        )
        .bind(&node.node_type)
        .bind(&node.label)
        .bind(&node.metadata)
        .bind(now)
        .fetch_one(&mut *tx)
        .await
        .map_err(classify_postgres_error)?;
        node_ids.push(row.get::<i64, _>("id"));
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
        let result = sqlx::query(
            "INSERT INTO swee_edges \
             (edge_type, source_id, target_id, confidence, metadata, created_at) \
             VALUES ($1, $2, $3, $4, $5, $6)",
        )
        .bind(&edge.edge_type)
        .bind(source_id)
        .bind(target_id)
        .bind(edge.confidence)
        .bind(&edge.metadata)
        .bind(now)
        .execute(&mut *tx)
        .await
        .map_err(classify_postgres_error)?;
        if result.rows_affected() != 1 {
            return Err(StoreError::Conflict("duplicate edge".into()));
        }
        edges_created += 1;
    }

    let mut revisions_written = 0usize;
    for revision in &mut record.revisions {
        if let Some(index) = revision
            .node_id
            .strip_prefix("index:")
            .and_then(|value| value.parse::<usize>().ok())
        {
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
        .map_err(classify_postgres_error)?;
        revisions_written += result.rows_affected() as usize;
    }

    let result = sqlx::query(
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
    .map_err(classify_postgres_error)?;
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

fn classify_postgres_error(error: sqlx::Error) -> StoreError {
    match error {
        sqlx::Error::Database(database)
            if database.is_unique_violation() || database.code().as_deref() == Some("23505") =>
        {
            StoreError::Conflict(database.message().to_owned())
        }
        error => StoreError::from(error),
    }
}
