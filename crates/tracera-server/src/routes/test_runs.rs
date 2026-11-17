//! Unavailable test-runs operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/projects/{project_id}/test-runs/stats",
    "/api/v1/test-runs",
    "/api/v1/test-runs/{id}",
    "/api/v1/test-runs/{id}/activities",
    "/api/v1/test-runs/{id}/cancel",
    "/api/v1/test-runs/{id}/complete",
    "/api/v1/test-runs/{id}/results",
    "/api/v1/test-runs/{id}/results/bulk",
    "/api/v1/test-runs/{id}/start",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
