//! AgilePlus governance ingestion — SPEC-009 HTTP handler.
//!
//! This is the **distinct** AgilePlus endpoint (`POST /api/v1/ingest/agileplus`).
//! It is deliberately not the AgCord path: AgCord payloads (`items[]`) are
//! served by `POST /ingest/agcord`, so a 200 from here is evidence of governed
//! AgilePlus acceptance only.
//!
//! Failure modes are all fail-closed:
//!
//! | Condition                        | Status |
//! | -------------------------------- | ------ |
//! | ingest token not configured      | 503    |
//! | missing / invalid token          | 401    |
//! | malformed JSON                   | 400    |
//! | missing / non-UUIDv4 idempotency | 400    |
//! | wrong producer or bad entity     | 422    |
//! | consumed key, replay, stale rev  | 409    |
//! | store cannot record provenance   | 501    |
//!
//! AgilePlus owns governance/acceptance state; Tracera owns product state and
//! evidence. Nothing here marks a Tracera product capability verified — an
//! incoming `work_item` with status `done` is stored as governance evidence
//! only, and the response always reports `product_capabilities_verified: 0`.

use axum::{
    extract::{rejection::JsonRejection, State},
    http::{HeaderMap, StatusCode},
    response::IntoResponse,
    Json,
};
use chrono::Utc;
use serde_json::{json, Value};
use std::collections::HashMap;

use super::agileplus_contract::{
    constant_time_equal, external_prefix, fingerprint, validate, Rejection, ValidatedEnvelope,
    AGILEPLUS_TOKEN_ENV, AGILEPLUS_TOKEN_HEADER, IDEMPOTENCY_HEADER,
};
use crate::store::{AgilePlusIngestRecord, AgilePlusRevision, StoreError};

use super::super::AppState;

fn rejection(status: StatusCode, code: &str, message: &str) -> (StatusCode, Json<Value>) {
    (
        status,
        Json(json!({"status": "rejected", "error": code, "message": message})),
    )
}

fn rejected(rejection_value: &Rejection) -> (StatusCode, Json<Value>) {
    rejection(
        rejection_value.status,
        rejection_value.code,
        &rejection_value.message,
    )
}

fn store_failure(error: StoreError) -> (StatusCode, Json<Value>) {
    match error {
        StoreError::UnsupportedOperation(operation) => rejection(
            StatusCode::NOT_IMPLEMENTED,
            "agileplus_provenance_unsupported",
            &format!("store backend cannot record `{operation}`"),
        ),
        StoreError::Database(message) => {
            tracing::error!("AgilePlus ingest store failure: {message}");
            rejection(
                StatusCode::INTERNAL_SERVER_ERROR,
                "agileplus_store_error",
                "provenance persistence failed",
            )
        }
    }
}

fn idempotency_key(headers: &HeaderMap) -> Result<String, (StatusCode, Json<Value>)> {
    let key = headers
        .get(IDEMPOTENCY_HEADER)
        .and_then(|value| value.to_str().ok())
        .unwrap_or_default()
        .trim()
        .to_string();
    match uuid::Uuid::parse_str(&key) {
        Ok(parsed) if parsed.get_version_num() == 4 => Ok(key),
        _ => Err(rejection(
            StatusCode::BAD_REQUEST,
            "agileplus_missing_idempotency_key",
            "X-Idempotency-Key must be a UUID v4",
        )),
    }
}

/// Authenticate the producer. Returns `Err` with the response to send.
fn authenticate(headers: &HeaderMap) -> Result<(), (StatusCode, Json<Value>)> {
    let Ok(expected) = std::env::var(AGILEPLUS_TOKEN_ENV) else {
        return Err(rejection(
            StatusCode::SERVICE_UNAVAILABLE,
            "agileplus_ingest_not_configured",
            &format!("set {AGILEPLUS_TOKEN_ENV} to enable AgilePlus ingestion"),
        ));
    };
    let provided = headers
        .get(AGILEPLUS_TOKEN_HEADER)
        .and_then(|value| value.to_str().ok())
        .unwrap_or_default();
    if provided.is_empty() || !constant_time_equal(provided.as_bytes(), expected.as_bytes()) {
        return Err(rejection(
            StatusCode::UNAUTHORIZED,
            "agileplus_unauthorized",
            "missing or invalid X-AgilePlus-Token",
        ));
    }
    Ok(())
}

/// `POST /api/v1/ingest/agileplus` — SPEC-009 governed ingestion.
pub(crate) async fn ingest_agileplus(
    State(state): State<AppState>,
    headers: HeaderMap,
    body: Result<Json<Value>, JsonRejection>,
) -> impl IntoResponse {
    if let Err(response) = authenticate(&headers) {
        return response;
    }
    let Ok(Json(raw)) = body else {
        return rejection(
            StatusCode::BAD_REQUEST,
            "agileplus_malformed_body",
            "request body must be JSON",
        );
    };
    let key = match idempotency_key(&headers) {
        Ok(key) => key,
        Err(response) => return response,
    };
    let ValidatedEnvelope { envelope, kinds } = match validate(&raw) {
        Ok(validated) => validated,
        Err(rejection_value) => return rejected(&rejection_value),
    };

    // A consumed key is a conflict before anything is written. The
    // fingerprint lets an identical replay be distinguished from a
    // conflicting replay instead of both looking like "duplicate".
    match state.store.get_agileplus_ingest_key(key.clone()).await {
        Ok(Some(previous)) => {
            let identical = previous.body_fingerprint == fingerprint(&raw);
            return (
                StatusCode::CONFLICT,
                Json(json!({
                    "status": "rejected",
                    "error": "agileplus_idempotency_key_consumed",
                    "message": "X-Idempotency-Key was already consumed",
                    "ingestion_id": previous.ingestion_id,
                    "identical_replay": identical,
                    "conflicting_replay": !identical,
                })),
            );
        }
        Ok(None) => {}
        Err(err) => return store_failure(err),
    }
    // A revision must strictly advance what was already accepted.
    for entity in &envelope.entities {
        let Some(incoming) = entity.metadata.version else {
            continue;
        };
        match state
            .store
            .get_agileplus_revision(entity.agileplus_id.clone())
            .await
        {
            Ok(Some(accepted)) if incoming <= accepted => {
                return rejection(
                    StatusCode::CONFLICT,
                    "agileplus_stale_revision",
                    &format!(
                        "{}: revision {incoming} does not advance accepted revision {accepted}",
                        entity.agileplus_id
                    ),
                );
            }
            Ok(_) => {}
            Err(err) => return store_failure(err),
        }
    }

    let now = Utc::now();
    let ingestion_id = format!("ING-{}", uuid::Uuid::new_v4());
    let mut node_ids: HashMap<String, String> = HashMap::new();
    let mut revisions: Vec<AgilePlusRevision> = Vec::new();
    for (entity, kind) in envelope.entities.iter().zip(kinds.iter()) {
        let metadata = json!({
            "agileplus_id": entity.agileplus_id,
            "external_id": format!("{}{}", external_prefix(&entity.entity_type), entity.agileplus_id),
            "agileplus_entity": entity.entity_type,
            "source": "agileplus",
            "revision": entity.metadata.version,
            "status": entity.metadata.status,
            "author": entity.metadata.author,
            "decided_at": entity.metadata.decided_at,
            "governance_owner": "agileplus",
            "product_state_owner": "tracera",
            "capability_verified": false,
            "ingestion_id": ingestion_id,
            "body": entity.body,
        });
        let node_id = match state
            .store
            .create_swee_node((*kind).to_string(), entity.title.clone(), metadata, now)
            .await
        {
            Ok(node_id) => node_id,
            Err(err) => return store_failure(err),
        };
        node_ids.insert(entity.agileplus_id.clone(), node_id.clone());
        revisions.push(AgilePlusRevision {
            agileplus_id: entity.agileplus_id.clone(),
            entity_type: entity.entity_type.clone(),
            revision: entity.metadata.version.unwrap_or_default(),
            node_id,
        });
    }

    // Only fully resolved links become edges. A link whose endpoint is not in
    // this request is reported, never fabricated.
    let mut trace_links_created = 0usize;
    let mut unresolved: Vec<Value> = Vec::new();
    for link in &envelope.trace_links {
        let (Some(source_node), Some(target_node)) =
            (node_ids.get(&link.source_id), node_ids.get(&link.target_id))
        else {
            unresolved.push(json!({
                "source_id": link.source_id,
                "target_id": link.target_id,
                "relation": link.relation,
                "reason": "endpoint_not_in_this_request",
            }));
            continue;
        };
        let edge_metadata = json!({
            "agileplus_source_id": link.source_id,
            "agileplus_target_id": link.target_id,
            "ingestion_id": ingestion_id,
        });
        if let Err(err) = state
            .store
            .create_swee_edge(
                link.relation.clone(),
                source_node.clone(),
                target_node.clone(),
                link.confidence,
                "agileplus".to_string(),
                edge_metadata,
                now,
            )
            .await
        {
            return store_failure(err);
        }
        trace_links_created += 1;
    }

    let record = AgilePlusIngestRecord {
        idempotency_key: key,
        body_fingerprint: fingerprint(&raw),
        ingestion_id: ingestion_id.clone(),
        revisions,
    };
    if let Err(err) = state.store.record_agileplus_ingest(record, now).await {
        // Never report acceptance when the provenance receipt did not land.
        return rejection(
            StatusCode::CONFLICT,
            "agileplus_idempotency_key_consumed",
            &format!("idempotency receipt could not be recorded: {err}"),
        );
    }

    (
        StatusCode::OK,
        Json(json!({
            "status": "accepted",
            "ingestion_id": ingestion_id,
            "entities_processed": envelope.entities.len(),
            "entities_accepted": envelope.entities.len(),
            "entities_rejected": 0,
            "rejections": [],
            "trace_links_created": trace_links_created,
            "trace_links_unresolved": unresolved,
            "coverage_delta": {
                "nodes_added": envelope.entities.len(),
                "edges_added": trace_links_created,
            },
            "ownership": {
                "governance": "agileplus",
                "product_state_and_evidence": "tracera",
            },
            "product_capabilities_verified": 0,
            "not_implemented": ["memory_distillation", "coverage_score_recomputation"],
        })),
    )
}

#[cfg(test)]
#[path = "agileplus_tests.rs"]
mod tests;
