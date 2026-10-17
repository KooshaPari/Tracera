//! Unavailable test-cases operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/projects/{project_id}/test-cases/stats",
    "/api/v1/test-cases",
    "/api/v1/test-cases/{id}",
    "/api/v1/test-cases/{id}/activities",
    "/api/v1/test-cases/{id}/approve",
    "/api/v1/test-cases/{id}/deprecate",
    "/api/v1/test-cases/{id}/status",
    "/api/v1/test-cases/{id}/submit-review",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
