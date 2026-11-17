use chrono::{DateTime, Utc};
use serde_json::Value;
use sqlx::{Row, SqlitePool};

use crate::store::{BoxFuture, IngestOutcome, IngestRecord, StoreError, StoreResult};

use super::ts_to_str;

/// Apply an ingest batch in a single SQLite transaction.
///
/// All rows are written through one `BEGIN ... COMMIT`; any error returns
/// `Err` and drops the transaction, which rolls back every prior statement in
/// the batch.
pub(super) fn persist_ingest_batch(
    pool: &SqlitePool,
    records: Vec<IngestRecord>,
    now: DateTime<Utc>,
) -> BoxFuture<'_, StoreResult<IngestOutcome>> {
    Box::pin(async move {
        let now_str = ts_to_str(now);
        let mut tx = pool.begin().await.map_err(StoreError::from)?;
        let mut outcome = IngestOutcome::default();

        for record in records {
            // 1. Story: idempotency key is the primary key.
            let existing_story =
                sqlx::query("SELECT title, description, status FROM stories WHERE id = ?1")
                    .bind(&record.story_id)
                    .fetch_optional(&mut *tx)
                    .await
                    .map_err(StoreError::from)?;

            match existing_story {
                None => {
                    sqlx::query(
                        "INSERT INTO stories \
                         (id, sprint_id, title, description, status, story_points, created_at, updated_at) \
                         VALUES (?1, NULL, ?2, ?3, ?4, NULL, ?5, ?5)",
                    )
                    .bind(&record.story_id)
                    .bind(&record.title)
                    .bind(&record.description)
                    .bind(&record.status)
                    .bind(&now_str)
                    .execute(&mut *tx)
                    .await
                    .map_err(StoreError::from)?;
                    outcome.stories_created += 1;
                }
                Some(row) => {
                    let title: String = row.try_get("title").unwrap_or_default();
                    let description: String = row.try_get("description").unwrap_or_default();
                    let status: String = row.try_get("status").unwrap_or_default();

                    if title != record.title
                        || description != record.description
                        || status != record.status
                    {
                        sqlx::query(
                            "UPDATE stories \
                             SET title = ?2, description = ?3, status = ?4, updated_at = ?5 \
                             WHERE id = ?1",
                        )
                        .bind(&record.story_id)
                        .bind(&record.title)
                        .bind(&record.description)
                        .bind(&record.status)
                        .bind(&now_str)
                        .execute(&mut *tx)
                        .await
                        .map_err(StoreError::from)?;
                        outcome.stories_updated += 1;
                    } else {
                        outcome.stories_unchanged += 1;
                    }
                }
            }

            // 2. Evidence: deterministic id; refresh metadata in place.
            if let Some(evidence) = &record.evidence {
                let meta_str =
                    serde_json::to_string(&evidence.metadata).unwrap_or_else(|_| "{}".to_string());
                let existing_evidence = sqlx::query(
                    "SELECT artifact_id, kind, url, metadata FROM evidence WHERE id = ?1",
                )
                .bind(&evidence.id)
                .fetch_optional(&mut *tx)
                .await
                .map_err(StoreError::from)?;

                match existing_evidence {
                    None => {
                        sqlx::query(
                            "INSERT INTO evidence \
                             (id, artifact_id, kind, url, metadata, created_at, updated_at) \
                             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?6)",
                        )
                        .bind(&evidence.id)
                        .bind(&record.story_id)
                        .bind(&evidence.kind)
                        .bind(&evidence.url)
                        .bind(&meta_str)
                        .bind(&now_str)
                        .execute(&mut *tx)
                        .await
                        .map_err(StoreError::from)?;
                        outcome.evidence_created += 1;
                    }
                    Some(row) => {
                        let artifact_id: String = row.try_get("artifact_id").unwrap_or_default();
                        let kind: String = row.try_get("kind").unwrap_or_default();
                        let url: String = row.try_get("url").unwrap_or_default();
                        let old_meta: Value = serde_json::from_str(
                            &row.try_get::<String, _>("metadata").unwrap_or_default(),
                        )
                        .unwrap_or(Value::Null);

                        if artifact_id != record.story_id
                            || kind != evidence.kind
                            || url != evidence.url
                            || old_meta != evidence.metadata
                        {
                            sqlx::query(
                                "UPDATE evidence \
                                 SET artifact_id = ?2, kind = ?3, url = ?4, metadata = ?5, \
                                     updated_at = ?6 \
                                 WHERE id = ?1",
                            )
                            .bind(&evidence.id)
                            .bind(&record.story_id)
                            .bind(&evidence.kind)
                            .bind(&evidence.url)
                            .bind(&meta_str)
                            .bind(&now_str)
                            .execute(&mut *tx)
                            .await
                            .map_err(StoreError::from)?;
                            outcome.evidence_updated += 1;
                        } else {
                            outcome.evidence_unchanged += 1;
                        }
                    }
                }
            }

            // 3. Trace links: immutable once present; never duplicated.
            for link in &record.trace_links {
                let result = sqlx::query(
                    "INSERT INTO trace_links \
                     (id, source_id, target_id, relationship, confidence, source, created_at, updated_at) \
                     VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?7) \
                     ON CONFLICT DO NOTHING",
                )
                .bind(&link.id)
                .bind(&record.story_id)
                .bind(&link.target_id)
                .bind(&link.relationship)
                .bind(link.confidence)
                .bind(&link.source)
                .bind(&now_str)
                .execute(&mut *tx)
                .await
                .map_err(StoreError::from)?;

                if result.rows_affected() == 1 {
                    outcome.trace_links_created += 1;
                } else {
                    outcome.trace_links_unchanged += 1;
                }
            }
        }

        tx.commit().await.map_err(StoreError::from)?;
        Ok(outcome)
    })
}
