//! Forward-on-stub middleware. Off unless LEGACY_BASE_URL is set.
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
    let owned = legacy
        .owned_prefixes
        .iter()
        .any(|p| path.starts_with(p.as_str()));
    let bytes = match to_bytes(body, MAX_BODY).await {
        Ok(b) => b,
        Err(_) => return StatusCode::PAYLOAD_TOO_LARGE.into_response(),
    };
    if !owned {
        let rebuilt = Request::from_parts(parts.clone(), Body::from(bytes.clone()));
        let resp = next.run(rebuilt).await;
        let is_stub = resp.status() == StatusCode::NOT_IMPLEMENTED
            && resp.headers().get(STUB).map_or(false, |v| v == "true");
        if !is_stub || upgrade {
            return resp;
        }
    }
    metrics::counter!("tracera_stub_forwarded_total", "route" => path.clone()).increment(1);
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
            let status =
                StatusCode::from_u16(r.status().as_u16()).unwrap_or(StatusCode::BAD_GATEWAY);
            let mut headers = HeaderMap::new();
            for (k, v) in r.headers().iter() {
                if !hop_by_hop(k) {
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
                axum::routing::get(|| async {
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
                axum::routing::any(move || {
                    let c1 = c1.clone();
                    async move {
                        c1.fetch_add(1, Ordering::SeqCst);
                        (status, "from-legacy")
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
            client: reqwest::Client::new(),
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
        assert_eq!(r.headers().get("x-tracera-served-by").unwrap(), "legacy");
        assert_eq!(r.text().await.unwrap(), "from-legacy");
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
            r.headers()
                .get("x-tracera-served-by")
                .map(|v| v.to_str().unwrap().to_string()),
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
}
