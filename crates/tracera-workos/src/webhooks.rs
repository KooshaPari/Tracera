//! WorkOS webhook signature verification + event dispatch.
//!
//! WorkOS sends webhooks with these HTTP headers (all required):
//! - `WorkOS-Signature`: `t=<unix_ts>,v1=<hex_hmac>` (multiple `v1=` allowed
//!   during a key rotation window)
//! - `WorkOS-Event-Id`: a unique id for this delivery
//! - `WorkOS-Event-Type`: e.g. `dsync.user.created`, `audit.log.created`
//!
//! Verification: compute `HMAC_SHA256(secret, "<unix_ts>.<raw_body>")`, hex-encode,
//! and compare in constant time against any of the `v1=` values. Also enforce a
//! timestamp tolerance (default 5 minutes) to defeat replay.

use chrono::Utc;
use hmac::{Hmac, Mac};
use serde::{Deserialize, Serialize};
use sha2::Sha256;
use std::collections::HashSet;
use subtle::ConstantTimeEq;

use crate::error::{WorkOSError, WorkOSResult};

type HmacSha256 = Hmac<Sha256>;

/// Default replay-protection window. Production tenants should keep this ≤ 300s.
pub const DEFAULT_TOLERANCE_SECONDS: i64 = 300;

/// The `WorkOS-Signature` header parsed into its constituent parts.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SignatureHeader {
    pub timestamp: i64,
    pub v1_signatures: Vec<String>,
}

impl SignatureHeader {
    /// Parse a header value like `t=1700000000,v1=abc...,v1=def...`.
    pub fn parse(header_value: &str) -> WorkOSResult<Self> {
        let mut timestamp: Option<i64> = None;
        let mut v1_signatures: Vec<String> = Vec::new();
        for part in header_value.split(',') {
            let part = part.trim();
            if part.is_empty() {
                continue;
            }
            let (key, value) = part.split_once('=').ok_or_else(|| {
                WorkOSError::WebhookSignatureHeader(format!(
                    "missing '=' in segment {part:?}"
                ))
            })?;
            match key.trim() {
                "t" => {
                    timestamp = Some(value.trim().parse::<i64>().map_err(|e| {
                        WorkOSError::WebhookSignatureHeader(format!(
                            "invalid timestamp {value:?}: {e}"
                        ))
                    })?);
                }
                "v1" => v1_signatures.push(value.trim().to_string()),
                _ => {
                    // Future-proofing — silently ignore unknown keys.
                }
            }
        }
        let timestamp = timestamp
            .ok_or_else(|| WorkOSError::WebhookSignatureHeader("missing t= segment".into()))?;
        if v1_signatures.is_empty() {
            return Err(WorkOSError::WebhookSignatureHeader(
                "missing v1= segment".into(),
            ));
        }
        Ok(Self {
            timestamp,
            v1_signatures,
        })
    }
}

/// Verify a webhook request.
///
/// `secret` is the `WORKOS_WEBHOOK_SECRET` from the dashboard (`whsec_*`).
/// `signature_header` is the literal `WorkOS-Signature` value.
/// `body` is the raw bytes of the request body (do not re-serialize or trim).
pub fn verify_signature(
    secret: &str,
    signature_header: &str,
    body: &[u8],
    tolerance_seconds: i64,
    now: chrono::DateTime<chrono::Utc>,
) -> WorkOSResult<()> {
    let parsed = SignatureHeader::parse(signature_header)?;
    let drift = (now.timestamp() - parsed.timestamp).abs();
    if drift > tolerance_seconds {
        return Err(WorkOSError::WebhookTimestampSkew(drift));
    }
    let expected_hex = compute_signature(secret, parsed.timestamp, body);
    for candidate in &parsed.v1_signatures {
        if constant_time_hex_eq(candidate.as_bytes(), expected_hex.as_bytes()) {
            return Ok(());
        }
    }
    Err(WorkOSError::WebhookSignatureInvalid)
}

fn compute_signature(secret: &str, timestamp: i64, body: &[u8]) -> String {
    let mut mac = HmacSha256::new_from_slice(secret.as_bytes())
        .expect("HMAC accepts any key length");
    mac.update(timestamp.to_string().as_bytes());
    mac.update(b".");
    mac.update(body);
    let bytes = mac.finalize().into_bytes();
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

fn constant_time_hex_eq(left: &[u8], right: &[u8]) -> bool {
    // Both inputs must already be valid lowercase hex; reject length mismatch
    // without leaking the length difference.
    if left.len() != right.len() {
        // Use a dummy compare to keep work independent of lengths.
        let _ = left.ct_eq(right);
        return false;
    }
    left.ct_eq(right).into()
}

// ---------------------------------------------------------------------------
// Event types (the subset we dispatch on)
// ---------------------------------------------------------------------------

/// Top-level webhook envelope — fields are stable across event types.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct WebhookEnvelope {
    pub id: String,
    #[serde(rename = "event")]
    pub event_type: String,
    #[serde(default)]
    pub created_at: Option<chrono::DateTime<chrono::Utc>>,
    #[serde(default)]
    pub data: serde_json::Value,
    #[serde(default)]
    pub organization_id: Option<String>,
}

/// Returned by [`dispatch`] describing how the event was routed.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum DispatchResult {
    /// Directory Sync event → [`crate::sync`].
    DirectorySync,
    /// Audit log event → [`crate::audit`].
    AuditLog,
    /// Other event type we don't act on (logged and acknowledged).
    Ignored,
    /// Event type we recognise but haven't implemented a handler for yet.
    Unhandled(String),
}

impl DispatchResult {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::DirectorySync => "directory_sync",
            Self::AuditLog => "audit_log",
            Self::Ignored => "ignored",
            Self::Unhandled(_) => "unhandled",
        }
    }
}

/// Map an event type string to a dispatch bucket.
///
/// We split on the leading prefix because WorkOS's event taxonomy uses dotted
/// namespaces: `dsync.*`, `authentication.*`, `audit.*`, etc.
pub fn dispatch(envelope: &WebhookEnvelope) -> DispatchResult {
    const SUPPORTED: &str = "supported event families: dsync.*, audit.*, authentication.*";
    let event = envelope.event_type.as_str();
    if event.is_empty() {
        return DispatchResult::Ignored;
    }
    // Split on the first '.' to get the family.
    let family = event.split('.').next().unwrap_or("");
    match family {
        "dsync" => DispatchResult::DirectorySync,
        "audit" => DispatchResult::AuditLog,
        // authentication.* events are accepted but not yet handled; we'll log
        // and 200 the request so WorkOS stops retrying.
        "authentication" => DispatchResult::Unhandled(SUPPORTED.to_string()),
        _ => DispatchResult::Ignored,
    }
}

/// List of directory-sync event types we know about. Used by tests and by the
/// handler in `router.rs` to give a clear 4xx response on truly unknown events.
pub fn known_directory_event_types() -> &'static [&'static str] {
    &[
        "dsync.user.created",
        "dsync.user.updated",
        "dsync.user.deleted",
        "dsync.group.created",
        "dsync.group.updated",
        "dsync.group.deleted",
        "dsync.group.user_added",
        "dsync.group.user_removed",
        "dsync.organization.created",
        "dsync.organization.updated",
        "dsync.organization.deleted",
    ]
}

/// List of audit-log event types we know about.
pub fn known_audit_event_types() -> &'static [&'static str] {
    &[
        "audit.log.created",
        "audit.log.updated",
    ]
}

fn known_event_set() -> HashSet<&'static str> {
    let mut s: HashSet<&'static str> = HashSet::new();
    s.extend(known_directory_event_types().iter().copied());
    s.extend(known_audit_event_types().iter().copied());
    s
}

/// Helper used by [`dispatch`] to validate that the event name is one of ours.
/// Returns `true` if the event is in our known set.
pub fn is_known_event(event_type: &str) -> bool {
    known_event_set().contains(event_type)
}

#[cfg(test)]
mod tests {
    use super::*;

    const SECRET: &str = "whsec_test_super_secret";

    fn signed_header(secret: &str, body: &[u8], ts: i64) -> String {
        format!("t={ts},v1={}", compute_signature(secret, ts, body))
    }

    #[test]
    fn signature_header_parses_single_v1() {
        let h = SignatureHeader::parse("t=1700000000,v1=deadbeef").unwrap();
        assert_eq!(h.timestamp, 1700000000);
        assert_eq!(h.v1_signatures, vec!["deadbeef".to_string()]);
    }

    #[test]
    fn signature_header_parses_multiple_v1_during_rotation() {
        let h = SignatureHeader::parse("t=1700000000,v1=aaa,v1=bbb,v1=ccc").unwrap();
        assert_eq!(h.v1_signatures.len(), 3);
    }

    #[test]
    fn signature_header_rejects_missing_timestamp() {
        let err = SignatureHeader::parse("v1=deadbeef").unwrap_err();
        assert!(matches!(err, WorkOSError::WebhookSignatureHeader(_)));
    }

    #[test]
    fn signature_header_rejects_missing_v1() {
        let err = SignatureHeader::parse("t=1700000000").unwrap_err();
        assert!(matches!(err, WorkOSError::WebhookSignatureHeader(_)));
    }

    #[test]
    fn signature_header_rejects_malformed_segment() {
        let err = SignatureHeader::parse("nope").unwrap_err();
        assert!(matches!(err, WorkOSError::WebhookSignatureHeader(_)));
    }

    #[test]
    fn verify_signature_accepts_valid_header() {
        let body = br#"{"event":"dsync.user.created"}"#;
        let now = Utc::now().timestamp();
        let header = signed_header(SECRET, body, now);
        verify_signature(SECRET, &header, body, DEFAULT_TOLERANCE_SECONDS, Utc::now()).unwrap();
    }

    #[test]
    fn verify_signature_rejects_tampered_body() {
        let body = br#"{"event":"dsync.user.created"}"#;
        let now = Utc::now().timestamp();
        let header = signed_header(SECRET, body, now);
        let tampered = br#"{"event":"dsync.user.deleted"}"#;
        let result = verify_signature(SECRET, &header, tampered, DEFAULT_TOLERANCE_SECONDS, Utc::now());
        assert!(matches!(result, Err(WorkOSError::WebhookSignatureInvalid)));
    }

    #[test]
    fn verify_signature_rejects_wrong_secret() {
        let body = br#"{"event":"dsync.user.created"}"#;
        let now = Utc::now().timestamp();
        let header = signed_header(SECRET, body, now);
        let result = verify_signature("not-the-secret", &header, body, DEFAULT_TOLERANCE_SECONDS, Utc::now());
        assert!(matches!(result, Err(WorkOSError::WebhookSignatureInvalid)));
    }

    #[test]
    fn verify_signature_rejects_stale_timestamp() {
        let body = br#"{"event":"dsync.user.created"}"#;
        let ancient = Utc::now().timestamp() - (DEFAULT_TOLERANCE_SECONDS + 60);
        let header = signed_header(SECRET, body, ancient);
        let result = verify_signature(SECRET, &header, body, DEFAULT_TOLERANCE_SECONDS, Utc::now());
        assert!(matches!(result, Err(WorkOSError::WebhookTimestampSkew(_))));
    }

    #[test]
    fn verify_signature_accepts_any_matching_v1_during_rotation() {
        let body = br#"{"event":"dsync.user.created"}"#;
        let now = Utc::now().timestamp();
        let real = compute_signature(SECRET, now, body);
        let header = format!("t={now},v1=00000000000000000000000000000000,v1={real}");
        verify_signature(SECRET, &header, body, DEFAULT_TOLERANCE_SECONDS, Utc::now()).unwrap();
    }

    #[test]
    fn dispatch_routes_dsync_to_directory_sync() {
        let env = WebhookEnvelope {
            id: "evt_01".into(),
            event_type: "dsync.user.created".into(),
            created_at: None,
            data: serde_json::json!({}),
            organization_id: None,
        };
        assert_eq!(dispatch(&env), DispatchResult::DirectorySync);
    }

    #[test]
    fn dispatch_routes_audit_to_audit_log() {
        let env = WebhookEnvelope {
            id: "evt_01".into(),
            event_type: "audit.log.created".into(),
            created_at: None,
            data: serde_json::json!({}),
            organization_id: None,
        };
        assert_eq!(dispatch(&env), DispatchResult::AuditLog);
    }

    #[test]
    fn dispatch_marks_authentication_as_unhandled() {
        let env = WebhookEnvelope {
            id: "evt_01".into(),
            event_type: "authentication.sso_succeeded".into(),
            created_at: None,
            data: serde_json::json!({}),
            organization_id: None,
        };
        assert!(matches!(dispatch(&env), DispatchResult::Unhandled(_)));
    }

    #[test]
    fn dispatch_ignores_unknown_families() {
        let env = WebhookEnvelope {
            id: "evt_01".into(),
            event_type: "connection.activated".into(),
            created_at: None,
            data: serde_json::json!({}),
            organization_id: None,
        };
        assert_eq!(dispatch(&env), DispatchResult::Ignored);
    }

    #[test]
    fn is_known_event_returns_true_for_supported_events() {
        assert!(is_known_event("dsync.user.created"));
        assert!(is_known_event("audit.log.created"));
        assert!(!is_known_event("foo.bar"));
    }

    #[test]
    fn envelope_deserializes_workos_payload() {
        let json = r#"{
            "id": "evt_01",
            "event": "dsync.user.created",
            "created_at": "2026-09-03T12:00:00Z",
            "data": {"id": "user_1", "email": "a@b.co"},
            "organization_id": "org_01"
        }"#;
        let env: WebhookEnvelope = serde_json::from_str(json).unwrap();
        assert_eq!(env.event_type, "dsync.user.created");
        assert_eq!(env.organization_id.as_deref(), Some("org_01"));
    }
}
