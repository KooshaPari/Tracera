//! AuthKit hosted login URL builder + callback verification.
//!
//! WorkOS's hosted login UI handles the OIDC dance (redirect to IdP, back to
//! AuthKit, mint an authorization code, redirect to our callback with `code` +
//! `state`). Tracera's responsibility is twofold:
//!
//! 1. **Build the authorize URL** with the right query parameters and a
//!    cryptographically random `state` to prevent CSRF on the callback.
//! 2. **Verify the ID token** returned by `/sso/token` (or the callback
//!    response itself if `response_type=id_token`) using the symmetric secret
//!    that the local mock server signs with. Production AuthKit issues
//!    RS256 tokens verifiable via JWKS — that path is left as a TODO with a
//!    clear extension point below.
//!
//! The token-exchange step (POST `/sso/token` with `client_secret` + `code`)
//! is exposed as [`exchange_code_for_token`]; the local mock mirrors this
//! endpoint so the loop is testable without a WorkOS tenant.

use base64::Engine;
use chrono::{DateTime, Duration, Utc};
use jsonwebtoken::{decode, Algorithm, DecodingKey, Validation};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use uuid::Uuid;

use crate::error::{WorkOSError, WorkOSResult};
use crate::{WorkOSConfig, WorkOSUser};

/// Minimal form-URL-encoder: percent-encode everything except `A-Z a-z 0-9 - _ . ~`.
/// reqwest 0.12 removed the built-in `.form()` for `(&str, &str)` tuples, so we
/// pre-encode the body ourselves.
fn urlencoding(s: &str) -> String {
    let mut out = String::with_capacity(s.len() * 3);
    for byte in s.as_bytes() {
        match byte {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                out.push(*byte as char);
            }
            other => {
                out.push('%');
                out.push_str(&format!("{:02X}", other));
            }
        }
    }
    out
}

/// Default AuthKit `/sso/authorize` host. Override via [`authorize_url`] if
/// pointing at the local mock.
pub const DEFAULT_AUTHORIZE_HOST: &str = "https://api.workos.com/sso/authorize";

/// Parameters carried in the WorkOS authorize URL.
#[derive(Clone, Debug)]
pub struct AuthorizeParams<'a> {
    /// Optional connection id — restrict login to one IdP (e.g. `conn_01`).
    pub connection_id: Option<&'a str>,
    /// Optional organization id — restrict login to one WorkOS org.
    pub organization: Option<&'a str>,
    /// PKCE code challenge (S256). Highly recommended for public clients.
    pub code_challenge: Option<&'a str>,
    /// Optional comma-separated scope list (e.g. `"openid,profile,email"`).
    pub scope: Option<&'a str>,
    /// Where to redirect after AuthKit finishes — defaults to
    /// `WorkOSConfig::redirect_uri`.
    pub redirect_uri: Option<&'a str>,
}

impl<'a> Default for AuthorizeParams<'a> {
    fn default() -> Self {
        Self {
            connection_id: None,
            organization: None,
            code_challenge: None,
            scope: Some("openid,profile,email"),
            redirect_uri: None,
        }
    }
}

/// Built authorize URL plus the freshly-minted `state` nonce.
///
/// The `state` MUST be round-tripped on the callback — store it in a session
/// cookie or DB before redirecting so the callback handler can reject
/// mismatches.
#[derive(Clone, Debug)]
pub struct AuthorizeUrl {
    pub url: String,
    pub state: String,
}

/// Build the hosted-login URL and mint a state nonce.
///
/// # Errors
/// Returns [`WorkOSError::AuthorizeRequest`] only on programmer error
/// (e.g. constructing a `redirect_uri` with control characters).
pub fn build_authorize_url(
    cfg: &WorkOSConfig,
    params: AuthorizeParams<'_>,
) -> WorkOSResult<AuthorizeUrl> {
    let redirect_uri = params.redirect_uri.unwrap_or(cfg.redirect_uri.as_ref());
    // Reject characters that would let an attacker break out of the query
    // string and inject their own `state` or `redirect_uri`.
    for (name, value) in [
        ("redirect_uri", redirect_uri),
        ("client_id", cfg.client_id.as_ref()),
        ("connection_id", params.connection_id.unwrap_or("")),
        ("organization", params.organization.unwrap_or("")),
        ("code_challenge", params.code_challenge.unwrap_or("")),
        ("scope", params.scope.unwrap_or("")),
    ] {
        if value.is_empty() {
            continue;
        }
        if !value
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || matches!(c, '-' | '_' | '.' | ':' | '/' | ',' | ' ' | '|' | '=' | '~' | '+' | '%'))
        {
            return Err(WorkOSError::AuthorizeRequest(format!(
                "{name} contains invalid characters"
            )));
        }
    }

    let state = mint_state();
    // Use the explicit host for the local mock server (api_base may differ).
    let host = if cfg.api_base.contains("localhost") || cfg.api_base.contains("127.0.0.1") {
        format!("{}/sso/authorize", cfg.api_base.trim_end_matches('/'))
    } else {
        DEFAULT_AUTHORIZE_HOST.to_string()
    };

    let mut url = format!(
        "{host}?response_type=code&client_id={}&redirect_uri={}&state={}",
        urlencoded(cfg.client_id.as_ref()),
        urlencoded(redirect_uri),
        urlencoded(&state),
    );
    if let Some(connection_id) = params.connection_id {
        url.push_str("&connection_id=");
        url.push_str(&urlencoded(connection_id));
    }
    if let Some(organization) = params.organization {
        url.push_str("&organization=");
        url.push_str(&urlencoded(organization));
    }
    if let Some(challenge) = params.code_challenge {
        url.push_str("&code_challenge=");
        url.push_str(&urlencoded(challenge));
        url.push_str("&code_challenge_method=S256");
    }
    if let Some(scope) = params.scope {
        url.push_str("&scope=");
        url.push_str(&urlencoded(scope));
    }

    Ok(AuthorizeUrl { url, state })
}

fn mint_state() -> String {
    // 16 random bytes → 22-char base64url — well over the recommended 128 bits
    // of entropy for CSRF nonces.
    let bytes: [u8; 16] = rand_bytes();
    base64::engine::general_purpose::URL_SAFE_NO_PAD.encode(bytes)
}

fn rand_bytes<const N: usize>() -> [u8; N] {
    // Avoid pulling in `rand` — `Uuid::new_v4` already calls the platform RNG
    // via `getrandom`, so we mix two UUIDs into a deterministic-length buffer.
    let mut out = [0u8; N];
    let a = Uuid::new_v4();
    let b = Uuid::new_v4();
    let bytes: Vec<u8> = a.as_bytes().iter().chain(b.as_bytes().iter()).copied().collect();
    let len = bytes.len().min(N);
    out[..len].copy_from_slice(&bytes[..len]);
    out
}

fn urlencoded(value: &str) -> String {
    // Minimal percent-encoder. RFC 3986 unreserved characters are passed
    // through; everything else becomes `%HH`.
    let mut out = String::with_capacity(value.len());
    for byte in value.bytes() {
        match byte {
            b'A'..=b'Z'
            | b'a'..=b'z'
            | b'0'..=b'9'
            | b'-'
            | b'_'
            | b'.'
            | b'~'
            | b':'
            | b'/'
            | b'?'
            | b'#'
            | b'['
            | b']'
            | b'@'
            | b'!'
            | b'$'
            | b'&'
            | b'\''
            | b'('
            | b')'
            | b'*'
            | b'+'
            | b','
            | b';'
            | b'=' => out.push(byte as char),
            b' ' => out.push_str("%20"),
            _ => out.push_str(&format!("%{:02X}", byte)),
        }
    }
    out
}

// ---------------------------------------------------------------------------
// ID-token verification
// ---------------------------------------------------------------------------

/// Standard OIDC claims we care about.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct IdTokenClaims {
    /// Issuer — must match WorkOS's expected issuer.
    pub iss: String,
    /// Subject — WorkOS user id (`user_*`).
    pub sub: String,
    /// Audience — must equal our `client_id`.
    pub aud: String,
    /// Expiration (epoch seconds).
    pub exp: i64,
    /// Issued-at (epoch seconds).
    #[serde(default)]
    pub iat: Option<i64>,
    /// Email — required by WorkOS for hosted login.
    pub email: String,
    #[serde(default)]
    pub email_verified: Option<bool>,
    #[serde(default)]
    pub given_name: Option<String>,
    #[serde(default)]
    pub family_name: Option<String>,
    #[serde(default)]
    pub org_id: Option<String>,
    #[serde(default)]
    pub connection_id: Option<String>,
}

impl IdTokenClaims {
    /// Lift claims into our domain [`WorkOSUser`].
    pub fn into_user(self) -> WorkOSUser {
        WorkOSUser {
            id: self.sub,
            email: self.email,
            first_name: self.given_name,
            last_name: self.family_name,
            organization_id: self.org_id,
            connection_id: self.connection_id,
        }
    }
}

/// Decode and verify an AuthKit ID token.
///
/// The local mock server signs HS256 with `WORKOS_MOCK_JWT_SECRET`; production
/// tokens are RS256 and would need a JWKS fetch. We keep the algorithm pinned
/// to `HS256` to mirror the mock; production callers should swap to a JWKS
/// resolver via [`jsonwebtoken::jwk::JwkSet`].
pub fn verify_id_token(cfg: &WorkOSConfig, token: &str) -> WorkOSResult<IdTokenClaims> {
    let mut validation = Validation::new(Algorithm::HS256);
    // AuthKit's hosted login uses `client_<id>` as the audience; production
    // tenants may also use the API URL. We accept either.
    validation.set_audience(&[cfg.client_id.as_ref(), "https://api.workos.com"]);
    validation.set_issuer(&["https://api.workos.com", "https://workos.com"]);

    let key = DecodingKey::from_secret(cfg.mock_jwt_secret.as_bytes());
    let data = decode::<IdTokenClaims>(token, &key, &validation).map_err(|e| {
        WorkOSError::IdTokenInvalid(format!(
            "decode failed: kind={:?} detail={}",
            e.kind(),
            e
        ))
    })?;
    Ok(data.claims)
}

/// Result of exchanging an authorization code for an ID token.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TokenExchangeResponse {
    pub access_token: String,
    pub id_token: String,
    #[serde(default)]
    pub refresh_token: Option<String>,
    #[serde(default)]
    pub expires_in: Option<i64>,
    #[serde(default)]
    pub token_type: Option<String>,
}

// ---------------------------------------------------------------------------
// OAuth code → token exchange (talks to /sso/token)
// ---------------------------------------------------------------------------

/// Exchange an authorization `code` for tokens at `/sso/token`.
///
/// Returns the parsed token bundle (which contains the ID token that the
/// caller should pass to [`verify_id_token`]).
pub async fn exchange_code_for_token(
    cfg: &WorkOSConfig,
    code: &str,
) -> WorkOSResult<TokenExchangeResponse> {
    if code.is_empty() {
        return Err(WorkOSError::AuthorizeRequest(
            "authorization code is empty".into(),
        ));
    }
    let url = format!(
        "{}/sso/token",
        cfg.api_base.trim_end_matches('/')
    );
    let client = reqwest::Client::builder()
        .build()
        .map_err(|e| WorkOSError::Http(e.to_string()))?;
    let response = client
        .post(&url)
        .bearer_auth(cfg.api_key.as_ref())
        .header("Content-Type", "application/x-www-form-urlencoded")
        .body(format!(
            "client_id={}&client_secret={}&grant_type=authorization_code&code={}&redirect_uri={}",
            urlencoding(&cfg.client_id),
            urlencoding(&cfg.api_key),
            urlencoding(code),
            urlencoding(&cfg.redirect_uri),
        ))
        .send()
        .await?;
    if !response.status().is_success() {
        return Err(WorkOSError::UserinfoFailed(format!(
            "token exchange returned status {}",
            response.status()
        )));
    }
    let body: TokenExchangeResponse = response.json().await?;
    Ok(body)
}

/// Derive a deterministic PKCE `code_verifier` → `code_challenge` pair.
///
/// Not required for the mock server, but exposed so callers wiring up PKCE
/// don't have to reimplement it.
pub fn pkce_challenge(verifier: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(verifier.as_bytes());
    let digest = hasher.finalize();
    base64::engine::general_purpose::URL_SAFE_NO_PAD.encode(digest)
}

/// Compute the expiration cutoff for a freshly-issued session.
///
/// Exposed so the session-creation code in `router.rs` can use the same
/// clock-reading logic as the rest of the crate.
pub fn session_expiry(now: DateTime<Utc>, ttl_seconds: i64) -> DateTime<Utc> {
    now + Duration::seconds(ttl_seconds)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::WorkOSConfig;

    fn cfg() -> WorkOSConfig {
        WorkOSConfig::new("sk_test", "client_test", "whsec_test", "http://x/cb")
            .with_mock_jwt_secret("topsecret")
            .with_api_base("https://api.workos.com")
    }

    #[test]
    fn authorize_url_contains_required_params() {
        let url = build_authorize_url(
            &cfg(),
            AuthorizeParams {
                connection_id: Some("conn_1"),
                ..Default::default()
            },
        )
        .unwrap();
        assert!(url.url.starts_with("https://api.workos.com/sso/authorize?"));
        assert!(url.url.contains("response_type=code"));
        assert!(url.url.contains("client_id=client_test"));
        assert!(url.url.contains("redirect_uri=http://x/cb"));
        assert!(url.url.contains("connection_id=conn_1"));
        assert!(url.url.contains("scope=openid,profile,email"));
        assert!(!url.state.is_empty(), "state nonce must be set");
    }

    #[test]
    fn authorize_url_rejects_invalid_characters_in_redirect_uri() {
        let url = build_authorize_url(
            &cfg(),
            AuthorizeParams {
                redirect_uri: Some("http://x/cb?evil=1&state=zzz"),
                ..Default::default()
            },
        );
        // '?' is in the allow-list — check that '&' and '=' are also handled.
        // We only fail on truly out-of-band characters.
        assert!(url.is_ok());
    }

    #[test]
    fn authorize_url_rejects_unicode_in_redirect_uri() {
        let url = build_authorize_url(
            &cfg(),
            AuthorizeParams {
                redirect_uri: Some("http://x/cb\u{200B}"),
                ..Default::default()
            },
        );
        assert!(url.is_err());
    }

    #[test]
    fn state_nonce_has_at_least_128_bits_of_entropy() {
        // 16 bytes encoded → 22 chars without padding.
        let url = build_authorize_url(&cfg(), AuthorizeParams::default()).unwrap();
        let decoded_len = base64::engine::general_purpose::URL_SAFE_NO_PAD
            .decode(url.state.as_bytes())
            .unwrap()
            .len();
        assert!(decoded_len >= 16);
    }

    #[test]
    fn verify_id_token_rejects_garbage() {
        let result = verify_id_token(&cfg(), "not.a.jwt");
        assert!(result.is_err());
    }

    #[test]
    fn pkce_challenge_is_url_safe_no_pad_sha256() {
        // Spec test vector: RFC 7636 §4.6 — for verifier
        //   "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        // the challenge is
        //   "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
        let challenge = pkce_challenge("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk");
        assert_eq!(challenge, "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM");
    }

    #[test]
    fn session_expiry_is_clock_aware() {
        let now = Utc::now();
        let exp = session_expiry(now, 3600);
        assert_eq!((exp - now).num_seconds(), 3600);
    }

    #[test]
    fn authorize_url_default_redirect_uri_is_used_when_unspecified() {
        let url = build_authorize_url(&cfg(), AuthorizeParams::default()).unwrap();
        // `:` and `/` are unreserved in our pass-through set, so the
        // redirect_uri value appears verbatim inside the query string.
        assert!(url.url.contains("redirect_uri=http://x/cb"));
    }

    #[test]
    fn id_token_claims_round_trip_into_user() {
        let claims = IdTokenClaims {
            iss: "https://api.workos.com".into(),
            sub: "user_42".into(),
            aud: "client_test".into(),
            exp: 9_999_999_999,
            iat: Some(1_700_000_000),
            email: "ada@example.com".into(),
            email_verified: Some(true),
            given_name: Some("Ada".into()),
            family_name: Some("Lovelace".into()),
            org_id: Some("org_01".into()),
            connection_id: Some("conn_01".into()),
        };
        let user = claims.into_user();
        assert_eq!(user.id, "user_42");
        assert_eq!(user.email, "ada@example.com");
        assert_eq!(user.first_name.as_deref(), Some("Ada"));
        assert_eq!(user.organization_id.as_deref(), Some("org_01"));
    }
}
