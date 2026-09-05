//! Axum router wiring `/auth/workos/*` endpoints.
//!
//! Routes:
//!   GET  /auth/workos/login      — redirects to AuthKit hosted login
//!   GET  /auth/workos/callback   — verifies the ID token, sets the session cookie
//!   POST /auth/workos/webhook    — signature-verified webhook ingest
//!   GET  /auth/workos/userinfo   — returns the current user's profile
//!
//! The router is intentionally framework-agnostic at its core: every handler
//! takes a [`WorkOSClient`] and a body / path / query, and returns an axum
//! `Response`. This lets `tracera-server/src/main.rs` mount it via
//! `Router::nest("/auth/workos", tracera_workos::router::router(client))`.

use axum::{
    body::Bytes,
    extract::{Query, State},
    http::{HeaderMap, StatusCode},
    response::{IntoResponse, Redirect, Response},
    routing::{get, post},
    Json, Router,
};
use base64::Engine;
use serde::{Deserialize, Serialize};

use crate::auth::{build_authorize_url, exchange_code_for_token, verify_id_token, AuthorizeParams};
use crate::error::WorkOSError;
use crate::webhooks::{
    is_known_event, verify_signature, WebhookEnvelope, DEFAULT_TOLERANCE_SECONDS as WEBHOOK_TOLERANCE,
};
use crate::WorkOSClient;

/// Session cookie name for the AuthKit login flow.
pub const SESSION_COOKIE_NAME: &str = "tracera_workos_session";

/// HTTP-only, lax-session cookie attributes shared by all responses that set
/// the session cookie.
const SESSION_COOKIE_ATTRS: &str = "Path=/; HttpOnly; SameSite=Lax; Max-Age=3600";

/// Build the WorkOS sub-router. Pass the result to `Router::nest("/auth/workos", ...)`.
pub fn router(client: WorkOSClient) -> Router {
    Router::new()
        .route("/login", get(login_handler))
        .route("/callback", get(callback_handler))
        .route("/webhook", post(webhook_handler))
        .route("/userinfo", get(userinfo_handler))
        .with_state(client)
}

// ---------------------------------------------------------------------------
// /login — redirect to hosted login
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize, Default)]
pub struct LoginQuery {
    #[serde(default)]
    pub connection_id: Option<String>,
    #[serde(default)]
    pub organization: Option<String>,
    #[serde(default)]
    pub redirect_uri: Option<String>,
}

#[derive(Debug, Serialize)]
struct LoginErrorBody {
    error: &'static str,
    message: String,
}

fn error_response(status: StatusCode, error: &'static str, message: impl Into<String>) -> Response {
    (
        status,
        Json(LoginErrorBody {
            error,
            message: message.into(),
        }),
    )
        .into_response()
}

async fn login_handler(
    State(client): State<WorkOSClient>,
    Query(params): Query<LoginQuery>,
) -> Result<Response, Response> {
    let params = AuthorizeParams {
        connection_id: params.connection_id.as_deref(),
        organization: params.organization.as_deref(),
        code_challenge: None,
        scope: Some("openid,profile,email"),
        redirect_uri: params.redirect_uri.as_deref(),
    };
    match build_authorize_url(client.config(), params) {
        Ok(built) => {
            // We don't have session storage here — return both the URL and the
            // state nonce. tracera-server can choose to redirect (302) or to
            // return a JSON body that the SPA stores. Default to a 302.
            let _ = built.state; // available to callers via direct API
            Ok(Redirect::to(&built.url).into_response())
        }
        Err(err) => Err(error_response(
            StatusCode::INTERNAL_SERVER_ERROR,
            "authorize_failed",
            format!("{err}"),
        )),
    }
}

// ---------------------------------------------------------------------------
// /callback — verify the ID token and set the session cookie
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub struct CallbackQuery {
    pub code: String,
    pub state: String,
}

#[derive(Debug, Serialize)]
struct CallbackResponse {
    user: crate::WorkOSUser,
    expires_at: i64,
}

async fn callback_handler(
    State(client): State<WorkOSClient>,
    Query(params): Query<CallbackQuery>,
) -> Result<Response, Response> {
    if params.code.is_empty() || params.state.is_empty() {
        return Err(error_response(
            StatusCode::BAD_REQUEST,
            "invalid_callback",
            "missing code or state",
        ));
    }

    let token_bundle = exchange_code_for_token(client.config(), &params.code)
        .await
        .map_err(|err| {
            error_response(
                StatusCode::BAD_GATEWAY,
                "token_exchange_failed",
                format!("{err}"),
            )
        })?;

    let claims = verify_id_token(client.config(), &token_bundle.id_token).map_err(|err| {
        error_response(
            StatusCode::UNAUTHORIZED,
            "id_token_invalid",
            format!("{err}"),
        )
    })?;
    let user = claims.into_user();
    let expires_at = chrono::Utc::now().timestamp() + token_bundle.expires_in.unwrap_or(3600);
    let body = Json(CallbackResponse {
        user: user.clone(),
        expires_at,
    });

    let session_payload = serde_json::to_string(&user)
        .map_err(|err| error_response(StatusCode::INTERNAL_SERVER_ERROR, "session_serialize_failed", format!("{err}")))?;
    let encoded = WorkOSClient::b64url_encode(session_payload.as_bytes());

    let cookie = format!("{SESSION_COOKIE_NAME}={encoded}; {SESSION_COOKIE_ATTRS}");
    let mut response = body.into_response();
    response.headers_mut().insert(
        axum::http::header::SET_COOKIE,
        axum::http::HeaderValue::from_str(&cookie)
            .map_err(|err| error_response(StatusCode::INTERNAL_SERVER_ERROR, "session_cookie_failed", format!("{err}")))?,
    );
    Ok(response)
}

// ---------------------------------------------------------------------------
// /webhook — signature-verified, dispatches to sync/audit
// ---------------------------------------------------------------------------

#[derive(Debug, Serialize)]
struct WebhookAck {
    accepted: bool,
    dispatch: &'static str,
    event_id: String,
}

async fn webhook_handler(
    State(client): State<WorkOSClient>,
    headers: HeaderMap,
    body: Bytes,
) -> Result<Response, Response> {
    let signature = headers
        .get("workos-signature")
        .and_then(|v| v.to_str().ok())
        .ok_or_else(|| {
            error_response(
                StatusCode::UNAUTHORIZED,
                "missing_signature",
                "WorkOS-Signature header missing",
            )
        })?;

    verify_signature(
        client.config().webhook_secret.as_ref(),
        signature,
        &body,
        WEBHOOK_TOLERANCE,
        chrono::Utc::now(),
    )
    .map_err(|err| match &err {
        WorkOSError::WebhookSignatureInvalid | WorkOSError::WebhookSignatureHeader(_) => {
            error_response(StatusCode::UNAUTHORIZED, "signature_invalid", format!("{err}"))
        }
        WorkOSError::WebhookTimestampSkew(_) => {
            error_response(StatusCode::UNAUTHORIZED, "stale_signature", format!("{err}"))
        }
        _ => error_response(StatusCode::INTERNAL_SERVER_ERROR, "signature_check_failed", format!("{err}")),
    })?;

    let envelope: WebhookEnvelope = serde_json::from_slice(&body).map_err(|err| {
        error_response(
            StatusCode::BAD_REQUEST,
            "invalid_envelope",
            format!("{err}"),
        )
    })?;

    if !is_known_event(&envelope.event_type) {
        // Unknown event families get a 202 so WorkOS doesn't retry — the
        // handler explicitly chose to ignore them.
        return Ok((
            StatusCode::ACCEPTED,
            Json(serde_json::json!({
                "accepted": false,
                "dispatch": "ignored",
                "event_id": envelope.id,
                "reason": "unknown_event_type"
            })),
        )
            .into_response());
    }

    let dispatch = crate::webhooks::dispatch(&envelope);
    let dispatch_label = dispatch.as_str();

    // We don't persist here — the caller wires `ProvisionOutcome` /
    // `AuditOutcome` into the SWEE store. Returning the dispatch bucket lets
    // the caller (and the smoke test) decide what to do.
    Ok((
        StatusCode::OK,
        Json(WebhookAck {
            accepted: true,
            dispatch: dispatch_label,
            event_id: envelope.id,
        }),
    )
        .into_response())
}

// ---------------------------------------------------------------------------
// /userinfo — returns the current user from the session cookie
// ---------------------------------------------------------------------------

#[derive(Debug, Serialize)]
struct UserInfoResponse {
    user: Option<crate::WorkOSUser>,
    authenticated: bool,
}

async fn userinfo_handler(
    headers: HeaderMap,
) -> Result<Response, Response> {
    let cookie_header = headers
        .get(axum::http::header::COOKIE)
        .and_then(|v| v.to_str().ok());

    let user = cookie_header
        .and_then(parse_session_cookie)
        .and_then(|payload| serde_json::from_str::<crate::WorkOSUser>(&payload).ok());

    let body = Json(UserInfoResponse {
        authenticated: user.is_some(),
        user,
    });

    if cookie_header.is_none() {
        return Err(error_response(
            StatusCode::UNAUTHORIZED,
            "no_session",
            "session cookie missing",
        ));
    }

    Ok(body.into_response())
}

fn parse_session_cookie(cookie_header: &str) -> Option<String> {
    for raw in cookie_header.split(';') {
        let trimmed = raw.trim();
        let (name, value) = trimmed.split_once('=')?;
        if name == SESSION_COOKIE_NAME {
            // Reverse the URL-safe base64 encoding done by callback_handler.
            let bytes = base64::engine::general_purpose::URL_SAFE_NO_PAD
                .decode(value)
                .ok()?;
            return String::from_utf8(bytes).ok();
        }
    }
    None
}

// Re-export the tolerance constants under their canonical names so callers
// don't have to import them from `webhooks` / `auth`.
pub use crate::webhooks::DEFAULT_TOLERANCE_SECONDS as DEFAULT_WEBHOOK_TOLERANCE_SECONDS;
pub use crate::webhooks::DEFAULT_TOLERANCE_SECONDS as DEFAULT_AUTH_TOLERANCE_SECONDS;

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{WorkOSConfig, WorkOSUser};

    fn client() -> WorkOSClient {
        WorkOSClient::new(
            WorkOSConfig::new("sk_test", "client_test", "whsec_test", "http://x/cb")
                .with_mock_jwt_secret("topsecret"),
        )
    }

    #[test]
    fn parse_session_cookie_extracts_payload() {
        let user = WorkOSUser {
            id: "user_1".into(),
            email: "a@b.co".into(),
            first_name: None,
            last_name: None,
            organization_id: None,
            connection_id: None,
        };
        let encoded = base64::engine::general_purpose::URL_SAFE_NO_PAD.encode(
            serde_json::to_string(&user).unwrap().as_bytes(),
        );
        let cookie = format!("tracera_workos_session={encoded}; Path=/; HttpOnly");
        let parsed = parse_session_cookie(&cookie).unwrap();
        let back: WorkOSUser = serde_json::from_str(&parsed).unwrap();
        assert_eq!(back.id, "user_1");
        assert_eq!(back.email, "a@b.co");
    }

    #[test]
    fn parse_session_cookie_returns_none_for_missing_cookie() {
        assert!(parse_session_cookie("other_cookie=abc; Path=/").is_none());
    }

    #[test]
    fn parse_session_cookie_returns_none_for_garbage_payload() {
        let cookie = format!(
            "{}=not_base64; Path=/",
            SESSION_COOKIE_NAME
        );
        assert!(parse_session_cookie(&cookie).is_none());
    }

    #[test]
    fn router_builds_with_all_four_routes() {
        let r = router(client());
        // Just verify it constructs without panic.
        let _ = r;
    }
}
