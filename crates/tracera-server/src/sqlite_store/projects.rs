use chrono::Utc;
use serde_json::Value;
use sqlx::{Row, SqlitePool};

use crate::store::{
    project_display_name, BoxFuture, ListParams, ProjectSummary, StoreError, StoreResult,
};

use super::str_to_ts;

fn summary_from_row(row: &sqlx::sqlite::SqliteRow) -> ProjectSummary {
    let id: String = row.try_get("id").unwrap_or_default();
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
    let metadata: Value = row
        .try_get::<String, _>("metadata")
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_else(|| Value::Object(Default::default()));
    let name: String = row
        .try_get("name")
        .unwrap_or_else(|_| project_display_name(&id));
    let description: Option<String> = row.try_get("description").ok().flatten();
    ProjectSummary {
        name,
        description,
        metadata,
        id,
        created_at,
        updated_at,
        problem_count,
    }
}

pub(super) fn list_projects(
    pool: &SqlitePool,
    params: ListParams,
) -> BoxFuture<'_, StoreResult<Vec<ProjectSummary>>> {
    Box::pin(async move {
        let rows = sqlx::query(
            "SELECT p.id, p.name, p.description, p.metadata, p.created_at, p.updated_at, \
             (SELECT COUNT(*) FROM problems pr WHERE pr.project_id = p.id AND pr.deleted_at IS NULL) AS problem_count \
             FROM projects p ORDER BY p.updated_at DESC, p.id ASC LIMIT ?1 OFFSET ?2",
        )
            .bind(params.page_size as i64)
            .bind(params.offset() as i64)
            .fetch_all(pool)
            .await
            .map_err(StoreError::from)?;

        Ok(rows.iter().map(summary_from_row).collect())
    })
}

pub(super) fn count_projects(pool: &SqlitePool) -> BoxFuture<'_, StoreResult<i64>> {
    Box::pin(async move {
        let row = sqlx::query("SELECT COUNT(*) AS cnt FROM projects")
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
        let row = sqlx::query(
            "SELECT p.id, p.name, p.description, p.metadata, p.created_at, p.updated_at, \
             (SELECT COUNT(*) FROM problems pr WHERE pr.project_id = p.id AND pr.deleted_at IS NULL) AS problem_count \
             FROM projects p WHERE p.id = ?1",
        )
            .bind(&project_id)
            .fetch_optional(pool)
            .await
            .map_err(StoreError::from)?;
        Ok(row.as_ref().map(summary_from_row))
    })
}
