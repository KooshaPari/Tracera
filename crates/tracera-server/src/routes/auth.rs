//! Legacy auth operations intentionally remain unavailable in this API.
//!
//! Authentication belongs to WorkOS AuthKit and the deployment ingress
//! (Cloudflare Access / authenticated Caddy proxy), not these legacy routes.
//! See `docs/quickstart.md` section 5, `docs/04-guides/ENVIRONMENTS.md`, and
//! `deploy/selfhost/README.md`. The latter documents an unwired AuthKit insertion
//! point: upstream ownership is a design boundary, not proof of live protection.
//! The separate `/auth/workos/*` integration is configured by the existing router.
//! These responses never create credentials, end sessions, or refresh tokens.
use axum::{extract::MatchedPath, http::StatusCode, routing::any, Json, Router};
use serde::Serialize;

const MESSAGE: &str = "Authentication is handled upstream by WorkOS AuthKit and the deployment ingress (Cloudflare Access / authenticated Caddy proxy); this legacy API operation is not implemented.";

#[derive(Serialize)]
struct AuthNotImplemented {
    error: &'static str,
    route: String,
    message: &'static str,
}

async fn unavailable(path: MatchedPath) -> impl axum::response::IntoResponse {
    metrics::counter!("tracera_stub_responses_total", "route" => path.as_str().to_owned())
        .increment(1);
    (
        StatusCode::NOT_IMPLEMENTED,
        [("x-tracera-not-implemented", "true")],
        Json(AuthNotImplemented {
            error: "not_implemented",
            route: path.as_str().to_owned(),
            message: MESSAGE,
        }),
    )
}

pub(super) fn routes<S: Clone + Send + Sync + 'static>() -> Router<S> {
    Router::new()
        .route("/api/v1/auth/login", any(unavailable))
        .route("/api/v1/auth/logout", any(unavailable))
        .route("/api/v1/auth/refresh", any(unavailable))
}

pub(crate) const ROUTES: &[&str] = &[
    "/api/v1/auth/account",
    "/api/v1/auth/authkit/authorize",
    "/api/v1/auth/authkit/callback",
    "/api/v1/auth/authkit/refresh",
    "/api/v1/auth/change-password",
    "/api/v1/auth/profile",
    "/api/v1/auth/request-verification",
    "/api/v1/auth/reset-password",
    "/api/v1/auth/reset-password/confirm",
    "/api/v1/auth/user",
    "/api/v1/auth/verify-email",
    "/auth/me",
];

pub(crate) fn w9_routes() -> Router<crate::AppState> {
    ROUTES.iter().fold(Router::new(), |router, path| {
        router.route(path, any(crate::not_implemented::not_implemented))
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::{
        body::{to_bytes, Body},
        http::Request,
    };
    use tower::ServiceExt;

    async fn assert_contract(path: &str) {
        for method in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"] {
            let response = routes::<()>()
                .oneshot(
                    Request::builder()
                        .method(method)
                        .uri(format!("{path}?ignored=private-value"))
                        .header("content-type", "application/json")
                        .body(Body::from("{invalid-json"))
                        .unwrap(),
                )
                .await
                .unwrap();
            assert_eq!(
                response.status(),
                StatusCode::NOT_IMPLEMENTED,
                "{method} {path}"
            );
            assert_eq!(response.headers()["content-type"], "application/json");
            assert_eq!(response.headers()["x-tracera-not-implemented"], "true");
            assert!(!response.headers().contains_key("set-cookie"));
            assert!(!response.headers().contains_key("location"));
            let body: serde_json::Value =
                serde_json::from_slice(&to_bytes(response.into_body(), 4096).await.unwrap())
                    .unwrap();
            assert_eq!(
                body,
                serde_json::json!({
                    "error": "not_implemented", "route": path, "message": MESSAGE
                })
            );
        }
    }

    #[tokio::test]
    async fn login_returns_upstream_owned_501() {
        assert_contract("/api/v1/auth/login").await;
    }

    #[tokio::test]
    async fn logout_returns_upstream_owned_501() {
        assert_contract("/api/v1/auth/logout").await;
    }

    #[tokio::test]
    async fn refresh_returns_upstream_owned_501() {
        assert_contract("/api/v1/auth/refresh").await;
    }
}

/// Authorized product scope shared by every durable observation handler.
pub(super) struct ProductScope(pub (String, u64));

#[derive(Serialize)]
struct ProductAccessDenied {
    error: &'static str,
}

impl<S: Send + Sync> axum::extract::FromRequestParts<S> for ProductScope {
    type Rejection = axum::response::Response;

    async fn from_request_parts(
        parts: &mut axum::http::request::Parts,
        state: &S,
    ) -> Result<Self, Self::Rejection> {
        use axum::{extract::Path, response::IntoResponse};
        let Path(scope) = Path::<(String, u64)>::from_request_parts(parts, state)
            .await
            .map_err(IntoResponse::into_response)?;
        let allowed = std::env::var("TRACERA_PRODUCT_IDS")
            .ok()
            .is_some_and(|ids| {
                ids.split(',')
                    .map(str::trim)
                    .any(|id| !id.is_empty() && id == scope.0)
            });
        if !allowed {
            return Err((
                StatusCode::FORBIDDEN,
                Json(ProductAccessDenied {
                    error: "product_access_denied",
                }),
            )
                .into_response());
        }
        Ok(Self(scope))
    }
}
