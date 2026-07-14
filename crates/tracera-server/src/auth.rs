use axum::{
    extract::{Request, State},
    http::{header, HeaderMap, HeaderValue, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
    Json,
};
use jsonwebtoken::{decode, Algorithm, DecodingKey, Validation};
use serde::{Deserialize, Serialize};
use std::{collections::HashSet, env, sync::Arc};

const READ_SCOPE: &[&str] = &["tracera:read"];
const ANALYZE_SCOPE: &[&str] = &["tracera:analyze"];
const EVIDENCE_WRITE_SCOPES: &[&str] = &["tracera:write", "tracera:evidence"];
const SDLC_WRITE_SCOPES: &[&str] = &["tracera:write", "tracera:sdlc"];
const INGEST_WRITE_SCOPES: &[&str] = &["tracera:write", "tracera:ingest"];

#[derive(Clone)]
pub struct AuthState {
    verifier: Arc<JwtVerifier>,
}

struct JwtVerifier {
    key: DecodingKey,
    validation: Validation,
}

#[derive(Debug, Deserialize)]
struct Claims {
    sub: String,
    #[allow(dead_code)]
    exp: usize,
    #[allow(dead_code)]
    iss: String,
    #[allow(dead_code)]
    aud: String,
    #[serde(default)]
    scope: String,
    #[serde(default)]
    permissions: Vec<String>,
}

#[derive(Debug)]
enum SigningMode {
    Hs256(String),
    Rs256(String),
}

#[derive(Debug)]
struct AuthConfig {
    audience: String,
    issuer: String,
    signing: SigningMode,
}

#[derive(Serialize)]
struct AuthErrorBody {
    error: &'static str,
}

impl AuthConfig {
    fn from_env() -> Result<Self, String> {
        Self::from_values(
            env::var("TRACERA_JWT_AUDIENCE").ok(),
            env::var("TRACERA_JWT_ISSUER").ok(),
            env::var("TRACERA_JWT_SECRET").ok(),
            env::var("TRACERA_JWT_PUBLIC_KEY").ok(),
        )
    }

    fn from_values(
        audience: Option<String>,
        issuer: Option<String>,
        secret: Option<String>,
        public_key: Option<String>,
    ) -> Result<Self, String> {
        let audience = required_value("TRACERA_JWT_AUDIENCE", audience)?;
        let issuer = required_value("TRACERA_JWT_ISSUER", issuer)?;
        let secret = non_empty(secret);
        let public_key = non_empty(public_key).map(|value| value.replace("\\n", "\n"));

        let signing = match (secret, public_key) {
            (Some(secret), None) => {
                if secret.as_bytes().len() < 32 {
                    return Err("TRACERA_JWT_SECRET must contain at least 32 bytes".to_string());
                }
                SigningMode::Hs256(secret)
            }
            (None, Some(public_key)) => SigningMode::Rs256(public_key),
            (Some(_), Some(_)) => {
                return Err(
                    "configure exactly one of TRACERA_JWT_SECRET or TRACERA_JWT_PUBLIC_KEY"
                        .to_string(),
                )
            }
            (None, None) => {
                return Err(
                    "configure exactly one of TRACERA_JWT_SECRET or TRACERA_JWT_PUBLIC_KEY"
                        .to_string(),
                )
            }
        };

        Ok(Self {
            audience,
            issuer,
            signing,
        })
    }
}

impl JwtVerifier {
    fn from_config(config: AuthConfig) -> Result<Self, String> {
        let (algorithm, key) = match config.signing {
            SigningMode::Hs256(secret) => (
                Algorithm::HS256,
                DecodingKey::from_secret(secret.as_bytes()),
            ),
            SigningMode::Rs256(public_key) => (
                Algorithm::RS256,
                DecodingKey::from_rsa_pem(public_key.as_bytes()).map_err(|_| {
                    "TRACERA_JWT_PUBLIC_KEY must be a valid RSA PEM key".to_string()
                })?,
            ),
        };
        let mut validation = Validation::new(algorithm);
        validation.set_audience(&[config.audience]);
        validation.set_issuer(&[config.issuer]);
        validation.set_required_spec_claims(&["exp", "sub", "iss", "aud"]);
        validation.leeway = 0;

        Ok(Self { key, validation })
    }

    fn authorize(&self, headers: &HeaderMap, required_scopes: &[&str]) -> Result<(), AuthFailure> {
        let token = bearer_token(headers)?;
        let token_data = decode::<Claims>(token, &self.key, &self.validation)
            .map_err(|_| AuthFailure::Unauthorized)?;
        if token_data.claims.sub.trim().is_empty() {
            return Err(AuthFailure::Unauthorized);
        }

        let scopes = token_data
            .claims
            .scope
            .split_ascii_whitespace()
            .map(str::to_owned)
            .chain(token_data.claims.permissions)
            .collect::<HashSet<_>>();
        if required_scopes.iter().all(|scope| scopes.contains(*scope)) {
            Ok(())
        } else {
            Err(AuthFailure::Forbidden)
        }
    }
}

impl AuthState {
    pub fn from_env() -> Result<Self, String> {
        Ok(Self {
            verifier: Arc::new(JwtVerifier::from_config(AuthConfig::from_env()?)?),
        })
    }
}

#[derive(Debug, PartialEq, Eq)]
enum AuthFailure {
    Unauthorized,
    Forbidden,
}

impl IntoResponse for AuthFailure {
    fn into_response(self) -> Response {
        match self {
            Self::Unauthorized => (
                StatusCode::UNAUTHORIZED,
                [(header::WWW_AUTHENTICATE, HeaderValue::from_static("Bearer"))],
                Json(AuthErrorBody {
                    error: "unauthorized",
                }),
            )
                .into_response(),
            Self::Forbidden => (
                StatusCode::FORBIDDEN,
                Json(AuthErrorBody {
                    error: "insufficient_scope",
                }),
            )
                .into_response(),
        }
    }
}

fn required_value(name: &str, value: Option<String>) -> Result<String, String> {
    non_empty(value).ok_or_else(|| format!("{name} must be configured"))
}

fn non_empty(value: Option<String>) -> Option<String> {
    value.and_then(|value| {
        let value = value.trim().to_string();
        (!value.is_empty()).then_some(value)
    })
}

fn bearer_token(headers: &HeaderMap) -> Result<&str, AuthFailure> {
    let mut values = headers.get_all(header::AUTHORIZATION).iter();
    let value = values.next().ok_or(AuthFailure::Unauthorized)?;
    if values.next().is_some() {
        return Err(AuthFailure::Unauthorized);
    }
    let value = value.to_str().map_err(|_| AuthFailure::Unauthorized)?;
    let mut parts = value.split_ascii_whitespace();
    let scheme = parts.next().ok_or(AuthFailure::Unauthorized)?;
    let token = parts.next().ok_or(AuthFailure::Unauthorized)?;
    if !scheme.eq_ignore_ascii_case("bearer") || token.is_empty() || parts.next().is_some() {
        return Err(AuthFailure::Unauthorized);
    }
    Ok(token)
}

async fn authorize(
    state: AuthState,
    request: Request,
    next: Next,
    required_scopes: &[&str],
) -> Response {
    match state.verifier.authorize(request.headers(), required_scopes) {
        Ok(()) => next.run(request).await,
        Err(error) => error.into_response(),
    }
}

pub async fn require_read(
    State(state): State<AuthState>,
    request: Request,
    next: Next,
) -> Response {
    authorize(state, request, next, READ_SCOPE).await
}

pub async fn require_analyze(
    State(state): State<AuthState>,
    request: Request,
    next: Next,
) -> Response {
    authorize(state, request, next, ANALYZE_SCOPE).await
}

pub async fn require_evidence_write(
    State(state): State<AuthState>,
    request: Request,
    next: Next,
) -> Response {
    authorize(state, request, next, EVIDENCE_WRITE_SCOPES).await
}

pub async fn require_sdlc_write(
    State(state): State<AuthState>,
    request: Request,
    next: Next,
) -> Response {
    authorize(state, request, next, SDLC_WRITE_SCOPES).await
}

pub async fn require_ingest_write(
    State(state): State<AuthState>,
    request: Request,
    next: Next,
) -> Response {
    authorize(state, request, next, INGEST_WRITE_SCOPES).await
}

#[cfg(test)]
mod tests;
