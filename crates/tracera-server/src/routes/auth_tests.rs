#[cfg(test)]
mod tests {
    use crate::auth::{AuthProfile, AuthToken};
    use crate::router::auth_routes::ROUTES;
    use crate::AppState;
    use axum::{
        body::{to_bytes, Body},
        http::{Request, StatusCode},
        Router,
    };
    use serde_json::Value;
    use std::{sync::Arc, time::Instant};
    use tower::ServiceExt;

    const SERVICE_TOKEN: &str = "slice-25-service-token";

    async fn fixture(profile: AuthProfile, token: AuthToken) -> Router {
        let pool = crate::db::connect_sqlite("sqlite::memory:").await.unwrap();
        sqlx::migrate!("./migrations-sqlite")
            .run(&pool)
            .await
            .unwrap();
        let state = AppState {
            store: Arc::new(crate::sqlite_store::SqliteStore::new(pool)),
            version: "test".into(),
            backend: "sqlite",
            started_at: Instant::now(),
            workos_client: tracera_workos::WorkOSClient::default_for_router(),
            cache: None,
            neo4j: None,
            r2: None,
            frontend: crate::FrontendState::Ok,
            frontend_dist: std::path::PathBuf::new(),
        };
        crate::router::build_router_with_profile(state, profile, token)
    }

    async fn get(app: Router, authorization: Option<&str>, origin: Option<&str>) -> StatusCode {
        let mut builder = Request::builder().uri("/api/v1/projects");
        if let Some(value) = authorization {
            builder = builder.header("authorization", value);
        }
        if let Some(value) = origin {
            builder = builder.header("origin", value);
        }
        app.oneshot(builder.body(Body::empty()).unwrap())
            .await
            .unwrap()
            .status()
    }

    async fn post(app: Router, authorization: Option<&str>, csrf: Option<&str>) -> StatusCode {
        let mut builder = Request::builder()
            .method("POST")
            .uri("/api/v1/projects")
            .header("content-type", "application/json")
            .header("origin", "http://127.0.0.1:18000");
        if let Some(value) = authorization {
            builder = builder.header("authorization", value);
        }
        if let Some(value) = csrf {
            builder = builder.header("x-csrf-token", value);
        }
        app.oneshot(builder.body(Body::from("{}")).unwrap())
            .await
            .unwrap()
            .status()
    }

    #[tokio::test]
    async fn valid_browser_client_succeeds() {
        let app = fixture(AuthProfile::BrowserCsrfOrigin, None).await;
        let token = crate::middleware::issue_csrf_token().await;
        assert_eq!(
            post(app, None, Some(&token)).await,
            StatusCode::NOT_IMPLEMENTED
        );
    }

    #[tokio::test]
    async fn invalid_origin_is_rejected() {
        let app = fixture(AuthProfile::BrowserCsrfOrigin, None).await;
        let token = crate::middleware::issue_csrf_token().await;
        let response = app
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri("/api/v1/projects")
                    .header("content-type", "application/json")
                    .header("origin", "https://evil.example")
                    .header("x-csrf-token", &token)
                    .body(Body::from("{}"))
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::FORBIDDEN);
    }

    #[tokio::test]
    async fn valid_service_bearer_succeeds_without_browser_csrf() {
        let app = fixture(AuthProfile::BearerService, Some(Arc::from(SERVICE_TOKEN))).await;
        assert_eq!(
            post(app, Some("Bearer slice-25-service-token"), None).await,
            StatusCode::NOT_IMPLEMENTED
        );
    }

    #[tokio::test]
    async fn invalid_bearer_token_is_rejected() {
        let app = fixture(AuthProfile::BearerService, Some(Arc::from(SERVICE_TOKEN))).await;
        assert_eq!(
            get(app, Some("Bearer wrong-token"), None).await,
            StatusCode::UNAUTHORIZED
        );
    }

    #[test]
    fn unset_profile_defaults_to_browser_and_invalid_profile_is_rejected() {
        let original = std::env::var_os(AuthProfile::ENV);
        std::env::remove_var(AuthProfile::ENV);
        let default_profile = AuthProfile::from_env();
        std::env::set_var(AuthProfile::ENV, "invalid");
        let invalid_profile = AuthProfile::from_env();
        match original {
            Some(value) => std::env::set_var(AuthProfile::ENV, value),
            None => std::env::remove_var(AuthProfile::ENV),
        }
        assert_eq!(default_profile, Ok(AuthProfile::BrowserCsrfOrigin));
        assert!(invalid_profile.is_err());
    }

    #[tokio::test]
    async fn unconfigured_bearer_profile_is_rejected() {
        let app = fixture(AuthProfile::BearerService, None).await;
        assert_eq!(
            get(app, Some("Bearer slice-25-service-token"), None).await,
            StatusCode::SERVICE_UNAVAILABLE
        );
    }

    #[tokio::test]
    async fn service_profile_does_not_accept_browser_origin_as_bypass() {
        let app = fixture(AuthProfile::BearerService, Some(Arc::from(SERVICE_TOKEN))).await;
        assert_eq!(
            get(app, None, Some("http://127.0.0.1:18000")).await,
            StatusCode::UNAUTHORIZED
        );
    }

    #[tokio::test]
    async fn legacy_auth_routes_stay_unimplemented() {
        let app = fixture(AuthProfile::BearerService, Some(Arc::from(SERVICE_TOKEN))).await;
        for path in [
            "/api/v1/auth/login",
            "/api/v1/auth/logout",
            "/api/v1/auth/refresh",
        ] {
            let response = app
                .clone()
                .oneshot(
                    Request::builder()
                        .method("POST")
                        .uri(path)
                        .header("authorization", "Bearer slice-25-service-token")
                        .body(Body::empty())
                        .unwrap(),
                )
                .await
                .unwrap();
            assert_eq!(response.status(), StatusCode::NOT_IMPLEMENTED, "{path}");
            let body: Value =
                serde_json::from_slice(&to_bytes(response.into_body(), 4096).await.unwrap())
                    .unwrap();
            assert_eq!(body["error"], "not_implemented");
        }
    }

    #[test]
    fn unavailable_mcp_adapter_route_is_declared() {
        assert_eq!(ROUTES.len(), 12);
    }
}
