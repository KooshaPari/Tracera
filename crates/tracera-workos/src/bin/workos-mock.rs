//! Mock WorkOS server.
//!
//! Mirrors a tiny slice of WorkOS's REST surface so Tracera's `/auth/workos/*`
//! flow can be exercised end-to-end without a real WorkOS tenant:
//!
//!   GET  /sso/authorize           — echo the params back as JSON so we can
//!                                   inspect the redirect URL. Real AuthKit
//!                                   redirects the browser; the mock just
//!                                   returns a 200 with the same query so
//!                                   tests can assert on it.
//!   POST /sso/token               — issues an HS256 ID token signed with
//!                                   `WORKOS_MOCK_JWT_SECRET`.
//!   POST /webhooks/dsync          — fires a sample `dsync.user.created` event
//!                                   with a properly-signed `WorkOS-Signature`.
//!   POST /webhooks/audit          — fires a sample `audit.log.created` event.
//!   GET  /healthz                 — liveness probe.
//!
//! Env vars:
//!   PORT                  — default 9000
//!   WORKOS_MOCK_JWT_SECRET — default "dev-only-mock-secret-do-not-use-in-prod"
//!   WORKOS_MOCK_WEBHOOK_SECRET — default "whsec_mock_secret"
//!
//! Listens on `0.0.0.0:$PORT` so docker / dev tunnels work out of the box.

use axum::{
    extract::{Query, State},
    http::{HeaderMap, StatusCode},
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use base64::Engine;
use chrono::{Duration, Utc};
use jsonwebtoken::{encode, EncodingKey, Header};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::net::SocketAddr;
use std::sync::Arc;

type HmacSha256 = ();

#[derive(Clone)]
struct MockState {
    jwt_secret: Arc<str>,
    webhook_secret: Arc<str>,
}

// ---------------------------------------------------------------------------
// Token minting
// ---------------------------------------------------------------------------

#[derive(Serialize)]
struct MockClaims {
    iss: String,
    sub: String,
    aud: String,
    exp: i64,
    iat: i64,
    email: String,
    email_verified: bool,
    given_name: String,
    family_name: String,
    org_id: String,
    connection_id: String,
}

#[derive(Deserialize)]
struct TokenRequest {
    #[serde(default)]
    client_id: Option<String>,
    #[serde(default)]
    code: Option<String>,
    /// Test hook: override the email on the issued token.
    #[serde(default)]
    email: Option<String>,
    #[serde(default)]
    sub: Option<String>,
}

/// Mint a JWT for an arbitrary subject/email pair. Used by `/sso/token` and
/// exposed as a helper for tests.
fn mint_token(state: &MockState, claims: &MockClaims) -> String {
    let key = EncodingKey::from_secret(state.jwt_secret.as_bytes());
    encode(&Header::new(jsonwebtoken::Algorithm::HS256), claims, &key)
        .expect("HS256 encode never fails with a valid key")
}

// ---------------------------------------------------------------------------
// Webhook signing (mirrors the verifier in `tracera-workos::webhooks`).
//
// Implemented as a fully self-contained HMAC-SHA256 (RFC 2104) that only depends
// on `sha2::Sha256` for the underlying hash function. No `digest` trait imports,
// no `KeyInit`, no `core_api`. This sidesteps the `digest 0.10` vs `0.11` version
// conflict in the workspace.
fn hmac_sha256(key: &[u8], msg: &[u8]) -> [u8; 32] {
    const BLOCK_SIZE: usize = 64;
    // 1. K' = K if len(K) == B; K' = H(K) if len(K) > B; K' = K || 0..0 if len(K) < B
    let key_block: [u8; BLOCK_SIZE] = if key.len() > BLOCK_SIZE {
        let mut h = sha2::Sha256::default();
        sha2::Digest::update(&mut h, key);
        let mut b = [0u8; BLOCK_SIZE];
        let out = sha2::Digest::finalize(h);
        b[..32].copy_from_slice(&out);
        b
    } else {
        let mut b = [0u8; BLOCK_SIZE];
        b[..key.len()].copy_from_slice(key);
        b
    };
    // 2. ipad = K' XOR 0x36 repeated; opad = K' XOR 0x5c repeated
    let mut ipad = [0x36u8; BLOCK_SIZE];
    let mut opad = [0x5cu8; BLOCK_SIZE];
    for i in 0..BLOCK_SIZE {
        ipad[i] ^= key_block[i];
        opad[i] ^= key_block[i];
    }
    // 3. H(opad || H(ipad || msg))
    let mut h1 = sha2::Sha256::default();
    sha2::Digest::update(&mut h1, &ipad);
    sha2::Digest::update(&mut h1, msg);
    let inner = sha2::Digest::finalize(h1);
    let mut h2 = sha2::Sha256::default();
    sha2::Digest::update(&mut h2, &opad);
    sha2::Digest::update(&mut h2, &inner);
    sha2::Digest::finalize(h2).into()
}

fn sign_webhook(secret: &str, ts: i64, body: &[u8]) -> String {
    let mut msg = Vec::with_capacity(20 + body.len());
    msg.extend_from_slice(ts.to_string().as_bytes());
    msg.push(b'.');
    msg.extend_from_slice(body);
    let mac = hmac_sha256(secret.as_bytes(), &msg);
    let hex: String = mac.iter().map(|b| format!("{b:02x}")).collect();
    format!("t={ts},v1={hex}")
}

// ---------------------------------------------------------------------------
// Handlers
// ---------------------------------------------------------------------------

async fn authorize(Query(params): axum::extract::Query<std::collections::HashMap<String, String>>) -> Json<Value> {
    Json(json!({
        "kind": "mock_authorize",
        "received_query": params,
        "note": "real AuthKit would 302 here; the mock echoes so tests can inspect"
    }))
}

async fn token(
    State(state): State<MockState>,
    headers: HeaderMap,
    axum::Form(req): axum::Form<TokenRequest>,
) -> Result<Json<Value>, StatusCode> {
    let _ = headers; // reserved for future bearer-style auth
    let now = Utc::now();
    let claims = MockClaims {
        iss: "https://api.workos.com".into(),
        sub: req.sub.clone().unwrap_or_else(|| "user_mock".into()),
        aud: req.client_id.clone().unwrap_or_else(|| "client_mock".into()),
        exp: (now + Duration::hours(1)).timestamp(),
        iat: now.timestamp(),
        email: req.email.clone().unwrap_or_else(|| "mock@workos.test".into()),
        email_verified: true,
        given_name: "Mock".into(),
        family_name: "User".into(),
        org_id: "org_mock".into(),
        connection_id: "conn_mock".into(),
    };
    let token = mint_token(&state, &claims);
    Ok(Json(json!({
        "access_token": format!("at_{}", base64::engine::general_purpose::URL_SAFE_NO_PAD.encode(token.as_bytes())),
        "id_token": token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": format!("rt_{}", uuid::Uuid::new_v4()),
        "_echo": {
            "code": req.code,
            "sub": claims.sub,
            "email": claims.email
        }
    })))
}

#[derive(Deserialize)]
struct WebhookFireRequest {
    #[serde(default)]
    event: Option<String>,
    #[serde(default)]
    payload: Option<Value>,
}

async fn fire_dsync(
    State(state): State<MockState>,
    axum::Json(req): axum::Json<WebhookFireRequest>,
) -> impl IntoResponse {
    let payload = req.payload.unwrap_or_else(|| {
        json!({
            "id": "user_demo",
            "email": "demo@workos.test",
            "first_name": "Demo",
            "last_name": "User",
            "state": "active",
            "organization_id": "org_mock",
            "groups": [{"id": "group_eng", "name": "Engineering"}],
            "custom_attributes": {}
        })
    });
    let event_type = req
        .event
        .unwrap_or_else(|| "dsync.user.created".into());
    let body = json!({
        "id": format!("evt_{}", uuid::Uuid::new_v4()),
        "event": event_type,
        "created_at": Utc::now().to_rfc3339(),
        "data": payload,
        "organization_id": "org_mock"
    });
    let body_bytes = serde_json::to_vec(&body).unwrap();
    let ts = Utc::now().timestamp();
    let signature = sign_webhook(&state.webhook_secret, ts, &body_bytes);
    (
        StatusCode::OK,
        [(axum::http::header::CONTENT_TYPE, "application/json")],
        Json(json!({
            "signature": signature,
            "timestamp": ts,
            "body": body
        })),
    )
}

async fn fire_audit(
    State(state): State<MockState>,
    axum::Json(req): axum::Json<WebhookFireRequest>,
) -> impl IntoResponse {
    let payload = req.payload.unwrap_or_else(|| {
        json!({
            "id": "audit_demo",
            "created_at": Utc::now().to_rfc3339(),
            "action": "user.session.created",
            "actor": {"id": "user_demo", "type": "user", "name": "Demo"},
            "target": {"id": "session_demo", "type": "session", "name": "Session"},
            "organization_id": "org_mock",
            "context": {"ip": "127.0.0.1"},
            "metadata": {}
        })
    });
    let event_type = req
        .event
        .unwrap_or_else(|| "audit.log.created".into());
    let body = json!({
        "id": format!("evt_{}", uuid::Uuid::new_v4()),
        "event": event_type,
        "created_at": Utc::now().to_rfc3339(),
        "data": payload,
        "organization_id": "org_mock"
    });
    let body_bytes = serde_json::to_vec(&body).unwrap();
    let ts = Utc::now().timestamp();
    let signature = sign_webhook(&state.webhook_secret, ts, &body_bytes);
    (
        StatusCode::OK,
        Json(json!({
            "signature": signature,
            "timestamp": ts,
            "body": body
        })),
    )
}

async fn healthz() -> &'static str {
    "ok"
}

// ---------------------------------------------------------------------------
// Entrypoint
// ---------------------------------------------------------------------------

#[tokio::main]
async fn main() {
    let port: u16 = std::env::var("PORT")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(9000);
    let bind = std::env::var("BIND_ADDR").unwrap_or_else(|_| "0.0.0.0".to_string());

    let jwt_secret: Arc<str> = std::env::var("WORKOS_MOCK_JWT_SECRET")
        .unwrap_or_else(|_| "dev-only-mock-secret-do-not-use-in-prod".to_string())
        .into();
    let webhook_secret: Arc<str> = std::env::var("WORKOS_MOCK_WEBHOOK_SECRET")
        .unwrap_or_else(|_| "whsec_mock_secret".to_string())
        .into();

    let state = MockState {
        jwt_secret: jwt_secret.clone(),
        webhook_secret: webhook_secret.clone(),
    };

    let app = Router::new()
        .route("/sso/authorize", get(authorize))
        .route("/sso/token", post(token))
        .route("/webhooks/dsync", post(fire_dsync))
        .route("/webhooks/audit", post(fire_audit))
        .route("/healthz", get(healthz))
        .with_state(state);

    let addr: SocketAddr = format!("{bind}:{port}").parse().expect("valid bind addr");
    println!(
        "workos-mock listening on http://{addr} (jwt secret: {}…, webhook secret: {}…)",
        &jwt_secret.chars().take(8).collect::<String>(),
        &webhook_secret.chars().take(8).collect::<String>(),
    );

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap_or_else(|e| {
        eprintln!("FATAL: cannot bind workos-mock to {addr}: {e}");
        std::process::exit(1);
    });

    if let Err(e) = axum::serve(listener, app).await {
        eprintln!("FATAL: workos-mock stopped unexpectedly: {e}");
        std::process::exit(1);
    }
}
