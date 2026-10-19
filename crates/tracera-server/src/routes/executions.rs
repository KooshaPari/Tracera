//! Unavailable executions operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/executions/{id}",
    "/api/v1/executions/{id}/advance",
    "/api/v1/executions/{id}/complete",
    "/api/v1/executions/{id}/start",
    "/api/v1/projects/{project_id}/executions",
    "/api/v1/projects/{project_id}/executions/{param6}",
    "/api/v1/projects/{project_id}/executions/{param6}/artifacts",
    "/api/v1/projects/{project_id}/executions/{param6}/artifacts/{param8}/download",
    "/api/v1/projects/{project_id}/executions/{param6}/complete",
    "/api/v1/projects/{project_id}/executions/{param6}/start",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
