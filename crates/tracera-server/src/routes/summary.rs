//! Shared summaries use persisted project/problem records, matching Projects.
use crate::handlers::dashboard::{DashboardProjectStatsResponse, DashboardSummaryResponse};
use crate::{AppState, ErrorResponse};
use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
fn failure() -> (StatusCode, Json<ErrorResponse>) {
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(ErrorResponse {
            error: "project_summary_failed",
        }),
    )
}
pub(crate) async fn dashboard_summary(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<DashboardSummaryResponse>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    use std::collections::BTreeMap;

    let mut projects = Vec::new();
    let mut page = 1;
    loop {
        let batch = state
            .store
            .list_projects(crate::store::ListParams {
                page,
                page_size: crate::store::MAX_PAGE_SIZE,
            })
            .await
            .map_err(|_| failure())?;
        let complete = batch.len() < crate::store::MAX_PAGE_SIZE as usize;
        projects.extend(batch);
        if complete {
            break;
        }
        page += 1;
    }

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
                type_counts: BTreeMap::from([("problem".to_owned(), project.problem_count)]),
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
        type_distribution: BTreeMap::from([("problem".to_owned(), total_item_count)]),
    }))
}

pub(crate) async fn project_summary(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> Result<Json<DashboardProjectStatsResponse>, (StatusCode, Json<ErrorResponse>)> {
    let summary = dashboard_summary(State(state)).await?.0;
    summary
        .per_project
        .into_iter()
        .find(|(key, _)| key == &id)
        .map(|(_, stats)| Json(stats))
        .ok_or((
            StatusCode::NOT_FOUND,
            Json(ErrorResponse {
                error: "project_not_found",
            }),
        ))
}
#[cfg(test)]
#[path = "summary_tests.rs"]
mod tests;

#[path = "links.rs"]
mod links;
pub(crate) fn routes() -> axum::Router<AppState> {
    use axum::routing::{any, get};
    axum::Router::new()
        .route("/api/v1/links", any(links::unavailable))
        .route("/api/v1/links/{id}", any(links::unavailable))
        .route(
            "/api/v1/projects/{project_id}/links",
            any(links::unavailable),
        )
        .route(
            "/api/v1/projects/{project_id}/summary",
            get(project_summary),
        )
}
