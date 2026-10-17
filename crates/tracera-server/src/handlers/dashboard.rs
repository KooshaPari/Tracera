use axum::Json;
use chrono::DateTime;
use serde::Serialize;
use serde_json::Value;

use crate::store::{ListParams, TeamRow};
use crate::{bad_request, ErrorResponse};

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

#[path = "../routes/summary.rs"]
pub(crate) mod summary;
pub(crate) use summary::dashboard_summary;

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
// Evidence counts alone cannot establish organizational coverage or gap counts.
pub(crate) use crate::not_implemented::not_implemented as org_metrics;
