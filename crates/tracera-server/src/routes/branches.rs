//! Unavailable branches operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/branches/{id}",
    "/api/v1/branches/{id}/compare/{param6}",
    "/api/v1/branches/{id}/merge",
    "/api/v1/branches/{id}/versions",
    "/api/v1/projects/{project_id}/branches",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
