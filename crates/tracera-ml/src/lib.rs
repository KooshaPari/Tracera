//! `tracera-ml` — embeddings, vector stores, and retrieval-augmented generation.
//!
//! This crate is split into focused modules so each backend can evolve
//! independently:
//!
//! - [`embeddings`] — the [`embeddings::Embedder`] trait, a deterministic
//!   mock embedder for tests/dev, and an ONNX Runtime inference path gated by
//!   the `onnx` feature flag.
//! - [`qdrant`] — async Qdrant client wrapper (search + upsert).
//! - [`pgvector`] — Postgres / pgvector query helpers (cosine search + KNN
//!   filter pushdown).
//! - [`rag`] — the retrieval pipeline: embed the query → vector search →
//!   graph expansion → cross-encoder style rerank → assembled context.
//!
//! All public types are re-exported here so downstream crates can simply
//! `use tracera_ml::*` (or pick the submodule).

#![deny(unsafe_code)]
#![warn(missing_debug_implementations)]

pub mod embeddings;
pub mod pgvector;
pub mod qdrant;
pub mod rag;

pub use embeddings::{Embedder, EmbedderError, Embedding, MockEmbedder, EMBEDDING_DIM};
pub use pgvector::{PgVectorHit, PgVectorStore};
pub use qdrant::{QdrantClient, QdrantHit, QdrantPoint, QdrantSearchRequest};
pub use rag::{
    GraphExpander, GraphNeighbor, RagConfig, RagPipeline, RagResult, RetrievalSource, Reranker,
    RerankMethod, ScoredChunk,
};

// ONNX-backed embedder is only available with the `onnx` feature. We
// re-export the items behind the same gate so the default build stays clean.
#[cfg(feature = "onnx")]
pub use embeddings::{OnnxEmbedder, OnnxEmbedderConfig};

/// Crate-wide error type. Each module may surface its own error nested under
/// `details` for richer diagnostics, but the top-level `MlError` enum lets
/// callers pattern-match on the high-level failure category without coupling
/// to a specific backend.
#[derive(Debug, thiserror::Error)]
pub enum MlError {
    #[error("embedder error: {0}")]
    Embedder(#[from] embeddings::EmbedderError),

    #[error("qdrant error: {0}")]
    Qdrant(#[from] qdrant::QdrantError),

    #[error("pgvector error: {0}")]
    PgVector(#[from] pgvector::PgVectorError),

    #[error("rag pipeline error: {0}")]
    Rag(#[from] rag::RagError),

    #[error("serialization error: {0}")]
    Serde(#[from] serde_json::Error),

    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
}

/// Convenience alias used across this crate.
pub type MlResult<T> = Result<T, MlError>;
