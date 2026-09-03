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
use std::time::Duration;
use tokio::time::timeout;

use crate::store::{
    BoxFuture, EvidenceItem, ListParams, Problem, ProjectSummary, Sprint, Store, StoreError,
    StoreResult, Story, TeamRow, TraceLink,
};

#[derive(Clone)]
pub struct PgStore {
    pub pool: PgPool,
}

const READINESS_TIMEOUT: Duration = Duration::from_secs(1);

impl PgStore {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
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

    fn list_trace_links_for_artifact(
        &self,
        artifact_id: String,
    ) -> BoxFuture<'_, StoreResult<Vec<TraceLink>>> {
        Box::pin(async move {
            let rows = sqlx::query(
                "SELECT id, source_id, target_id, relationship, confidence, source, created_at, updated_at \
                 FROM trace_links \
                 WHERE source_id = $1 OR target_id = $1 \
                 ORDER BY created_at ASC, id ASC",
            )
            .bind(&artifact_id)
            .fetch_all(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(rows.into_iter().map(pg_row_to_trace_link).collect())
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

    fn list_projects(&self, params: ListParams) -> BoxFuture<'_, StoreResult<Vec<ProjectSummary>>> {
        Box::pin(async move {
            let rows = sqlx::query(
                "SELECT project_id::text AS project_id,
                        COUNT(*)::bigint AS problem_count,
                        MIN(created_at) AS created_at,
                        MAX(updated_at) AS updated_at
                 FROM problems
                 WHERE deleted_at IS NULL
                 GROUP BY project_id
                 ORDER BY MAX(updated_at) DESC, project_id ASC LIMIT $1 OFFSET $2",
            )
            .bind(params.page_size as i64)
            .bind(params.offset() as i64)
            .fetch_all(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(rows
                .into_iter()
                .map(|row| {
                    let id: String = row.try_get("project_id").unwrap_or_default();
                    let created_at = row.try_get("created_at").unwrap_or_else(|_| Utc::now());
                    let updated_at = row.try_get("updated_at").unwrap_or_else(|_| Utc::now());
                    ProjectSummary {
                        name: format!("Project {id}"),
                        description: Some("Derived from persisted problem records".to_string()),
                        metadata: Value::Object(Default::default()),
                        id,
                        created_at,
                        updated_at,
                        problem_count: row.try_get("problem_count").unwrap_or_default(),
                    }
                })
                .collect())
        })
    }

    fn count_projects(&self) -> BoxFuture<'_, StoreResult<i64>> {
        Box::pin(async move {
            let row = sqlx::query(
                "SELECT COUNT(DISTINCT project_id) AS cnt FROM problems WHERE deleted_at IS NULL",
            )
            .fetch_one(&self.pool)
            .await
            .map_err(StoreError::from)?;
            Ok(row.try_get("cnt").unwrap_or(0))
        })
    }

    fn get_project(
        &self,
        project_id: String,
    ) -> BoxFuture<'_, StoreResult<Option<ProjectSummary>>> {
        Box::pin(async move {
            let rows = sqlx::query(
                "SELECT project_id::text AS project_id,
                        COUNT(*)::bigint AS problem_count,
                        MIN(created_at) AS created_at,
                        MAX(updated_at) AS updated_at
                 FROM problems
                 WHERE deleted_at IS NULL AND project_id = $1
                 GROUP BY project_id",
            )
            .bind(&project_id)
            .fetch_all(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(rows.into_iter().next().map(|row| ProjectSummary {
                id: project_id.clone(),
                name: format!("Project {project_id}"),
                description: Some("Derived from persisted problem records".to_string()),
                metadata: Value::Object(Default::default()),
                problem_count: row.try_get("problem_count").unwrap_or_default(),
                created_at: row.try_get("created_at").unwrap_or_else(|_| Utc::now()),
                updated_at: row.try_get("updated_at").unwrap_or_else(|_| Utc::now()),
            }))
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

    fn check_readiness(&self) -> BoxFuture<'_, StoreResult<()>> {
        Box::pin(async move {
            timeout(
                READINESS_TIMEOUT,
                sqlx::query("SELECT 1").execute(&self.pool),
            )
            .await
            .map_err(|_| StoreError::Database("readiness probe timed out".to_string()))?
            .map(|_| ())
            .map_err(StoreError::from)
        })
    }

    // -----------------------------------------------------------------------
    // Problems (ITIL) — Postgres implementations
    // -----------------------------------------------------------------------

    fn list_problems(
        &self,
        project_id: String,
        status_filter: Option<String>,
        params: ListParams,
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
                         WHERE project_id = $1 AND status = $2 AND deleted_at IS NULL \
                         ORDER BY created_at DESC, id ASC LIMIT $3 OFFSET $4",
                    )
                    .bind(&project_id)
                    .bind(&status)
                    .bind(params.page_size as i64)
                    .bind(params.offset() as i64)
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
                         WHERE project_id = $1 AND deleted_at IS NULL \
                         ORDER BY created_at DESC, id ASC LIMIT $2 OFFSET $3",
                    )
                    .bind(&project_id)
                    .bind(params.page_size as i64)
                    .bind(params.offset() as i64)
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
                 $1, $2, $3, $4, $5, $6, $7, $8, $9, $10::jsonb, $11, $12, $13, $14, $15, \
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
                 WHERE project_id = $1 AND deleted_at IS NULL",
            )
            .bind(&project_id)
            .fetch_one(&self.pool)
            .await
            .map_err(StoreError::from)?;
            let count: i64 = row.try_get("cnt").unwrap_or(0);
            Ok(count)
        })
    }

    fn count_problems_filtered(
        &self,
        project_id: String,
        status_filter: Option<String>,
    ) -> BoxFuture<'_, StoreResult<i64>> {
        Box::pin(async move {
            let (query, status) = match status_filter {
                Some(_) => ("SELECT COUNT(*) AS cnt FROM problems WHERE project_id = $1 AND status = $2 AND deleted_at IS NULL", status_filter),
                None => ("SELECT COUNT(*) AS cnt FROM problems WHERE project_id = $1 AND deleted_at IS NULL", None),
            };
            let mut request = sqlx::query(query).bind(&project_id);
            if let Some(status) = status {
                request = request.bind(status);
            }
            let row = request
                .fetch_one(&self.pool)
                .await
                .map_err(StoreError::from)?;
            Ok(row.try_get("cnt").unwrap_or(0))
        })
    }

    // -----------------------------------------------------------------------
    // SWEE Graph operations — Postgres implementations
    // -----------------------------------------------------------------------

    fn create_swee_node(
        &self,
        node_type: String,
        label: String,
        metadata: Value,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<String>> {
        Box::pin(async move {
            let row: (i64,) = sqlx::query_as(
                "INSERT INTO swee_nodes (type, name, metadata, created_at, updated_at) \
                 VALUES ($1, $2, $3::jsonb, $4, $5) \
                 RETURNING id",
            )
            .bind(&node_type)
            .bind(&label)
            .bind(&metadata)
            .bind(now)
            .bind(now)
            .fetch_one(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(row.0.to_string())
        })
    }

    #[allow(clippy::too_many_arguments)]
    fn create_swee_edge(
        &self,
        edge_type: String,
        source_id: String,
        target_id: String,
        confidence: f64,
        _source: String,
        metadata: Value,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<String>> {
        Box::pin(async move {
            let src_id: i64 = source_id.parse().unwrap_or(0);
            let tgt_id: i64 = target_id.parse().unwrap_or(0);

            let row: (i64,) = sqlx::query_as(
                "INSERT INTO swee_edges (source_id, target_id, type, weight, metadata, created_at) \
                 VALUES ($1, $2, $3, $4, $5::jsonb, $6) \
                 RETURNING id",
            )
            .bind(src_id)
            .bind(tgt_id)
            .bind(&edge_type)
            .bind(confidence)
            .bind(&metadata)
            .bind(now)
            .fetch_one(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(row.0.to_string())
        })
    }

    fn list_swee_nodes(
        &self,
        node_type: Option<String>,
    ) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
        Box::pin(async move {
            let rows = match node_type {
                Some(ref nt) => {
                    sqlx::query(
                        "SELECT id, type, name, metadata::text, created_at, updated_at \
                         FROM swee_nodes WHERE type = $1 ORDER BY created_at DESC",
                    )
                    .bind(nt)
                    .fetch_all(&self.pool)
                    .await
                    .map_err(StoreError::from)?
                }
                None => {
                    sqlx::query(
                        "SELECT id, type, name, metadata::text, created_at, updated_at \
                         FROM swee_nodes ORDER BY created_at DESC",
                    )
                    .fetch_all(&self.pool)
                    .await
                    .map_err(StoreError::from)?
                }
            };

            Ok(rows
                .into_iter()
                .map(|r| {
                    let meta_str: String = r.try_get("metadata").unwrap_or_default();
                    let metadata: Value = serde_json::from_str(&meta_str)
                        .unwrap_or(Value::Object(Default::default()));
                    let id: i64 = r.try_get("id").unwrap_or_default();
                    serde_json::json!({
                        "id": id.to_string(),
                        "node_type": r.try_get::<String, _>("type").unwrap_or_default(),
                        "label": r.try_get::<String, _>("name").unwrap_or_default(),
                        "metadata": metadata,
                        "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
                        "updated_at": r.try_get::<String, _>("updated_at").unwrap_or_default(),
                    })
                })
                .collect())
        })
    }

    fn list_swee_edges(
        &self,
        edge_type: Option<String>,
    ) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
        Box::pin(async move {
            let rows = match edge_type {
                Some(ref et) => {
                    sqlx::query(
                        "SELECT id, source_id, target_id, type, weight, metadata::text, created_at \
                         FROM swee_edges WHERE type = $1 ORDER BY created_at DESC",
                    )
                    .bind(et)
                    .fetch_all(&self.pool)
                    .await
                    .map_err(StoreError::from)?
                }
                None => {
                    sqlx::query(
                        "SELECT id, source_id, target_id, type, weight, metadata::text, created_at \
                         FROM swee_edges ORDER BY created_at DESC",
                    )
                    .fetch_all(&self.pool)
                    .await
                    .map_err(StoreError::from)?
                }
            };

            Ok(rows
                .into_iter()
                .map(|r| {
                    let meta_str: String = r.try_get("metadata").unwrap_or_default();
                    let metadata: Value = serde_json::from_str(&meta_str)
                        .unwrap_or(Value::Object(Default::default()));
                    let id: i64 = r.try_get("id").unwrap_or_default();
                    let src_id: i64 = r.try_get("source_id").unwrap_or_default();
                    let tgt_id: i64 = r.try_get("target_id").unwrap_or_default();
                    serde_json::json!({
                        "id": id.to_string(),
                        "source_id": src_id.to_string(),
                        "target_id": tgt_id.to_string(),
                        "edge_type": r.try_get::<String, _>("type").unwrap_or_default(),
                        "weight": r.try_get::<f64, _>("weight").unwrap_or(1.0),
                        "metadata": metadata,
                        "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
                    })
                })
                .collect())
        })
    }

    fn get_swee_node(&self, id: String) -> BoxFuture<'_, StoreResult<Option<Value>>> {
        Box::pin(async move {
            let row = sqlx::query(
                "SELECT id, type, name, metadata::text, created_at, updated_at \
                 FROM swee_nodes WHERE id = $1",
            )
            .bind(&id)
            .fetch_optional(&self.pool)
            .await
            .map_err(StoreError::from)?;

            Ok(row.map(|r| {
                let meta_str: String = r.try_get("metadata").unwrap_or_default();
                let metadata: Value = serde_json::from_str(&meta_str)
                    .unwrap_or(Value::Object(Default::default()));
                let db_id: i64 = r.try_get("id").unwrap_or_default();
                serde_json::json!({
                    "id": db_id.to_string(),
                    "node_type": r.try_get::<String, _>("type").unwrap_or_default(),
                    "label": r.try_get::<String, _>("name").unwrap_or_default(),
                    "metadata": metadata,
                    "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
                    "updated_at": r.try_get::<String, _>("updated_at").unwrap_or_default(),
                })
            }))
        })
    }

    fn get_swee_neighbors(
        &self,
        id: String,
        direction: String,
    ) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
        Box::pin(async move {
            let rows = match direction.as_str() {
                "forward" => {
                    sqlx::query(
                        "SELECT e.id, e.source_id, e.target_id, e.type, e.weight, e.metadata::text, e.created_at \
                         FROM swee_edges e WHERE e.source_id = $1::bigint ORDER BY e.created_at DESC",
                    )
                    .bind(&id)
                    .fetch_all(&self.pool)
                    .await
                    .map_err(StoreError::from)?
                }
                "reverse" => {
                    sqlx::query(
                        "SELECT e.id, e.source_id, e.target_id, e.type, e.weight, e.metadata::text, e.created_at \
                         FROM swee_edges e WHERE e.target_id = $1::bigint ORDER BY e.created_at DESC",
                    )
                    .bind(&id)
                    .fetch_all(&self.pool)
                    .await
                    .map_err(StoreError::from)?
                }
                _ => {
                    // "both" or any other value
                    sqlx::query(
                        "SELECT e.id, e.source_id, e.target_id, e.type, e.weight, e.metadata::text, e.created_at \
                         FROM swee_edges e WHERE e.source_id = $1::bigint OR e.target_id = $1::bigint ORDER BY e.created_at DESC",
                    )
                    .bind(&id)
                    .fetch_all(&self.pool)
                    .await
                    .map_err(StoreError::from)?
                }
            };

            Ok(rows
                .into_iter()
                .map(|r| {
                    let meta_str: String = r.try_get("metadata").unwrap_or_default();
                    let metadata: Value = serde_json::from_str(&meta_str)
                        .unwrap_or(Value::Object(Default::default()));
                    let eid: i64 = r.try_get("id").unwrap_or_default();
                    let src_id: i64 = r.try_get("source_id").unwrap_or_default();
                    let tgt_id: i64 = r.try_get("target_id").unwrap_or_default();
                    serde_json::json!({
                        "id": eid.to_string(),
                        "source_id": src_id.to_string(),
                        "target_id": tgt_id.to_string(),
                        "edge_type": r.try_get::<String, _>("type").unwrap_or_default(),
                        "weight": r.try_get::<f64, _>("weight").unwrap_or(1.0),
                        "metadata": metadata,
                        "created_at": r.try_get::<String, _>("created_at").unwrap_or_default(),
                    })
                })
                .collect())
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

fn pg_row_to_trace_link(r: sqlx::postgres::PgRow) -> TraceLink {
    TraceLink {
        id: r.try_get("id").unwrap_or_default(),
        source_id: r.try_get("source_id").unwrap_or_default(),
        target_id: r.try_get("target_id").unwrap_or_default(),
        relationship: r.try_get("relationship").unwrap_or_default(),
        confidence: r.try_get("confidence").unwrap_or_default(),
        source: r.try_get("source").unwrap_or_default(),
        created_at: r.try_get("created_at").unwrap_or_else(|_| Utc::now()),
        updated_at: r.try_get("updated_at").unwrap_or_else(|_| Utc::now()),
    }
}
