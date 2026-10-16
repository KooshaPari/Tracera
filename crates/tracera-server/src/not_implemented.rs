//! Honest responses for registered capabilities that have no implementation.
use axum::{
    extract::{MatchedPath, OriginalUri},
    http::{header::HeaderName, StatusCode},
    response::IntoResponse,
    Json,
};
use serde::Serialize;

pub const SINCE: &str = "2026-10-16";

#[derive(Serialize)]
pub struct NotImplementedResponse {
    error: &'static str,
    route: String,
    since: &'static str,
}

pub async fn not_implemented(
    path: MatchedPath,
    OriginalUri(uri): OriginalUri,
) -> impl IntoResponse {
    // Template labels keep IDs and query strings out of metric cardinality.
    metrics::counter!("tracera_stub_responses_total", "route" => path.as_str().to_owned())
        .increment(1);
    (
        StatusCode::NOT_IMPLEMENTED,
        [(HeaderName::from_static("x-tracera-not-implemented"), "true")],
        Json(NotImplementedResponse {
            error: "not_implemented",
            route: uri.path().to_owned(),
            since: SINCE,
        }),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::{
        body::{to_bytes, Body},
        http::Request,
        routing::any,
        Router,
    };
    use tower::ServiceExt;

    #[tokio::test]
    async fn get_stub_returns_typed_501_and_counts_template() {
        let recorder = metrics_exporter_prometheus::PrometheusBuilder::new().build_recorder();
        let handle = recorder.handle();
        let _guard = metrics::set_default_local_recorder(&recorder);
        let app = Router::new().route("/api/v1/items/{id}", any(not_implemented));
        let response = app
            .oneshot(
                Request::builder()
                    .uri("/api/v1/items/real-id?secret=ignored")
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::NOT_IMPLEMENTED);
        assert_eq!(response.headers()["x-tracera-not-implemented"], "true");
        let body: serde_json::Value =
            serde_json::from_slice(&to_bytes(response.into_body(), 4096).await.unwrap()).unwrap();
        assert_eq!(
            body,
            serde_json::json!({"error":"not_implemented", "route":"/api/v1/items/real-id", "since":SINCE})
        );
        assert!(handle
            .render()
            .contains("tracera_stub_responses_total{route=\"/api/v1/items/{id}\"} 1"));
    }
    #[tokio::test]
    async fn reprobe_every_registered_stub_get() {
        let pattern =
            regex::Regex::new(r#"(?s)\.route\(\s*"([^"]+)",\s*any\(not_implemented\)"#).unwrap();
        let parameter = regex::Regex::new(r"\{[^}]+\}").unwrap();
        let mut probed = 0;
        for capture in pattern.captures_iter(include_str!("router.rs")) {
            let template = &capture[1];
            let path = parameter.replace_all(template, "probe-id");
            let app = Router::new().route(template, any(not_implemented));
            let response = app
                .oneshot(
                    Request::builder()
                        .uri(path.as_ref())
                        .body(Body::empty())
                        .unwrap(),
                )
                .await
                .unwrap();
            assert_eq!(response.status(), StatusCode::NOT_IMPLEMENTED, "{path}");
            assert_eq!(response.headers()["x-tracera-not-implemented"], "true");
            let body: serde_json::Value =
                serde_json::from_slice(&to_bytes(response.into_body(), 4096).await.unwrap())
                    .unwrap();
            assert_eq!(body["error"], "not_implemented");
            assert_eq!(body["route"], path.as_ref());
            assert!(body.get("stub").is_none());
            probed += 1;
        }
        assert!(
            probed > 50,
            "expected full registered stub cohort, got {probed}"
        );
        println!("GET reprobe: {probed} registered stub routes, zero 200 stub responses");
    }
}
