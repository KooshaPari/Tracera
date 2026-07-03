/// SqliteStore — SQLite on-device/per-project backend implementing `Store`.
///
/// Uses runtime `sqlx::query()` (not macros) so the PG `.sqlx/` offline cache
/// remains the sole compile-time check surface; `env -u DATABASE_URL cargo build`
/// stays green without a live DB.
///
/// Backend selection: any `DATABASE_URL` with scheme `sqlite://` or a plain
/// file path ending in `.db` routes here. A special `sqlite::memory:` URL gives
/// an in-process ephemeral store — used by tests.
///
/// Timestamps are stored as ISO-8601 TEXT (SQLite has no native timestamp type).
/// The `members` column from the PG TEXT[] is stored as a JSON array string.
use chrono::{DateTime, Utc};
use serde_json::Value;
use sqlx::{Row, SqlitePool};

use crate::store::{
    BoxFuture, EvidenceItem, Sprint, Store, StoreError, StoreResult, Story, TeamRow, TraceLink,
};

#[derive(Clone)]
pub struct SqliteStore {
    pub pool: SqlitePool,
}

impl SqliteStore {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }
}

// Helpers for timestamp round-trips (TEXT ↔ DateTime<Utc>)
fn ts_to_str(dt: DateTime<Utc>) -> String {
    dt.to_rfc3339()
}

fn str_to_ts(s: &str) -> DateTime<Utc> {
    DateTime::parse_from_rfc3339(s)
        .map(|dt| dt.with_timezone(&Utc))
        .unwrap_or_else(|_| Utc::now())
}

impl Store for SqliteStore {
    fn list_evidence(&self) -> BoxFuture<'_, StoreResult<Vec<EvidenceItem>>> {
        Box::pin(async move {
            let rows = sqlx::query(
                "SELECT id, artifact_id, kind, url, metadata, created_at, updated_at
                 FROM evidence ORDER BY created_at ASC",
            )
            .fetch_all(&self.pool)
            .await
            .map_err(StoreError::from)?;

            let items = rows
                .into_iter()
                .map(|r| {
                    let meta_str: String = r.try_get("metadata").unwrap_or_default();
                    let metadata: Value =
                        serde_json::from_str(&meta_str).unwrap_or(Value::Object(Default::default()));
                    EvidenceItem {
                        id: r.try_get("id").unwrap_or_default(),
                        artifact_id: r.try_get("artifact_id").unwrap_or_default(),
                        kind: r.try_get("kind").unwrap_or_default(),
                        url: r.try_get("url").unwrap_or_default(),
                        metadata,
                        created_at: str_to_ts(&r.try_get::<String, _>("created_at").unwrap_or_default()),
                        updated_at: str_to_ts(&r.try_get::<String, _>("updated_at").unwrap_or_default()),
                    }
                })
                .collect();

            Ok(items)
        })
    }

    fn create_evidence(
        &self,
        id: String,
        artifact_id: String,
        kind: String,
        url: String,
        metadata: Value,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<EvidenceItem>> {
        Box::pin(async move {
            let meta_str = serde_json::to_string(&metadata)
                .unwrap_or_else(|_| "{}".to_string());
            let now_str = ts_to_str(now);

            sqlx::query(
                "INSERT INTO evidence (id, artifact_id, kind, url, metadata, created_at, updated_at)
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            )
            .bind(&id)
            .bind(&artifact_id)
            .bind(&kind)
            .bind(&url)
            .bind(&meta_str)
            .bind(&now_str)
            .bind(&now_str)
            .execute(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(EvidenceItem {
                id,
                artifact_id,
                kind,
                url,
                metadata,
                created_at: now,
                updated_at: now,
            })
        })
    }

    fn list_sprints(&self) -> BoxFuture<'_, StoreResult<Vec<Sprint>>> {
        Box::pin(async move {
            let rows = sqlx::query(
                "SELECT id, name, goal, start_date, end_date, status, created_at, updated_at
                 FROM sprints ORDER BY created_at ASC",
            )
            .fetch_all(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(rows
                .into_iter()
                .map(|r| Sprint {
                    id: r.try_get("id").unwrap_or_default(),
                    name: r.try_get("name").unwrap_or_default(),
                    goal: r.try_get("goal").unwrap_or_default(),
                    start_date: str_to_ts(&r.try_get::<String, _>("start_date").unwrap_or_default()),
                    end_date: str_to_ts(&r.try_get::<String, _>("end_date").unwrap_or_default()),
                    status: r.try_get("status").unwrap_or_default(),
                    created_at: str_to_ts(&r.try_get::<String, _>("created_at").unwrap_or_default()),
                    updated_at: str_to_ts(&r.try_get::<String, _>("updated_at").unwrap_or_default()),
                })
                .collect())
        })
    }

    fn create_sprint(
        &self,
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
            .execute(&self.pool)
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

    fn list_stories(&self) -> BoxFuture<'_, StoreResult<Vec<Story>>> {
        Box::pin(async move {
            let rows = sqlx::query(
                "SELECT id, sprint_id, title, description, status, story_points, created_at, updated_at
                 FROM stories ORDER BY created_at ASC",
            )
            .fetch_all(&self.pool)
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
                    created_at: str_to_ts(&r.try_get::<String, _>("created_at").unwrap_or_default()),
                    updated_at: str_to_ts(&r.try_get::<String, _>("updated_at").unwrap_or_default()),
                })
                .collect())
        })
    }

    fn create_story(
        &self,
        id: String,
        sprint_id: Option<String>,
        title: String,
        description: String,
        status: String,
        story_points: Option<i64>,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<Story>> {
        Box::pin(async move {
            let now_str = ts_to_str(now);
            sqlx::query(
                "INSERT INTO stories (id, sprint_id, title, description, status, story_points, created_at, updated_at)
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            )
            .bind(&id)
            .bind(&sprint_id)
            .bind(&title)
            .bind(&description)
            .bind(&status)
            .bind(story_points)
            .bind(&now_str)
            .bind(&now_str)
            .execute(&self.pool)
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
        })
    }

    fn create_trace_link(
        &self,
        id: String,
        source_id: String,
        target_id: String,
        relationship: String,
        confidence: f64,
        source: String,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<TraceLink>> {
        Box::pin(async move {
            let now_str = ts_to_str(now);
            sqlx::query(
                "INSERT INTO trace_links \
                 (id, source_id, target_id, relationship, confidence, source, created_at, updated_at)
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            )
            .bind(&id)
            .bind(&source_id)
            .bind(&target_id)
            .bind(&relationship)
            .bind(confidence)
            .bind(&source)
            .bind(&now_str)
            .bind(&now_str)
            .execute(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(TraceLink {
                id,
                source_id,
                target_id,
                relationship,
                confidence,
                source,
                created_at: now,
                updated_at: now,
            })
        })
    }

    fn list_teams(&self) -> BoxFuture<'_, StoreResult<Vec<TeamRow>>> {
        Box::pin(async move {
            let rows = sqlx::query(
                "SELECT id, name, description, members FROM teams ORDER BY id ASC",
            )
            .fetch_all(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(rows
                .into_iter()
                .map(|r| {
                    let members_str: String = r.try_get("members").unwrap_or_else(|_| "[]".to_string());
                    let members: Vec<String> =
                        serde_json::from_str(&members_str).unwrap_or_default();
                    TeamRow {
                        id: r.try_get("id").unwrap_or_default(),
                        name: r.try_get("name").unwrap_or_default(),
                        description: r.try_get("description").unwrap_or_default(),
                        members,
                    }
                })
                .collect())
        })
    }

    fn count_evidence(&self) -> BoxFuture<'_, StoreResult<i64>> {
        Box::pin(async move {
            let row = sqlx::query("SELECT COUNT(*) as cnt FROM evidence")
                .fetch_one(&self.pool)
                .await
                .map_err(StoreError::from)?;
            let count: i64 = row.try_get("cnt").unwrap_or(0);
            Ok(count)
        })
    }
}
