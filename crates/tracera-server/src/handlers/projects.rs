use axum::http::StatusCode;
use axum::Json;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::store::ProjectSummary;
use crate::validation::{validate_text, MAX_LONG_TEXT_CHARS, MAX_SHORT_TEXT_CHARS};
use crate::{bad_request, ErrorResponse};

use super::super::AppState;

type ApiErr = (StatusCode, Json<ErrorResponse>);

#[derive(Deserialize)]
pub(crate) struct ProjectCreate {
    pub(crate) name: String,
    #[serde(default)]
    pub(crate) description: Option<String>,
}

#[derive(Deserialize)]
pub(crate) struct ProjectUpdate {
    #[serde(default)]
    pub(crate) name: Option<String>,
    #[serde(default)]
    pub(crate) description: Option<String>,
}

#[derive(Serialize)]
pub(crate) struct ProjectOut {
    id: String,
    name: String,
    description: Option<String>,
    created_at: chrono::DateTime<chrono::Utc>,
    updated_at: chrono::DateTime<chrono::Utc>,
    metadata: serde_json::Value,
    problem_count: i64,
}

impl From<ProjectSummary> for ProjectOut {
    fn from(p: ProjectSummary) -> Self {
        Self {
            id: p.id,
            name: p.name,
            description: p.description,
            created_at: p.created_at,
            updated_at: p.updated_at,
            metadata: p.metadata,
            problem_count: p.problem_count,
        }
    }
}

fn db_err(what: &'static str, e: crate::store::StoreError) -> ApiErr {
    tracing::error!("{what}: {e}");
    let msg = e.to_string();
    if msg.contains("UNIQUE") {
        return (
            StatusCode::CONFLICT,
            Json(ErrorResponse { error: "project already exists" }),
        );
    }
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(ErrorResponse { error: "project persistence failed" }),
    )
}

pub(crate) async fn create_project(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<ProjectCreate>,
) -> Result<(StatusCode, Json<ProjectOut>), ApiErr> {
    validate_text(&payload.name, "invalid name", MAX_SHORT_TEXT_CHARS, true).map_err(bad_request)?;
    if let Some(d) = payload.description.as_deref() {
        validate_text(d, "invalid description", MAX_LONG_TEXT_CHARS, false).map_err(bad_request)?;
    }
    let id = format!("proj-{}", Uuid::new_v4());
    let p = state
        .store
        .create_project(id, payload.name.trim().to_string(), payload.description)
        .await
        .map_err(|e| db_err("create_project", e))?;
    Ok((StatusCode::CREATED, Json(p.into())))
}

pub(crate) async fn update_project(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Path(project_id): axum::extract::Path<String>,
    Json(payload): Json<ProjectUpdate>,
) -> Result<Json<ProjectOut>, ApiErr> {
    if let Some(n) = payload.name.as_deref() {
        validate_text(n, "invalid name", MAX_SHORT_TEXT_CHARS, true).map_err(bad_request)?;
    }
    if let Some(d) = payload.description.as_deref() {
        validate_text(d, "invalid description", MAX_LONG_TEXT_CHARS, false).map_err(bad_request)?;
    }
    match state
        .store
        .update_project(project_id, payload.name, payload.description)
        .await
        .map_err(|e| db_err("update_project", e))?
    {
        Some(p) => Ok(Json(p.into())),
        None => Err((StatusCode::NOT_FOUND, Json(ErrorResponse { error: "project not found" }))),
    }
}

pub(crate) async fn delete_project(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Path(project_id): axum::extract::Path<String>,
) -> Result<StatusCode, ApiErr> {
    let removed = state
        .store
        .delete_project(project_id)
        .await
        .map_err(|e| db_err("delete_project", e))?;
    if removed {
        Ok(StatusCode::NO_CONTENT)
    } else {
        Err((StatusCode::NOT_FOUND, Json(ErrorResponse { error: "project not found" })))
    }
}
