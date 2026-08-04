/// PgStore — Postgres backend implementing `Store`.
///
/// Uses runtime `sqlx::query()` (not macros) so `env -u DATABASE_URL cargo build`
/// stays green. There is no pre-existing `.sqlx/` offline cache on this branch;
/// adding one would require a live Postgres for `cargo sqlx prepare`.
/// The runtime query path is equally correct at runtime and avoids the two-DB
/// prepare problem noted in the task specification.
use chrono::{DateTime, Utc};
use serde_json::Value;
use sqlx::{PgPool, Row};

use crate::store::{
    BenchmarkRun, BoxFuture, EvidenceItem, Problem, Sprint, Store, StoreError, StoreResult, Story,
    TeamRow, TraceLink,
};

#[derive(Clone)]
pub struct PgStore {
    pub pool: PgPool,
}

impl PgStore {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    fn get_benchmark_run_by_replay_hash(
        &self,
        replay_hash: String,
    ) -> BoxFuture<'_, StoreResult<Option<BenchmarkRun>>> {
        Box::pin(async move {
            let row = sqlx::query("SELECT run_id, session_id, attempt_id, schema_version, replay_hash, outcome_sha256, key_id, signature_digest, status, metadata::text, created_at, updated_at FROM benchmark_runs WHERE replay_hash = $1")
            .bind(replay_hash)
            .fetch_optional(&self.pool)
            .await
            .map_err(StoreError::from)?;
            Ok(row.map(pg_row_to_benchmark_run))
        })
    }
}

impl Store for PgStore {
    fn list_evidence(&self) -> BoxFuture<'_, StoreResult<Vec<EvidenceItem>>> {
        Box::pin(async move {
            let rows = sqlx::query(
                "SELECT id, artifact_id, kind, url, metadata::text, \
                 created_at, updated_at \
                 FROM evidence ORDER BY created_at ASC",
            )
            .fetch_all(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(rows
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
                        created_at: r.try_get("created_at").unwrap_or_else(|_| Utc::now()),
                        updated_at: r.try_get("updated_at").unwrap_or_else(|_| Utc::now()),
                    }
                })
                .collect())
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
            sqlx::query(
                "INSERT INTO evidence \
                 (id, artifact_id, kind, url, metadata, created_at, updated_at) \
                 VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7)",
            )
            .bind(&id)
            .bind(&artifact_id)
            .bind(&kind)
            .bind(&url)
            .bind(&meta_str)
            .bind(now)
            .bind(now)
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
                "SELECT id, name, goal, start_date, end_date, status, created_at, updated_at \
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
                    start_date: r.try_get("start_date").unwrap_or_else(|_| Utc::now()),
                    end_date: r.try_get("end_date").unwrap_or_else(|_| Utc::now()),
                    status: r.try_get("status").unwrap_or_default(),
                    created_at: r.try_get("created_at").unwrap_or_else(|_| Utc::now()),
                    updated_at: r.try_get("updated_at").unwrap_or_else(|_| Utc::now()),
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
                "SELECT id, sprint_id, title, description, status, story_points, \
                 created_at, updated_at FROM stories ORDER BY created_at ASC",
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
                    created_at: r.try_get("created_at").unwrap_or_else(|_| Utc::now()),
                    updated_at: r.try_get("updated_at").unwrap_or_else(|_| Utc::now()),
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
            sqlx::query(
                "INSERT INTO trace_links \
                 (id, source_id, target_id, relationship, confidence, source, created_at, updated_at) \
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            )
            .bind(&id)
            .bind(&source_id)
            .bind(&target_id)
            .bind(&relationship)
            .bind(confidence)
            .bind(&source)
            .bind(now)
            .bind(now)
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
                    // members is TEXT[] in Postgres; sqlx decodes it as Vec<String>
                    let members: Vec<String> = r.try_get("members").unwrap_or_default();
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
            let row = sqlx::query("SELECT COUNT(*) AS cnt FROM evidence")
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
                 outcome_sha256, key_id, signature_digest, status, metadata::text, created_at, updated_at \
                 FROM benchmark_runs WHERE run_id = $1",
            )
            .bind(&run_id)
            .fetch_optional(&self.pool)
            .await
            .map_err(StoreError::from)?;
            Ok(row.map(pg_row_to_benchmark_run))
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
            sqlx::query(
                "INSERT INTO benchmark_runs \
                 (run_id, session_id, attempt_id, schema_version, replay_hash, outcome_sha256, \
                  key_id, signature_digest, status, metadata, created_at, updated_at) \
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10::jsonb, $11, $12) \
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
            .bind(now)
            .bind(now)
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
    // Problems (ITIL) — Postgres implementations
    // -----------------------------------------------------------------------

    fn list_problems(
        &self,
        project_id: String,
        status_filter: Option<String>,
    ) -> BoxFuture<'_, StoreResult<Vec<Problem>>> {
        Box::pin(async move {
            let rows = match status_filter {
                Some(status) => {
                    sqlx::query(
                        "SELECT id, project_id::text, problem_number, title, description, status, \
                         resolution_type, category, sub_category, tags::text, impact_level, urgency, \
                         priority, rca_performed, root_cause_identified, workaround_available, \
                         permanent_fix_available, assigned_to, assigned_team, owner, known_error_id, \
                         created_at, updated_at, deleted_at \
                         FROM problems \
                         WHERE project_id = $1::uuid AND status = $2 AND deleted_at IS NULL \
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
                        "SELECT id, project_id::text, problem_number, title, description, status, \
                         resolution_type, category, sub_category, tags::text, impact_level, urgency, \
                         priority, rca_performed, root_cause_identified, workaround_available, \
                         permanent_fix_available, assigned_to, assigned_team, owner, known_error_id, \
                         created_at, updated_at, deleted_at \
                         FROM problems \
                         WHERE project_id = $1::uuid AND deleted_at IS NULL \
                         ORDER BY created_at DESC",
                    )
                    .bind(&project_id)
                    .fetch_all(&self.pool)
                    .await
                    .map_err(StoreError::from)?
                }
            };

            Ok(rows.into_iter().map(pg_row_to_problem).collect())
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
            let tags_jsonb = tags.clone().unwrap_or(Value::Null);

            sqlx::query(
                "INSERT INTO problems (\
                 id, project_id, problem_number, title, description, status, resolution_type, \
                 category, sub_category, tags, impact_level, urgency, priority, rca_performed, \
                 root_cause_identified, workaround_available, permanent_fix_available, \
                 assigned_to, assigned_team, owner, known_error_id, created_at, updated_at, deleted_at\
                 ) VALUES (\
                 $1, $2::uuid, $3, $4, $5, $6, $7, $8, $9, $10::jsonb, $11, $12, $13, $14, $15, \
                 $16, $17, $18, $19, $20, $21, $22, $23, NULL)",
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
            .bind(&tags_jsonb)
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
            .bind(now)
            .bind(now)
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
                 WHERE project_id = $1::uuid AND deleted_at IS NULL",
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
// Row → Problem mapper for PgStore
// -----------------------------------------------------------------------
fn pg_row_to_problem(r: sqlx::postgres::PgRow) -> Problem {
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
        created_at: r.try_get("created_at").unwrap_or_else(|_| Utc::now()),
        updated_at: r.try_get("updated_at").unwrap_or_else(|_| Utc::now()),
        deleted_at: r.try_get("deleted_at").ok().flatten(),
    }
}

fn pg_row_to_benchmark_run(r: sqlx::postgres::PgRow) -> BenchmarkRun {
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
        created_at: r.try_get("created_at").unwrap_or_else(|_| Utc::now()),
        updated_at: r.try_get("updated_at").unwrap_or_else(|_| Utc::now()),
    }
}
