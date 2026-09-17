use chrono::{DateTime, Utc};
use sqlx::{Row, SqlitePool};

use crate::store::{BoxFuture, Sprint, StoreError, StoreResult};

use super::ts_to_str;

pub(super) fn list_sprints(pool: &SqlitePool) -> BoxFuture<'_, StoreResult<Vec<Sprint>>> {
    Box::pin(async move {
        let rows = sqlx::query(
            "SELECT id, name, goal, start_date, end_date, status, created_at, updated_at
             FROM sprints ORDER BY created_at ASC",
        )
        .fetch_all(pool)
        .await
        .map_err(StoreError::from)?;

        Ok(rows
            .into_iter()
            .map(|r| Sprint {
                id: r.try_get("id").unwrap_or_default(),
                name: r.try_get("name").unwrap_or_default(),
                goal: r.try_get("goal").unwrap_or_default(),
                start_date: super::str_to_ts(
                    &r.try_get::<String, _>("start_date").unwrap_or_default(),
                ),
                end_date: super::str_to_ts(&r.try_get::<String, _>("end_date").unwrap_or_default()),
                status: r.try_get("status").unwrap_or_default(),
                created_at: super::str_to_ts(
                    &r.try_get::<String, _>("created_at").unwrap_or_default(),
                ),
                updated_at: super::str_to_ts(
                    &r.try_get::<String, _>("updated_at").unwrap_or_default(),
                ),
            })
            .collect())
    })
}

pub(super) fn create_sprint(
    pool: &SqlitePool,
    id: String,
    name: String,
    goal: String,
    start_date: DateTime<Utc>,
    end_date: DateTime<Utc>,
    now: DateTime<Utc>,
) -> BoxFuture<'_, StoreResult<Sprint>> {
    Box::pin(async move {
        let now_str = ts_to_str(now);
        sqlx::query(
            "INSERT INTO sprints (id, name, goal, start_date, end_date, status, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, 'planned', ?6, ?7)",
        )
        .bind(&id)
        .bind(&name)
        .bind(&goal)
        .bind(ts_to_str(start_date))
        .bind(ts_to_str(end_date))
        .bind(&now_str)
        .bind(&now_str)
        .execute(pool)
        .await
        .map_err(StoreError::from)?;

        Ok(Sprint {
            id,
            name,
            goal,
            start_date,
            end_date,
            status: "planned".to_string(),
            created_at: now,
            updated_at: now,
        })
    })
}
