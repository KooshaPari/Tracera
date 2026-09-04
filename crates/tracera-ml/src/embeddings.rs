//! Embeddings: deterministic mock + ONNX Runtime interface.
//!
//! The mock embedder is the default and is sufficient for unit tests, CI, and
//! any environment where you don't want to ship a multi-hundred-megabyte model
//! file. It hashes each token through `sha2`, projects to a fixed-dimensional
//! unit vector, and is *deterministic* — the same input always produces the
//! same vector, which is essential for test stability.
//!
//! The ONNX embedder (`OnnxEmbedder`) is feature-gated behind `onnx` and uses
//! the `ort` crate to load a model file (e.g. an all-MiniLM export) and run
//! inference. It implements the same [`Embedder`] trait so callers don't need
//! to special-case backends.

use std::path::PathBuf;

use async_trait::async_trait;
use sha2::{Digest, Sha256};

/// Fixed dimensionality for the mock embedder. Real models vary (384 for
/// MiniLM-L6, 768 for base BERT, 1536 for OpenAI `text-embedding-3-small`,
/// etc.) — call sites should consult [`Embedder::dim`] instead of hard-coding.
pub const EMBEDDING_DIM: usize = 384;

/// Errors produced by embedders.
#[derive(Debug, thiserror::Error)]
pub enum EmbedderError {
    #[error("input too long: {0} tokens (max {1})")]
    InputTooLong(usize, usize),

    #[error("empty input")]
    EmptyInput,

    #[error("model load error: {0}")]
    ModelLoad(String),

    #[error("inference error: {0}")]
    Inference(String),
}

/// Output of a single embedding call: the vector plus a stable identifier for
/// the source (handy for cache lookups).
#[derive(Debug, Clone)]
pub struct Embedding {
    pub vector: Vec<f32>,
}

impl Embedding {
    pub fn dim(&self) -> usize {
        self.vector.len()
    }
}

/// The core trait every embedder implements.
///
/// `async_trait` lets us hold the trait in dyn-compatible storage; for
/// production hot paths callers usually hold a concrete type (e.g.
/// `Arc<MockEmbedder>`) and dispatch is monomorphized.
#[async_trait]
pub trait Embedder: Send + Sync {
    /// Dimensionality of vectors this embedder produces.
    fn dim(&self) -> usize;

    /// Embed a single piece of text.
    async fn embed(&self, text: &str) -> Result<Embedding, EmbedderError>;

    /// Embed a batch. The default implementation just calls [`Self::embed`]
    /// in order; backends with native batching (ONNX) should override.
    async fn embed_batch(&self, texts: &[&str]) -> Result<Vec<Embedding>, EmbedderError> {
        let mut out = Vec::with_capacity(texts.len());
        for t in texts {
            out.push(self.embed(t).await?);
        }
        Ok(out)
    }
}

// ---------------------------------------------------------------------------
// Mock embedder
// ---------------------------------------------------------------------------

/// Deterministic, dependency-free embedder. Splits input on whitespace +
/// punctuation, hashes each token into the `EMBEDDING_DIM`-sized space using
/// `sha256`, and L2-normalizes. Identical inputs → identical vectors, which is
/// what tests want.
#[derive(Debug, Clone, Default)]
pub struct MockEmbedder {
    dim: usize,
}

impl MockEmbedder {
    pub fn new() -> Self {
        Self { dim: EMBEDDING_DIM }
    }

    pub fn with_dim(dim: usize) -> Self {
        Self { dim }
    }

    /// Split input into tokens. Kept `pub(crate)` so tests can exercise it.
    pub(crate) fn tokenize(text: &str) -> Vec<String> {
        // Lowercase + split on anything that isn't an ASCII letter/digit/underscore.
        // We're deliberately simple — this is a mock, not a tokenizer.
        let lower = text.to_lowercase();
        let mut tokens = Vec::new();
        let mut cur = String::new();
        for ch in lower.chars() {
            if ch.is_ascii_alphanumeric() || ch == '_' {
                cur.push(ch);
            } else if !cur.is_empty() {
                tokens.push(std::mem::take(&mut cur));
            }
        }
        if !cur.is_empty() {
            tokens.push(cur);
        }
        tokens
    }
}

#[async_trait]
impl Embedder for MockEmbedder {
    fn dim(&self) -> usize {
        self.dim
    }

    async fn embed(&self, text: &str) -> Result<Embedding, EmbedderError> {
        if text.trim().is_empty() {
            return Err(EmbedderError::EmptyInput);
        }
        let tokens = Self::tokenize(text);
        if tokens.is_empty() {
            return Err(EmbedderError::EmptyInput);
        }

        // Accumulator in f32 to keep the maths the same shape as a real model.
        let mut acc = vec![0f32; self.dim];
        for token in &tokens {
            // Hash → 32 bytes; fold into our dim via mod. Two tokens hashing to
            // the same bucket add rather than overwrite so common tokens don't
            // collapse to identical embeddings.
            let digest = Sha256::digest(token.as_bytes());
            for (i, byte) in digest.iter().enumerate() {
                // Spread each digest byte across `dim / 32` slots to make sure
                // smaller `dim` values still get reasonable coverage.
                let slot = (i * self.dim / digest.len()).min(self.dim - 1);
                acc[slot] += f32::from(*byte) / 255.0;
            }
        }

        // L2 normalize. A non-token input would otherwise produce the zero
        // vector, which breaks cosine similarity downstream.
        let norm: f32 = acc.iter().map(|v| v * v).sum::<f32>().sqrt();
        if norm > 0.0 {
            for v in &mut acc {
                *v /= norm;
            }
        } else {
            // Degenerate case — fall back to a unit vector in slot 0.
            acc[0] = 1.0;
        }

        Ok(Embedding { vector: acc })
    }
}

// ---------------------------------------------------------------------------
// ONNX Runtime embedder (feature-gated)
// ---------------------------------------------------------------------------

/// Configuration for the ONNX-backed embedder.
#[derive(Debug, Clone)]
pub struct OnnxEmbedderConfig {
    /// Path to the `.onnx` model file on disk.
    pub model_path: PathBuf,
    /// Tokenizer JSON (e.g. `tokenizer.json` from a Hugging Face export).
    /// Currently unused here — tokenization is left to the caller and the
    /// input is treated as already-tokenized IDs. Kept in the config so future
    /// revisions can wire up a real tokenizer without breaking the API.
    pub tokenizer_path: Option<PathBuf>,
    /// Output dimension of the model (read from the config file).
    pub dim: usize,
    /// Maximum token count the model accepts.
    pub max_tokens: usize,
    /// Execution providers to try, in priority order.
    /// Defaults to CPU; on macOS/Windows builds `ort` will pick the best
    /// available provider automatically.
    pub execution_providers: Vec<String>,
}

impl OnnxEmbedderConfig {
    pub fn new(model_path: impl Into<PathBuf>, dim: usize) -> Self {
        Self {
            model_path: model_path.into(),
            tokenizer_path: None,
            dim,
            max_tokens: 512,
            execution_providers: vec!["CPU".to_string()],
        }
    }
}

/// ONNX Runtime-backed embedder. Only available when the crate is built with
/// `--features onnx`.
#[cfg(feature = "onnx")]
#[derive(Debug)]
pub struct OnnxEmbedder {
    session: ort::session::Session,
    config: OnnxEmbedderConfig,
}

#[cfg(feature = "onnx")]
impl OnnxEmbedder {
    pub fn load(config: OnnxEmbedderConfig) -> Result<Self, EmbedderError> {
        use ort::session::Session;

        // Build the session. We deliberately use the builder API so callers can
        // attach execution providers if they want GPU acceleration.
        let mut builder = Session::builder()
            .map_err(|e| EmbedderError::ModelLoad(e.to_string()))?;

        // Configure execution providers. `ort` 2.x exposes this via
        // `commit_from_requested`. Failures here are non-fatal — we keep going
        // with CPU if a provider isn't available, which is the right behavior
        // for a portable crate.
        let providers: Vec<ort::execution_providers::ExecutionProviderDispatch> = config
            .execution_providers
            .iter()
            .filter_map(|name| match name.as_str() {
                "CPU" => Some(ort::execution_providers::CPUExecutionProvider::default().build()),
                "CUDA" => ort::execution_providers::CUDAExecutionProvider::default().build().ok(),
                "TensorRT" => ort::execution_providers::TensorRTExecutionProvider::default()
                    .build()
                    .ok(),
                "CoreML" => ort::execution_providers::CoreMLExecutionProvider::default().build().ok(),
                _ => None,
            })
            .collect();
        if !providers.is_empty() {
            builder = builder
                .with_execution_providers(providers)
                .map_err(|e| EmbedderError::ModelLoad(e.to_string()))?;
        }

        let session = builder
            .commit_from_file(&config.model_path)
            .map_err(|e| EmbedderError::ModelLoad(format!("{}: {}", config.model_path.display(), e)))?;

        Ok(Self { session, config })
    }
}

#[cfg(feature = "onnx")]
#[async_trait]
impl Embedder for OnnxEmbedder {
    fn dim(&self) -> usize {
        self.config.dim
    }

    async fn embed(&self, _text: &str) -> Result<Embedding, EmbedderError> {
        // The actual tokenization + tensor construction depends on the chosen
        // model. Rather than baking in a single tokenizer, we return a clear
        // error if this method is called directly — production callers should
        // go through a thin wrapper that does tokenization + mean-pooling +
        // normalization specific to their model.
        Err(EmbedderError::Inference(
            "OnnxEmbedder::embed requires a model-specific tokenizer; implement and dispatch \
             from your application code, or use `embed_batch_ids` for raw int32 input."
                .to_string(),
        ))
    }

    /// Lower-level entry point: takes pre-tokenized input_ids + attention_mask
    /// and returns the model's last_hidden_state mean-pooled to a vector.
    async fn embed_batch_ids(
        &self,
        input_ids: &[i64],
        attention_mask: &[i64],
    ) -> Result<Embedding, EmbedderError> {
        use ort::value::Tensor;

        if input_ids.len() != attention_mask.len() {
            return Err(EmbedderError::Inference(format!(
                "input_ids.len()={} != attention_mask.len()={}",
                input_ids.len(),
                attention_mask.len()
            )));
        }
        if input_ids.len() > self.config.max_tokens {
            return Err(EmbedderError::InputTooLong(
                input_ids.len(),
                self.config.max_tokens,
            ));
        }

        let seq_len = input_ids.len();
        // Model wants [batch=1, seq_len] int64 tensors.
        let ids_owned = input_ids.to_vec();
        let mask_owned = attention_mask.to_vec();

        let ids_tensor =
            Tensor::from_array(([1usize, seq_len], ids_owned)).map_err(|e| EmbedderError::Inference(e.to_string()))?;
        let mask_tensor = Tensor::from_array(([1usize, seq_len], mask_owned))
            .map_err(|e| EmbedderError::Inference(e.to_string()))?;

        let outputs = self
            .session
            .run(ort::inputs![ids_tensor, mask_tensor])
            .map_err(|e| EmbedderError::Inference(e.to_string()))?;

        // The model exports a single `last_hidden_state` output shaped
        // [1, seq_len, hidden_dim]. Mean-pool over the sequence dimension
        // weighted by the attention mask so padding doesn't pollute the result.
        let (_shape, data) = outputs["last_hidden_state"]
            .try_extract_tensor::<f32>()
            .map_err(|e| EmbedderError::Inference(e.to_string()))?;

        let hidden = self.config.dim;
        let mut pooled = vec![0f32; hidden];
        let mut weight_sum = 0f32;
        for (i, &m) in attention_mask.iter().enumerate() {
            if m == 0 {
                continue;
            }
            weight_sum += 1.0;
            for h in 0..hidden {
                // Safety: `data` has exactly seq_len * hidden f32s.
                pooled[h] += data[i * hidden + h];
            }
        }
        if weight_sum > 0.0 {
            for v in &mut pooled {
                *v /= weight_sum;
            }
        }
        // L2 normalize.
        let norm: f32 = pooled.iter().map(|v| v * v).sum::<f32>().sqrt();
        if norm > 0.0 {
            for v in &mut pooled {
                *v /= norm;
            }
        }

        Ok(Embedding { vector: pooled })
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn approx_eq(a: f32, b: f32, eps: f32) -> bool {
        (a - b).abs() < eps
    }

    #[tokio::test]
    async fn mock_embedder_is_deterministic() {
        let e = MockEmbedder::new();
        let v1 = e.embed("hello world").await.unwrap();
        let v2 = e.embed("hello world").await.unwrap();
        assert_eq!(v1.vector, v2.vector, "same input must produce same vector");
    }

    #[tokio::test]
    async fn mock_embedder_rejects_empty() {
        let e = MockEmbedder::new();
        assert!(matches!(e.embed("").await, Err(EmbedderError::EmptyInput)));
        assert!(matches!(e.embed("   ").await, Err(EmbedderError::EmptyInput)));
        assert!(matches!(
            e.embed("!!!").await,
            Err(EmbedderError::EmptyInput)
        ));
    }

    #[tokio::test]
    async fn mock_embedder_is_normalized() {
        let e = MockEmbedder::new();
        let v = e.embed("a quick brown fox jumps over the lazy dog").await.unwrap();
        let norm: f32 = v.vector.iter().map(|x| x * x).sum::<f32>().sqrt();
        assert!(approx_eq(norm, 1.0, 1e-4), "vector should be unit length, got {}", norm);
    }

    #[tokio::test]
    async fn mock_embedder_similar_inputs_have_higher_similarity() {
        let e = MockEmbedder::new();
        let a = e.embed("database connection pool exhausted").await.unwrap();
        let b = e.embed("database connection pool drained").await.unwrap();
        let c = e.embed("the cat sat on the mat").await.unwrap();

        let sim = |x: &[f32], y: &[f32]| -> f32 {
            x.iter().zip(y.iter()).map(|(a, b)| a * b).sum()
        };
        let ab = sim(&a.vector, &b.vector);
        let ac = sim(&a.vector, &c.vector);
        assert!(
            ab > ac,
            "related sentences should be more similar than unrelated ones: ab={ab}, ac={ac}"
        );
    }

    #[tokio::test]
    async fn mock_embedder_batch_preserves_order() {
        let e = MockEmbedder::new();
        let inputs = ["alpha", "beta", "gamma"];
        let single: Vec<Vec<f32>> = futures::future::join_all(inputs.iter().map(|s| e.embed(s)))
            .await
            .into_iter()
            .map(|r| r.unwrap().vector)
            .collect();
        let batch = e.embed_batch(&inputs).await.unwrap();
        assert_eq!(batch.len(), single.len());
        for (i, (s, b)) in single.iter().zip(batch.iter()).enumerate() {
            assert_eq!(s, &b.vector, "batch[{i}] mismatch");
        }
    }

    #[tokio::test]
    async fn mock_embedder_custom_dim() {
        let e = MockEmbedder::with_dim(64);
        let v = e.embed("foo bar").await.unwrap();
        assert_eq!(v.dim(), 64);
    }

    #[test]
    fn tokenize_handles_punctuation_and_case() {
        let t = MockEmbedder::tokenize("Hello, World! It's_2026.");
        assert_eq!(t, vec!["hello", "world", "it", "s_2026"]);
    }

    #[tokio::test]
    async fn embedding_trait_object_works() {
        let e: std::sync::Arc<dyn Embedder> = std::sync::Arc::new(MockEmbedder::new());
        let v = e.embed("dispatch").await.unwrap();
        assert_eq!(v.dim(), EMBEDDING_DIM);
    }
}
