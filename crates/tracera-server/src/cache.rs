//! Upstash / Redis cache client for trace-link hot cache.
//! Activates when env `CACHE_URL` is set. Falls back to a no-op client when unset
//! so the server boots cleanly in dev/test without a cache backend.
//!
//! Protocol: Upstash "Global" REST API (`https://<endpoint>.upstash.io`) with token auth.
//! Standard Redis commands via GET/POST to `/` endpoint.
//! Doc: https://docs.upstash.com/redis/api/rest

use std::sync::Arc;
use std::time::Duration;
use tracing::{debug, warn};

#[derive(Clone)]
pub struct CacheClient {
    inner: Arc<CacheInner>,
}

enum CacheInner {
    Disabled,
    Upstash {
        base_url: String,
        token: String,
        client: reqwest::Client,
    },
}

impl CacheClient {
    /// Construct from `CACHE_URL` env var.
    /// Expected formats:
    /// - `redis://<endpoint>.upstash.io:<port>` + `CACHE_TOKEN=...` (ignored if URL embeds token)
    /// - `upstash://:<token>@<host>`
    /// - `https://<endpoint>.upstash.io` + `CACHE_TOKEN=...` (REST, primary path)
    pub fn from_env() -> Self {
        let url = std::env::var("CACHE_URL").ok();
        let token = std::env::var("CACHE_TOKEN").ok();

        if url.is_none() {
            debug!("CACHE_URL not set; cache layer disabled (no-op)");
            return Self { inner: Arc::new(CacheInner::Disabled) };
        }

        let url = url.unwrap();
        let (base_url, embedded_token) = parse_redis_url(&url);
        let token = token.or(embedded_token);

        let token = match token {
            Some(t) if !t.is_empty() => t,
            _ => {
                warn!("CACHE_URL set but CACHE_TOKEN missing or empty; cache disabled");
                return Self { inner: Arc::new(CacheInner::Disabled) };
            }
        };

        let client = reqwest::Client::builder()
            .timeout(Duration::from_millis(500))
            .build()
            .expect("reqwest client build");

        Self {
            inner: Arc::new(CacheInner::Upstash { base_url, token, client }),
        }
    }

    pub fn is_enabled(&self) -> bool {
        matches!(*self.inner, CacheInner::Upstash { .. })
    }

    /// GET `key`. Returns `None` on miss or any failure (best-effort cache, never fatal).
    pub async fn get(&self, key: &str) -> Option<String> {
        match &*self.inner {
            CacheInner::Disabled => None,
            CacheInner::Upstash { base_url, token, client } => {
                let resp = client
                    .post(format!("{}/get/{}", base_url, urlencoded(key)))
                    .bearer_auth(token)
                    .send()
                    .await
                    .ok()?;
                let body: UpstashResponse = resp.json().await.ok()?;
                if !body.ok { return None; }
                body.result.and_then(|v| match v {
                    serde_json::Value::String(s) => Some(s),
                    serde_json::Value::Null => None,
                    _ => Some(v.to_string()),
                })
            }
        }
    }

    /// SET `key` `value` with optional TTL (seconds). Best-effort — logs + ignores failures.
    pub async fn set(&self, key: &str, value: &str, ttl_secs: Option<u64>) {
        match &*self.inner {
            CacheInner::Disabled => {}
            CacheInner::Upstash { base_url, token, client } => {
                let key_enc = urlencoded(key);
                let val_enc = urlencoded(value);
                let mut cmd: Vec<String> = vec!["SET".to_string(), key_enc, val_enc];
                if let Some(ttl) = ttl_secs {
                    cmd.push("EX".to_string());
                    cmd.push(ttl.to_string());
                }
                let body: Vec<serde_json::Value> = cmd
                    .iter()
                    .enumerate()
                    .map(|(i, s)| if i == 0 { serde_json::json!(s) } else { serde_json::json!(s) })
                    .collect();
                let _ = client
                    .post(format!("{}/pipeline", base_url))
                    .bearer_auth(token)
                    .json(&body)
                    .send()
                    .await;
            }
        }
    }

    /// DELETE `key`. Best-effort.
    pub async fn del(&self, key: &str) {
        match &*self.inner {
            CacheInner::Disabled => {}
            CacheInner::Upstash { base_url, token, client } => {
                let _ = client
                    .post(format!("{}/del/{}", base_url, urlencoded(key)))
                    .bearer_auth(token)
                    .send()
                    .await;
            }
        }
    }
}

/// Best-effort wrapper that logs and swallows errors — never fatal.
async fn _safe_get(_client: &CacheClient, _key: &str) -> Option<String> {
    _client.get(_key).await
}

#[derive(serde::Deserialize)]
struct UpstashResponse {
    #[serde(default)]
    ok: bool,
    #[serde(default)]
    result: Option<serde_json::Value>,
    #[serde(default)]
    error: Option<String>,
}

fn parse_redis_url(s: &str) -> (String, Option<String>) {
    // Strip scheme prefix if any.
    let stripped = s
        .strip_prefix("upstash://")
        .or_else(|| s.strip_prefix("redis://"))
        .or_else(|| s.strip_prefix("https://"))
        .or_else(|| s.strip_prefix("http://"))
        .unwrap_or(s);

    // `:<token>@<host>` (Upstash CLI format)
    if let Some(at_idx) = stripped.find('@') {
        let token = stripped[..at_idx].trim_start_matches(':').to_string();
        let host = &stripped[at_idx + 1..];
        let base = if s.starts_with("https://") || s.starts_with("http://") {
            format!("https://{}", host)
        } else {
            format!("https://{}", host)
        };
        return (base, Some(token));
    }

    // Plain host[:port]
    let host = stripped.trim_end_matches('/');
    (format!("https://{}", host), None)
}

fn urlencoded(s: &str) -> String {
    // Minimal URL-encoding for Redis command parts (no space, no special chars except -._).
    // Upstash REST actually decodes raw — but we encode reserved chars defensively.
    s.chars()
        .map(|c| match c {
            ':' => "%3A",
            '/' => "%2F",
            '@' => "%40",
            '?' => "%3F",
            '#' => "%23",
            ' ' => "%20",
            _ if c.is_ascii_alphanumeric() || "-_.~".contains(c) => c.to_string(),
            other => format!("%{:02X}", other as u32),
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_redis_url_with_token() {
        let (base, tok) = parse_redis_url("redis://:ABC123@us1-aware-kangaroo-12345.upstash.io:6379");
        assert_eq!(base, "https://us1-aware-kangaroo-12345.upstash.io");
        assert_eq!(tok, Some("ABC123".to_string()));
    }

    #[test]
    fn parse_redis_url_plain() {
        let (base, tok) = parse_redis_url("redis://localhost:6379");
        assert_eq!(base, "https://localhost:6379");
        assert_eq!(tok, None);
    }

    #[test]
    fn disabled_when_no_env() {
        std::env::remove_var("CACHE_URL");
        std::env::remove_var("CACHE_TOKEN");
        let c = CacheClient::from_env();
        assert!(!c.is_enabled());
    }

    #[test]
    fn disabled_when_url_but_no_token() {
        std::env::set_var("CACHE_URL", "redis://localhost:6379");
        std::env::remove_var("CACHE_TOKEN");
        let c = CacheClient::from_env();
        assert!(!c.is_enabled());
    }
}
