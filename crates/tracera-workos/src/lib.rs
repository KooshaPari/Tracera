//! WorkOS integration for Tracera.
//!
//! This crate wires WorkOS (AuthKit hosted login + Directory Sync + Webhooks +
! Audit Logs) into the Tracera server's `/auth/workos/*` route group.
//!
//! It is deliberately framework-agnostic at the API surface — the modules here
//! expose pure functions (`auth::build_authorize_url`, `auth::verify_id_token`,
//! `webhooks::verify_signature`, etc.) plus thin axum handlers in
//! [`router`] that the tracera-server wires under `/auth/workos/*`.
//!
//! The mock server at `src/bin/workos-mock.rs` returns JWTs that satisfy
//! `auth::verify_id_token` so the full Tracera login → callback → webhook loop
//! can be exercised locally without a live WorkOS tenant.
//!
//! # Modules
//! - [`auth`] — AuthKit hosted login URL builder + callback verification.
//! - [`webhooks`] — HMAC-SHA256 webhook signature verification + dispatch.
//! - [`sync`] — Directory Sync: map WorkOS directory events to Agent / Person
//!   / Team graph nodes.
//! - [`audit`] — Audit log ingest → normalized graph events.
//! - [`router`] — axum router exposing `/auth/workos/{login,callback,webhook,userinfo}`.
//! - [`error`] — shared error type for the crate.

#![deny(rust_2018_idioms)]
#![warn(missing_debug_implementations)]

pub mod audit;
pub mod auth;
pub mod error;
pub mod router;
pub mod sync;
pub mod webhooks;

use base64::Engine;
use serde::{Deserialize, Serialize};
use std::sync::Arc;

/// Configuration for connecting to a WorkOS tenant.
///
/// `WorkOSConfig::from_env` is the preferred entrypoint — it reads the same
/// env-var names that WorkOS publishes in its dashboard:
/// `WORKOS_API_KEY`, `WORKOS_CLIENT_ID`, `WORKOS_WEBHOOK_SECRET`,
/// `WORKOS_REDIRECT_URI`, `WORKOS_API_BASE` (defaults to `https://api.workos.com`).
#[derive(Clone, Debug)]
pub struct WorkOSConfig {
    /// WorkOS API key (`sk_*`). Used for server-to-server calls.
    pub api_key: Arc<str>,
    /// WorkOS client ID (`client_*`). Identifies the application.
    pub client_id: Arc<str>,
    /// HMAC-SHA256 shared secret used to sign webhooks (`whsec_*`).
    pub webhook_secret: Arc<str>,
    /// Redirect URI registered with AuthKit; the hosted login UI bounces the
    /// browser back here with `code` + `state`.
    pub redirect_uri: Arc<str>,
    /// Base URL for WorkOS REST API. Override for the local mock server.
    pub api_base: Arc<str>,
    /// HS256 signing secret used by the local mock server to issue ID tokens.
    /// Production tokens are RS256-signed by AuthKit and verified with a JWKS
    /// fetch; we keep a symmetric fallback so the dev mock can round-trip.
    pub mock_jwt_secret: Arc<str>,
}

impl WorkOSConfig {
    /// Load config from environment variables. Missing values produce a clear
    /// error instead of silently defaulting to empty strings.
    pub fn from_env() -> Result<Self, error::WorkOSError> {
        let api_key = std::env::var("WORKOS_API_KEY")
            .map_err(|_| error::WorkOSError::Config("WORKOS_API_KEY not set".into()))?;
        let client_id = std::env::var("WORKOS_CLIENT_ID")
            .map_err(|_| error::WorkOSError::Config("WORKOS_CLIENT_ID not set".into()))?;
        let webhook_secret = std::env::var("WORKOS_WEBHOOK_SECRET")
            .map_err(|_| error::WorkOSError::Config("WORKOS_WEBHOOK_SECRET not set".into()))?;
        let redirect_uri = std::env::var("WORKOS_REDIRECT_URI")
            .map_err(|_| error::WorkOSError::Config("WORKOS_REDIRECT_URI not set".into()))?;

        let api_base = std::env::var("WORKOS_API_BASE")
            .unwrap_or_else(|_| "https://api.workos.com".to_string());

        // Optional: HS256 secret used only by the local mock to sign ID tokens.
        let mock_jwt_secret = std::env::var("WORKOS_MOCK_JWT_SECRET")
            .unwrap_or_else(|_| "dev-only-mock-secret-do-not-use-in-prod".to_string());

        Ok(Self {
            api_key: Arc::from(api_key),
            client_id: Arc::from(client_id),
            webhook_secret: Arc::from(webhook_secret),
            redirect_uri: Arc::from(redirect_uri),
            api_base: Arc::from(api_base),
            mock_jwt_secret: Arc::from(mock_jwt_secret),
        })
    }

    /// Construct config from explicit values. Primarily used by tests.
    pub fn new(
        api_key: impl Into<String>,
        client_id: impl Into<String>,
        webhook_secret: impl Into<String>,
        redirect_uri: impl Into<String>,
    ) -> Self {
        Self {
            api_key: Arc::from(api_key.into()),
            client_id: Arc::from(client_id.into()),
            webhook_secret: Arc::from(webhook_secret.into()),
            redirect_uri: Arc::from(redirect_uri.into()),
            api_base: Arc::from("https://api.workos.com"),
            mock_jwt_secret: Arc::from("dev-only-mock-secret-do-not-use-in-prod"),
        }
    }

    /// Override the API base URL (for the local mock server).
    pub fn with_api_base(mut self, base: impl Into<String>) -> Self {
        self.api_base = Arc::from(base.into());
        self
    }

    /// Override the mock JWT secret (must match `WORKOS_MOCK_JWT_SECRET` on
    /// the server side so `verify_id_token` can validate).
    pub fn with_mock_jwt_secret(mut self, secret: impl Into<String>) -> Self {
        self.mock_jwt_secret = Arc::from(secret.into());
        self
    }
}

/// Tracera-side authenticated user derived from a verified WorkOS ID token.
///
/// Returned by `/auth/workos/userinfo` and stored in the session after a
/// successful `/auth/workos/callback`.
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
pub struct WorkOSUser {
    /// WorkOS subject identifier (`sub` claim). Stable per user per connection.
    pub id: String,
    /// Email address (`email` claim).
    pub email: String,
    /// Optional first/last name fields from the directory profile.
    #[serde(default)]
    pub first_name: Option<String>,
    #[serde(default)]
    pub last_name: Option<String>,
    /// Directory/organization id (`org_id` claim) if available.
    #[serde(default)]
    pub organization_id: Option<String>,
    /// Connection id (`connection_id` claim) — distinguishes AuthKit vs
    /// enterprise SSO connections.
    #[serde(default)]
    pub connection_id: Option<String>,
}

/// Authenticated client wrapping a [`WorkOSConfig`].
///
/// Cloning is cheap (everything inside `Arc`); pass it via `axum::extract::State`
/// in the tracera-server router.
#[derive(Clone, Debug)]
pub struct WorkOSClient {
    config: Arc<WorkOSConfig>,
}

impl WorkOSClient {
    /// Create a new client.
    pub fn new(config: WorkOSConfig) -> Self {
        Self {
            config: Arc::new(config),
        }
    }

    /// Borrow the inner config (needed by every public function in the module).
    pub fn config(&self) -> &WorkOSConfig {
        &self.config
    }

    /// Convenience: base64url-encode a string slice (used in JWT segmenting
    /// and in the OAuth `state` parameter nonce).
    pub fn b64url_encode(bytes: &[u8]) -> String {
        base64::engine::general_purpose::URL_SAFE_NO_PAD.encode(bytes)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn config_from_explicit_values_round_trips() {
        let cfg = WorkOSConfig::new("sk_test", "client_test", "whsec_test", "http://x/cb")
            .with_api_base("http://localhost:9000")
            .with_mock_jwt_secret("topsecret");
        assert_eq!(cfg.api_key.as_ref(), "sk_test");
        assert_eq!(cfg.client_id.as_ref(), "client_test");
        assert_eq!(cfg.webhook_secret.as_ref(), "whsec_test");
        assert_eq!(cfg.redirect_uri.as_ref(), "http://x/cb");
        assert_eq!(cfg.api_base.as_ref(), "http://localhost:9000");
        assert_eq!(cfg.mock_jwt_secret.as_ref(), "topsecret");
    }

    #[test]
    fn b64url_encode_is_url_safe_no_pad() {
        // Padding stripped, '+' and '/' replaced.
        let out = WorkOSClient::b64url_encode(b"hello world");
        assert!(!out.contains('='));
        assert!(!out.contains('+'));
        assert!(!out.contains('/'));
    }

    #[test]
    fn workos_user_deserializes_minimal_payload() {
        let json = r#"{"id":"user_01","email":"a@b.co"}"#;
        let user: WorkOSUser = serde_json::from_str(json).unwrap();
        assert_eq!(user.id, "user_01");
        assert_eq!(user.email, "a@b.co");
        assert!(user.first_name.is_none());
        assert!(user.organization_id.is_none());
    }

    #[test]
    fn workos_user_deserializes_full_payload() {
        let json = r#"{
            "id":"user_01",
            "email":"a@b.co",
            "first_name":"Ada",
            "last_name":"Lovelace",
            "organization_id":"org_01",
            "connection_id":"conn_01"
        }"#;
        let user: WorkOSUser = serde_json::from_str(json).unwrap();
        assert_eq!(user.first_name.as_deref(), Some("Ada"));
        assert_eq!(user.last_name.as_deref(), Some("Lovelace"));
        assert_eq!(user.organization_id.as_deref(), Some("org_01"));
        assert_eq!(user.connection_id.as_deref(), Some("conn_01"));
    }
}
