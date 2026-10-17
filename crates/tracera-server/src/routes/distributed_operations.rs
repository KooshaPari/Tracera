//! Unavailable distributed-operations operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/distributed-operations",
    "/distributed-operations/assign",
    "/distributed-operations/participants/result",
    "/distributed-operations/{param2}/complete",
    "/distributed-operations/{param2}/participants/{id}",
    "/distributed-operations/{param2}/results",
    "/distributed-operations/{param2}/status",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
