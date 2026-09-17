use chrono::{DateTime, Utc};
use sqlx::{PgPool, Row};

use crate::store::{Sprint, StoreError, StoreResult};

pub(super) async fn list_sprints(pool: &PgPool) -> StoreResult<Vec<Sprint>> {
    let rows = sqlx::query(
        "SELECT id, name, goal, start_date, end_date, status, created_at, updated_at \
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
            start_date: r.try_get("start_date").unwrap_or_else(|_| Utc::now()),
            end_date: r.try_get("end_date").unwrap_or_else(|_| Utc::now()),
            status: r.try_get("status").unwrap_or_default(),
            created_at: r.try_get("created_at").unwrap_or_else(|_| Utc::now()),
            updated_at: r.try_get("updated_at").unwrap_or_else(|_| Utc::now()),
        })
        .collect())
}

pub(super) async fn create_sprint(
    pool: &PgPool,
    id: String,
    name: String,
    goal: String,
    start_date: DateTime<Utc>,
    end_date: DateTime<Utc>,
    now: DateTime<Utc>,
) -> StoreResult<Sprint> {
    sqlx::query(
        "INSERT INTO sprints \
         (id, name, goal, start_date, end_date, status, created_at, updated_at) \
         VALUES ($1, $2, $3, $4, $5, 'planned', $6, $7)",
    )
    .bind(&id)
    .bind(&name)
    .bind(&goal)
    .bind(start_date)
    .bind(end_date)
    .bind(now)
    .bind(now)
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
}
