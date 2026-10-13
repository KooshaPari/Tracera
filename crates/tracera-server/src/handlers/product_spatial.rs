//! Bounded, authenticated, read-only spatial product projection.
//! This route does not perform per-product authorization or claim a complete
//! historic graph. Use deployment-wide bearer auth and deny external untrusted
//! scopes until fine-grained product grants are implemented.

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use serde::Deserialize;
use tracera_server::product::{
    compile_spatial_projection, ProjectionScope, SpatialProjection, ViewKind,
};

use crate::{AppState, ErrorResponse};

#[derive(Debug, Deserialize)]
pub(crate) struct SpatialQuery {
    /// Explicit snapshot pin. Never silently mix current and historic records.
    pub baseline_revision: u64,
    /// Number of canonical nodes displayed, clamped to 1..=500.
    pub max_nodes: Option<usize>,
    /// Number of typed relations displayed, clamped to 1..=1500.
    pub max_relations: Option<usize>,
    pub view: Option<String>,
}

fn view_kind(value: Option<&str>) -> Result<ViewKind, ()> {
    match value.unwrap_or("assembly") {
        "assembly" => Ok(ViewKind::Assembly),
        "flow" => Ok(ViewKind::Flow),
        "environment" => Ok(ViewKind::Environment),
        "hybrid" => Ok(ViewKind::Hybrid),
        _ => Err(()),
    }
}

pub(crate) async fn get_spatial_projection(
    State(state): State<AppState>,
    Path(product_id): Path<String>,
    Query(query): Query<SpatialQuery>,
) -> Result<Json<SpatialProjection>, (StatusCode, Json<ErrorResponse>)> {
    if product_id.trim().is_empty() || product_id.len() > 256 {
        return Err((StatusCode::BAD_REQUEST, Json(ErrorResponse { error: "invalid product id" })));
    }
    let view = view_kind(query.view.as_deref())
        .map_err(|_| (StatusCode::BAD_REQUEST, Json(ErrorResponse { error: "invalid spatial view" })))?;
    let max_nodes = query.max_nodes.unwrap_or(128).clamp(1, 500);
    let max_relations = query.max_relations.unwrap_or(384).clamp(1, 1500);
    let (nodes, relations, input_complete) = state.store
        .product_spatial_slice(
            product_id.clone(), query.baseline_revision, max_nodes, max_relations,
        )
        .await
        .map_err(|err| {
            tracing::error!("spatial product read failed: {err}");
            (StatusCode::INTERNAL_SERVER_ERROR, Json(ErrorResponse {
                error: "product snapshot retrieval failed",
            }))
        })?;
    if nodes.is_empty() {
        return Err((StatusCode::NOT_FOUND, Json(ErrorResponse {
            error: "product baseline not found",
        })));
    }
    let scope = ProjectionScope {
        product_id, baseline_revision: query.baseline_revision, view,
        max_nodes, max_relations,
    };
    let result = compile_spatial_projection(scope, &nodes, &relations, input_complete)
        .map_err(|err| {
            tracing::warn!("invalid source graph for spatial projection: {err}");
            (StatusCode::UNPROCESSABLE_ENTITY, Json(ErrorResponse {
                error: "inconsistent product snapshot",
            }))
        })?;
    Ok(Json(result))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn view_discriminant_is_strict_and_non-implicit() {
        assert_eq!(view_kind(None), Ok(ViewKind::Assembly));
        assert_eq!(view_kind(Some("hybrid")), Ok(ViewKind::Hybrid));
        assert!(view_kind(Some("other")).is_err());
    }
}
