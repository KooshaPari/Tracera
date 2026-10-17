//! Unavailable concepts operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/concepts/{id}",
    "/api/v1/concepts/{id}/projections",
    "/api/v1/concepts/{id}/projections/{param6}",
    "/api/v1/projects/{project_id}/concepts",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
