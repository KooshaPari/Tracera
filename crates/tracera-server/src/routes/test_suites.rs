//! Unavailable test-suites operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/projects/{project_id}/test-suites/stats",
    "/api/v1/test-suites",
    "/api/v1/test-suites/{id}",
    "/api/v1/test-suites/{id}/activities",
    "/api/v1/test-suites/{id}/status",
    "/api/v1/test-suites/{id}/test-cases",
    "/api/v1/test-suites/{id}/test-cases/reorder",
    "/api/v1/test-suites/{id}/test-cases/{param6}",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
