mod evidence;
mod items;
mod problems;
mod projects;
mod sprints;
mod stories;
mod swee;
mod trace_links;

/// SqliteStore — SQLite on-device/per-project backend implementing `Store`.
use chrono::{DateTime, Utc};
use serde_json::Value;
use sqlx::{Row, SqlitePool};

use tracera_server::product::{GeometryTruth, SpatialNode, SpatialRelation};
use crate::store::{
    BoxFuture, EvidenceItem, ListParams, Problem, ProjectSummary, Sprint, Store, StoreError,
    StoreResult, Story, TeamRow, TraceLink,
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
pub(super) fn ts_to_str(dt: DateTime<Utc>) -> String {
    dt.to_rfc3339()
}

pub(super) fn str_to_ts(s: &str) -> DateTime<Utc> {
    DateTime::parse_from_rfc3339(s)
        .map(|dt| dt.with_timezone(&Utc))
        .unwrap_or_else(|_| Utc::now())
}

#[allow(dead_code)]
pub(super) fn opt_ts_to_str(dt: Option<DateTime<Utc>>) -> Option<String> {
    dt.map(ts_to_str)
}

pub(super) fn str_to_opt_ts(s: Option<String>) -> Option<DateTime<Utc>> {
    s.and_then(|v| {
        DateTime::parse_from_rfc3339(&v)
            .ok()
            .map(|dt| dt.with_timezone(&Utc))
    })
}

impl Store for SqliteStore {
    fn search_items(
        &self,
        query: String,
        project_id: Option<String>,
        limit: i64,
        offset: i64,
    ) -> BoxFuture<'_, StoreResult<crate::item::ItemPage>> {
        Box::pin(items::search(&self.pool, query, project_id, limit, offset))
    }

    fn list_items(
        &self,
        filter: crate::item::ItemFilter,
        limit: i64,
        offset: i64,
    ) -> BoxFuture<'_, StoreResult<crate::item::ItemPage>> {
        Box::pin(items::list(&self.pool, filter, limit, offset))
    }
    fn get_item(&self, id: String) -> BoxFuture<'_, StoreResult<Option<crate::item::Item>>> {
        Box::pin(items::get(&self.pool, id))
    }
    fn create_item(&self, item: crate::item::Item) -> BoxFuture<'_, StoreResult<()>> {
        Box::pin(items::create(&self.pool, item))
    }
    fn list_evidence(&self) -> BoxFuture<'_, StoreResult<Vec<EvidenceItem>>> {
        evidence::list_evidence(&self.pool)
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
        evidence::create_evidence(&self.pool, id, artifact_id, kind, url, metadata, now)
    }

    fn list_sprints(&self) -> BoxFuture<'_, StoreResult<Vec<Sprint>>> {
        sprints::list_sprints(&self.pool)
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
        sprints::create_sprint(&self.pool, id, name, goal, start_date, end_date, now)
    }

    fn list_stories(&self) -> BoxFuture<'_, StoreResult<Vec<Story>>> {
        stories::list_stories(&self.pool)
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
        stories::create_story(
            &self.pool,
            id,
            sprint_id,
            title,
            description,
            status,
            story_points,
            now,
        )
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
        trace_links::create_trace_link(
            &self.pool,
            id,
            source_id,
            target_id,
            relationship,
            confidence,
            source,
            now,
        )
    }

    fn list_trace_links_for_artifact(
        &self,
        artifact_id: String,
    ) -> BoxFuture<'_, StoreResult<Vec<TraceLink>>> {
        trace_links::list_trace_links_for_artifact(&self.pool, artifact_id)
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

    fn list_projects(&self, params: ListParams) -> BoxFuture<'_, StoreResult<Vec<ProjectSummary>>> {
        projects::list_projects(&self.pool, params)
    }

    fn count_projects(&self) -> BoxFuture<'_, StoreResult<i64>> {
        projects::count_projects(&self.pool)
    }

    fn get_project(
        &self,
        project_id: String,
    ) -> BoxFuture<'_, StoreResult<Option<ProjectSummary>>> {
        projects::get_project(&self.pool, project_id)
    }

    fn count_evidence(&self) -> BoxFuture<'_, StoreResult<i64>> {
        evidence::count_evidence(&self.pool)
    }

    fn check_readiness(&self) -> BoxFuture<'_, StoreResult<()>> {
        Box::pin(async move {
            sqlx::query("SELECT 1")
                .execute(&self.pool)
                .await
                .map(|_| ())
                .map_err(StoreError::from)
        })
    }

    fn list_problems(
        &self,
        project_id: String,
        status_filter: Option<String>,
        params: ListParams,
    ) -> BoxFuture<'_, StoreResult<Vec<Problem>>> {
        problems::list_problems(&self.pool, project_id, status_filter, params)
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
        problems::create_problem(
            &self.pool,
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
            now,
        )
    }

    fn count_problems(&self, project_id: String) -> BoxFuture<'_, StoreResult<i64>> {
        problems::count_problems(&self.pool, project_id)
    }

    fn count_problems_filtered(
        &self,
        project_id: String,
        status_filter: Option<String>,
    ) -> BoxFuture<'_, StoreResult<i64>> {
        problems::count_problems_filtered(&self.pool, project_id, status_filter)
    }

    fn dashboard_status_counts(&self) -> BoxFuture<'_, StoreResult<Vec<(String, String, i64)>>> {
        problems::dashboard_status_counts(&self.pool)
    }

    fn create_swee_node(
        &self,
        node_type: String,
        label: String,
        metadata: Value,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<String>> {
        swee::create_swee_node(&self.pool, node_type, label, metadata, now)
    }

    #[allow(clippy::too_many_arguments)]
    fn create_swee_edge(
        &self,
        edge_type: String,
        source_id: String,
        target_id: String,
        confidence: f64,
        source: String,
        metadata: Value,
        now: DateTime<Utc>,
    ) -> BoxFuture<'_, StoreResult<String>> {
        swee::create_swee_edge(
            &self.pool, edge_type, source_id, target_id, confidence, source, metadata, now,
        )
    }

    fn product_spatial_slice(
        &self,
        product_id: String,
        baseline_revision: u64,
        max_nodes: usize,
        max_relations: usize,
    ) -> BoxFuture<'_, StoreResult<(Vec<SpatialNode>, Vec<SpatialRelation>, bool)>> {
        Box::pin(async move {
            let revision = i64::try_from(baseline_revision)
                .map_err(|_| StoreError::Database("baseline revision out of range".into()))?;
            let node_rows = sqlx::query("SELECT id, intent_kind, title FROM product_nodes WHERE product_id = ?1 AND baseline_revision = ?2 ORDER BY id LIMIT ?3")
                .bind(&product_id)
                .bind(revision)
                .bind((max_nodes.saturating_add(1).min(501)) as i64)
                .fetch_all(&self.pool)
                .await
                .map_err(StoreError::from)?;
            let node_truncated = node_rows.len() > max_nodes;
            let nodes: Vec<SpatialNode> = node_rows.into_iter().take(max_nodes)
                .map(|row| SpatialNode {
                    id: row.get("id"),
                    product_id: product_id.clone(),
                    baseline_revision,
                    kind: row.get("intent_kind"),
                    label: row.get("title"),
                    geometry_truth: GeometryTruth::Semantic,
                    geometry_source_ref: None,
                }).collect();
            let visible: std::collections::HashSet<&str> =
                nodes.iter().map(|node| node.id.as_str()).collect();
            let edge_rows = sqlx::query("SELECT e.id, e.source_id, e.target_id, e.edge_type FROM product_edges e JOIN product_nodes s ON e.source_id=s.id JOIN product_nodes t ON e.target_id=t.id WHERE s.product_id=?1 AND t.product_id=?1 AND s.baseline_revision=?2 AND t.baseline_revision=?2 ORDER BY e.id LIMIT ?3")
                .bind(&product_id)
                .bind(revision)
                .bind((max_relations.saturating_add(1).min(1501)) as i64)
                .fetch_all(&self.pool)
                .await
                .map_err(StoreError::from)?;
            let edge_truncated = edge_rows.len() > max_relations;
            let mut clipped_relations = false;
            let mut relations = Vec::new();
            for row in edge_rows.into_iter().take(max_relations) {
                let source_id: String = row.get("source_id");
                let target_id: String = row.get("target_id");
                if !visible.contains(source_id.as_str()) || !visible.contains(target_id.as_str()) {
                    clipped_relations = true;
                    continue;
                }
                let edge_id: i64 = row.get("id");
                relations.push(SpatialRelation {
                    id: edge_id.to_string(),
                    source_id,
                    target_id,
                    kind: row.get("edge_type"),
                    source_ref: None,
                });
            }
            Ok((nodes, relations, !node_truncated && !edge_truncated && !clipped_relations))
        })
    }

    fn list_swee_nodes(&self, node_type: Option<String>) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
        swee::list_swee_nodes(&self.pool, node_type)
    }

    fn list_swee_edges(&self, edge_type: Option<String>) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
        swee::list_swee_edges(&self.pool, edge_type)
    }

    fn get_swee_node(&self, id: String) -> BoxFuture<'_, StoreResult<Option<Value>>> {
        swee::get_swee_node(&self.pool, id)
    }

    fn get_swee_neighbors(
        &self,
        id: String,
        direction: String,
    ) -> BoxFuture<'_, StoreResult<Vec<Value>>> {
        swee::get_swee_neighbors(&self.pool, id, direction)
    }
}
