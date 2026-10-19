//! Unavailable equivalence operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/projects/{project_id}/equivalence/export",
    "/api/v1/projects/{project_id}/equivalence/export-statistics",
    "/api/v1/projects/{project_id}/equivalence/import",
    "/api/v1/projects/{project_id}/equivalence/validate",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
