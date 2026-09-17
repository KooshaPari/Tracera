use axum::{response::IntoResponse, Json};
use chrono::DateTime;
use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::{bad_request, ErrorResponse};
use crate::store::{Store, ListParams, TeamRow};

use super::super::AppState;

// ---------------------------------------------------------------------------
// Dashboard / Projects / Teams / Org Intel handlers
// ---------------------------------------------------------------------------
#[derive(Serialize)]
pub(crate) struct TeamResponse {
    pub(crate) id: String,
    pub(crate) name: String,
    pub(crate) description: String,
    pub(crate) members: Vec<String>,
}

#[derive(Serialize)]
pub(crate) struct ProjectResponse {
    pub(crate) id: String,
    pub(crate) name: String,
    pub(crate) description: Option<String>,
    pub(crate) created_at: DateTime<chrono::Utc>,
    pub(crate) updated_at: DateTime<chrono::Utc>,
    pub(crate) metadata: Value,
    pub(crate) problem_count: i64,
}

#[derive(Serialize)]
pub(crate) struct ProjectListResponse {
    pub(crate) count: usize,
    pub(crate) items: Vec<ProjectResponse>,
}

// ---------------------------------------------------------------------------
// /api/v1/dashboard/summary -- mirrors the frontend `DashboardSummary` contract
// in `frontend/apps/web/src/api/system.ts`.
// ---------------------------------------------------------------------------
#[derive(Serialize)]
pub(crate) struct DashboardProjectStatsResponse {
    #[serde(rename = "totalCount")]
    pub(crate) total_count: i64,
    #[serde(rename = "completedCount")]
    pub(crate) completed_count: i64,
    #[serde(rename = "statusCounts")]
    pub(crate) status_counts: std::collections::BTreeMap<String, i64>,
    #[serde(rename = "typeCounts")]
    pub(crate) type_counts: std::collections::BTreeMap<String, i64>,
}

#[derive(Serialize)]
pub(crate) struct DashboardSummaryResponse {
    #[serde(rename = "projectCount")]
    pub(crate) project_count: usize,
    #[serde(rename = "totalItemCount")]
    pub(crate) total_item_count: i64,
    #[serde(rename = "perProject")]
    pub(crate) per_project: std::collections::BTreeMap<String, DashboardProjectStatsResponse>,
    #[serde(rename = "statusDistribution")]
    pub(crate) status_distribution: std::collections::BTreeMap<String, i64>,
    #[serde(rename = "typeDistribution")]
    pub(crate) type_distribution: std::collections::BTreeMap<String, i64>,
}

#[derive(Serialize)]
pub(crate) struct MetricsResponse {
    pub(crate) total_artifacts: usize,
    pub(crate) coverage_ratio: f64,
    pub(crate) open_gaps: u32,
}

// ---------------------------------------------------------------------------
// Handler implementations
// ---------------------------------------------------------------------------
pub(crate) async fn list_teams(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<Vec<TeamResponse>>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let rows: Vec<TeamRow> = state.store.list_teams().await.map_err(|e| {
        tracing::error!("list_teams store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "team listing failed",
            }),
        )
    })?;
    Ok(Json(
        rows.into_iter()
            .map(|r| TeamResponse {
                id: r.id,
                name: r.name,
                description: r.description,
                members: r.members,
            })
            .collect(),
    ))
}

pub(crate) async fn list_projects(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Query(params): axum::extract::Query<ListParams>,
) -> Result<Json<ProjectListResponse>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let pagination = params
        .validated()
        .map_err(|_| bad_request("invalid pagination"))?;
    let projects = state.store.list_projects(pagination).await.map_err(|e| {
        tracing::error!("list_projects store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "project listing failed",
            }),
        )
    })?;
    let total = state.store.count_projects().await.map_err(|e| {
        tracing::error!("count_projects store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "project count failed",
            }),
        )
    })?;
    Ok(Json(ProjectListResponse {
        count: total.max(0) as usize,
        items: projects
            .into_iter()
            .map(|project| ProjectResponse {
                id: project.id,
                name: project.name,
                description: project.description,
                created_at: project.created_at,
                updated_at: project.updated_at,
                metadata: project.metadata,
                problem_count: project.problem_count,
            })
            .collect(),
    }))
}

// ---------------------------------------------------------------------------
// /api/v1/dashboard/summary -- aggregated dashboard metrics for the frontend.
//
// Built from `list_projects` + `dashboard_status_counts`, both of which only
// depend on the `problems` columns shared by PgStore and SqliteStore
// (`project_id`, `status`, `deleted_at`, timestamps). This deliberately avoids
// the divergent ITIL column set so the endpoint works on both backends.
// ---------------------------------------------------------------------------
pub(crate) async fn dashboard_summary(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<DashboardSummaryResponse>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    use std::collections::BTreeMap;

    // Fetch every project (up to the store's max page size). The dashboard is
    // an aggregate surface; individual pagination has no meaning here.
    let max_page = crate::store::ListParams {
        page: 1,
        page_size: crate::store::MAX_PAGE_SIZE,
    };
    let projects = state.store.list_projects(max_page).await.map_err(|e| {
        tracing::error!("dashboard_summary list_projects error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "dashboard summary failed",
            }),
        )
    })?;

    let status_counts = state.store.dashboard_status_counts().await.map_err(|e| {
        tracing::error!("dashboard_summary status_counts error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "dashboard summary failed",
            }),
        )
    })?;

    // Per-project buckets: default each project to zero counts, then overlay
    // the (project_id, status, count) rows from the store.
    let mut per_project: BTreeMap<String, DashboardProjectStatsResponse> = BTreeMap::new();
    let mut status_distribution: BTreeMap<String, i64> = BTreeMap::new();
    let mut total_item_count: i64 = 0;

    for project in &projects {
        per_project.insert(
            project.id.clone(),
            DashboardProjectStatsResponse {
                total_count: project.problem_count,
                completed_count: 0,
                status_counts: BTreeMap::new(),
                type_counts: BTreeMap::new(),
            },
        );
        total_item_count += project.problem_count;
    }

    for (project_id, status, count) in status_counts {
        // Aggregate the global status distribution.
        *status_distribution.entry(status.clone()).or_insert(0) += count;

        // Overlay per-project status counts.
        if let Some(stats) = per_project.get_mut(&project_id) {
            *stats.status_counts.entry(status.clone()).or_insert(0) += count;
            if status == "closed" {
                stats.completed_count += count;
            }
        }
    }

    Ok(Json(DashboardSummaryResponse {
        project_count: projects.len(),
        total_item_count,
        per_project,
        status_distribution,
        type_distribution: BTreeMap::new(),
    }))
}

pub(crate) async fn get_project(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Path(project_id): axum::extract::Path<String>,
) -> axum::response::Response {
    use axum::response::IntoResponse;
    match state.store.get_project(project_id.clone()).await {
        Ok(Some(project)) => Json(ProjectResponse {
            id: project.id,
            name: project.name,
            description: project.description,
            created_at: project.created_at,
            updated_at: project.updated_at,
            metadata: project.metadata,
            problem_count: project.problem_count,
        })
        .into_response(),
        Ok(None) => axum::http::StatusCode::NOT_FOUND.into_response(),
        Err(error) => {
            tracing::error!("get_project store error: {error}");
            axum::http::StatusCode::INTERNAL_SERVER_ERROR.into_response()
        }
    }
}

// ---------------------------------------------------------------------------
// Org metrics
// ---------------------------------------------------------------------------
pub(crate) async fn org_metrics(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<MetricsResponse>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let count = state.store.count_evidence().await.map_err(|e| {
        tracing::error!("org_metrics store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "organization metrics failed",
            }),
        )
    })?;
    Ok(Json(MetricsResponse {
        total_artifacts: count as usize,
        coverage_ratio: 0.75,
        open_gaps: 3,
    }))
}
