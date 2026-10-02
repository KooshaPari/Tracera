use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use serde::Deserialize;

use crate::{
    product::{application::MAX_PRODUCT_READ_LIMIT, ProductPersistenceError},
    AppState,
};

#[derive(Debug, Deserialize)]
pub(crate) struct LimitQuery {
    #[serde(default = "default_limit")]
    limit: u32,
}

#[derive(Debug, Deserialize)]
pub(crate) struct ObservationQuery {
    #[serde(default = "default_limit")]
    limit: u32,
    subject_local_id: Option<String>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct InvalidationQuery {
    #[serde(default = "default_limit")]
    limit: u32,
    target_ref: String,
}

#[derive(Debug, Deserialize)]
pub(crate) struct ReuseQuery {
    #[serde(default = "default_limit")]
    limit: u32,
    candidate_ref: String,
}

fn default_limit() -> u32 {
    100
}

fn bounded_limit(limit: u32) -> u32 {
    limit.clamp(1, MAX_PRODUCT_READ_LIMIT)
}

/// These are bounded reads, not cursor APIs. Reaching the limit leaves
/// completeness unproven, even when the true count happens to equal the limit.
fn page_info(count: usize, limit: u32) -> serde_json::Value {
    let complete = count < limit as usize;
    serde_json::json!({
        "limit": limit,
        "returned": count,
        "complete": complete,
        "completeness": if complete { "complete" } else { "unknown_at_limit" },
        "pagination_supported": false,
        "continuation": null
    })
}

fn persistence_error(error: ProductPersistenceError) -> (StatusCode, Json<serde_json::Value>) {
    let (status, kind) = match &error {
        ProductPersistenceError::NotFound(_) => (StatusCode::NOT_FOUND, "not_found"),
        ProductPersistenceError::Conflict(_) => (StatusCode::CONFLICT, "conflict"),
        ProductPersistenceError::Invalid(_) => (StatusCode::BAD_REQUEST, "invalid"),
        ProductPersistenceError::Backend(_) => {
            (StatusCode::INTERNAL_SERVER_ERROR, "persistence_error")
        }
    };
    let message = if matches!(&error, ProductPersistenceError::Backend(_)) {
        tracing::error!(error = %error, "product persistence request failed");
        "product persistence unavailable".to_string()
    } else {
        error.to_string()
    };
    (
        status,
        Json(serde_json::json!({"error": kind, "message": message})),
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
    let limit = bounded_limit(query.limit);
    let entities = state
        .product
        .list_baseline_entities(&product_id, &baseline_id, limit)
        .await
        .map_err(persistence_error)?;
    let count = entities.len();
    Ok(Json(serde_json::json!({
        "product_id": product_id,
        "baseline_id": baseline_id,
        "entities": entities,
        "count": count,
        "page": page_info(count, limit)
    })))
}

pub(crate) async fn list_observations(
    State(state): State<AppState>,
    Path((product_id, baseline_id)): Path<(String, String)>,
    Query(query): Query<ObservationQuery>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let limit = bounded_limit(query.limit);
    let observations = state
        .product
        .list_observations(
            &product_id,
            &baseline_id,
            query.subject_local_id.as_deref(),
            limit,
        )
        .await
        .map_err(persistence_error)?;
    let count = observations.len();
    Ok(Json(serde_json::json!({
        "product_id": product_id,
        "baseline_id": baseline_id,
        "subject_local_id": query.subject_local_id,
        "observations": observations,
        "count": count,
        "page": page_info(count, limit)
    })))
}

pub(crate) async fn list_reuse_decisions(
    State(state): State<AppState>,
    Path((product_id, baseline_id)): Path<(String, String)>,
    Query(query): Query<ReuseQuery>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let limit = bounded_limit(query.limit);
    // Product scope is part of the application/port call, not an empty-list probe.
    let decisions = state
        .product
        .list_reuse_decisions_for_target(&product_id, &baseline_id, &query.candidate_ref, limit)
        .await
        .map_err(persistence_error)?;
    let count = decisions.len();
    Ok(Json(serde_json::json!({
        "product_id": product_id,
        "baseline_id": baseline_id,
        "candidate_ref": query.candidate_ref,
        "reuse_decisions": decisions,
        "count": count,
        "page": page_info(count, limit)
    })))
}

pub(crate) async fn list_invalidations(
    State(state): State<AppState>,
    Path(target_kind): Path<String>,
    Query(query): Query<InvalidationQuery>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let limit = bounded_limit(query.limit);
    let invalidations = state
        .product
        .list_invalidations(&target_kind, &query.target_ref, limit)
        .await
        .map_err(persistence_error)?;
    let count = invalidations.len();
    Ok(Json(serde_json::json!({
        "target_kind": target_kind,
        "target_ref": query.target_ref,
        "invalidations": invalidations,
        "count": count,
        "page": page_info(count, limit)
    })))
}

#[cfg(test)]
mod tests;
