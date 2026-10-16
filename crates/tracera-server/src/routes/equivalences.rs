//! Unavailable equivalences operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/equivalences/batch-confirm",
    "/api/v1/equivalences/batch-reject",
    "/api/v1/equivalences/{id}/confirm",
    "/api/v1/equivalences/{id}/reject",
    "/equivalences",
    "/equivalences/bulk-confirm",
    "/equivalences/bulk-reject",
    "/equivalences/concepts",
    "/equivalences/concepts/{param3}",
    "/equivalences/concepts/{param3}/projections",
    "/equivalences/concepts/{param3}/projections/{param5}",
    "/equivalences/{param2}",
    "/equivalences/{param2}/confirm",
    "/equivalences/{param2}/reject",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
