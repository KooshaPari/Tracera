//! Product-scoped durable evidence and explainable detector API.
use crate::{
    product::{persistence::*, ProductDetectorSuite},
    store::{StoreError, StoreResult},
    AppState,
};
use axum::{
    extract::{Path, State},
    http::StatusCode,
    routing::get,
    Json, Router,
};
use serde_json::{json, Value};
type Failure = (StatusCode, Json<Value>);
fn failure(status: StatusCode, code: &str) -> Failure {
    (status, Json(json!({"error":code})))
}
async fn bounded<T>(work: impl std::future::Future<Output = StoreResult<T>>) -> Result<T, Failure> {
    tokio::time::timeout(std::time::Duration::from_secs(5), work)
        .await
        .map_err(|_| failure(StatusCode::SERVICE_UNAVAILABLE, "product_query_timeout"))?
        .map_err(|error| match error {
            StoreError::Conflict(_) => failure(StatusCode::CONFLICT, "immutable_evidence_conflict"),
            StoreError::Database(_) => {
                failure(StatusCode::SERVICE_UNAVAILABLE, "product_store_unavailable")
            }
            StoreError::UnsupportedOperation(_) => {
                failure(StatusCode::NOT_IMPLEMENTED, "product_store_unsupported")
            }
        })
}
async fn ingest(
    State(state): State<AppState>,
    Path((product, baseline)): Path<(String, u64)>,
    Json(batch): Json<ProductObservationBatch>,
) -> Result<Json<ProductIngestReceipt>, Failure> {
    if batch.product_id.as_str() != product || batch.baseline.number() != baseline {
        return Err(failure(
            StatusCode::UNPROCESSABLE_ENTITY,
            "product_scope_mismatch",
        ));
    }
    batch
        .validate()
        .map_err(|_| failure(StatusCode::UNPROCESSABLE_ENTITY, "invalid_product_batch"))?;
    bounded(state.store.ingest_product_observations(batch))
        .await
        .map(Json)
}
async fn model(
    state: &AppState,
    product: String,
    baseline: u64,
) -> Result<ProductObservationModel, Failure> {
    if baseline > i64::MAX as u64 {
        return Err(failure(StatusCode::BAD_REQUEST, "invalid_baseline"));
    }
    bounded(state.store.product_observations(product, baseline))
        .await?
        .ok_or_else(|| failure(StatusCode::NOT_FOUND, "product_baseline_not_found"))
}
async fn read(
    State(state): State<AppState>,
    Path((product, baseline)): Path<(String, u64)>,
) -> Result<Json<ProductObservationModel>, Failure> {
    model(&state, product, baseline).await.map(Json)
}
async fn findings(
    State(state): State<AppState>,
    Path((product, baseline)): Path<(String, u64)>,
) -> Result<Json<crate::product::DetectorResult>, Failure> {
    let model = model(&state, product, baseline).await?;
    Ok(Json(ProductDetectorSuite::new(86400).run(
        &model.product_id,
        &model.intents,
        &model.observations,
    )))
}
pub(crate) fn routes() -> Router<AppState> {
    Router::new()
        .route(
            "/api/v1/products/{product}/baselines/{baseline}/observations",
            get(read).post(ingest),
        )
        .route(
            "/api/v1/products/{product}/baselines/{baseline}/findings",
            get(findings),
        )
}
#[cfg(test)]
#[path = "product_observation_tests.rs"]
mod tests;
