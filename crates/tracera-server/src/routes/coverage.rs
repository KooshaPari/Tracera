//! Unavailable coverage operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/coverage",
    "/api/v1/coverage/{id}",
    "/api/v1/coverage/{id}/activities",
    "/api/v1/coverage/{id}/verify",
    "/api/v1/projects/{project_id}/coverage",
    "/api/v1/projects/{project_id}/coverage/gaps",
    "/api/v1/projects/{project_id}/coverage/matrix",
    "/api/v1/projects/{project_id}/coverage/stats",
    "/api/v1/projects/{project_id}/coverage/{param6}",
    "/api/v1/projects/{project_id}/coverage/{param6}/verify",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
