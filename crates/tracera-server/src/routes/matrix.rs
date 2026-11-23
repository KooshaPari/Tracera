//! Canonical project traceability matrix and honest export formats.
use crate::router::project_graph_data;

use crate::AppState;
use axum::{
    extract::{Path, Query, State},
    http::{header, StatusCode},
    response::{IntoResponse, Response},
    Json,
};
use serde::Deserialize;
use serde_json::{json, Value};

type Reply = Result<Json<Value>, (StatusCode, Json<Value>)>;

#[derive(Default, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct ExportParams {
    format: Option<String>,
}

pub(crate) async fn matrix(State(state): State<AppState>, Path(id): Path<String>) -> Reply {
    let graph = project_graph_data::load(&id, &state).await?;
    Ok(Json(project_graph_data::matrix_json(&graph)))
}

pub(crate) async fn export(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Query(p): Query<ExportParams>,
) -> Result<Response, (StatusCode, Json<Value>)> {
    let format = p.format.as_deref().unwrap_or("csv");
    if !matches!(format, "csv" | "json" | "xlsx") {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(json!({"error":"unsupported_export_format"})),
        ));
    }
    if format == "xlsx" {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(json!({"error":"unsupported_export_format"})),
        ));
    }
    let graph = project_graph_data::load(&id, &state).await?;
    let (content_type, body) = if format == "json" {
        (
            "application/json",
            serde_json::to_vec(&project_graph_data::matrix_json(&graph)).unwrap_or_default(),
        )
    } else {
        ("text/csv", project_graph_data::csv_export(&graph))
    };
    Ok((StatusCode::OK, [(header::CONTENT_TYPE, content_type)], body).into_response())
}

#[cfg(test)]
#[path = "project_graph_tests.rs"]
mod tests;
