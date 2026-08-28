use axum::{
    body::Body,
    extract::State,
    http::{header::AUTHORIZATION, Request, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
};
use std::sync::Arc;

pub(crate) type AuthToken = Option<Arc<str>>;

/// Protect every application route when a public listener is enabled. Health
/// probes remain unauthenticated so orchestrators can determine liveness and
/// readiness without carrying application credentials.
pub(crate) async fn require_bearer(
    State(expected): State<AuthToken>,
    request: Request<Body>,
    next: Next,
) -> Response {
    if expected.is_none() || is_health_route(request.uri().path()) {
        return next.run(request).await;
    }

    let valid = request
        .headers()
        .get(AUTHORIZATION)
        .and_then(|value| value.to_str().ok())
        .and_then(|value| value.strip_prefix("Bearer "))
        .is_some_and(|provided| {
            constant_time_equal(provided.as_bytes(), expected.as_ref().unwrap().as_bytes())
        });

    if valid {
        next.run(request).await
    } else {
        (
            StatusCode::UNAUTHORIZED,
            [("www-authenticate", "Bearer")],
            "unauthorized",
        )
            .into_response()
    }
}

fn is_health_route(path: &str) -> bool {
    matches!(
        path,
        "/health" | "/healthz" | "/ready" | "/readyz" | "/api/v1/health" | "/api/v1/csrf-token"
    ) || path.ends_with("/health")
        || path.ends_with("/healthz")
}

fn constant_time_equal(left: &[u8], right: &[u8]) -> bool {
    let mut difference = left.len() ^ right.len();
    for index in 0..left.len().max(right.len()) {
        difference |= usize::from(left.get(index).copied().unwrap_or_default())
            ^ usize::from(right.get(index).copied().unwrap_or_default());
    }
    difference == 0
}

#[cfg(test)]
mod tests {
    use super::{constant_time_equal, is_health_route};

    #[test]
    fn constant_time_comparison_requires_exact_bytes() {
        assert!(constant_time_equal(b"token", b"token"));
        assert!(!constant_time_equal(b"token", b"Token"));
        assert!(!constant_time_equal(b"token", b"token-extra"));
    }

    #[test]
    fn health_probe_routes_are_public_but_application_routes_are_not() {
        for path in [
            "/health",
            "/healthz",
            "/ready",
            "/readyz",
            "/evidence/health",
            "/api/v1/health",
            "/api/v1/csrf-token",
        ] {
            assert!(is_health_route(path), "{path} should be a probe route");
        }
        assert!(!is_health_route("/evidence"));
        assert!(!is_health_route("/api/v1/projects"));
    }
}
