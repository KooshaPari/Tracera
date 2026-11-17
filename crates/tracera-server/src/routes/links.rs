//! Item-link storage is not implemented. Artifact trace links are a distinct
//! model without project membership; do not misrepresent them as item links.
use axum::{extract::MatchedPath, http::StatusCode, Json};
use serde::Serialize;
#[derive(Serialize)]
pub(super) struct Unimplemented {
    error: &'static str,
    route: String,
}
pub(super) async fn unavailable(path: MatchedPath) -> (StatusCode, Json<Unimplemented>) {
    (
        StatusCode::NOT_IMPLEMENTED,
        Json(Unimplemented {
            error: "not_implemented",
            route: path.as_str().to_owned(),
        }),
    )
}
