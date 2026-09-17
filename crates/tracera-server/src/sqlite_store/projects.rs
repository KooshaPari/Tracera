use chrono::Utc;
use serde_json::Value;
use sqlx::{Row, SqlitePool};

use crate::store::{project_display_name, BoxFuture, ListParams, ProjectSummary, StoreError, StoreResult};

use super::str_to_ts;

pub(super) fn list_projects(pool: &SqlitePool, params: ListParams) -> BoxFuture<'_, StoreResult<Vec<ProjectSummary>>> {
    Box::pin(async move {
        let rows = sqlx::query(
            "SELECT project_id, COUNT(*) AS problem_count, MIN(created_at) AS created_at, MAX(updated_at) AS updated_at
             FROM problems
             WHERE deleted_at IS NULL
             GROUP BY project_id
             ORDER BY MAX(updated_at) DESC, project_id ASC LIMIT ?1 OFFSET ?2",
        )
        .bind(params.page_size as i64)
        .bind(params.offset() as i64)
        .fetch_all(pool)
        .await
        .map_err(StoreError::from)?;

        Ok(rows
            .into_iter()
            .map(|row| {
                let id: String = row.try_get("project_id").unwrap_or_default();
                let problem_count: i64 = row.try_get("problem_count").unwrap_or_default();
                let created_at = row
                    .try_get::<String, _>("created_at")
                    .ok()
                    .map(|s| str_to_ts(&s))
                    .unwrap_or_else(Utc::now);
                let updated_at = row
                    .try_get::<String, _>("updated_at")
                    .ok()
                    .map(|s| str_to_ts(&s))
                    .unwrap_or_else(Utc::now);
                ProjectSummary {
                    name: project_display_name(&id),
                    description: Some("Derived from persisted problem records".to_string()),
                    metadata: Value::Object(Default::default()),
                    id,
                    created_at,
                    updated_at,
                    problem_count,
                }
            })
            .collect())
    })
}

pub(super) fn count_projects(pool: &SqlitePool) -> BoxFuture<'_, StoreResult<i64>> {
    Box::pin(async move {
        let row = sqlx::query(
            "SELECT COUNT(DISTINCT project_id) AS cnt FROM problems WHERE deleted_at IS NULL",
        )
        .fetch_one(pool)
        .await
        .map_err(StoreError::from)?;
        Ok(row.try_get("cnt").unwrap_or(0))
    })
}

pub(super) fn get_project(
    pool: &SqlitePool,
    project_id: String,
) -> BoxFuture<'_, StoreResult<Option<ProjectSummary>>> {
    Box::pin(async move {
        let rows = sqlx::query(
            "SELECT project_id, COUNT(*) AS problem_count, MIN(created_at) AS created_at, MAX(updated_at) AS updated_at
             FROM problems
             WHERE deleted_at IS NULL AND project_id = ?1
             GROUP BY project_id",
        )
        .bind(&project_id)
        .fetch_all(pool)
        .await
        .map_err(StoreError::from)?;

        Ok(rows.into_iter().next().map(|row| {
            let created_at = row
                .try_get::<String, _>("created_at")
                .ok()
                .map(|s| str_to_ts(&s))
                .unwrap_or_else(Utc::now);
            let updated_at = row
                .try_get::<String, _>("updated_at")
                .ok()
                .map(|s| str_to_ts(&s))
                .unwrap_or_else(Utc::now);
            ProjectSummary {
                id: project_id.clone(),
                name: project_display_name(&project_id),
                description: Some("Derived from persisted problem records".to_string()),
                metadata: Value::Object(Default::default()),
                problem_count: row.try_get("problem_count").unwrap_or_default(),
                created_at,
                updated_at,
            }
        }))
    })
}
