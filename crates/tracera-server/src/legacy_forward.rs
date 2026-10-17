//! Forward-on-stub middleware. Off unless LEGACY_BASE_URL is set.
//! The legacy service MUST accept the same bearer token as this server:
//! the bridge relays `authorization` verbatim and runs after require_bearer,
//! so a legacy that rejects it answers 401/403 which is relayed as-is.
//! Forwards only responses that carry `x-tracera-not-implemented: true`
//! (set by crate::not_implemented), plus always-owned legacy prefixes.
use axum::{
    body::{to_bytes, Body},
    extract::{Request, State},
    http::{header, HeaderMap, HeaderName, HeaderValue, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
    Json,
};
use std::{sync::Arc, time::Duration};

pub const FORWARDED: &str = "x-tracera-forwarded";
const STUB: &str = "x-tracera-not-implemented";
const MAX_BODY: usize = crate::router::MAX_REQUEST_BODY_BYTES;

#[derive(Clone)]
pub struct Legacy {
    pub base: String,
    pub owned_prefixes: Vec<String>,
    pub client: reqwest::Client,
}

impl Legacy {
    pub fn from_env() -> Option<Arc<Self>> {
        let base = std::env::var("LEGACY_BASE_URL")
            .ok()?
            .trim_end_matches('/')
            .to_string();
        if base.is_empty() {
            return None;
        }
        let owned_prefixes = std::env::var("LEGACY_OWNED_PREFIXES")
            .unwrap_or_default()
            .split(',')
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect();
        let client = reqwest::Client::builder()
            .timeout(Duration::from_secs(8))
            .redirect(reqwest::redirect::Policy::none())
            .build()
            .ok()?;
        Some(Arc::new(Self {
            base,
            owned_prefixes,
            client,
        }))
    }
}

fn hop_by_hop(name: &HeaderName) -> bool {
    matches!(
        name.as_str(),
        "connection"
            | "keep-alive"
            | "proxy-authenticate"
            | "proxy-authorization"
            | "te"
            | "trailers"
            | "transfer-encoding"
            | "upgrade"
            | "host"
            | "content-length"
            | "cookie"
    )
}

pub async fn forward_on_stub(
    State(legacy): State<Option<Arc<Legacy>>>,
    req: Request,
    next: Next,
) -> Response {
    let Some(legacy) = legacy else {
        return next.run(req).await;
    };
    if req.headers().contains_key(FORWARDED) {
        return next.run(req).await;
    }
    let upgrade = req.headers().contains_key(header::UPGRADE)
        || req
            .headers()
            .get(header::ACCEPT)
            .map_or(false, |v| v.as_bytes().starts_with(b"text/event-stream"));
    let (parts, body) = req.into_parts();
    let path = parts.uri.path().to_string();
    let owned_prefix = legacy.owned_prefixes.iter().find_map(|p| {
        let p = p.trim_end_matches('/');
        if path == p || path.starts_with(&format!("{p}/")) {
            Some(p.to_string())
        } else {
            None
        }
    });
    let owned = owned_prefix.is_some();
    let bytes = match to_bytes(body, MAX_BODY).await {
        Ok(b) => b,
        Err(_) => return StatusCode::PAYLOAD_TOO_LARGE.into_response(),
    };
    let mut route_label = owned_prefix.clone().unwrap_or_default();
    if !owned {
        let rebuilt = Request::from_parts(parts.clone(), Body::from(bytes.clone()));
        let resp = next.run(rebuilt).await;
        let is_stub = resp.status() == StatusCode::NOT_IMPLEMENTED
            && resp
                .headers()
                .get(STUB)
                .map_or(false, |v| v == "true");
        if !is_stub || upgrade {
            return resp;
        }
        // Metric label = matched route template (carried from not_implemented), never the raw path.
        route_label = resp
            .headers()
            .get("x-tracera-stub-template")
            .and_then(|v| v.to_str().ok())
            .unwrap_or("stub")
            .to_string();
    }
    // The bridge cannot proxy upgrades/SSE; refuse them on owned prefixes.
    if upgrade {
        return (
            StatusCode::NOT_IMPLEMENTED,
            Json(serde_json::json!({"error":"upgrade_not_supported_by_bridge"})),
        )
            .into_response();
    }
    metrics::counter!("tracera_stub_forwarded_total", "route" => route_label).increment(1);
    let mut url = format!("{}{}", legacy.base, path);
    if let Some(q) = parts.uri.query() {
        url.push('?');
        url.push_str(q);
    }
    let mut headers = HeaderMap::new();
    for (k, v) in parts.headers.iter() {
        if !hop_by_hop(k) {
            headers.append(k.clone(), v.clone());
        }
    }
    headers.insert(
        HeaderName::from_static("x-tracera-forwarded"),
        HeaderValue::from_static("1"),
    );
    let result = legacy
        .client
        .request(parts.method.clone(), &url)
        .headers(headers)
        .body(bytes.to_vec())
        .send()
        .await;
    match result {
        Ok(r) => {
            let status = StatusCode::from_u16(r.status().as_u16())
                .unwrap_or(StatusCode::BAD_GATEWAY);
            let mut headers = HeaderMap::new();
            for (k, v) in r.headers().iter() {
                let n = k.as_str();
                if !hop_by_hop(k) && n != "set-cookie" && !n.starts_with("access-control-") {
                    headers.append(k.clone(), v.clone());
                }
            }
            headers.insert(
                HeaderName::from_static("x-tracera-served-by"),
                HeaderValue::from_static("legacy"),
            );
            match r.bytes().await {
                Ok(b) => (status, headers, b).into_response(),
                Err(_) => legacy_unavailable(),
            }
        }
        Err(_) => legacy_unavailable(),
    }
}

fn legacy_unavailable() -> Response {
    (
        StatusCode::BAD_GATEWAY,
        Json(serde_json::json!({"error":"legacy_unavailable"})),
    )
        .into_response()
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::{routing::post, Router};
    use std::sync::atomic::{AtomicUsize, Ordering};
    use tokio::net::TcpListener;

    async fn spawn_app(legacy: Option<Arc<Legacy>>) -> String {
        let app = Router::new()
            .route(
                "/stub",
                axum::routing::any(|| async {
                    (
                        StatusCode::NOT_IMPLEMENTED,
                        [(HeaderName::from_static("x-tracera-not-implemented"), "true")],
                        "stub",
                    )
                }),
            )
            .route("/real", axum::routing::get(|| async { "real" }))
            .layer(axum::middleware::from_fn_with_state(
                legacy,
                forward_on_stub,
            ));
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap();
        tokio::spawn(async move { axum::serve(listener, app).await.unwrap() });
        format!("http://127.0.0.1:{}", addr.port())
    }


    async fn spawn_legacy(status: StatusCode, calls: std::sync::Arc<AtomicUsize>) -> String {
        let c1 = calls.clone();
        let c2 = calls.clone();
        let app = Router::new()
            .route(
                "/stub",
                axum::routing::any(move |uri: axum::http::Uri, body: String| {
                    let c1 = c1.clone();
                    async move {
                        c1.fetch_add(1, Ordering::SeqCst);
                        (status, format!("echo:{body}|{}", uri.query().unwrap_or("")))
                    }
                }),
            )
            .route(
                "/echo",
                post(move |body: String| {
                    let c2 = c2.clone();
                    async move {
                        c2.fetch_add(1, Ordering::SeqCst);
                        format!("echo:{body}")
                    }
                }),
            );
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap();
        tokio::spawn(async move { axum::serve(listener, app).await.unwrap() });
        format!("http://127.0.0.1:{}", addr.port())
    }

    fn legacy_for(base: &str) -> Option<Arc<Legacy>> {
        Some(Arc::new(Legacy {
            base: base.to_string(),
            owned_prefixes: vec![],
            client: reqwest::Client::builder()
                .redirect(reqwest::redirect::Policy::none())
                .build()
                .unwrap(),
        }))
    }

    #[tokio::test]
    async fn bridge_off_keeps_501() {
        let app = spawn_app(None).await;
        let r = reqwest::get(format!("{app}/stub")).await.unwrap();
        assert_eq!(r.status(), StatusCode::NOT_IMPLEMENTED);
    }

    #[tokio::test]
    async fn stub_get_forwarded() {
        let calls = std::sync::Arc::new(AtomicUsize::new(0));
        let legacy = spawn_legacy(StatusCode::OK, calls.clone()).await;
        let app = spawn_app(legacy_for(&legacy)).await;
        let r = reqwest::get(format!("{app}/stub")).await.unwrap();
        assert_eq!(r.status(), StatusCode::OK);
        assert_eq!(
            r.headers().get("x-tracera-served-by").unwrap(),
            "legacy"
        );
        assert_eq!(r.text().await.unwrap(), "echo:|");
        assert_eq!(calls.load(Ordering::SeqCst), 1);
    }

    #[tokio::test]
    async fn loop_guard_not_forwarded() {
        let calls = std::sync::Arc::new(AtomicUsize::new(0));
        let legacy = spawn_legacy(StatusCode::OK, calls.clone()).await;
        let app = spawn_app(legacy_for(&legacy)).await;
        let r = reqwest::Client::new()
            .get(format!("{app}/stub"))
            .header("x-tracera-forwarded", "1")
            .send()
            .await
            .unwrap();
        assert_eq!(r.status(), StatusCode::NOT_IMPLEMENTED);
        assert_eq!(calls.load(Ordering::SeqCst), 0);
    }

    #[tokio::test]
    async fn legacy_down_gives_502() {
        let dead = Some(Arc::new(Legacy {
            base: "http://127.0.0.1:9".to_string(),
            owned_prefixes: vec![],
            client: reqwest::Client::builder()
                .timeout(Duration::from_millis(300))
                .build()
                .unwrap(),
        }));
        let app = spawn_app(dead).await;
        let r = reqwest::get(format!("{app}/stub")).await.unwrap();
        assert_eq!(r.status(), StatusCode::BAD_GATEWAY);
    }

    #[tokio::test]
    async fn legacy_error_status_passes_through() {
        let calls = std::sync::Arc::new(AtomicUsize::new(0));
        let legacy = spawn_legacy(StatusCode::NOT_FOUND, calls.clone()).await;
        let app = spawn_app(legacy_for(&legacy)).await;
        let r = reqwest::get(format!("{app}/stub")).await.unwrap();
        assert_eq!(r.status(), StatusCode::NOT_FOUND);
    }

    #[tokio::test]
    async fn real_route_not_forwarded() {
        let calls = std::sync::Arc::new(AtomicUsize::new(0));
        let legacy = spawn_legacy(StatusCode::OK, calls.clone()).await;
        let app = spawn_app(legacy_for(&legacy)).await;
        let r = reqwest::get(format!("{app}/real")).await.unwrap();
        assert_eq!(r.status(), StatusCode::OK);
        assert_eq!(r.text().await.unwrap(), "real");
        assert_eq!(calls.load(Ordering::SeqCst), 0);
    }

    #[tokio::test]
    async fn owned_prefix_bypasses_local() {
        let calls = std::sync::Arc::new(AtomicUsize::new(0));
        let legacy_base = spawn_legacy(StatusCode::OK, calls.clone()).await;
        let mut l = (*legacy_for(&legacy_base).unwrap()).clone();
        l.owned_prefixes = vec!["/real".to_string()];
        let app = spawn_app(Some(Arc::new(l))).await;
        // /real is a real local route, but the owned prefix forces legacy;
        // legacy mock has no /real route -> its 404 proves we forwarded.
        let r = reqwest::get(format!("{app}/real")).await.unwrap();
        assert_eq!(r.status(), StatusCode::NOT_FOUND);
        assert_eq!(
            r.headers().get("x-tracera-served-by").map(|v| v.to_str().unwrap().to_string()),
            Some("legacy".to_string())
        );
    }

    #[tokio::test]
    async fn cookie_header_stripped() {
        // Legacy /echo route asserts by echoing body; we check via a
        // dedicated capture: use a tiny handler that returns whether it saw a Cookie header.
        let app_legacy = Router::new().route(
            "/stub",
            axum::routing::any(|headers: HeaderMap| async move {
                if headers.contains_key(header::COOKIE) {
                    "cookie-leaked"
                } else {
                    "cookie-clean"
                }
            }),
        );
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap();
        tokio::spawn(async move { axum::serve(listener, app_legacy).await.unwrap() });
        let base = format!("http://127.0.0.1:{}", addr.port());
        let app = spawn_app(legacy_for(&base)).await;
        let r = reqwest::Client::new()
            .get(format!("{app}/stub"))
            .header(header::COOKIE, "session=secret")
            .send()
            .await
            .unwrap();
        assert_eq!(r.text().await.unwrap(), "cookie-clean");
    }
    #[tokio::test]
    async fn owned_prefix_segment_boundary() {
        let calls = std::sync::Arc::new(AtomicUsize::new(0));
        let legacy = spawn_legacy(StatusCode::OK, calls.clone()).await;
        let mut l = legacy_for(&legacy).unwrap();
        Arc::get_mut(&mut l).unwrap().owned_prefixes = vec!["/legacy".into()];
        let app = spawn_app(Some(l)).await;
        let r = reqwest::get(format!("{app}/legacy/x")).await.unwrap();
        // forwarded: legacy mock has no /legacy/x -> its 404 + served-by prove the hop
        // (the mock only counts hits on its registered routes, so no counter assert here)
        assert_eq!(r.status(), StatusCode::NOT_FOUND);
        assert_eq!(
            r.headers().get("x-tracera-served-by").unwrap(),
            "legacy"
        );
        // "/legacyx" is NOT owned (no segment boundary) -> local 404, no forward
        let r2 = reqwest::get(format!("{app}/legacyx")).await.unwrap();
        assert_eq!(r2.status(), StatusCode::NOT_FOUND);
        assert!(r2.headers().get("x-tracera-served-by").is_none());
        // mock counts only its registered routes; /legacy/x 404'd on the mock,
        // so 0 proves /legacyx never crossed the bridge
        assert_eq!(calls.load(Ordering::SeqCst), 0);
    }

    #[tokio::test]
    async fn owned_upgrade_rejected() {
        let calls = std::sync::Arc::new(AtomicUsize::new(0));
        let legacy = spawn_legacy(StatusCode::OK, calls.clone()).await;
        let mut l = legacy_for(&legacy).unwrap();
        Arc::get_mut(&mut l).unwrap().owned_prefixes = vec!["/legacy".into()];
        let app = spawn_app(Some(l)).await;
        let r = reqwest::Client::new()
            .get(format!("{app}/legacy/stream"))
            .header("accept", "text/event-stream")
            .send()
            .await
            .unwrap();
        assert_eq!(r.status(), StatusCode::NOT_IMPLEMENTED);
        assert_eq!(calls.load(Ordering::SeqCst), 0);
    }

    #[tokio::test]
    async fn legacy_set_cookie_and_cors_headers_stripped() {
        let calls = std::sync::Arc::new(AtomicUsize::new(0));
        // legacy that returns set-cookie + access-control-*
        let app_legacy = Router::new().route(
            "/stub",
            axum::routing::any(|| async {
                (
                    StatusCode::OK,
                    [
                        ("set-cookie", "sid=evil"),
                        ("access-control-allow-origin", "*"),
                        ("x-keep", "1"),
                    ],
                    "ok",
                )
            }),
        );
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap();
        tokio::spawn(async move { axum::serve(listener, app_legacy).await.unwrap() });
        let app = spawn_app(legacy_for(&format!("http://127.0.0.1:{}", addr.port()))).await;
        let r = reqwest::get(format!("{app}/stub")).await.unwrap();
        assert_eq!(r.status(), StatusCode::OK);
        assert!(r.headers().get("set-cookie").is_none());
        assert!(r.headers().get("access-control-allow-origin").is_none());
        assert_eq!(r.headers().get("x-keep").unwrap(), "1");
        let _ = calls;
    }

    #[tokio::test]
    async fn legacy_redirect_not_followed() {
        let app_legacy = Router::new().route(
            "/stub",
            axum::routing::any(|| async {
                (StatusCode::FOUND, [("location", "http://evil.example/")], "")
            }),
        );
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap();
        tokio::spawn(async move { axum::serve(listener, app_legacy).await.unwrap() });
        let app = spawn_app(legacy_for(&format!("http://127.0.0.1:{}", addr.port()))).await;
        let r = reqwest::Client::builder()
            .redirect(reqwest::redirect::Policy::none())
            .build()
            .unwrap()
            .get(format!("{app}/stub"))
            .send()
            .await
            .unwrap();
        assert_eq!(r.status(), StatusCode::FOUND);
        assert_eq!(r.headers().get("location").unwrap(), "http://evil.example/");
    }

    #[tokio::test]
    async fn rust_4xx_not_forwarded() {
        let calls = std::sync::Arc::new(AtomicUsize::new(0));
        let legacy = spawn_legacy(StatusCode::OK, calls.clone()).await;
        let app = spawn_app(legacy_for(&legacy)).await;
        // unregistered path -> local 404, must not forward
        let r = reqwest::get(format!("{app}/nope")).await.unwrap();
        assert_eq!(r.status(), StatusCode::NOT_FOUND);
        assert_eq!(calls.load(Ordering::SeqCst), 0);
    }

    #[tokio::test]
    async fn post_body_and_query_forwarded() {
        let calls = std::sync::Arc::new(AtomicUsize::new(0));
        let legacy = spawn_legacy(StatusCode::OK, calls.clone()).await;
        let app = spawn_app(legacy_for(&legacy)).await;
        let r = reqwest::Client::new()
            .post(format!("{app}/stub?a=1&b=2"))
            .body("payload")
            .send()
            .await
            .unwrap();
        assert_eq!(r.status(), StatusCode::OK);
        assert_eq!(r.text().await.unwrap(), "echo:payload|a=1&b=2");
        assert_eq!(calls.load(Ordering::SeqCst), 1);
    }

    #[tokio::test]
    async fn auth_header_relayed() {
        // legacy 401s unless the bearer arrives; bridge must relay authorization verbatim
        let app_legacy = Router::new().route(
            "/stub",
            axum::routing::any(|req: Request| async move {
                match req.headers().get("authorization") {
                    Some(v) if v == "Bearer t" => (StatusCode::OK, "authed"),
                    _ => (StatusCode::UNAUTHORIZED, "no-auth"),
                }
            }),
        );
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap();
        tokio::spawn(async move { axum::serve(listener, app_legacy).await.unwrap() });
        let app = spawn_app(legacy_for(&format!("http://127.0.0.1:{}", addr.port()))).await;
        let r = reqwest::Client::new()
            .get(format!("{app}/stub"))
            .header("authorization", "Bearer t")
            .send()
            .await
            .unwrap();
        assert_eq!(r.status(), StatusCode::OK);
        assert_eq!(r.text().await.unwrap(), "authed");
        let r2 = reqwest::get(format!("{app}/stub")).await.unwrap();
        assert_eq!(r2.status(), StatusCode::UNAUTHORIZED);
    }

}
