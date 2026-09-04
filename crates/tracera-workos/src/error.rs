//! Crate-wide error type for `tracera-workos`.
//!
//! All public functions in this crate return [`Result<T, WorkOSError>`] so that
//! callers (the axum handlers, sync logic, audit ingest) get a single error
//! type to convert into HTTP responses.

use thiserror::Error;

#[derive(Debug, Error)]
pub enum WorkOSError {
    /// Required configuration is missing or malformed.
    #[error("workos config error: {0}")]
    Config(String),

    /// The hosted login URL could not be built (invalid parameters).
    #[error("invalid authorize request: {0}")]
    AuthorizeRequest(String),

    /// ID-token verification failed (bad signature, expired, wrong issuer,
    /// wrong audience, etc.).
    #[error("id token verification failed: {0}")]
    IdTokenInvalid(String),

    /// JWT decoding step (base64) failed before signature check.
    #[error("id token malformed: {0}")]
    IdTokenMalformed(String),

    /// Webhook signature didn't match the expected HMAC.
    #[error("webhook signature mismatch")]
    WebhookSignatureInvalid,

    /// Webhook signature header missing or not parseable.
    #[error("webhook signature header missing or malformed: {0}")]
    WebhookSignatureHeader(String),

    /// Webhook timestamp drift exceeded the configured tolerance.
    #[error("webhook timestamp drift {0}s exceeds tolerance")]
    WebhookTimestampSkew(i64),

    /// Directory event did not contain a recognized resource type.
    #[error("unsupported directory event: {0}")]
    UnsupportedDirectoryEvent(String),

    /// Network/HTTP error talking to WorkOS REST.
    #[error("workos http error: {0}")]
    Http(String),

    /// JSON serialization/deserialization failure.
    #[error("workos json error: {0}")]
    Json(String),

    /// Userinfo lookup failed (token not found, expired, etc.).
    #[error("userinfo lookup failed: {0}")]
    UserinfoFailed(String),
}

/// Convenience result alias.
pub type WorkOSResult<T> = Result<T, WorkOSError>;

impl From<jsonwebtoken::errors::Error> for WorkOSError {
    fn from(value: jsonwebtoken::errors::Error) -> Self {
        // `jsonwebtoken` errors carry useful context — keep the kind-tagged
        // message instead of swallowing it.
        WorkOSError::IdTokenInvalid(value.to_string())
    }
}

impl From<base64::DecodeError> for WorkOSError {
    fn from(value: base64::DecodeError) -> Self {
        WorkOSError::IdTokenMalformed(value.to_string())
    }
}

impl From<reqwest::Error> for WorkOSError {
    fn from(value: reqwest::Error) -> Self {
        WorkOSError::Http(value.to_string())
    }
}

impl From<serde_json::Error> for WorkOSError {
    fn from(value: serde_json::Error) -> Self {
        WorkOSError::Json(value.to_string())
    }
}
