use super::str_to_ts;
use crate::store::{project_display_name, BoxFuture, ListParams, ProjectSummary, StoreResult};
use serde_json::Value;
use sqlx::{Row, SqlitePool};

const PROJECTS: &str = "
 SELECT id,name,description,created_at,updated_at,problem_count FROM (
   SELECT id,name,description,created_at,updated_at,0 AS problem_count FROM canonical_projects
   UNION ALL
   SELECT p.project_id AS id,p.project_id AS name,'Derived from persisted problem records' AS description,
          MIN(p.created_at) AS created_at,MAX(p.updated_at) AS updated_at,COUNT(*) AS problem_count
   FROM problems p WHERE p.deleted_at IS NULL
     AND NOT EXISTS (SELECT 1 FROM canonical_projects c WHERE c.id=p.project_id)
   GROUP BY p.project_id
 )";

fn project_from_row(row: sqlx::sqlite::SqliteRow) -> ProjectSummary {
    let id: String = row.get("id");
    ProjectSummary {
        name: if row.get::<i64, _>("problem_count") > 0 {
            project_display_name(&id)
        } else {
            row.get("name")
        },
        description: row.get("description"),
        metadata: Value::Object(Default::default()),
        id,
        created_at: str_to_ts(&row.get::<String, _>("created_at")),
        updated_at: str_to_ts(&row.get::<String, _>("updated_at")),
        problem_count: row.get("problem_count"),
    }
}

pub(super) fn list_projects(
    pool: &SqlitePool,
    params: ListParams,
) -> BoxFuture<'_, StoreResult<Vec<ProjectSummary>>> {
    Box::pin(async move {
        let sql = format!("{PROJECTS} ORDER BY updated_at DESC,id ASC LIMIT ?1 OFFSET ?2");
        let rows = sqlx::query(sqlx::AssertSqlSafe(&*sql))
            .bind(params.page_size as i64)
            .bind(params.offset() as i64)
            .fetch_all(pool)
            .await?;
        Ok(rows.into_iter().map(project_from_row).collect())
    })
}
pub(super) fn count_projects(pool: &SqlitePool) -> BoxFuture<'_, StoreResult<i64>> {
    Box::pin(async move {
        let sql = format!("SELECT COUNT(*) FROM ({PROJECTS})");
        Ok(sqlx::query_scalar(sqlx::AssertSqlSafe(&*sql))
            .fetch_one(pool)
            .await?)
    })
}
pub(super) fn get_project(
    pool: &SqlitePool,
    id: String,
) -> BoxFuture<'_, StoreResult<Option<ProjectSummary>>> {
    Box::pin(async move {
        let sql = format!("{PROJECTS} WHERE id=?1");
        Ok(sqlx::query(sqlx::AssertSqlSafe(&*sql))
            .bind(id)
            .fetch_optional(pool)
            .await?
            .map(project_from_row))
    })
}
