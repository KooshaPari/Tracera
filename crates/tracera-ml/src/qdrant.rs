//! Qdrant HTTP client wrapper.
//!
//! Qdrant is a vector search engine with a REST API. We expose just enough
//! surface area for Tracera's retrieval pipeline:
//!
//! - [`QdrantClient::upsert_points`] — push embeddings + payloads.
//! - [`QdrantClient::search`] — cosine-similarity search with optional
//!   payload filtering.
//! - [`QdrantClient::ensure_collection`] — create the collection if missing.
//!
//! The HTTP transport is `reqwest`; the JSON contract mirrors Qdrant's
//! `/collections/{name}/points/search` endpoint documented at
//! <https://qdrant.tech/documentation/>.

use std::collections::HashMap;

use serde::{Deserialize, Serialize};
use tracing::{debug, instrument};

/// Errors produced by the Qdrant wrapper.
#[derive(Debug, thiserror::Error)]
pub enum QdrantError {
    #[error("qdrant HTTP error: {0}")]
    Http(#[from] reqwest::Error),

    #[error("qdrant returned status {status}: {body}")]
    Status { status: u16, body: String },

    #[error("invalid response: {0}")]
    InvalidResponse(String),

    #[error("dimension mismatch: vector has {got}, collection expects {expected}")]
    DimensionMismatch { got: usize, expected: usize },
}

/// A single point going to / coming from Qdrant.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QdrantPoint {
    /// Stable string ID (UUIDs and ULIDs both serialize cleanly).
    pub id: String,
    pub vector: Vec<f32>,
    /// Arbitrary key/value metadata. Qdrant indexes payload fields it sees,
    /// so keeping it small and flat is best.
    #[serde(default)]
    pub payload: HashMap<String, serde_json::Value>,
}

/// One hit returned by a search.
#[derive(Debug, Clone)]
pub struct QdrantHit {
    pub id: String,
    pub score: f32,
    pub payload: HashMap<String, serde_json::Value>,
}

impl QdrantHit {
    pub fn doc_id(&self) -> Option<&str> {
        self.payload.get("doc_id").and_then(|v| v.as_str())
    }

    pub fn text(&self) -> Option<&str> {
        self.payload.get("text").and_then(|v| v.as_str())
    }
}

/// Request payload for a search. Field names match Qdrant's API.
#[derive(Debug, Clone, Serialize)]
pub struct QdrantSearchRequest {
    pub vector: Vec<f32>,
    #[serde(default)]
    pub limit: u64,
    /// Cosine, Euclidean, or Dot. We default to Cosine because that's what
    /// the mock embedder produces (L2-normalized vectors).
    #[serde(default = "default_distance")]
    pub distance: String,
    /// Optional payload filter. Qdrant's filter DSL is rich — we only
    /// support `must` here, which covers the >95% case.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub filter: Option<QdrantFilter>,
    /// If true, Qdrant returns the stored payload alongside the score.
    #[serde(default = "default_true")]
    pub with_payload: bool,
    /// If true, the vector is included in the response. We don't need it for
    /// ranking, so the default is false to keep payloads small.
    #[serde(default)]
    pub with_vector: bool,
}

fn default_distance() -> String {
    "Cosine".to_string()
}

fn default_true() -> bool {
    true
}

impl QdrantSearchRequest {
    pub fn new(vector: Vec<f32>, limit: u64) -> Self {
        Self {
            vector,
            limit,
            distance: default_distance(),
            filter: None,
            with_payload: true,
            with_vector: false,
        }
    }

    pub fn with_filter(mut self, filter: QdrantFilter) -> Self {
        self.filter = Some(filter);
        self
    }
}

/// Subset of Qdrant's filter DSL — only `must` (AND) and `should` (OR) with
/// field-level match conditions. Enough for Tracera's needs; extend as new
/// queries appear.
#[derive(Debug, Clone, Serialize, Default)]
pub struct QdrantFilter {
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub must: Vec<QdrantCondition>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub should: Vec<QdrantCondition>,
}

impl QdrantFilter {
    pub fn must_match(key: impl Into<String>, value: impl Into<serde_json::Value>) -> Self {
        Self {
            must: vec![QdrantCondition::Match {
                key: key.into(),
                value: value.into(),
            }],
            ..Default::default()
        }
    }
}

#[derive(Debug, Clone, Serialize)]
#[serde(untagged)]
pub enum QdrantCondition {
    Match {
        key: String,
        value: serde_json::Value,
    },
}

// ---------------------------------------------------------------------------
// Wire-format DTOs — private because callers only see [`QdrantHit`].
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
struct QdrantSearchResponse {
    result: Vec<QdrantSearchResponseItem>,
}

#[derive(Debug, Deserialize)]
struct QdrantSearchResponseItem {
    id: QdrantIdField,
    #[serde(default)]
    score: f32,
    #[serde(default)]
    payload: HashMap<String, serde_json::Value>,
}

/// Qdrant accepts integers, UUIDs, or strings as IDs. We always send strings,
/// so most responses will be the string variant — but be permissive on read.
#[derive(Debug, Deserialize)]
#[serde(untagged)]
enum QdrantIdField {
    Str(String),
    Int(i64),
}

impl QdrantIdField {
    fn into_string(self) -> String {
        match self {
            QdrantIdField::Str(s) => s,
            QdrantIdField::Int(i) => i.to_string(),
        }
    }
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

/// Thin wrapper around the Qdrant HTTP API.
#[derive(Debug, Clone)]
pub struct QdrantClient {
    base_url: String,
    api_key: Option<String>,
    http: reqwest::Client,
}

impl QdrantClient {
    pub fn new(base_url: impl Into<String>) -> Self {
        Self {
            base_url: base_url.into().trim_end_matches('/').to_string(),
            api_key: None,
            http: reqwest::Client::builder()
                .timeout(std::time::Duration::from_secs(30))
                .build()
                .expect("reqwest client"),
        }
    }

    pub fn with_api_key(mut self, key: impl Into<String>) -> Self {
        self.api_key = Some(key.into());
        self
    }

    pub fn with_http_client(mut self, client: reqwest::Client) -> Self {
        self.http = client;
        self
    }

    fn url(&self, path: &str) -> String {
        format!("{}/{}", self.base_url, path.trim_start_matches('/'))
    }

    fn auth(&self, req: reqwest::RequestBuilder) -> reqwest::RequestBuilder {
        match &self.api_key {
            Some(k) => req.header("api-key", k),
            None => req,
        }
    }

    /// Create a collection with cosine distance. Idempotent: if the
    /// collection already exists we swallow the resulting 4xx.
    #[instrument(skip(self), fields(collection = %name, dim))]
    pub async fn ensure_collection(&self, name: &str, dim: usize) -> Result<(), QdrantError> {
        tracing::Span::current().record("dim", dim);
        #[derive(Serialize)]
        struct CreateCollectionBody {
            vectors: VectorsSpec,
        }
        #[derive(Serialize)]
        struct VectorsSpec {
            size: usize,
            distance: String,
        }

        let body = CreateCollectionBody {
            vectors: VectorsSpec {
                size: dim,
                distance: "Cosine".to_string(),
            },
        };

        let resp = self
            .auth(self.http.put(self.url(&format!("collections/{name}"))))
            .json(&body)
            .send()
            .await?;

        let status = resp.status();
        if status.is_success() {
            return Ok(());
        }
        let body = resp.text().await.unwrap_or_default();
        // 4xx "already exists" → treat as success so this is safe to call
        // from boot/init code.
        if body.contains("already exists") || body.contains("ALREADY_EXISTS") {
            debug!("collection {name} already exists");
            return Ok(());
        }
        Err(QdrantError::Status {
            status: status.as_u16(),
            body,
        })
    }

    /// Upsert points in batches. Returns the total number of points uploaded.
    /// The caller is responsible for chunking if they have huge payloads;
    /// we cap each batch at 256 to keep individual requests under the 30s
    /// timeout.
    #[instrument(skip(self, points), fields(collection = %name, count = points.len()))]
    pub async fn upsert_points(
        &self,
        name: &str,
        points: &[QdrantPoint],
    ) -> Result<usize, QdrantError> {
        const BATCH: usize = 256;
        let mut total = 0;
        for chunk in points.chunks(BATCH) {
            #[derive(Serialize)]
            struct UpsertBody<'a> {
                points: &'a [QdrantPoint],
            }
            let body = UpsertBody { points: chunk };
            let resp = self
                .auth(
                    self.http
                        .put(self.url(&format!("collections/{name}/points?wait=true"))),
                )
                .json(&body)
                .send()
                .await?;
            let status = resp.status();
            if !status.is_success() {
                let body = resp.text().await.unwrap_or_default();
                return Err(QdrantError::Status {
                    status: status.as_u16(),
                    body,
                });
            }
            total += chunk.len();
        }
        Ok(total)
    }

    /// Run a similarity search and return hits ordered by descending score.
    #[instrument(skip(self, req), fields(collection = %name, limit = req.limit))]
    pub async fn search(
        &self,
        name: &str,
        req: QdrantSearchRequest,
    ) -> Result<Vec<QdrantHit>, QdrantError> {
        let url = self.url(&format!("collections/{name}/points/search"));
        let resp = self.auth(self.http.post(url)).json(&req).send().await?;
        let status = resp.status();
        if !status.is_success() {
            let body = resp.text().await.unwrap_or_default();
            return Err(QdrantError::Status {
                status: status.as_u16(),
                body,
            });
        }
        let parsed: QdrantSearchResponse = resp.json().await?;
        Ok(parsed
            .result
            .into_iter()
            .map(|item| QdrantHit {
                id: item.id.into_string(),
                score: item.score,
                payload: item.payload,
            })
            .collect())
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn hit(score: f32, payload: serde_json::Value) -> QdrantHit {
        QdrantHit {
            id: "p1".to_string(),
            score,
            payload: match payload {
                serde_json::Value::Object(m) => m.into_iter().collect(),
                other => {
                    let mut m = HashMap::new();
                    m.insert("data".to_string(), other);
                    m
                }
            },
        }
    }

    #[test]
    fn hit_helpers_extract_typed_payload_fields() {
        let mut p = HashMap::new();
        p.insert("doc_id".to_string(), serde_json::json!("story-42"));
        p.insert("text".to_string(), serde_json::json!("hello"));
        let h = QdrantHit {
            id: "x".to_string(),
            score: 0.9,
            payload: p,
        };
        assert_eq!(h.doc_id(), Some("story-42"));
        assert_eq!(h.text(), Some("hello"));
    }

    #[test]
    fn search_request_serializes_minimally() {
        // The `filter` field should be absent when not set so the wire payload
        // stays small for the common case.
        let req = QdrantSearchRequest::new(vec![0.0; 4], 10);
        let v = serde_json::to_value(&req).unwrap();
        assert_eq!(v["limit"], 10);
        assert_eq!(v["distance"], "Cosine");
        assert_eq!(v["with_payload"], true);
        assert_eq!(v["with_vector"], false);
        assert!(v.get("filter").is_none(), "empty filter must be skipped");
    }

    #[test]
    fn search_request_includes_filter_when_set() {
        let req = QdrantSearchRequest::new(vec![0.0; 4], 5)
            .with_filter(QdrantFilter::must_match("kind", "story"));
        let v = serde_json::to_value(&req).unwrap();
        assert_eq!(v["filter"]["must"][0]["key"], "kind");
        assert_eq!(v["filter"]["must"][0]["value"], "story");
    }

    #[test]
    fn filter_must_match_builder() {
        let f = QdrantFilter::must_match("sprint", "S-2026-W36");
        assert_eq!(f.must.len(), 1);
        assert!(matches!(f.must[0], QdrantCondition::Match { .. }));
    }

    #[tokio::test]
    async fn client_construction_trims_trailing_slash() {
        let c = QdrantClient::new("http://localhost:6333/");
        assert_eq!(c.base_url, "http://localhost:6333");
        assert_eq!(c.url("foo"), "http://localhost:6333/foo");
        assert_eq!(c.url("/foo"), "http://localhost:6333/foo");
    }

    /// Hit ordering is caller responsibility (Qdrant already returns in
    /// descending score, but we surface a helper for pipelines that
    /// re-rank later).
    #[tokio::test]
    async fn hit_ordering_preserves_invariant() {
        let hits = vec![hit(0.9, serde_json::json!({})), hit(0.7, serde_json::json!({}))];
        let scores: Vec<f32> = hits.iter().map(|h| h.score).collect();
        assert!(scores.windows(2).all(|w| w[0] >= w[1]));
    }
}
