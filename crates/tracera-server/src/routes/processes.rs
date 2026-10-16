//! Unavailable processes operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/processes",
    "/api/v1/processes/{id}",
    "/api/v1/processes/{id}/activate",
    "/api/v1/processes/{id}/deprecate",
    "/api/v1/processes/{id}/executions",
    "/api/v1/processes/{id}/versions",
    "/api/v1/projects/{project_id}/processes/stats",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
