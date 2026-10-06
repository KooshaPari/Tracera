use http::{header, Uri};
use std::collections::VecDeque;
use std::net::SocketAddr;
use uuid::Uuid;

pub(crate) static CSRF_TOKENS: std::sync::OnceLock<tokio::sync::Mutex<VecDeque<String>>> =
    std::sync::OnceLock::new();

pub(crate) const MAX_CSRF_TOKENS: usize = 1024;
pub(crate) const CANONICAL_BROWSER_ORIGIN: &str = "http://127.0.0.1:18000";

pub(crate) const TRUSTED_BROWSER_ORIGINS: &[&str] = &[
    "https://tracera-kappa.vercel.app",
    "https://tracera.pheno.studio",
    "http://127.0.0.1:18000",
    "http://localhost:18000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
];

pub(crate) fn trusted_browser_origins(extra_from_env: Option<&str>) -> Vec<String> {
    use std::collections::HashSet;

    let mut seen = HashSet::new();
    let mut origins = Vec::new();
    let mut push = |value: &str| {
        let trimmed = value.trim().trim_end_matches('/');
        if trimmed.is_empty() {
            return;
        }
        let Ok(uri) = trimmed.parse::<Uri>() else {
            return;
        };
        if !matches!(uri.scheme_str(), Some("http" | "https"))
            || uri.authority().is_none()
            || uri.path() != "/"
            || uri.query().is_some()
        {
            return;
        }
        let normalized = format!(
            "{}://{}",
            uri.scheme_str().expect("validated scheme"),
            uri.authority().expect("validated authority")
        );
        if seen.insert(normalized.clone()) {
            origins.push(normalized);
        }
    };

    for origin in TRUSTED_BROWSER_ORIGINS {
        push(origin);
    }
    if let Some(raw) = extra_from_env {
        for origin in raw.split(',') {
            push(origin);
        }
    }
    origins
}

/// CSRF protection middleware.
///
/// For state-mutating requests (POST/PUT/DELETE/PATCH), verifies that the
/// request originates from an allowed origin. This prevents cross-site request
/// forgery attacks where a malicious site could submit forms on behalf of
/// authenticated users.
///
/// Tokens are process-local and bounded. They are deliberately independent of
/// bearer authentication: browser mutations must prove both the canonical
/// browser origin and possession of a token issued by this process.
pub(crate) async fn csrf_protection(
    request: axum::http::Request<axum::body::Body>,
    next: axum::middleware::Next,
) -> Result<axum::http::Response<axum::body::Body>, axum::http::StatusCode> {
    let method = request.method().clone();

    // Only check state-mutating methods
    if method == axum::http::Method::GET
        || method == axum::http::Method::HEAD
        || method == axum::http::Method::OPTIONS
    {
        return Ok(next.run(request).await);
    }

    let origin_is_canonical = request
        .headers()
        .get(header::ORIGIN)
        .and_then(|value| value.to_str().ok())
        .is_some_and(is_canonical_browser_origin);
    let referer_is_canonical = request
        .headers()
        .get(header::REFERER)
        .and_then(|value| value.to_str().ok())
        .is_some_and(is_canonical_browser_origin);
    if !origin_is_canonical && !referer_is_canonical {
        tracing::warn!("CSRF: blocked request without canonical Origin or Referer");
        return Err(axum::http::StatusCode::FORBIDDEN);
    }

    let Some(token) = request
        .headers()
        .get("x-csrf-token")
        .and_then(|value| value.to_str().ok())
    else {
        tracing::warn!("CSRF: blocked request without token");
        return Err(axum::http::StatusCode::FORBIDDEN);
    };
    if !csrf_token_is_issued(token).await {
        tracing::warn!("CSRF: blocked request with unissued token");
        return Err(axum::http::StatusCode::FORBIDDEN);
    }

    Ok(next.run(request).await)
}

pub(crate) fn is_canonical_browser_origin(value: &str) -> bool {
    let Ok(uri) = value.parse::<Uri>() else {
        return false;
    };
    if !matches!(uri.scheme_str(), Some("http" | "https")) {
        return false;
    }
    let Some(authority) = uri.authority() else {
        return false;
    };
    let origin = format!(
        "{}://{}",
        uri.scheme_str().expect("validated scheme"),
        authority
    );
    let extra = std::env::var("TRACERA_ALLOWED_ORIGINS").ok();
    trusted_browser_origins(extra.as_deref())
        .iter()
        .any(|allowed| allowed == &origin)
}

pub(crate) fn csrf_tokens() -> &'static tokio::sync::Mutex<VecDeque<String>> {
    CSRF_TOKENS.get_or_init(|| tokio::sync::Mutex::new(VecDeque::new()))
}

pub(crate) async fn issue_csrf_token() -> String {
    let token = Uuid::new_v4().to_string();
    let mut tokens = csrf_tokens().lock().await;
    tokens.push_back(token.clone());
    if tokens.len() > MAX_CSRF_TOKENS {
        tokens.pop_front();
    }
    token
}

pub(crate) async fn csrf_token_is_issued(candidate: &str) -> bool {
    csrf_tokens()
        .lock()
        .await
        .iter()
        .any(|token| token == candidate)
}

// ---------------------------------------------------------------------------
// Simple in-memory per-IP rate limiter (no external crate needed)
// ---------------------------------------------------------------------------
#[allow(dead_code)]
pub(crate) async fn rate_limit_middleware(
    req: axum::http::Request<axum::body::Body>,
    next: axum::middleware::Next,
) -> Result<axum::response::Response, std::convert::Infallible> {
    use std::collections::HashMap;
    use std::net::IpAddr;
    use std::sync::OnceLock;
    use tokio::sync::RwLock;

    static LIMITS: OnceLock<RwLock<HashMap<IpAddr, (u32, std::time::Instant)>>> = OnceLock::new();
    let limits = LIMITS.get_or_init(|| RwLock::new(HashMap::new()));

    let max_rps: u32 = std::env::var("TRACERA_RATE_LIMIT_RPS")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(100);

    let ip = req
        .extensions()
        .get::<axum::extract::ConnectInfo<SocketAddr>>()
        .map(|c| c.0.ip())
        .unwrap_or_else(|| "0.0.0.0".parse().unwrap());

    let now = std::time::Instant::now();
    let mut map = limits.write().await;
    let entry = map.entry(ip).or_insert((0, now));
    if now.duration_since(entry.1).as_secs() >= 1 {
        entry.0 = 0;
        entry.1 = now;
    }
    entry.0 += 1;
    let over_limit = entry.0 > max_rps;
    drop(map);

    if over_limit {
        return Ok(axum::response::Response::builder()
            .status(429)
            .header("content-type", "application/json")
            .header("retry-after", "1")
            .body(axum::body::Body::from(
                "{\"error\":\"rate_limit_exceeded\",\"retry_after_seconds\":1}",
            ))
            .unwrap());
    }

    Ok(next.run(req).await)
}
