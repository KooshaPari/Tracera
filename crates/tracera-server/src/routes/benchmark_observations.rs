//! Connect the existing benchmark envelope adapter to durable product evidence.
//! Product/capability assignment is explicit; run/session identities remain provenance.
use crate::{
    product::{
        observation::BenchmarkCausality, persistence::ProductObservationBatch, AcceptedIntent,
        BaselineRevision, Observation, ObservationKind, ObservationResult, ObservationSource,
        ProductId,
    },
    AppState,
};
use axum::{
    extract::{Path, State},
    http::StatusCode,
    routing::post,
    Json, Router,
};
use chrono::{DateTime, Utc};
use serde::Deserialize;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    product_id: ProductId,
    baseline: BaselineRevision,
    capability_id: String,
    intents: Vec<AcceptedIntent>,
    /// Source observation time, retained on exact retry; not the HTTP request time.
    recorded_at: DateTime<Utc>,
    envelope: Value,
}
fn invalid() -> (StatusCode, Json<Value>) {
    (
        StatusCode::UNPROCESSABLE_ENTITY,
        Json(json!({"error":"invalid_benchmark_envelope"})),
    )
}
fn convert(input: Request) -> Result<ProductObservationBatch, (StatusCode, Json<Value>)> {
    // Reuse the already-established run/session/attempt/status/replay validation.
    let issue = crate::ingest::benchmark_run_to_issue(&input.envelope).map_err(|_| invalid())?;
    let field = |key: &str| {
        input
            .envelope
            .get(key)
            .and_then(Value::as_str)
            .ok_or_else(invalid)
    };
    let schema = field("schema_version")?;
    if schema != "1.0.0" {
        return Err(invalid());
    }
    let tenant = field("tenant_id")?;
    if tenant.is_empty()
        || tenant.len() > 64
        || !tenant
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_')
    {
        return Err(invalid());
    }
    let run_id = field("run_id")?;
    let session_id = field("session_id")?;
    let attempt_id = field("attempt_id")?;
    let replay_hash = input
        .envelope
        .pointer("/result/replay_hash")
        .and_then(Value::as_str)
        .ok_or_else(invalid)?;
    let envelope_bytes = serde_json::to_vec(&input.envelope).map_err(|_| invalid())?;
    let causality = BenchmarkCausality {
        tenant_id: tenant.into(),
        run_id: run_id.into(),
        session_id: session_id.into(),
        attempt_id: attempt_id.into(),
        replay_hash: replay_hash.into(),
        envelope_sha256: Sha256::digest(envelope_bytes)
            .iter()
            .map(|byte| format!("{byte:02x}"))
            .collect(),
    };
    let id = format!("{tenant}:{run_id}:{attempt_id}");
    let observation = Observation {
        id: id.clone(),
        product_id: input.product_id.clone(),
        baseline: input.baseline,
        kind: ObservationKind::TestResult,
        result: match issue.status.as_str() {
            "passed" => ObservationResult::Passed,
            "failed" | "timeout" => ObservationResult::Failed,
            "cancelled" => ObservationResult::Unknown,
            _ => return Err(invalid()),
        },
        source: ObservationSource {
            collector: "helios-benchmark-envelope".into(),
            version: schema.into(),
            artifact_ref: Some(issue.url),
            causality: Some(causality),
        },
        recorded_at: input.recorded_at,
        capability_id: Some(input.capability_id),
    };
    Ok(ProductObservationBatch {
        product_id: input.product_id,
        baseline: input.baseline,
        idempotency_key: id,
        intents: input.intents,
        observations: vec![observation],
    })
}
async fn ingest(
    State(state): State<AppState>,
    Path(scope): Path<(String, u64)>,
    Json(input): Json<Request>,
) -> Result<Json<crate::product::persistence::ProductIngestReceipt>, (StatusCode, Json<Value>)> {
    let batch = convert(input)?;
    super::product_observation_routes::ingest(State(state), Path(scope), Json(batch)).await
}
pub(crate) fn routes() -> Router<AppState> {
    Router::new().route(
        "/api/v1/products/{product}/baselines/{baseline}/benchmark-observations",
        post(ingest),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn existing_envelope_statuses_preserve_outcome_semantics() {
        for (status, expected) in [
            ("passed", ObservationResult::Passed),
            ("failed", ObservationResult::Failed),
            ("timeout", ObservationResult::Failed),
            ("cancelled", ObservationResult::Unknown),
        ] {
            let mut envelope: Value =
                serde_json::from_str(include_str!("../../testdata/helios-benchmark-run.json"))
                    .unwrap();
            envelope["result"]["status"] = json!(status);
            let request: Request = serde_json::from_value(json!({"product_id":"product","baseline":1,"capability_id":"capability","intents":[],"recorded_at":"2026-10-16T00:00:00Z","envelope":envelope})).unwrap();
            let batch = convert(request).unwrap();
            assert_eq!(batch.observations[0].result, expected);
            assert_eq!(
                batch.observations[0]
                    .source
                    .causality
                    .as_ref()
                    .unwrap()
                    .session_id,
                envelope["session_id"]
            );
        }
    }
}
