use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use serde::Deserialize;

use crate::{product::ProductPersistenceError, AppState};

#[derive(Debug, Deserialize)]
pub(crate) struct LimitQuery {
    #[serde(default = "default_limit")]
    limit: usize,
}

#[derive(Debug, Deserialize)]
pub(crate) struct ObservationQuery {
    #[serde(default = "default_limit")]
    limit: usize,
    subject_local_id: Option<String>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct InvalidationQuery {
    #[serde(default = "default_limit")]
    limit: usize,
    target_ref: String,
}

#[derive(Debug, Deserialize)]
pub(crate) struct ReuseQuery {
    #[serde(default = "default_limit")]
    limit: usize,
    candidate_ref: String,
}

fn default_limit() -> usize {
    100
}

fn bounded_limit(limit: usize) -> usize {
    limit.clamp(1, 1000)
}

fn persistence_error(error: ProductPersistenceError) -> (StatusCode, Json<serde_json::Value>) {
    let (status, kind) = match error {
        ProductPersistenceError::NotFound(_) => (StatusCode::NOT_FOUND, "not_found"),
        ProductPersistenceError::Conflict(_) => (StatusCode::CONFLICT, "conflict"),
        ProductPersistenceError::Invalid(_) => (StatusCode::BAD_REQUEST, "invalid"),
        ProductPersistenceError::Backend(_) => {
            (StatusCode::INTERNAL_SERVER_ERROR, "persistence_error")
        }
    };
    (
        status,
        Json(serde_json::json!({"error": kind, "message": error.to_string()})),
    )
}

pub(crate) async fn get_product(
    State(state): State<AppState>,
    Path(product_id): Path<String>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let product = state
        .product
        .get_product(&product_id)
        .await
        .map_err(persistence_error)?
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({"error":"not_found","product_id":product_id})),
            )
        })?;
    Ok(Json(serde_json::json!({"product": product})))
}

pub(crate) async fn list_baseline_entities(
    State(state): State<AppState>,
    Path((product_id, baseline_id)): Path<(String, String)>,
    Query(query): Query<LimitQuery>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let entities = state
        .product
        .list_baseline_entities(&product_id, &baseline_id, bounded_limit(query.limit))
        .await
        .map_err(persistence_error)?;
    Ok(Json(serde_json::json!({
        "product_id": product_id,
        "baseline_id": baseline_id,
        "entities": entities,
        "count": entities.len()
    })))
}

pub(crate) async fn list_observations(
    State(state): State<AppState>,
    Path((product_id, baseline_id)): Path<(String, String)>,
    Query(query): Query<ObservationQuery>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let observations = state
        .product
        .list_observations(
            &product_id,
            &baseline_id,
            query.subject_local_id.as_deref(),
            bounded_limit(query.limit),
        )
        .await
        .map_err(persistence_error)?;
    Ok(Json(serde_json::json!({
        "product_id": product_id,
        "baseline_id": baseline_id,
        "subject_local_id": query.subject_local_id,
        "observations": observations,
        "count": observations.len()
    })))
}

pub(crate) async fn list_reuse_decisions(
    State(state): State<AppState>,
    Path((product_id, baseline_id)): Path<(String, String)>,
    Query(query): Query<ReuseQuery>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    // Baseline membership is product-scoped in the persistence port. Resolve it
    // first so a path that names product A cannot project reuse decisions for a
    // baseline owned by product B.
    state
        .product
        .list_baseline_entities(&product_id, &baseline_id, 1)
        .await
        .map_err(persistence_error)?;

    let decisions = state
        .product
        .list_reuse_decisions_for_target(
            &baseline_id,
            &query.candidate_ref,
            bounded_limit(query.limit),
        )
        .await
        .map_err(persistence_error)?;
    Ok(Json(serde_json::json!({
        "product_id": product_id,
        "baseline_id": baseline_id,
        "candidate_ref": query.candidate_ref,
        "reuse_decisions": decisions,
        "count": decisions.len()
    })))
}

pub(crate) async fn list_invalidations(
    State(state): State<AppState>,
    Path(target_kind): Path<String>,
    Query(query): Query<InvalidationQuery>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let invalidations = state
        .product
        .list_invalidations(
            &target_kind,
            &query.target_ref,
            bounded_limit(query.limit),
        )
        .await
        .map_err(persistence_error)?;
    Ok(Json(serde_json::json!({
        "target_kind": target_kind,
        "target_ref": query.target_ref,
        "invalidations": invalidations,
        "count": invalidations.len()
    })))
}
