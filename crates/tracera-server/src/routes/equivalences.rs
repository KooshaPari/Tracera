//! No corresponding domain repository methods or SQLite tables exist.
//! Keep unavailable capabilities explicit rather than deriving unrelated records.
use axum::{extract::MatchedPath, http::StatusCode, routing::any, Json, Router};
use serde::Serialize;

#[derive(Serialize)]
struct Unavailable {
    error: &'static str,
    route: String,
}

async fn unavailable(path: MatchedPath) -> impl axum::response::IntoResponse {
    metrics::counter!("tracera_stub_responses_total", "route" => path.as_str().to_owned())
        .increment(1);
    (
        StatusCode::NOT_IMPLEMENTED,
        [("x-tracera-not-implemented", "true")],
        Json(Unavailable {
            error: "not_implemented",
            route: path.as_str().to_owned(),
        }),
    )
}

pub(super) fn routes<S: Clone + Send + Sync + 'static>() -> Router<S> {
    Router::new()
        .route(
            "/api/v1/projects/{project_id}/equivalences",
            any(unavailable),
        )
        .route("/api/v1/equivalences/{id}", any(unavailable))
        .route(
            "/api/v1/projects/{project_id}/equivalences/detect",
            any(unavailable),
        )
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::{
        body::{to_bytes, Body},
        http::Request,
    };
    use tower::ServiceExt;

    #[tokio::test]
    async fn route_1_returns_template_501_for_reads_and_mutations() {
        let template = "/api/v1/projects/{project_id}/equivalences";
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
        let template = "/api/v1/equivalences/{id}";
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
        let template = "/api/v1/projects/{project_id}/equivalences/detect";
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
