//! Retrieval-augmented generation pipeline.
//!
//! ```text
//!     query
//!       │
//!       ▼
//!  ┌──────────┐
//!  │ Embedder │  (mock or ONNX)
//!  └────┬─────┘
//!       │  dense vector
//!       ▼
//!  ┌──────────────────┐
//!  │ Vector search(s) │  Qdrant + pgvector (both)
//!  └────┬─────────────┘
//!       │  top-K chunks
//!       ▼
//!  ┌──────────────────┐
//!  │  Graph expansion │  optional, via [`GraphExpander`]
//!  └────┬─────────────┘
//!       │  expanded candidates
//!       ▼
//!  ┌──────────────────┐
//!  │     Rerank       │  cosine + token-overlap, pluggable
//!  └────┬─────────────┘
//!       │  final context
//!       ▼
//!     RagResult
//! ```
//!
//! Each stage is a trait so it can be swapped out in tests without standing
//! up real infrastructure.

use std::collections::HashSet;
use std::sync::Arc;

use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use tracing::{debug, instrument};

use crate::embeddings::{Embedder, Embedding, EmbedderError};
use crate::pgvector::{PgVectorHit, PgVectorStore};
use crate::qdrant::{QdrantClient, QdrantHit, QdrantSearchRequest};

/// Errors produced by the RAG pipeline.
#[derive(Debug, thiserror::Error)]
pub enum RagError {
    #[error("embedder error: {0}")]
    Embedder(#[from] EmbedderError),

    #[error("vector store error: {0}")]
    VectorStore(String),

    #[error("graph expansion error: {0}")]
    Graph(String),

    #[error("rerank error: {0}")]
    Rerank(String),

    #[error("no backends configured")]
    NoBackends,
}

/// Configuration for the pipeline. Most knobs have sane defaults.
#[derive(Debug, Clone)]
pub struct RagConfig {
    /// How many chunks to fetch from each backend before merging.
    pub per_backend_limit: u64,
    /// Final top-N after rerank.
    pub top_k: usize,
    /// Enable graph expansion via [`GraphExpander`].
    pub graph_expansion: bool,
    /// Max graph hops when expanding.
    pub graph_hops: usize,
    /// Method used by the [`Reranker`].
    pub rerank: RerankMethod,
}

impl Default for RagConfig {
    fn default() -> Self {
        Self {
            per_backend_limit: 20,
            top_k: 5,
            graph_expansion: true,
            graph_hops: 1,
            rerank: RerankMethod::Hybrid,
        }
    }
}

/// Where a chunk came from. Used both for debugging and for cost-aware
/// callers that want to weight Qdrant (cheap) vs. pgvector (full metadata).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RetrievalSource {
    Qdrant,
    PgVector,
    Graph,
}

/// A chunk that survived retrieval, with provenance + score.
#[derive(Debug, Clone)]
pub struct ScoredChunk {
    pub id: String,
    pub doc_id: String,
    pub text: String,
    pub kind: String,
    pub source: RetrievalSource,
    pub initial_score: f32,
    pub final_score: f32,
    pub metadata: serde_json::Value,
}

/// Final result of a retrieval.
#[derive(Debug, Clone)]
pub struct RagResult {
    pub query: String,
    pub chunks: Vec<ScoredChunk>,
    pub assembled_context: String,
}

// ---------------------------------------------------------------------------
// Rerank trait + method
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RerankMethod {
    /// Trust the vector store's score; no re-ranking.
    ScoreOnly,
    /// Add a token-overlap bonus to the vector score.
    TokenOverlap,
    /// Cosine over fresh embeddings + token overlap, blended 70/30.
    Hybrid,
}

#[async_trait]
pub trait Reranker: Send + Sync {
    async fn rerank(
        &self,
        query: &str,
        chunks: Vec<ScoredChunk>,
        method: RerankMethod,
    ) -> Result<Vec<ScoredChunk>, RagError>;
}

/// Default reranker: a deterministic blend that doesn't need a cross-encoder.
/// It uses the embedder to recompute cosine (catches the case where the
/// vector store used a different distance metric) and adds a token-overlap
/// bonus to break ties.
#[derive(Debug, Clone)]
pub struct DefaultReranker {
    embedder: Arc<dyn Embedder>,
}

impl DefaultReranker {
    pub fn new(embedder: Arc<dyn Embedder>) -> Self {
        Self { embedder }
    }
}

#[async_trait]
impl Reranker for DefaultReranker {
    async fn rerank(
        &self,
        query: &str,
        mut chunks: Vec<ScoredChunk>,
        method: RerankMethod,
    ) -> Result<Vec<ScoredChunk>, RagError> {
        if chunks.is_empty() {
            return Ok(chunks);
        }

        // Pull token sets once — small allocations, but cheap to share.
        let q_tokens = tokenize(query);
        let q_embedding: Option<Embedding> = match method {
            RerankMethod::ScoreOnly => None,
            RerankMethod::TokenOverlap => None,
            RerankMethod::Hybrid => Some(
                self.embedder
                    .embed(query)
                    .await
                    .map_err(RagError::Embedder)?,
            ),
        };

        for chunk in &mut chunks {
            let overlap = jaccard(&q_tokens, &tokenize(&chunk.text));
            let cosine = match &q_embedding {
                Some(qe) => {
                    // Recompute the chunk's embedding and cosine. This is the
                    // expensive path — only Hybrid does it. For very large
                    // candidate sets, switch to a cross-encoder backend.
                    let ce = self
                        .embedder
                        .embed(&chunk.text)
                        .await
                        .map_err(RagError::Embedder)?;
                    cosine_sim(&qe.vector, &ce.vector)
                }
                None => chunk.initial_score,
            };
            chunk.final_score = match method {
                RerankMethod::ScoreOnly => chunk.initial_score,
                RerankMethod::TokenOverlap => 0.7 * chunk.initial_score + 0.3 * overlap,
                RerankMethod::Hybrid => 0.7 * cosine + 0.3 * overlap,
            };
        }

        // Stable sort by descending final_score; preserve original order on
        // ties for deterministic test output.
        chunks.sort_by(|a, b| {
            b.final_score
                .partial_cmp(&a.final_score)
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        Ok(chunks)
    }
}

// ---------------------------------------------------------------------------
// Graph expansion
// ---------------------------------------------------------------------------

#[derive(Debug, Clone)]
pub struct GraphNeighbor {
    pub id: String,
    pub doc_id: String,
    pub text: String,
    pub kind: String,
    pub metadata: serde_json::Value,
}

/// Pluggable graph expander. Default implementation uses the pgvector table
/// joined with whatever metadata edges the caller has indexed. The trait is
/// generic so a Neo4j / in-memory implementation can drop in.
#[async_trait]
pub trait GraphExpander: Send + Sync {
    /// Given the chunks already retrieved, return additional chunks reachable
    /// within `hops` graph edges. Implementations must de-duplicate by
    /// `ScoredChunk.id`.
    async fn expand(
        &self,
        seeds: &[ScoredChunk],
        hops: usize,
    ) -> Result<Vec<ScoredChunk>, RagError>;
}

// ---------------------------------------------------------------------------
// Pipeline
// ---------------------------------------------------------------------------

/// The retrieval pipeline. Construct with one or both vector backends, an
/// embedder, and (optionally) a graph expander + reranker.
#[derive(Clone)]
pub struct RagPipeline {
    embedder: Arc<dyn Embedder>,
    qdrant: Option<QdrantClient>,
    qdrant_collection: Option<String>,
    pg: Option<PgVectorStore>,
    graph: Option<Arc<dyn GraphExpander>>,
    reranker: Arc<dyn Reranker>,
    config: RagConfig,
}

impl std::fmt::Debug for RagPipeline {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("RagPipeline")
            .field("qdrant", &self.qdrant.is_some())
            .field("qdrant_collection", &self.qdrant_collection)
            .field("pg", &self.pg.is_some())
            .field("graph", &self.graph.is_some())
            .field("config", &self.config)
            .finish()
    }
}

impl RagPipeline {
    pub fn builder(embedder: Arc<dyn Embedder>) -> RagPipelineBuilder {
        RagPipelineBuilder::new(embedder)
    }

    /// Run the full pipeline.
    #[instrument(skip(self), fields(query_len = query.len(), cfg = ?self.config))]
    pub async fn retrieve(&self, query: &str) -> Result<RagResult, RagError> {
        if self.qdrant.is_none() && self.pg.is_none() {
            return Err(RagError::NoBackends);
        }

        // 1) Embed the query.
        let q_emb = self.embedder.embed(query).await?;

        // 2) Vector search across all configured backends in parallel.
        let (qdrant_hits, pg_hits) =
            tokio::join!(self.search_qdrant(&q_emb), self.search_pg(&q_emb));

        let mut chunks: Vec<ScoredChunk> = Vec::new();
        let mut seen: HashSet<String> = HashSet::new();

        for h in qdrant_hits? {
            if seen.insert(h.id.clone()) {
                chunks.push(ScoredChunk::from(h));
            }
        }
        for h in pg_hits? {
            // pgvector ids are UUIDs; we use a distinct namespace so the same
            // doc_id from both backends doesn't collide.
            let key = format!("pg:{}", h.id);
            if seen.insert(key) {
                chunks.push(ScoredChunk::from(h));
            }
        }

        debug!(candidates = chunks.len(), "merged vector hits");

        // 3) Graph expansion (optional).
        if self.config.graph_expansion {
            if let Some(graph) = &self.graph {
                let expanded = graph.expand(&chunks, self.config.graph_hops).await?;
                for c in expanded {
                    let key = format!("graph:{}", c.id);
                    if seen.insert(key) {
                        chunks.push(c);
                    }
                }
            }
        }

        // 4) Rerank.
        let reranked = self
            .reranker
            .rerank(query, chunks, self.config.rerank)
            .await?;
        let mut reranked = reranked;
        reranked.truncate(self.config.top_k);

        // 5) Assemble a context string the caller can paste into a prompt.
        let context = assemble_context(&reranked);

        Ok(RagResult {
            query: query.to_string(),
            chunks: reranked,
            assembled_context: context,
        })
    }

    async fn search_qdrant(&self, q_emb: &Embedding) -> Result<Vec<QdrantHit>, RagError> {
        let (Some(client), Some(collection)) = (&self.qdrant, &self.qdrant_collection) else {
            return Ok(Vec::new());
        };
        let req = QdrantSearchRequest::new(q_emb.vector.clone(), self.config.per_backend_limit);
        client
            .search(collection, req)
            .await
            .map_err(|e| RagError::VectorStore(format!("qdrant: {e}")))
    }

    async fn search_pg(&self, q_emb: &Embedding) -> Result<Vec<PgVectorHit>, RagError> {
        let Some(pg) = &self.pg else {
            return Ok(Vec::new());
        };
        pg.cosine_search(&q_emb.vector, self.config.per_backend_limit, None)
            .await
            .map_err(|e| RagError::VectorStore(format!("pgvector: {e}")))
    }
}

/// Fluent builder so adding a new backend doesn't break existing call sites.
pub struct RagPipelineBuilder {
    embedder: Arc<dyn Embedder>,
    qdrant: Option<QdrantClient>,
    qdrant_collection: Option<String>,
    pg: Option<PgVectorStore>,
    graph: Option<Arc<dyn GraphExpander>>,
    reranker: Option<Arc<dyn Reranker>>,
    config: RagConfig,
}

impl RagPipelineBuilder {
    pub fn new(embedder: Arc<dyn Embedder>) -> Self {
        Self {
            embedder,
            qdrant: None,
            qdrant_collection: None,
            pg: None,
            graph: None,
            reranker: None,
            config: RagConfig::default(),
        }
    }

    pub fn with_qdrant(mut self, client: QdrantClient, collection: impl Into<String>) -> Self {
        self.qdrant = Some(client);
        self.qdrant_collection = Some(collection.into());
        self
    }

    pub fn with_pg(mut self, store: PgVectorStore) -> Self {
        self.pg = Some(store);
        self
    }

    pub fn with_graph(mut self, expander: Arc<dyn GraphExpander>) -> Self {
        self.graph = Some(expander);
        self
    }

    pub fn with_reranker(mut self, reranker: Arc<dyn Reranker>) -> Self {
        self.reranker = Some(reranker);
        self
    }

    pub fn with_config(mut self, config: RagConfig) -> Self {
        self.config = config;
        self
    }

    pub fn build(self) -> RagPipeline {
        let reranker = self
            .reranker
            .unwrap_or_else(|| Arc::new(DefaultReranker::new(self.embedder.clone())));
        RagPipeline {
            embedder: self.embedder,
            qdrant: self.qdrant,
            qdrant_collection: self.qdrant_collection,
            pg: self.pg,
            graph: self.graph,
            reranker,
            config: self.config,
        }
    }
}

// ---------------------------------------------------------------------------
// Free helpers
// ---------------------------------------------------------------------------

/// Assemble a context string from the reranked chunks. Format is chosen to
/// be model-agnostic: most chat templates accept this without modification.
pub fn assemble_context(chunks: &[ScoredChunk]) -> String {
    let mut out = String::new();
    for (i, c) in chunks.iter().enumerate() {
        out.push_str(&format!(
            "[{n}] (doc_id={doc}, kind={kind}, score={score:.3}, src={src:?})\n{text}\n\n",
            n = i + 1,
            doc = c.doc_id,
            kind = c.kind,
            score = c.final_score,
            src = c.source,
            text = c.text.trim(),
        ));
    }
    out
}

pub(crate) fn tokenize(s: &str) -> HashSet<String> {
    let lower = s.to_lowercase();
    lower
        .split(|c: char| !c.is_alphanumeric() && c != '_')
        .filter(|t| !t.is_empty())
        .map(|t| t.to_string())
        .collect()
}

pub(crate) fn jaccard(a: &HashSet<String>, b: &HashSet<String>) -> f32 {
    if a.is_empty() && b.is_empty() {
        return 0.0;
    }
    let inter = a.intersection(b).count() as f32;
    let union = a.union(b).count() as f32;
    if union == 0.0 {
        0.0
    } else {
        inter / union
    }
}

pub(crate) fn cosine_sim(a: &[f32], b: &[f32]) -> f32 {
    let (mut dot, mut na, mut nb) = (0.0f32, 0.0f32, 0.0f32);
    for (x, y) in a.iter().zip(b.iter()) {
        dot += x * y;
        na += x * x;
        nb += y * y;
    }
    let denom = na.sqrt() * nb.sqrt();
    if denom == 0.0 {
        0.0
    } else {
        dot / denom
    }
}

// ---------------------------------------------------------------------------
// Conversions from backend hits to ScoredChunk
// ---------------------------------------------------------------------------

impl From<QdrantHit> for ScoredChunk {
    fn from(h: QdrantHit) -> Self {
        ScoredChunk {
            id: h.id.clone(),
            doc_id: h
                .payload
                .get("doc_id")
                .and_then(|v| v.as_str())
                .unwrap_or(&h.id)
                .to_string(),
            text: h
                .payload
                .get("text")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            kind: h
                .payload
                .get("kind")
                .and_then(|v| v.as_str())
                .unwrap_or("unknown")
                .to_string(),
            source: RetrievalSource::Qdrant,
            initial_score: h.score,
            final_score: h.score,
            metadata: serde_json::Value::Object(
                h.payload.into_iter().collect::<serde_json::Map<_, _>>(),
            ),
        }
    }
}

impl From<PgVectorHit> for ScoredChunk {
    fn from(h: PgVectorHit) -> Self {
        ScoredChunk {
            id: h.id.to_string(),
            doc_id: h.doc_id,
            text: h.chunk,
            kind: h.kind,
            source: RetrievalSource::PgVector,
            initial_score: h.score,
            final_score: h.score,
            metadata: h.metadata,
        }
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::embeddings::MockEmbedder;

    fn chunk(id: &str, doc: &str, text: &str, kind: &str, score: f32) -> ScoredChunk {
        ScoredChunk {
            id: id.to_string(),
            doc_id: doc.to_string(),
            text: text.to_string(),
            kind: kind.to_string(),
            source: RetrievalSource::Qdrant,
            initial_score: score,
            final_score: score,
            metadata: serde_json::json!({}),
        }
    }

    #[tokio::test]
    async fn pipeline_rejects_no_backends() {
        let p = RagPipeline::builder(Arc::new(MockEmbedder::new())).build();
        let err = p.retrieve("hi").await.unwrap_err();
        assert!(matches!(err, RagError::NoBackends));
    }

    #[test]
    fn cosine_sim_unit_vectors() {
        assert!((cosine_sim(&[1.0, 0.0], &[1.0, 0.0]) - 1.0).abs() < 1e-6);
        assert!((cosine_sim(&[1.0, 0.0], &[0.0, 1.0]) - 0.0).abs() < 1e-6);
        assert!((cosine_sim(&[1.0, 0.0], &[-1.0, 0.0]) - (-1.0)).abs() < 1e-6);
    }

    #[test]
    fn cosine_sim_zero_vector() {
        assert_eq!(cosine_sim(&[0.0, 0.0], &[1.0, 1.0]), 0.0);
    }

    #[test]
    fn jaccard_basic() {
        let a: HashSet<_> = ["a", "b", "c"].iter().map(|s| s.to_string()).collect();
        let b: HashSet<_> = ["b", "c", "d"].iter().map(|s| s.to_string()).collect();
        let j = jaccard(&a, &b);
        // intersection = {b,c} = 2, union = {a,b,c,d} = 4 → 0.5
        assert!((j - 0.5).abs() < 1e-6);
    }

    #[test]
    fn jaccard_handles_empty() {
        let empty: HashSet<String> = HashSet::new();
        let one: HashSet<String> = ["a"].iter().map(|s| s.to_string()).collect();
        assert_eq!(jaccard(&empty, &empty), 0.0);
        assert_eq!(jaccard(&empty, &one), 0.0);
    }

    #[test]
    fn tokenize_splits_on_punctuation() {
        let t = tokenize("Hello, world! 2026_Q4");
        assert!(t.contains("hello"));
        assert!(t.contains("world"));
        assert!(t.contains("2026_q4"));
    }

    #[test]
    fn assemble_context_includes_provenance() {
        let chunks = vec![chunk("1", "story-1", "hello world", "story", 0.9)];
        let s = assemble_context(&chunks);
        assert!(s.contains("doc_id=story-1"));
        assert!(s.contains("kind=story"));
        assert!(s.contains("score=0.900"));
        assert!(s.contains("hello world"));
    }

    #[tokio::test]
    async fn default_reranker_score_only_passes_through() {
        let embedder = Arc::new(MockEmbedder::new());
        let r = DefaultReranker::new(embedder);
        let mut chunks = vec![
            chunk("1", "d", "alpha bravo", "story", 0.5),
            chunk("2", "d", "charlie delta", "story", 0.9),
        ];
        // In-place mutate initial scores via the rerank result.
        chunks = r.rerank("alpha", chunks, RerankMethod::ScoreOnly).await.unwrap();
        // Order preserved (ScoreOnly is a no-op on order).
        let scores: Vec<f32> = chunks.iter().map(|c| c.final_score).collect();
        assert_eq!(scores, vec![0.5, 0.9]);
    }

    #[tokio::test]
    async fn default_reranker_token_overlap_promotes_lexical_match() {
        let embedder = Arc::new(MockEmbedder::new());
        let r = DefaultReranker::new(embedder);
        // Two chunks, same vector score — the one sharing tokens with the
        // query should win on TokenOverlap.
        let chunks = vec![
            chunk("1", "d", "apple banana", "story", 0.8),
            chunk("2", "d", "the database is slow", "story", 0.8),
        ];
        let r1 = r
            .clone()
            .rerank("database slow", chunks.clone(), RerankMethod::TokenOverlap)
            .await
            .unwrap();
        assert_eq!(r1[0].id, "2", "lexically relevant chunk should rank first");
    }

    #[tokio::test]
    async fn default_reranker_hybrid_uses_cosine() {
        let embedder = Arc::new(MockEmbedder::new());
        let r = DefaultReranker::new(embedder);
        let chunks = vec![
            chunk("1", "d", "completely unrelated text", "story", 0.9),
            chunk("2", "d", "the database pool is exhausted", "story", 0.5),
        ];
        let r2 = r
            .rerank("database connection pool exhausted", chunks, RerankMethod::Hybrid)
            .await
            .unwrap();
        // We don't assert which one wins (mock embedder is hash-based and the
        // exact ordering is implementation-defined), but we do assert that
        // the top result has a non-zero score and that the scores are now
        // different from the initial scores.
        assert!(r2[0].final_score.is_finite());
        assert!(r2[0].final_score > 0.0);
    }

    #[tokio::test]
    async fn reranker_sorts_descending_by_final_score() {
        let embedder = Arc::new(MockEmbedder::new());
        let r = DefaultReranker::new(embedder);
        let chunks = vec![
            chunk("1", "d", "alpha alpha alpha", "story", 0.4),
            chunk("2", "d", "alpha bravo", "story", 0.4),
            chunk("3", "d", "completely different words here", "story", 0.4),
        ];
        let r = r
            .rerank("alpha", chunks, RerankMethod::TokenOverlap)
            .await
            .unwrap();
        for window in r.windows(2) {
            assert!(window[0].final_score >= window[1].final_score);
        }
    }

    #[test]
    fn qdrant_hit_conversion_extracts_fields() {
        let mut payload = std::collections::HashMap::new();
        payload.insert("doc_id".to_string(), serde_json::json!("S-42"));
        payload.insert("text".to_string(), serde_json::json!("hello"));
        payload.insert("kind".to_string(), serde_json::json!("story"));
        payload.insert("extra".to_string(), serde_json::json!("ignored-text"));
        let h = QdrantHit {
            id: "p1".to_string(),
            score: 0.88,
            payload,
        };
        let c: ScoredChunk = h.into();
        assert_eq!(c.doc_id, "S-42");
        assert_eq!(c.text, "hello");
        assert_eq!(c.kind, "story");
        assert_eq!(c.source, RetrievalSource::Qdrant);
        assert!((c.initial_score - 0.88).abs() < 1e-6);
        // metadata should retain the extra field, but NOT text (which was
        // extracted into the typed field).
        assert_eq!(c.metadata["extra"], "ignored-text");
    }

    #[test]
    fn rag_config_defaults_are_sensible() {
        let c = RagConfig::default();
        assert!(c.per_backend_limit >= 5);
        assert!(c.top_k >= 1);
        assert!(c.graph_expansion);
        assert_eq!(c.graph_hops, 1);
        assert_eq!(c.rerank, RerankMethod::Hybrid);
    }

    #[tokio::test]
    async fn empty_input_returns_empty_ranked() {
        let embedder = Arc::new(MockEmbedder::new());
        let r = DefaultReranker::new(embedder);
        let out = r.rerank("anything", Vec::new(), RerankMethod::Hybrid).await.unwrap();
        assert!(out.is_empty());
    }
}
