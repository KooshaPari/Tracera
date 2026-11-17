//! Unavailable problems operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/problems",
    "/api/v1/problems/{id}",
    "/api/v1/problems/{id}/activities",
    "/api/v1/problems/{id}/close",
    "/api/v1/problems/{id}/rca",
    "/api/v1/problems/{id}/status",
    "/api/v1/projects/{project_id}/problems/stats",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
