use axum::http::StatusCode;

pub(crate) async fn create_project_stub() -> StatusCode {
    StatusCode::CREATED
}

pub(crate) async fn update_project_stub() -> StatusCode {
    StatusCode::OK
}

pub(crate) async fn delete_project_stub() -> StatusCode {
    StatusCode::NO_CONTENT
}
