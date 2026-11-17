//! Unavailable libraries operations: no matching Store contract.
use axum::{routing::any, Router};

pub(super) const ROUTES: &[&str] = &[
    "/api/v1/projects/{project_id}/libraries",
    "/api/v1/libraries/{id}",
    "/api/v1/libraries/{id}/components",
    "/api/v1/components/{id}",
    "/api/v1/components/{id}/usage",
];

pub(super) fn routes<S: Clone + Send + Sync + 'static>() -> Router<S> {
    ROUTES.iter().fold(Router::new(), |router, path| {
        router.route(path, any(crate::not_implemented::not_implemented))
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::http::StatusCode;
    use axum::{
        body::{to_bytes, Body},
        http::Request,
    };
    use tower::ServiceExt;

    #[tokio::test]
    async fn route_1_returns_template_501_for_reads_and_mutations() {
        let template = "/api/v1/projects/{project_id}/libraries";
        let path = template
            .replace("{project_id}", "project-a")
            .replace("{id}", "missing-id");
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
            let body: serde_json::Value =
                serde_json::from_slice(&to_bytes(response.into_body(), 4096).await.unwrap())
                    .unwrap();
            assert_eq!(
                body,
                serde_json::json!({"error": "not_implemented", "route": template})
            );
        }
    }
    #[tokio::test]
    async fn route_2_returns_template_501_for_reads_and_mutations() {
        let template = "/api/v1/libraries/{id}";
        let path = template
            .replace("{project_id}", "project-a")
            .replace("{id}", "missing-id");
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
            let body: serde_json::Value =
                serde_json::from_slice(&to_bytes(response.into_body(), 4096).await.unwrap())
                    .unwrap();
            assert_eq!(
                body,
                serde_json::json!({"error": "not_implemented", "route": template})
            );
        }
    }
    #[tokio::test]
    async fn route_3_returns_template_501_for_reads_and_mutations() {
        let template = "/api/v1/libraries/{id}/components";
        let path = template
            .replace("{project_id}", "project-a")
            .replace("{id}", "missing-id");
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
            let body: serde_json::Value =
                serde_json::from_slice(&to_bytes(response.into_body(), 4096).await.unwrap())
                    .unwrap();
            assert_eq!(
                body,
                serde_json::json!({"error": "not_implemented", "route": template})
            );
        }
    }
    #[tokio::test]
    async fn route_4_returns_template_501_for_reads_and_mutations() {
        let template = "/api/v1/components/{id}";
        let path = template
            .replace("{project_id}", "project-a")
            .replace("{id}", "missing-id");
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
            let body: serde_json::Value =
                serde_json::from_slice(&to_bytes(response.into_body(), 4096).await.unwrap())
                    .unwrap();
            assert_eq!(
                body,
                serde_json::json!({"error": "not_implemented", "route": template})
            );
        }
    }
    #[tokio::test]
    async fn route_5_returns_template_501_for_reads_and_mutations() {
        let template = "/api/v1/components/{id}/usage";
        let path = template
            .replace("{project_id}", "project-a")
            .replace("{id}", "missing-id");
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
            let body: serde_json::Value =
                serde_json::from_slice(&to_bytes(response.into_body(), 4096).await.unwrap())
                    .unwrap();
            assert_eq!(
                body,
                serde_json::json!({"error": "not_implemented", "route": template})
            );
        }
    }
}
