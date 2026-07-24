use axum::{extract::State, Json};
use serde::Serialize;

use super::AppState;

#[derive(Serialize)]
pub(super) struct StatusResponse {
    pub(crate) status: &'static str,
    pub(crate) service: &'static str,
}

#[derive(Serialize)]
pub(super) struct ReadyResponse {
    pub(crate) status: &'static str,
    pub(crate) service: &'static str,
    pub(crate) version: String,
    pub(crate) backend: &'static str,
    pub(crate) uptime_seconds: u64,
}

fn uptime_seconds(state: &AppState) -> u64 {
    state.started_at.elapsed().as_secs()
}

pub(super) async fn healthz() -> Json<StatusResponse> {
    Json(StatusResponse {
        status: "ok",
        service: "tracera-server",
    })
}

pub(super) async fn health(State(state): State<AppState>) -> Json<ReadyResponse> {
    let uptime_seconds = uptime_seconds(&state);
    Json(ReadyResponse {
        status: "ok",
        service: "tracera-server",
        version: state.version,
        backend: state.backend,
        uptime_seconds,
    })
}

pub(super) async fn readyz(State(state): State<AppState>) -> Json<ReadyResponse> {
    let uptime_seconds = uptime_seconds(&state);
    Json(ReadyResponse {
        status: "ready",
        service: "tracera-server",
        version: state.version,
        backend: state.backend,
        uptime_seconds,
    })
}

pub(super) async fn ready(State(state): State<AppState>) -> Json<ReadyResponse> {
    readyz(State(state)).await
}
