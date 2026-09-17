use axum::Json;
use chrono::Utc;
use serde::Deserialize;
use serde_json::Value;

use crate::{bad_request, ErrorResponse};

use crate::swee::{EdgeKind, NodeKind};

use super::super::AppState;
use super::evidence::empty_object;

// ---------------------------------------------------------------------------
// SWEE Graph CRUD handlers
// ---------------------------------------------------------------------------

#[derive(Deserialize)]
pub(crate) struct SweeNodeCreate {
    pub(crate) node_type: String,
    pub(crate) label: String,
    #[serde(default = "empty_object")]
    pub(crate) metadata: Value,
}

#[derive(Deserialize)]
pub(crate) struct SweeEdgeCreate {
    pub(crate) edge_type: String,
    pub(crate) source_id: String,
    pub(crate) target_id: String,
    #[serde(default = "default_confidence_1")]
    pub(crate) confidence: f64,
    #[serde(default = "default_edge_source_manual")]
    pub(crate) source: String,
    #[serde(default = "empty_object")]
    pub(crate) metadata: Value,
}

pub(crate) fn default_confidence_1() -> f64 {
    1.0
}

pub(crate) fn default_edge_source_manual() -> String {
    "manual".to_string()
}

pub(crate) async fn create_swee_node_handler(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<SweeNodeCreate>,
) -> Result<(axum::http::StatusCode, Json<Value>), (axum::http::StatusCode, Json<ErrorResponse>)> {
    if NodeKind::from_str(&payload.node_type).is_none() {
        return Err(bad_request("invalid node_type"));
    }
    let now = Utc::now();
    let id = state
        .store
        .create_swee_node(payload.node_type, payload.label, payload.metadata, now)
        .await
        .map_err(|e| {
            tracing::error!("create_swee_node failed: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "graph node creation failed",
                }),
            )
        })?;
    Ok((
        axum::http::StatusCode::CREATED,
        Json(serde_json::json!({"id": id})),
    ))
}

pub(crate) async fn list_swee_nodes_handler(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Query(params): axum::extract::Query<std::collections::HashMap<String, String>>,
) -> Result<Json<Value>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let node_type = params.get("node_type").cloned();
    let nodes = state.store.list_swee_nodes(node_type).await.map_err(|e| {
        tracing::error!("list_swee_nodes failed: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "graph node listing failed",
            }),
        )
    })?;
    Ok(Json(
        serde_json::json!({"count": nodes.len(), "items": nodes}),
    ))
}

pub(crate) async fn get_swee_node_handler(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Path(id): axum::extract::Path<String>,
) -> Result<Json<Value>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    match state.store.get_swee_node(id).await {
        Ok(Some(node)) => Ok(Json(node)),
        Ok(None) => Err((
            axum::http::StatusCode::NOT_FOUND,
            Json(ErrorResponse {
                error: "node not found",
            }),
        )),
        Err(e) => {
            tracing::error!("get_swee_node failed: {e}");
            Err((
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "graph node lookup failed",
                }),
            ))
        }
    }
}

pub(crate) async fn create_swee_edge_handler(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<SweeEdgeCreate>,
) -> Result<(axum::http::StatusCode, Json<Value>), (axum::http::StatusCode, Json<ErrorResponse>)> {
    if EdgeKind::from_str(&payload.edge_type).is_none() {
        return Err(bad_request("invalid edge_type"));
    }
    let now = Utc::now();
    let id = state
        .store
        .create_swee_edge(
            payload.edge_type,
            payload.source_id,
            payload.target_id,
            payload.confidence,
            payload.source,
            payload.metadata,
            now,
        )
        .await
        .map_err(|e| {
            tracing::error!("create_swee_edge failed: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "graph edge creation failed",
                }),
            )
        })?;
    Ok((
        axum::http::StatusCode::CREATED,
        Json(serde_json::json!({"id": id})),
    ))
}

pub(crate) async fn list_swee_edges_handler(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Query(params): axum::extract::Query<std::collections::HashMap<String, String>>,
) -> Result<Json<Value>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let edge_type = params.get("edge_type").cloned();
    let edges = state.store.list_swee_edges(edge_type).await.map_err(|e| {
        tracing::error!("list_swee_edges failed: {e}");
        (
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorResponse {
                error: "graph edge listing failed",
            }),
        )
    })?;
    Ok(Json(
        serde_json::json!({"count": edges.len(), "items": edges}),
    ))
}

pub(crate) async fn get_swee_neighbors_handler(
    axum::extract::State(state): axum::extract::State<AppState>,
    axum::extract::Path(id): axum::extract::Path<String>,
    axum::extract::Query(params): axum::extract::Query<std::collections::HashMap<String, String>>,
) -> Result<Json<Value>, (axum::http::StatusCode, Json<ErrorResponse>)> {
    let direction = params
        .get("direction")
        .cloned()
        .unwrap_or_else(|| "both".to_string());
    let neighbors = state
        .store
        .get_swee_neighbors(id.clone(), direction.clone())
        .await
        .map_err(|e| {
            tracing::error!("get_swee_neighbors failed: {e}");
            (
                axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorResponse {
                    error: "graph neighbor lookup failed",
                }),
            )
        })?;
    Ok(Json(serde_json::json!({
        "node_id": id,
        "direction": direction,
        "count": neighbors.len(),
        "items": neighbors,
    })))
}
