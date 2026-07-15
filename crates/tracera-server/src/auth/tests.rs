use super::{
    config::AuthConfig,
    middleware::{
        bearer_token, AuthFailure, JwtVerifier, EVIDENCE_WRITE_SCOPES,
        INGEST_WRITE_SCOPES, READ_SCOPE,
    },
};
use axum::http::{header, HeaderMap, HeaderValue};
use jsonwebtoken::{encode, Algorithm, EncodingKey, Header};
use serde::Serialize;
use std::time::{SystemTime, UNIX_EPOCH};

const SECRET: &str = "0123456789abcdef0123456789abcdef";

#[derive(Serialize)]
struct TestClaims<'a> {
    sub: &'a str,
    exp: usize,
    iss: &'a str,
    aud: &'a str,
    scope: &'a str,
    permissions: Vec<&'a str>,
}

fn verifier() -> JwtVerifier {
    JwtVerifier::from_config(
        AuthConfig::from_values(
            Some("tracera-api".to_string()),
            Some("tracera".to_string()),
            Some(SECRET.to_string()),
            None,
        )
        .unwrap(),
    )
    .unwrap()
}

fn token(scope: &str, issuer: &str, audience: &str, expires_in: i64) -> String {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs() as i64;
    encode(
        &Header::new(Algorithm::HS256),
        &TestClaims {
            sub: "user-1",
            exp: (now + expires_in) as usize,
            iss: issuer,
            aud: audience,
            scope,
            permissions: Vec::new(),
        },
        &EncodingKey::from_secret(SECRET.as_bytes()),
    )
    .unwrap()
}

fn headers(token: &str) -> HeaderMap {
    let mut headers = HeaderMap::new();
    headers.insert(
        header::AUTHORIZATION,
        HeaderValue::from_str(&format!("Bearer {token}")).unwrap(),
    );
    headers
}

#[test]
fn config_requires_bound_identity_and_exactly_one_key() {
    assert!(AuthConfig::from_values(None, None, None, None).is_err());
    assert!(AuthConfig::from_values(
        Some("tracera-api".into()),
        Some("tracera".into()),
        Some(SECRET.into()),
        Some("public-key".into()),
    )
    .is_err());
    assert!(AuthConfig::from_values(
        Some("tracera-api".into()),
        Some("tracera".into()),
        Some("short".into()),
        None,
    )
    .is_err());
}

#[test]
fn bearer_header_is_strict_and_case_insensitive() {
    let mut headers = HeaderMap::new();
    assert_eq!(bearer_token(&headers), Err(AuthFailure::Unauthorized));
    headers.insert(
        header::AUTHORIZATION,
        HeaderValue::from_static("bearer token"),
    );
    assert_eq!(bearer_token(&headers), Ok("token"));
    headers.insert(
        header::AUTHORIZATION,
        HeaderValue::from_static("Bearer token extra"),
    );
    assert_eq!(bearer_token(&headers), Err(AuthFailure::Unauthorized));
}

#[test]
fn valid_token_requires_every_scope() {
    let verifier = verifier();
    let token = token(
        "tracera:write tracera:evidence",
        "tracera",
        "tracera-api",
        300,
    );
    assert!(verifier
        .authorize(&headers(&token), EVIDENCE_WRITE_SCOPES)
        .is_ok());
    assert_eq!(
        verifier.authorize(&headers(&token), INGEST_WRITE_SCOPES),
        Err(AuthFailure::Forbidden)
    );
}

#[test]
fn invalid_expiry_issuer_and_audience_are_unauthorized() {
    let verifier = verifier();
    for token in [
        token("tracera:read", "tracera", "tracera-api", -10),
        token("tracera:read", "other", "tracera-api", 300),
        token("tracera:read", "tracera", "other", 300),
    ] {
        assert_eq!(
            verifier.authorize(&headers(&token), READ_SCOPE),
            Err(AuthFailure::Unauthorized)
        );
    }
}

#[test]
fn permissions_array_is_accepted() {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs() as usize;
    let token = encode(
        &Header::new(Algorithm::HS256),
        &TestClaims {
            sub: "user-1",
            exp: now + 300,
            iss: "tracera",
            aud: "tracera-api",
            scope: "",
            permissions: vec!["tracera:read"],
        },
        &EncodingKey::from_secret(SECRET.as_bytes()),
    )
    .unwrap();
    assert!(verifier().authorize(&headers(&token), READ_SCOPE).is_ok());
}
