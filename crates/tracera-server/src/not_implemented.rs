//! Honest responses for registered capabilities that have no implementation.
use axum::{
    extract::MatchedPath,
    http::{header::HeaderName, StatusCode},
    response::IntoResponse,
    Json,
};
use serde::Serialize;

#[derive(Serialize)]
pub struct NotImplementedResponse {
    error: &'static str,
    route: String,
}

pub async fn not_implemented(path: MatchedPath) -> impl IntoResponse {
    // Template labels keep IDs and query strings out of metric cardinality.
    let template = path.as_str().to_owned();
    metrics::counter!("tracera_stub_responses_total", "route" => template.clone()).increment(1);
    let mut headers = axum::http::HeaderMap::new();
    headers.insert(
        HeaderName::from_static("x-tracera-not-implemented"),
        axum::http::HeaderValue::from_static("true"),
    );
    headers.insert(
        HeaderName::from_static("x-tracera-stub-template"),
        axum::http::HeaderValue::from_str(&template)
            .unwrap_or(axum::http::HeaderValue::from_static("stub")),
    );
    (
        StatusCode::NOT_IMPLEMENTED,
        headers,
        Json(NotImplementedResponse {
            error: "not_implemented",
            route: template,
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
            serde_json::json!({"error":"not_implemented", "route":"/api/v1/items/{id}"})
        );
        assert!(handle
            .render()
            .contains("tracera_stub_responses_total{route=\"/api/v1/items/{id}\"} 1"));
    }
    #[tokio::test]
    async fn reprobe_every_registered_stub_get() {
        let any_stub =
            regex::Regex::new(r#"(?s)\.route\(\s*"([^"]+)",\s*any\(not_implemented\)"#).unwrap();
        let fallback_stub = regex::Regex::new(
            r#"(?s)\.route\(\s*"([^"]+)",\s*get\([^)]*\)\.fallback\(not_implemented\)"#,
        )
        .unwrap();
        let parameter = regex::Regex::new(r"\{[^}]+\}").unwrap();
        let router_src = include_str!("router.rs");
        let any_count = any_stub.captures_iter(router_src).count();
        let fallback_count = fallback_stub.captures_iter(router_src).count();
        let expected = any_count + fallback_count;
        // The floor guards the regexes themselves: if a refactor stops them
        // matching, this fails instead of silently probing zero routes.
        assert!(
            expected >= 30,
            "stub registration scan found only {expected} sites; pattern drift?"
        );
        let mut probed = 0;
        for capture in any_stub.captures_iter(router_src) {
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
            assert_eq!(body["route"], template);
            assert!(body.get("stub").is_none());
            probed += 1;
        }
        // `.fallback(not_implemented)` sites serve real GETs; the stub only
        // answers non-GET methods, so probe those with POST.
        for capture in fallback_stub.captures_iter(router_src) {
            let template = &capture[1];
            let path = parameter.replace_all(template, "probe-id");
            let app = Router::new().route(
                template,
                axum::routing::get(|| async { "real" }).fallback(not_implemented),
            );
            let response = app
                .oneshot(
                    Request::builder()
                        .method("POST")
                        .uri(path.as_ref())
                        .body(Body::empty())
                        .unwrap(),
                )
                .await
                .unwrap();
            assert_eq!(response.status(), StatusCode::NOT_IMPLEMENTED, "{path}");
            assert_eq!(response.headers()["x-tracera-not-implemented"], "true");
            probed += 1;
        }
        // Twelve journey registrations moved to routes/journeys.rs, where
        // data and exact template-501 contracts are exercised independently.
        assert_eq!(
            probed, expected,
            "every scanned stub registration must be probed"
        );
        println!("GET reprobe: {probed} registered stub routes, zero 200 stub responses");
    }
}
