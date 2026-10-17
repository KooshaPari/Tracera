//! Unavailable versions operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/projects/{project_id}/versions/compare/bulk",
    "/api/v1/projects/{project_id}/versions/compare/summary",
    "/api/v1/versions/{id}",
    "/api/v1/versions/{id}/snapshot",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
