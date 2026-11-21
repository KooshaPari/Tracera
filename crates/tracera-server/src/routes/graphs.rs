//! Project-scoped graph and viewport projections over canonical storage.
//! Unknown projects return 404; empty known projects return empty projections.
use crate::router::project_graph_data;

use crate::AppState;
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use serde::Deserialize;
use serde_json::{json, Value};

type Reply = Result<Json<Value>, (StatusCode, Json<Value>)>;

#[derive(Default, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Params {
    graph_id: Option<String>,
    graph_type: Option<String>,
}

pub(crate) async fn graphs(State(state): State<AppState>, Path(id): Path<String>) -> Reply {
    let graph = project_graph_data::load(&id, &state).await?;
    Ok(Json(
        json!({"graphs":[project_graph_data::graph_summary(&graph)]}),
    ))
}

pub(crate) async fn project_graph(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Query(p): Query<Params>,
) -> Reply {
    let graph = project_graph_data::load(&id, &state).await?;
    if let Some(requested) = p.graph_id.filter(|value| !value.is_empty()) {
        if requested != graph.project.id && requested != "traceability" {
            return Err((
                axum::http::StatusCode::NOT_FOUND,
                Json(json!({"error":"graph_not_found"})),
            ));
        }
    }
    if let Some(requested) = p.graph_type.filter(|value| !value.is_empty()) {
        if !requested.eq_ignore_ascii_case("traceability") {
            return Err((
                axum::http::StatusCode::NOT_FOUND,
                Json(json!({"error":"graph_not_found"})),
            ));
        }
    }
    Ok(Json(project_graph_data::projection_json(&graph)))
}

pub(crate) async fn viewport_graph(
    State(state): State<AppState>,
    Path(id): Path<String>,
    axum::Json(_body): axum::Json<Value>,
) -> Reply {
    let graph = project_graph_data::load(&id, &state).await?;
    Ok(Json(project_graph_data::viewport_json(&graph)))
}

// W9 unavailable routes retained: this module only implements the three
// project-scoped read paths used by the frontend graph hooks.
pub(super) const W9_ROUTES: &[&str] = &["/api/v1/graph/analysis/cache/invalidate"];
pub(super) fn w9_routes() -> axum::Router<AppState> {
    crate::router::w9_routes::unavailable_routes(W9_ROUTES)
}
