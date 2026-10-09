use crate::store::{project_display_name, ListParams, ProjectSummary, StoreResult};
use serde_json::Value;
use sqlx::{PgPool, Row};

const PROJECTS: &str = "
 SELECT id,name,description,created_at,updated_at,problem_count FROM (
   SELECT id,name,description,created_at,updated_at,0::bigint AS problem_count FROM canonical_projects
   UNION ALL
   SELECT p.project_id::text AS id,p.project_id::text AS name,'Derived from persisted problem records' AS description,
          MIN(p.created_at) AS created_at,MAX(p.updated_at) AS updated_at,COUNT(*)::bigint AS problem_count
   FROM problems p WHERE p.deleted_at IS NULL
     AND NOT EXISTS (SELECT 1 FROM canonical_projects c WHERE c.id=p.project_id::text)
   GROUP BY p.project_id
 ) AS projects";

fn project_from_row(row: sqlx::postgres::PgRow) -> ProjectSummary {
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
        created_at: row.get("created_at"),
        updated_at: row.get("updated_at"),
        problem_count: row.get("problem_count"),
    }
}
pub(super) async fn list_projects(
    pool: &PgPool,
    params: ListParams,
) -> StoreResult<Vec<ProjectSummary>> {
    let sql = format!("{PROJECTS} ORDER BY updated_at DESC,id ASC LIMIT $1 OFFSET $2");
    let rows = sqlx::query(sqlx::AssertSqlSafe(&*sql))
        .bind(params.page_size as i64)
        .bind(params.offset() as i64)
        .fetch_all(pool)
        .await?;
    Ok(rows.into_iter().map(project_from_row).collect())
}
pub(super) async fn count_projects(pool: &PgPool) -> StoreResult<i64> {
    let sql = format!("SELECT COUNT(*) FROM ({PROJECTS}) AS all_projects");
    Ok(sqlx::query_scalar(sqlx::AssertSqlSafe(&*sql))
        .fetch_one(pool)
        .await?)
}
pub(super) async fn get_project(pool: &PgPool, id: String) -> StoreResult<Option<ProjectSummary>> {
    let sql = format!("{PROJECTS} WHERE id=$1");
    Ok(sqlx::query(sqlx::AssertSqlSafe(&*sql))
        .bind(id)
        .fetch_optional(pool)
        .await?
        .map(project_from_row))
}
