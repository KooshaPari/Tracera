use chrono::{DateTime, Utc};
use sqlx::{PgPool, Row};

use crate::store::{Story, StoreError, StoreResult};

pub(super) async fn list_stories(pool: &PgPool) -> StoreResult<Vec<Story>> {
    let rows = sqlx::query(
        "SELECT id, sprint_id, title, description, status, story_points, \
         created_at, updated_at FROM stories ORDER BY created_at ASC",
    )
    .fetch_all(pool)
    .await
    .map_err(StoreError::from)?;

    Ok(rows
        .into_iter()
        .map(|r| Story {
            id: r.try_get("id").unwrap_or_default(),
            sprint_id: r.try_get("sprint_id").ok(),
            title: r.try_get("title").unwrap_or_default(),
            description: r.try_get("description").unwrap_or_default(),
            status: r.try_get("status").unwrap_or_default(),
            story_points: r.try_get("story_points").ok(),
            created_at: r.try_get("created_at").unwrap_or_else(|_| Utc::now()),
            updated_at: r.try_get("updated_at").unwrap_or_else(|_| Utc::now()),
        })
        .collect())
}

pub(super) async fn create_story(
    pool: &PgPool,
    id: String,
    sprint_id: Option<String>,
    title: String,
    description: String,
    status: String,
    story_points: Option<i64>,
    now: DateTime<Utc>,
) -> StoreResult<Story> {
    sqlx::query(
        "INSERT INTO stories \
         (id, sprint_id, title, description, status, story_points, created_at, updated_at) \
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
    )
    .bind(&id)
    .bind(&sprint_id)
    .bind(&title)
    .bind(&description)
    .bind(&status)
    .bind(story_points)
    .bind(now)
    .bind(now)
    .execute(pool)
    .await
    .map_err(StoreError::from)?;

    Ok(Story {
        id,
        sprint_id,
        title,
        description,
        status,
        story_points,
        created_at: now,
        updated_at: now,
    })
}
