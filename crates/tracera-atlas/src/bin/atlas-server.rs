//! `atlas-server`: optional HTTP service for Tracera Atlas.
//!
//! This binary is the daemon-mode entry point. It exposes a small REST
//! surface over the same [`AtlasEngine`] the library crate exposes, and is
//! intentionally minimal: every endpoint maps 1:1 to a method on the
//! engine. Future expansion (auth, persistence wiring, OpenTelemetry
//! export) should happen in dedicated layers below the router.
//!
//! Endpoints:
//!
//! - `GET  /healthz`            — liveness probe; returns `{"status":"ok"}`.
//! - `GET  /v1/work-items`      — list summaries of every work item.
//! - `POST /v1/work-items`      — create a new work item.
//! - `GET  /v1/work-items/:id`  — fetch one work item by id.
//! - `POST /v1/work-items/:id/assign`   — assign an agent.
//! - `POST /v1/work-items/:id/start`    — mark assigned agent as started.
//! - `POST /v1/work-items/:id/review`   — submit for review.
//! - `POST /v1/work-items/:id/approve`  — approve (sign-off, two-person).
//! - `POST /v1/work-items/:id/block`    — mark blocked.
//! - `POST /v1/work-items/:id/cancel`   — cancel.
//! - `GET  /v1/work-items/:id/changes`  — agent-of-record change log.
//! - `POST /v1/work-items/:id/sign-off` — record sign-off.
//! - `POST /v1/ci/webhook`     — ingest a GitHub Actions webhook.
//!
//! The `server` Cargo feature must be enabled to build this binary.
//! Running the binary without it will exit with an explanatory error.

use std::net::SocketAddr;
use std::sync::Arc;

use axum::extract::{Path, State};
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use axum::routing::{get, post};
use axum::{Json, Router};
use serde::Deserialize;
use tracing::{error, info, warn};

use tracera_atlas::observability::{SdlcEvent, SdlcEventKind, SdlcStage};
use tracera_atlas::{
    publish_ci_event, AoRQuery, AtlasEngine, ChangeKind, CiBridge, WorkItemId,
};

#[cfg(not(feature = "server"))]
compile_error!(
    "atlas-server requires the `server` feature. Build with `cargo build -p tracera-atlas --features server`."
);

// ---------- Shared state ----------

/// Wrapper around [`AtlasEngine`] that exposes an `axum::State` clone handle.
#[derive(Clone)]
struct AppState {
    engine: Arc<AtlasEngine>,
    ci: Arc<CiBridge>,
}

// ---------- Error mapping ----------

/// Top-level error type used by every handler.
#[derive(Debug)]
enum ApiError {
    /// The work item id was not found.
    NotFound,
    /// A delegation-state error occurred.
    Delegation(tracera_atlas::DelegationError),
    /// An agent-of-record error occurred.
    AoR(tracera_atlas::AoRError),
    /// A CI bridge error occurred.
    Ci(tracera_atlas::CiEventError),
    /// Request body failed to parse.
    BadRequest(String),
    /// Something unexpected — surfaced as a 500.
    Internal(String),
}

impl From<tracera_atlas::DelegationError> for ApiError {
    fn from(e: tracera_atlas::DelegationError) -> Self {
        Self::Delegation(e)
    }
}

impl From<tracera_atlas::AoRError> for ApiError {
    fn from(e: tracera_atlas::AoRError) -> Self {
        match e {
            tracera_atlas::AoRError::Delegation(d) => Self::Delegation(d),
            other => Self::AoR(other),
        }
    }
}

impl From<tracera_atlas::CiEventError> for ApiError {
    fn from(e: tracera_atlas::CiEventError) -> Self {
        Self::Ci(e)
    }
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, message) = match &self {
            Self::NotFound => (StatusCode::NOT_FOUND, "not_found".to_string()),
            Self::BadRequest(m) => (StatusCode::BAD_REQUEST, m.clone()),
            Self::Delegation(d) => (StatusCode::CONFLICT, d.to_string()),
            Self::AoR(a) => (StatusCode::CONFLICT, a.to_string()),
            Self::Ci(c) => (StatusCode::BAD_REQUEST, c.to_string()),
            Self::Internal(m) => {
                error!(error = %m, "internal server error");
                (StatusCode::INTERNAL_SERVER_ERROR, "internal_error".to_string())
            }
        };
        (status, Json(serde_json::json!({"error": message}))).into_response()
    }
}

// ---------- Request / response DTOs ----------

#[derive(Debug, Deserialize)]
struct CreateWorkRequest {
    title: String,
    #[serde(default)]
    stage: Option<SdlcStage>,
    #[serde(default)]
    description: Option<String>,
    #[serde(default)]
    created_by: Option<String>,
}

#[derive(Debug, Deserialize)]
struct AssignRequest {
    agent: String,
}

#[derive(Debug, Deserialize)]
struct StartRequest {
    agent: String,
}

#[derive(Debug, Deserialize)]
struct ReviewRequest {
    agent: String,
}

#[derive(Debug, Deserialize)]
struct ApproveRequest {
    reviewer: String,
}

#[derive(Debug, Deserialize)]
struct BlockRequest {
    #[serde(default)]
    reason: String,
}

#[derive(Debug, Deserialize)]
struct SignOffRequest {
    signer: String,
    #[serde(default)]
    note: Option<String>,
}

#[derive(Debug, Deserialize)]
struct ChangesQuery {
    #[serde(default)]
    actor: Option<String>,
    #[serde(default)]
    kind: Option<ChangeKind>,
    #[serde(default)]
    limit: Option<usize>,
}

#[derive(Debug, Deserialize)]
struct CiWebhookRequest {
    /// Raw provider-specific JSON payload.
    raw: serde_json::Value,
    /// Optional work-item id this CI event should be attributed to.
    #[serde(default)]
    work_item_id: Option<WorkItemId>,
}

// ---------- Handlers ----------

async fn healthz() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ok", "service": "atlas-server"}))
}

async fn list_work_items(State(s): State<AppState>) -> Json<serde_json::Value> {
    let items = s.engine.delegation().list();
    Json(serde_json::json!({"work_items": items}))
}

async fn create_work_item(
    State(s): State<AppState>,
    Json(req): Json<CreateWorkRequest>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let stage = req.stage.unwrap_or(SdlcStage::Ready);
    let created_by = req.created_by.map(tracera_atlas::AgentId::new);
    let item = s
        .engine
        .delegation()
        .create_work_with(&req.title, stage, req.description, created_by)
        .map_err(ApiError::from)?;
    Ok(Json(serde_json::json!({"work_item": item})))
}

async fn get_work_item(
    State(s): State<AppState>,
    Path(id): Path<uuid::Uuid>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let wid = WorkItemId(id);
    let item = s
        .engine
        .delegation()
        .get(&wid)
        .ok_or(ApiError::NotFound)?;
    Ok(Json(serde_json::json!({"work_item": item})))
}

async fn assign_work_item(
    State(s): State<AppState>,
    Path(id): Path<uuid::Uuid>,
    Json(req): Json<AssignRequest>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let wid = WorkItemId(id);
    let out = s
        .engine
        .delegation()
        .assign(&wid, &req.agent)
        .map_err(ApiError::from)?;
    Ok(Json(serde_json::json!({"assignment": out})))
}

async fn start_work_item(
    State(s): State<AppState>,
    Path(id): Path<uuid::Uuid>,
    Json(req): Json<StartRequest>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let wid = WorkItemId(id);
    let item = s
        .engine
        .delegation()
        .start(&wid, &req.agent)
        .map_err(ApiError::from)?;
    Ok(Json(serde_json::json!({"work_item": item})))
}

async fn review_work_item(
    State(s): State<AppState>,
    Path(id): Path<uuid::Uuid>,
    Json(req): Json<ReviewRequest>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let wid = WorkItemId(id);
    let item = s
        .engine
        .delegation()
        .submit_for_review(&wid, &req.agent)
        .map_err(ApiError::from)?;
    Ok(Json(serde_json::json!({"work_item": item})))
}

async fn approve_work_item(
    State(s): State<AppState>,
    Path(id): Path<uuid::Uuid>,
    Json(req): Json<ApproveRequest>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let wid = WorkItemId(id);
    let item = s
        .engine
        .delegation()
        .approve(&wid, &req.reviewer)
        .map_err(ApiError::from)?;
    Ok(Json(serde_json::json!({"work_item": item})))
}

async fn block_work_item(
    State(s): State<AppState>,
    Path(id): Path<uuid::Uuid>,
    Json(req): Json<BlockRequest>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let wid = WorkItemId(id);
    let item = s
        .engine
        .delegation()
        .block(&wid, &req.reason)
        .map_err(ApiError::from)?;
    Ok(Json(serde_json::json!({"work_item": item})))
}

async fn cancel_work_item(
    State(s): State<AppState>,
    Path(id): Path<uuid::Uuid>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let wid = WorkItemId(id);
    let item = s.engine.delegation().cancel(&wid).map_err(ApiError::from)?;
    Ok(Json(serde_json::json!({"work_item": item})))
}

async fn list_changes(
    State(s): State<AppState>,
    Path(id): Path<uuid::Uuid>,
    axum::extract::Query(q): axum::extract::Query<ChangesQuery>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let wid = WorkItemId(id);
    // Confirm the work item exists so we can return 404 instead of an empty list.
    if s.engine.delegation().get(&wid).is_none() {
        return Err(ApiError::NotFound);
    }
    let query = AoRQuery {
        work_item_id: Some(wid),
        actor: q.actor.map(tracera_atlas::ActorId::new),
        kind: q.kind,
        since: None,
        until: None,
        limit: q.limit,
    };
    let changes = s.engine.agent_of_record().query_changes(&query);
    Ok(Json(serde_json::json!({"changes": changes})))
}

async fn sign_off_work_item(
    State(s): State<AppState>,
    Path(id): Path<uuid::Uuid>,
    Json(req): Json<SignOffRequest>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let wid = WorkItemId(id);
    let sign_off = s
        .engine
        .agent_of_record()
        .sign_off(&wid, &req.signer, req.note.as_deref())
        .map_err(ApiError::from)?;
    Ok(Json(serde_json::json!({"sign_off": sign_off})))
}

async fn ci_webhook(
    State(s): State<AppState>,
    Json(req): Json<CiWebhookRequest>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let raw_str = serde_json::to_string(&req.raw).map_err(|e| ApiError::BadRequest(e.to_string()))?;
    let normalised = s.ci.detect_and_normalise(&raw_str).map_err(ApiError::from)?;
    let work_item_id = req.work_item_id.clone().unwrap_or_else(WorkItemId::new);
    let event = publish_ci_event(&normalised, work_item_id);
    publish_event(&s, event.clone());
    Ok(Json(serde_json::json!({
        "provider": normalised.provider,
        "kind": normalised.kind,
        "work_item_id": event.work_item_id,
        "event_id": event.id,
    })))
}

/// Hand an `SdlcEvent` to the engine's event bus. This is the single point
/// where HTTP-originated events get fanned out to subscribers.
fn publish_event(s: &AppState, event: SdlcEvent) {
    match &event.kind {
        SdlcEventKind::CiRunCompleted { .. } => {
            info!(event_id = %event.id, work_item_id = %event.work_item_id, "ci webhook ingested");
        }
        other => {
            warn!(event_id = %event.id, kind = ?other, "unexpected event kind in publish_event");
        }
    }
    s.engine.events().publish(event);
}

// ---------- main ----------

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    init_tracing();

    let bind: SocketAddr = std::env::var("ATLAS_BIND")
        .unwrap_or_else(|_| "0.0.0.0:18443".to_string())
        .parse()?;

    let state = AppState {
        engine: Arc::new(AtlasEngine::in_memory()),
        ci: Arc::new(CiBridge::new()),
    };

    let app = Router::new()
        .route("/healthz", get(healthz))
        .route("/v1/work-items", get(list_work_items).post(create_work_item))
        .route("/v1/work-items/{id}", get(get_work_item))
        .route("/v1/work-items/{id}/assign", post(assign_work_item))
        .route("/v1/work-items/{id}/start", post(start_work_item))
        .route("/v1/work-items/{id}/review", post(review_work_item))
        .route("/v1/work-items/{id}/approve", post(approve_work_item))
        .route("/v1/work-items/{id}/block", post(block_work_item))
        .route("/v1/work-items/{id}/cancel", post(cancel_work_item))
        .route("/v1/work-items/{id}/changes", get(list_changes))
        .route("/v1/work-items/{id}/sign-off", post(sign_off_work_item))
        .route("/v1/ci/webhook", post(ci_webhook))
        .with_state(state);

    info!(%bind, "atlas-server listening");
    let listener = tokio::net::TcpListener::bind(bind).await?;
    axum::serve(listener, app).await?;
    Ok(())
}

fn init_tracing() {
    use tracing_subscriber::EnvFilter;
    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("atlas_server=info,tracera_atlas=info"));
    let _ = tracing_subscriber::fmt()
        .with_env_filter(filter)
        .with_target(true)
        .try_init();
}
