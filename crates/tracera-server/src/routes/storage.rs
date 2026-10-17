//! Unavailable storage operations: no matching Store contract.
use crate::AppState;
use axum::Router;

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/storage/presigned-upload",
    "/api/v1/storage/{id}",
    "/storage/download",
    "/storage/info",
    "/storage/presigned-upload",
    "/storage/presigned/{param3}",
    "/storage/upload",
    "/storage/upload-with-thumbnail",
    "/storage/{param2}",
];

pub(super) fn routes() -> Router<AppState> {
    super::unavailable_routes(ROUTES)
}
