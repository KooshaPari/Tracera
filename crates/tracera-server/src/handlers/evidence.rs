use axum::Json;
use chrono::Utc;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::{bad_request, ErrorResponse};
use crate::store::{EvidenceItem, Store};
use crate::validation::{
    validate_text, MAX_ID_CHARS, MAX_METADATA_BYTES, MAX_SHORT_TEXT_CHARS, MAX_URL_CHARS,
};

use super::super::AppState;

// ---------------------------------------------------------------------------
// Evidence HTTP shapes (handlers delegate to store trait)
// ---------------------------------------------------------------------------
#[derive(Deserialize)]
pub(crate) struct EvidenceCreate {
    pub(crate) artifact_id: String,
    pub(crate) kind: String,
    pub(crate) url: String,
    #[serde(default = "empty_object")]
    pub(crate) metadata: serde_json::Value,
}

#[derive(Serialize)]
pub(crate) struct EvidenceList {
    pub(crate) items: Vec<EvidenceItem>,
    pub(crate) count: usize,
}

pub(crate) fn empty_object() -> serde_json::Value {
    serde_json::Value::Object(serde_json::Map::new())
}

pub(crate) fn validate_evidence(payload: &EvidenceCreate) -> Result<(), &'static str> {
    validate_text(
        &payload.artifact_id,
        "invalid artifact_id",
        MAX_ID_CHARS,
        true,
    )?;
    validate_text(&payload.kind, "invalid kind", MAX_SHORT_TEXT_CHARS, true)?;
    validate_text(&payload.url, "invalid url", MAX_URL_CHARS, true)?;
    if serde_json::to_vec(&payload.metadata)
        .map(|v| v.len())
        .unwrap_or(MAX_METADATA_BYTES + 1)
        > MAX_METADATA_BYTES
    {
        return Err("metadata too large");
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// Evidence handlers -- delegate to store trait
// ---------------------------------------------------------------------------
pub(crate) async fn list_evidence(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<Json<EvidenceList>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let items = state.store.list_evidence().await.map_err(|e| {
        tracing::error!("list_evidence store error: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "evidence listing failed",
            }),
        )
    })?;
    Ok(Json(EvidenceList {
        count: items.len(),
        items,
    }))
}

pub(crate) async fn create_evidence(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<EvidenceCreate>,
) -> Result<
    (axum::http::StatusCode, Json<EvidenceItem>),
    (axum::http::StatusCode, Json<ErrorResponse>),
> {
    validate_evidence(&payload).map_err(bad_request)?;
    let now = Utc::now();
    let id = format!("ev-{}", Uuid::new_v4());
    let meta =
        serde_json::to_value(&payload.metadata).unwrap_or(serde_json::Value::Object(serde_json::Map::new()));

    let item = state
        .store
        .create_evidence(
            id,
            payload.artifact_id,
            payload.kind,
            payload.url,
            meta,
            now,
        )
        .await
        .map_err(|e| {
            tracing::error!("create_evidence store insert failed: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "evidence persistence failed",
                }),
            )
        })?;

    Ok((axum::http::StatusCode::CREATED, Json(item)))
}
