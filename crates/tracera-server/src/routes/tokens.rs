//! Unavailable tokens operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &["/api/v1/tokens/{id}"];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
