use chrono::Utc;
use serde_json::Value;
use sqlx::{PgPool, Row};

use crate::store::{project_display_name, ListParams, ProjectSummary, StoreError, StoreResult};

fn summary_from_row(row: &sqlx::postgres::PgRow) -> ProjectSummary {
    let id: String = row.try_get("id").unwrap_or_default();
    let problem_count: i64 = row.try_get("problem_count").unwrap_or_default();
    let created_at = row.try_get("created_at").unwrap_or_else(|_| Utc::now());
    let updated_at = row.try_get("updated_at").unwrap_or_else(|_| Utc::now());
    let metadata: Value = row
        .try_get("metadata")
        .unwrap_or_else(|_| Value::Object(Default::default()));
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

pub(super) async fn list_projects(
    pool: &PgPool,
    params: ListParams,
) -> StoreResult<Vec<ProjectSummary>> {
    let rows = sqlx::query(
        "SELECT p.id, p.name, p.description, p.metadata, p.created_at, p.updated_at, \
         (SELECT COUNT(*) FROM problems pr WHERE pr.project_id::text = p.id AND pr.deleted_at IS NULL)::bigint AS problem_count \
         FROM projects p ORDER BY p.updated_at DESC, p.id ASC LIMIT $1 OFFSET $2",
    )
        .bind(params.page_size as i64)
        .bind(params.offset() as i64)
        .fetch_all(pool)
        .await
        .map_err(StoreError::from)?;
    Ok(rows.iter().map(summary_from_row).collect())
}

pub(super) async fn count_projects(pool: &PgPool) -> StoreResult<i64> {
    let row = sqlx::query("SELECT COUNT(*)::bigint AS cnt FROM projects")
        .fetch_one(pool)
        .await
        .map_err(StoreError::from)?;
    Ok(row.try_get("cnt").unwrap_or(0))
}

pub(super) async fn get_project(
    pool: &PgPool,
    project_id: String,
) -> StoreResult<Option<ProjectSummary>> {
    let row = sqlx::query(
        "SELECT p.id, p.name, p.description, p.metadata, p.created_at, p.updated_at, \
         (SELECT COUNT(*) FROM problems pr WHERE pr.project_id::text = p.id AND pr.deleted_at IS NULL)::bigint AS problem_count \
         FROM projects p WHERE p.id = $1",
    )
        .bind(&project_id)
        .fetch_optional(pool)
        .await
        .map_err(StoreError::from)?;
    Ok(row.as_ref().map(summary_from_row))
}
