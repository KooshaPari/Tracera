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
    BenchmarkRun, BoxFuture, EvidenceItem, Problem, Sprint, Store, StoreError, StoreResult, Story,
    TeamRow, TraceLink,
};

#[derive(Clone)]
pub struct SqliteStore {
    pub pool: SqlitePool,
}

impl SqliteStore {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    fn get_benchmark_run_by_replay_hash(
        &self,
        replay_hash: String,
    ) -> BoxFuture<'_, StoreResult<Option<BenchmarkRun>>> {
        Box::pin(async move {
            let row = sqlx::query("SELECT run_id, session_id, attempt_id, schema_version, replay_hash, outcome_sha256, key_id, signature_digest, status, metadata, created_at, updated_at FROM benchmark_runs WHERE replay_hash = ?1")
            .bind(replay_hash)
            .fetch_optional(&self.pool)
            .await
            .map_err(StoreError::from)?;
            Ok(row.map(row_to_benchmark_run))
        })
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

fn opt_ts_to_str(dt: Option<DateTime<Utc>>) -> Option<String> {
    dt.map(ts_to_str)
}

fn str_to_opt_ts(s: Option<String>) -> Option<DateTime<Utc>> {
    s.and_then(|v| {
        DateTime::parse_from_rfc3339(&v)
            .ok()
            .map(|dt| dt.with_timezone(&Utc))
    })
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
                    let metadata: Value = serde_json::from_str(&meta_str)
                        .unwrap_or(Value::Object(Default::default()));
                    EvidenceItem {
                        id: r.try_get("id").unwrap_or_default(),
                        artifact_id: r.try_get("artifact_id").unwrap_or_default(),
                        kind: r.try_get("kind").unwrap_or_default(),
                        url: r.try_get("url").unwrap_or_default(),
                        metadata,
                        created_at: str_to_ts(
                            &r.try_get::<String, _>("created_at").unwrap_or_default(),
                        ),
                        updated_at: str_to_ts(
                            &r.try_get::<String, _>("updated_at").unwrap_or_default(),
                        ),
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
            let meta_str = serde_json::to_string(&metadata).unwrap_or_else(|_| "{}".to_string());
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
                    start_date: str_to_ts(
                        &r.try_get::<String, _>("start_date").unwrap_or_default(),
                    ),
                    end_date: str_to_ts(&r.try_get::<String, _>("end_date").unwrap_or_default()),
                    status: r.try_get("status").unwrap_or_default(),
                    created_at: str_to_ts(
                        &r.try_get::<String, _>("created_at").unwrap_or_default(),
                    ),
                    updated_at: str_to_ts(
                        &r.try_get::<String, _>("updated_at").unwrap_or_default(),
                    ),
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
                    created_at: str_to_ts(
                        &r.try_get::<String, _>("created_at").unwrap_or_default(),
                    ),
                    updated_at: str_to_ts(
                        &r.try_get::<String, _>("updated_at").unwrap_or_default(),
                    ),
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
            let rows =
                sqlx::query("SELECT id, name, description, members FROM teams ORDER BY id ASC")
                    .fetch_all(&self.pool)
                    .await
                    .map_err(StoreError::from)?;

            Ok(rows
                .into_iter()
                .map(|r| {
                    let members_str: String =
                        r.try_get("members").unwrap_or_else(|_| "[]".to_string());
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

    fn get_benchmark_run(
        &self,
        run_id: String,
    ) -> BoxFuture<'_, StoreResult<Option<BenchmarkRun>>> {
        Box::pin(async move {
            let row = sqlx::query(
                "SELECT run_id, session_id, attempt_id, schema_version, replay_hash, \
                 outcome_sha256, key_id, signature_digest, status, metadata, created_at, updated_at \
                 FROM benchmark_runs WHERE run_id = ?1",
            )
            .bind(&run_id)
            .fetch_optional(&self.pool)
            .await
            .map_err(StoreError::from)?;
            Ok(row.map(row_to_benchmark_run))
        })
    }

    #[allow(clippy::too_many_arguments)]
    fn create_benchmark_run(
        &self,
        run_id: String,
        session_id: String,
        attempt_id: String,
        schema_version: String,
        replay_hash: String,
        outcome_sha256: String,
        key_id: String,
        signature_digest: String,
        status: String,
        metadata: Value,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<BenchmarkRun>> {
        Box::pin(async move {
            if let Some(existing) = self.get_benchmark_run(run_id.clone()).await? {
                if existing.replay_hash != replay_hash {
                    return Err(StoreError::Database(
                        "benchmark run_id already exists with a different replay_hash".to_string(),
                    ));
                }
                return Ok(existing);
            }

            let metadata_str =
                serde_json::to_string(&metadata).unwrap_or_else(|_| "{}".to_string());
            let now_str = ts_to_str(now);
            sqlx::query(
                "INSERT INTO benchmark_runs \
                 (run_id, session_id, attempt_id, schema_version, replay_hash, outcome_sha256, \
                  key_id, signature_digest, status, metadata, created_at, updated_at) \
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12) \
                 ON CONFLICT DO NOTHING",
            )
            .bind(&run_id)
            .bind(&session_id)
            .bind(&attempt_id)
            .bind(&schema_version)
            .bind(&replay_hash)
            .bind(&outcome_sha256)
            .bind(&key_id)
            .bind(&signature_digest)
            .bind(&status)
            .bind(&metadata_str)
            .bind(&now_str)
            .bind(&now_str)
            .execute(&self.pool)
            .await
            .map_err(StoreError::from)?;

            self.get_benchmark_run_by_replay_hash(replay_hash)
                .await?
                .ok_or_else(|| {
                    StoreError::Database("benchmark run insert returned no row".to_string())
                })
        })
    }

    // -----------------------------------------------------------------------
    // Problems (ITIL) — SQLite implementations
    // -----------------------------------------------------------------------

    fn list_problems(
        &self,
        project_id: String,
        status_filter: Option<String>,
    ) -> BoxFuture<'_, StoreResult<Vec<Problem>>> {
        Box::pin(async move {
            // Status filter is interpolated as a literal; the column whitelist
            // is constrained to a small enum validated server-side elsewhere.
            // For initial recovery we keep both branches explicit so the SQL
            // surface stays inspectable.
            let rows = match status_filter {
                Some(status) => {
                    sqlx::query(
                        "SELECT id, project_id, problem_number, title, description, status, \
                         resolution_type, category, sub_category, tags, impact_level, urgency, \
                         priority, rca_performed, root_cause_identified, workaround_available, \
                         permanent_fix_available, assigned_to, assigned_team, owner, known_error_id, \
                         created_at, updated_at, deleted_at \
                         FROM problems \
                         WHERE project_id = ?1 AND status = ?2 AND deleted_at IS NULL \
                         ORDER BY created_at DESC",
                    )
                    .bind(&project_id)
                    .bind(&status)
                    .fetch_all(&self.pool)
                    .await
                    .map_err(StoreError::from)?
                }
                None => {
                    sqlx::query(
                        "SELECT id, project_id, problem_number, title, description, status, \
                         resolution_type, category, sub_category, tags, impact_level, urgency, \
                         priority, rca_performed, root_cause_identified, workaround_available, \
                         permanent_fix_available, assigned_to, assigned_team, owner, known_error_id, \
                         created_at, updated_at, deleted_at \
                         FROM problems \
                         WHERE project_id = ?1 AND deleted_at IS NULL \
                         ORDER BY created_at DESC",
                    )
                    .bind(&project_id)
                    .fetch_all(&self.pool)
                    .await
                    .map_err(StoreError::from)?
                }
            };

            Ok(rows.into_iter().map(row_to_problem).collect())
        })
    }

    #[allow(clippy::too_many_arguments)]
    fn create_problem(
        &self,
        id: String,
        project_id: String,
        problem_number: String,
        title: String,
        description: Option<String>,
        status: String,
        resolution_type: Option<String>,
        category: Option<String>,
        sub_category: Option<String>,
        tags: Option<Value>,
        impact_level: String,
        urgency: String,
        priority: String,
        rca_performed: bool,
        root_cause_identified: bool,
        workaround_available: bool,
        permanent_fix_available: bool,
        assigned_to: Option<String>,
        assigned_team: Option<String>,
        owner: Option<String>,
        known_error_id: Option<String>,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<Problem>> {
        Box::pin(async move {
            let tags_str = tags
                .as_ref()
                .map(|v| serde_json::to_string(v).unwrap_or_else(|_| "null".to_string()));
            let now_str = ts_to_str(now);

            sqlx::query(
                "INSERT INTO problems (\
                 id, project_id, problem_number, title, description, status, resolution_type, \
                 category, sub_category, tags, impact_level, urgency, priority, rca_performed, \
                 root_cause_identified, workaround_available, permanent_fix_available, \
                 assigned_to, assigned_team, owner, known_error_id, created_at, updated_at, deleted_at\
                 ) VALUES (\
                 ?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13, ?14, ?15, ?16, ?17, ?18, ?19, \
                 ?20, ?21, ?22, ?23, NULL)",
            )
            .bind(&id)
            .bind(&project_id)
            .bind(&problem_number)
            .bind(&title)
            .bind(&description)
            .bind(&status)
            .bind(&resolution_type)
            .bind(&category)
            .bind(&sub_category)
            .bind(&tags_str)
            .bind(&impact_level)
            .bind(&urgency)
            .bind(&priority)
            .bind(rca_performed)
            .bind(root_cause_identified)
            .bind(workaround_available)
            .bind(permanent_fix_available)
            .bind(&assigned_to)
            .bind(&assigned_team)
            .bind(&owner)
            .bind(&known_error_id)
            .bind(&now_str)
            .bind(&now_str)
            .execute(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(Problem {
                id,
                project_id,
                problem_number,
                title,
                description,
                status,
                resolution_type,
                category,
                sub_category,
                tags,
                impact_level,
                urgency,
                priority,
                rca_performed,
                root_cause_identified,
                workaround_available,
                permanent_fix_available,
                assigned_to,
                assigned_team,
                owner,
                known_error_id,
                created_at: now,
                updated_at: now,
                deleted_at: None,
            })
        })
    }

    fn count_problems(&self, project_id: String) -> BoxFuture<'_, StoreResult<i64>> {
        Box::pin(async move {
            let row = sqlx::query(
                "SELECT COUNT(*) AS cnt FROM problems \
                 WHERE project_id = ?1 AND deleted_at IS NULL",
            )
            .bind(&project_id)
            .fetch_one(&self.pool)
            .await
            .map_err(StoreError::from)?;
            let count: i64 = row.try_get("cnt").unwrap_or(0);
            Ok(count)
        })
    }
}

// -----------------------------------------------------------------------
// Row → Problem mapper for SqliteStore (shared column decode logic)
// -----------------------------------------------------------------------
fn row_to_problem(r: sqlx::sqlite::SqliteRow) -> Problem {
    let tags_str: Option<String> = r.try_get("tags").ok().flatten();
    let tags: Option<Value> = tags_str.and_then(|s| serde_json::from_str(&s).ok());

    Problem {
        id: r.try_get("id").unwrap_or_default(),
        project_id: r.try_get("project_id").unwrap_or_default(),
        problem_number: r.try_get("problem_number").unwrap_or_default(),
        title: r.try_get("title").unwrap_or_default(),
        description: r.try_get("description").ok().flatten(),
        status: r.try_get("status").unwrap_or_default(),
        resolution_type: r.try_get("resolution_type").ok().flatten(),
        category: r.try_get("category").ok().flatten(),
        sub_category: r.try_get("sub_category").ok().flatten(),
        tags,
        impact_level: r.try_get("impact_level").unwrap_or_default(),
        urgency: r.try_get("urgency").unwrap_or_default(),
        priority: r.try_get("priority").unwrap_or_default(),
        rca_performed: r.try_get("rca_performed").unwrap_or(false),
        root_cause_identified: r.try_get("root_cause_identified").unwrap_or(false),
        workaround_available: r.try_get("workaround_available").unwrap_or(false),
        permanent_fix_available: r.try_get("permanent_fix_available").unwrap_or(false),
        assigned_to: r.try_get("assigned_to").ok().flatten(),
        assigned_team: r.try_get("assigned_team").ok().flatten(),
        owner: r.try_get("owner").ok().flatten(),
        known_error_id: r.try_get("known_error_id").ok().flatten(),
        created_at: str_to_ts(&r.try_get::<String, _>("created_at").unwrap_or_default()),
        updated_at: str_to_ts(&r.try_get::<String, _>("updated_at").unwrap_or_default()),
        deleted_at: str_to_opt_ts(r.try_get::<Option<String>, _>("deleted_at").ok().flatten()),
    }
}

fn row_to_benchmark_run(r: sqlx::sqlite::SqliteRow) -> BenchmarkRun {
    let metadata_str: String = r.try_get("metadata").unwrap_or_else(|_| "{}".to_string());
    let metadata = serde_json::from_str(&metadata_str).unwrap_or(Value::Object(Default::default()));
    BenchmarkRun {
        run_id: r.try_get("run_id").unwrap_or_default(),
        session_id: r.try_get("session_id").unwrap_or_default(),
        attempt_id: r.try_get("attempt_id").unwrap_or_default(),
        schema_version: r.try_get("schema_version").unwrap_or_default(),
        replay_hash: r.try_get("replay_hash").unwrap_or_default(),
        outcome_sha256: r.try_get("outcome_sha256").unwrap_or_default(),
        key_id: r.try_get("key_id").unwrap_or_default(),
        signature_digest: r.try_get("signature_digest").unwrap_or_default(),
        status: r.try_get("status").unwrap_or_default(),
        metadata,
        created_at: str_to_ts(&r.try_get::<String, _>("created_at").unwrap_or_default()),
        updated_at: str_to_ts(&r.try_get::<String, _>("updated_at").unwrap_or_default()),
    }
}

// Keep the helpers visible to clippy even when no other code in this module
// currently uses them — they're shared with the PgStore port in a follow-up.
#[allow(dead_code)]
fn _keep_helpers() {
    let _ = opt_ts_to_str(None);
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::store::Store;

    async fn benchmark_store() -> SqliteStore {
        let pool = SqlitePool::connect("sqlite::memory:").await.unwrap();
        sqlx::migrate!("./migrations-sqlite")
            .run(&pool)
            .await
            .expect("apply SQLite benchmark-run migration");
        SqliteStore::new(pool)
    }

    #[tokio::test]
    async fn benchmark_run_create_is_idempotent_and_replay_hash_is_unique() {
        let store = benchmark_store().await;
        let now = Utc::now();
        let metadata = serde_json::json!({
            "schema_version": "2.0.0",
            "replay_hash": "a".repeat(64),
            "outcome_sha256": "b".repeat(64),
            "key_id": "producer-a",
            "signature_digest": "c".repeat(64)
        });
        let first = store
            .create_benchmark_run(
                "run_a".to_string(),
                "ses_a".to_string(),
                "att_a".to_string(),
                "2.0.0".to_string(),
                "a".repeat(64),
                "b".repeat(64),
                "producer-a".to_string(),
                "c".repeat(64),
                "passed".to_string(),
                metadata.clone(),
                now,
            )
            .await
            .unwrap();
        let second = store
            .create_benchmark_run(
                "run_a".to_string(),
                "ses-a-new".to_string(),
                "att-a-new".to_string(),
                "2.0.0".to_string(),
                "a".repeat(64),
                "d".repeat(64),
                "producer-b".to_string(),
                "e".repeat(64),
                "failed".to_string(),
                serde_json::json!({"changed": true}),
                now + chrono::Duration::seconds(1),
            )
            .await
            .unwrap();
        assert_eq!(first.run_id, second.run_id);
        assert_eq!(first.replay_hash, second.replay_hash);
        assert_eq!(first.metadata, metadata);
        assert_eq!(second.status, "passed");

        let loaded = store
            .get_benchmark_run("run_a".to_string())
            .await
            .unwrap()
            .expect("idempotent row");
        assert_eq!(loaded.signature_digest, "c".repeat(64));

        let conflicting_hash = store
            .create_benchmark_run(
                "run_a".to_string(),
                "ses_a".to_string(),
                "att_a".to_string(),
                "2.0.0".to_string(),
                "f".repeat(64),
                "b".repeat(64),
                "producer-a".to_string(),
                "c".repeat(64),
                "passed".to_string(),
                metadata,
                now,
            )
            .await;
        assert!(conflicting_hash.is_err());

        let same_replay = store
            .create_benchmark_run(
                "run_b".to_string(),
                "ses_b".to_string(),
                "att_b".to_string(),
                "2.0.0".to_string(),
                "a".repeat(64),
                "b".repeat(64),
                "producer-a".to_string(),
                "c".repeat(64),
                "passed".to_string(),
                serde_json::json!({}),
                now,
            )
            .await;
        let same_replay = same_replay.expect("same replay hash should be idempotent");
        assert_eq!(same_replay.run_id, "run_a");
        assert_eq!(same_replay.replay_hash, "a".repeat(64));
    }
}
