//! Unavailable auth operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/auth/account",
    "/api/v1/auth/authkit/authorize",
    "/api/v1/auth/authkit/callback",
    "/api/v1/auth/authkit/refresh",
    "/api/v1/auth/change-password",
    "/api/v1/auth/profile",
    "/api/v1/auth/request-verification",
    "/api/v1/auth/reset-password",
    "/api/v1/auth/reset-password/confirm",
    "/api/v1/auth/user",
    "/api/v1/auth/verify-email",
    "/auth/me",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
