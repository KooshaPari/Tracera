//! SPEC-009 request contract for AgilePlus governance ingestion.
//!
//! Kept separate from the HTTP handler so the accepted schema, the entity
//! mapping and the fail-closed validation rules can be unit-tested without a
//! router. See `docs/specs/009-agileplus-tracera-governance-pipeline.md`.

use axum::http::StatusCode;
use serde::Deserialize;
use serde_json::Value;
use std::hash::{Hash, Hasher};

pub(crate) const AGILEPLUS_TOKEN_ENV: &str = "TRACERA_AGILEPLUS_TOKEN";
pub(crate) const AGILEPLUS_TOKEN_HEADER: &str = "x-agileplus-token";
pub(crate) const IDEMPOTENCY_HEADER: &str = "x-idempotency-key";
/// Accepted contract versions. Unknown versions are rejected, never coerced.
pub(crate) const ACCEPTED_VERSIONS: &[&str] = &["2026-08-30"];
/// Maximum entities per request (bounding work per accepted call).
pub(crate) const MAX_ENTITIES: usize = 500;

/// A fail-closed rejection with the HTTP status the handler must return.
#[derive(Debug, PartialEq, Eq)]
pub(crate) struct Rejection {
    pub(crate) status: StatusCode,
    pub(crate) code: &'static str,
    pub(crate) message: String,
}

impl Rejection {
    fn new(status: StatusCode, code: &'static str, message: impl Into<String>) -> Self {
        Self {
            status,
            code,
            message: message.into(),
        }
    }

    pub(crate) fn unprocessable(code: &'static str, message: impl Into<String>) -> Self {
        Self::new(StatusCode::UNPROCESSABLE_ENTITY, code, message)
    }
}

#[derive(Debug, Deserialize)]
pub(crate) struct Envelope {
    pub(crate) source: String,
    pub(crate) version: String,
    #[serde(default)]
    pub(crate) entities: Vec<Entity>,
    #[serde(default)]
    pub(crate) trace_links: Vec<TraceLink>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct Entity {
    #[serde(rename = "type")]
    pub(crate) entity_type: String,
    pub(crate) agileplus_id: String,
    pub(crate) title: String,
    #[serde(default)]
    pub(crate) body: Value,
    #[serde(default)]
    pub(crate) metadata: Metadata,
}

#[derive(Debug, Default, Deserialize)]
pub(crate) struct Metadata {
    #[serde(default)]
    pub(crate) author: Option<String>,
    #[serde(default)]
    pub(crate) status: Option<String>,
    #[serde(default)]
    pub(crate) version: Option<i64>,
    #[serde(default)]
    pub(crate) decided_at: Option<String>,
    #[serde(default)]
    pub(crate) verified: Option<bool>,
    #[serde(default)]
    pub(crate) product_verified: Option<bool>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct TraceLink {
    pub(crate) source_id: String,
    pub(crate) target_id: String,
    pub(crate) relation: String,
    #[serde(default = "default_confidence")]
    pub(crate) confidence: f64,
}

fn default_confidence() -> f64 {
    1.0
}

/// Map an AgilePlus entity type onto the canonical SWEE node kind.
///
/// The SWEE taxonomy is the persisted vocabulary; the SPEC-009 label is
/// recorded in node metadata as `agileplus_entity` so both vocabularies remain
/// recoverable.
pub(crate) fn node_kind(entity_type: &str) -> Option<&'static str> {
    match entity_type {
        "spec" => Some("specification"),
        "work_item" => Some("story"),
        "governance_decision" => Some("change_request"),
        "research_doc" => Some("evidence"),
        _ => None,
    }
}

/// SPEC-009 external-id prefix for a mapped entity type.
pub(crate) fn external_prefix(entity_type: &str) -> &'static str {
    match entity_type {
        "governance_decision" => "ap-gov:",
        "research_doc" => "ap-rd:",
        _ => "ap:",
    }
}

/// Constant-time byte comparison for short shared secrets.
pub(crate) fn constant_time_equal(left: &[u8], right: &[u8]) -> bool {
    let mut difference = left.len() ^ right.len();
    for index in 0..left.len().max(right.len()) {
        difference |= usize::from(left.get(index).copied().unwrap_or_default())
            ^ usize::from(right.get(index).copied().unwrap_or_default());
    }
    difference == 0
}

/// Body fingerprint used to distinguish an identical replay from a conflicting
/// replay on the same idempotency key. `serde_json::Value` serializes maps in
/// sorted key order, so this is stable across processes.
pub(crate) fn fingerprint(value: &Value) -> String {
    let canonical = serde_json::to_string(value).unwrap_or_default();
    let mut hasher = std::collections::hash_map::DefaultHasher::new();
    canonical.hash(&mut hasher);
    format!("{:016x}", hasher.finish())
}

/// A parsed envelope whose entities all passed validation, paired with the SWEE
/// node kind each entity maps onto.
pub(crate) struct ValidatedEnvelope {
    pub(crate) envelope: Envelope,
    pub(crate) kinds: Vec<&'static str>,
}

/// Parse and validate a SPEC-009 body.
///
/// Validation is all-or-nothing: a single defective entity rejects the request,
/// because partially ingested governance state cannot be verified.
pub(crate) fn validate(raw: &Value) -> Result<ValidatedEnvelope, Rejection> {
    let envelope: Envelope = serde_json::from_value(raw.clone()).map_err(|err| {
        Rejection::unprocessable(
            "agileplus_invalid_envelope",
            format!("body does not match SPEC-009: {err}"),
        )
    })?;

    if envelope.source != "agileplus" {
        return Err(Rejection::unprocessable(
            "agileplus_wrong_producer",
            "source must be \"agileplus\"; AgCord payloads belong on POST /ingest/agcord",
        ));
    }
    if !ACCEPTED_VERSIONS.contains(&envelope.version.as_str()) {
        return Err(Rejection::unprocessable(
            "agileplus_unsupported_version",
            format!("accepted versions: {}", ACCEPTED_VERSIONS.join(", ")),
        ));
    }
    if envelope.entities.is_empty() {
        return Err(Rejection::unprocessable(
            "agileplus_empty_entities",
            "entities[] must contain at least one governance entity",
        ));
    }
    if envelope.entities.len() > MAX_ENTITIES {
        return Err(Rejection::unprocessable(
            "agileplus_too_many_entities",
            format!("at most {MAX_ENTITIES} entities per request"),
        ));
    }

    let mut kinds = Vec::with_capacity(envelope.entities.len());
    for entity in &envelope.entities {
        kinds.push(validate_entity(entity)?);
    }
    for link in &envelope.trace_links {
        if !(0.0..=1.0).contains(&link.confidence) {
            return Err(Rejection::unprocessable(
                "agileplus_invalid_confidence",
                "trace link confidence must be between 0.0 and 1.0",
            ));
        }
    }

    Ok(ValidatedEnvelope { envelope, kinds })
}

fn validate_entity(entity: &Entity) -> Result<&'static str, Rejection> {
    let Some(kind) = node_kind(&entity.entity_type) else {
        return Err(Rejection::unprocessable(
            "agileplus_invalid_entity_type",
            format!(
                "{}: type `{}` is not one of spec|work_item|governance_decision|research_doc",
                entity.agileplus_id, entity.entity_type
            ),
        ));
    };
    if entity.agileplus_id.trim().is_empty() || !entity.agileplus_id.starts_with("AP-") {
        return Err(Rejection::unprocessable(
            "agileplus_invalid_id",
            format!(
                "{}: agileplus_id must be a non-empty AP-* reference",
                entity.agileplus_id
            ),
        ));
    }
    if entity.title.trim().is_empty() {
        return Err(Rejection::unprocessable(
            "agileplus_missing_title",
            format!("{}: title is required", entity.agileplus_id),
        ));
    }
    if entity.metadata.version.is_none_or(|version| version < 1) {
        return Err(Rejection::unprocessable(
            "agileplus_missing_revision",
            format!(
                "{}: metadata.version must be an integer >= 1",
                entity.agileplus_id
            ),
        ));
    }
    // AgilePlus owns governance; it may not assert Tracera product verification.
    let asserts_verification = entity.metadata.verified == Some(true)
        || entity.metadata.product_verified == Some(true)
        || entity.body.get("verified").and_then(Value::as_bool) == Some(true);
    if asserts_verification {
        return Err(Rejection::unprocessable(
            "agileplus_unaccepted_claim",
            format!(
                "{}: AgilePlus may not assert Tracera product verification",
                entity.agileplus_id
            ),
        ));
    }
    // A governance approval needs attributable provenance.
    let approval_without_provenance = entity.entity_type == "governance_decision"
        && entity.metadata.status.as_deref() == Some("approved")
        && (entity
            .metadata
            .author
            .as_deref()
            .unwrap_or_default()
            .is_empty()
            || entity
                .metadata
                .decided_at
                .as_deref()
                .unwrap_or_default()
                .is_empty());
    if approval_without_provenance {
        return Err(Rejection::unprocessable(
            "agileplus_forged_approval",
            format!(
                "{}: approval requires metadata.author and metadata.decided_at",
                entity.agileplus_id
            ),
        ));
    }
    Ok(kind)
}
