use axum::Json;
use chrono::Utc;
use serde::Deserialize;
use uuid::Uuid;

use crate::{bad_request, ErrorResponse};
use crate::store::{Story, TraceLink};
use crate::validation::{validate_text, MAX_ID_CHARS, MAX_LONG_TEXT_CHARS, MAX_SHORT_TEXT_CHARS};

use super::super::AppState;

// ---------------------------------------------------------------------------
// Story handlers
// ---------------------------------------------------------------------------
#[derive(Deserialize)]
pub(crate) struct StoryCreate {
    pub(crate) title: String,
    #[serde(default)]
    pub(crate) description: String,
    #[serde(default = "default_story_status")]
    pub(crate) status: String,
}

pub(crate) fn default_story_status() -> String {
    "open".to_string()
}

#[derive(Deserialize)]
pub(crate) struct TraceLinkCreate {
    pub(crate) source_id: String,
    pub(crate) target_id: String,
    pub(crate) relationship: String,
}

pub(crate) fn validate_story(payload: &StoryCreate) -> Result<(), &'static str> {
    validate_text(&payload.title, "invalid title", MAX_SHORT_TEXT_CHARS, true)?;
    validate_text(
        &payload.description,
        "invalid description",
        MAX_LONG_TEXT_CHARS,
        false,
    )?;
    validate_text(
        &payload.status,
        "invalid status",
        MAX_SHORT_TEXT_CHARS,
        true,
    )?;
    Ok(())
}

pub(crate) fn validate_trace_link(payload: &TraceLinkCreate) -> Result<(), &'static str> {
    validate_text(&payload.source_id, "invalid source_id", MAX_ID_CHARS, true)?;
    validate_text(&payload.target_id, "invalid target_id", MAX_ID_CHARS, true)?;
    validate_text(
        &payload.relationship,
        "invalid relationship",
        MAX_SHORT_TEXT_CHARS,
        true,
    )?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Story handler implementations
// ---------------------------------------------------------------------------
pub(crate) async fn list_stories(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<Vec<Story>>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let stories = state.store.list_stories().await.map_err(|e| {
        tracing::error!("list_stories store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "story listing failed",
            }),
        )
    })?;
    Ok(Json(stories))
}

pub(crate) async fn create_story(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<StoryCreate>,
) -> Result<(axum::http::StatusCode, Json<Story>), (axum::http::StatusCode, Json<ErrorResponse>)> {
    validate_story(&payload).map_err(bad_request)?;
    let now = Utc::now();
    let id = format!("story-{}", Uuid::new_v4());

    let story = state
        .store
        .create_story(
            id,
            None,
            payload.title,
            payload.description,
            payload.status,
            None,
            now,
        )
        .await
        .map_err(|e| {
            tracing::error!("create_story store insert failed: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "story persistence failed",
                }),
            )
        })?;

    Ok((axum::http::StatusCode::CREATED, Json(story)))
}

pub(crate) async fn list_stories_api(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<Vec<Story>>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let stories = state.store.list_stories().await.map_err(|e| {
        tracing::error!("list_stories_api store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "story listing failed",
            }),
        )
    })?;
    Ok(Json(stories))
}

pub(crate) async fn create_trace_link(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<TraceLinkCreate>,
) -> Result<(axum::http::StatusCode, Json<TraceLink>), (axum::http::StatusCode, Json<ErrorResponse>)>
{
    validate_trace_link(&payload).map_err(bad_request)?;
    let now = Utc::now();
    let id = format!("tl-{}", Uuid::new_v4());

    let link = state
        .store
        .create_trace_link(
            id,
            payload.source_id,
            payload.target_id,
            payload.relationship,
            1.0,
            "api".to_string(),
            now,
        )
        .await
        .map_err(|e| {
            tracing::error!("create_trace_link store insert failed: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "trace link persistence failed",
                }),
            )
        })?;

    Ok((axum::http::StatusCode::CREATED, Json(link)))
}
