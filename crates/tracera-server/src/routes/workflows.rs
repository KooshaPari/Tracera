//! Unavailable workflows operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/projects/{project_id}/workflows/runs",
    "/api/v1/projects/{project_id}/workflows/schedules",
    "/api/v1/projects/{project_id}/workflows/schedules/bootstrap",
    "/api/v1/projects/{project_id}/workflows/schedules/{param7}",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
