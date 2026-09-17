use axum::Json;
use chrono::{DateTime, Utc};
use serde::Deserialize;
use uuid::Uuid;

use crate::store::Sprint;
use crate::validation::{validate_text, MAX_LONG_TEXT_CHARS, MAX_SHORT_TEXT_CHARS};
use crate::{bad_request, ErrorResponse};

use super::super::AppState;

// ---------------------------------------------------------------------------
// SDLC-PM HTTP shapes
// ---------------------------------------------------------------------------
#[derive(Deserialize)]
pub(crate) struct SprintCreate {
    pub(crate) name: String,
    pub(crate) goal: String,
    pub(crate) start_date: DateTime<Utc>,
    pub(crate) end_date: DateTime<Utc>,
}

pub(crate) fn validate_sprint(payload: &SprintCreate) -> Result<(), &'static str> {
    validate_text(&payload.name, "invalid name", MAX_SHORT_TEXT_CHARS, true)?;
    validate_text(&payload.goal, "invalid goal", MAX_LONG_TEXT_CHARS, true)?;
    if payload.end_date < payload.start_date {
        return Err("invalid date range");
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// Sprint handlers -- delegate to store trait
// ---------------------------------------------------------------------------
pub(crate) async fn list_sprints(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<Vec<Sprint>>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let sprints = state.store.list_sprints().await.map_err(|e| {
        tracing::error!("list_sprints store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "sprint listing failed",
            }),
        )
    })?;
    Ok(Json(sprints))
}

pub(crate) async fn create_sprint(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<SprintCreate>,
) -> Result<(axum::http::StatusCode, Json<Sprint>), (axum::http::StatusCode, Json<ErrorResponse>)> {
    validate_sprint(&payload).map_err(bad_request)?;
    let now = Utc::now();
    let id = format!("sprint-{}", Uuid::new_v4());

    let sprint = state
        .store
        .create_sprint(
            id,
            payload.name,
            payload.goal,
            payload.start_date,
            payload.end_date,
            now,
        )
        .await
        .map_err(|e| {
            tracing::error!("create_sprint store insert failed: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "sprint persistence failed",
                }),
            )
        })?;

    Ok((axum::http::StatusCode::CREATED, Json(sprint)))
}
