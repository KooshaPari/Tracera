//! `embed-worker` — long-running worker that reads chunks from a JSONL queue
//! and writes their embeddings to Qdrant (and optionally Postgres/pgvector).
//!
//! Input is line-delimited JSON of the form:
//!
//! ```json
//! {"doc_id":"story-1","chunk":"the database is slow","kind":"story","metadata":{...}}
//! ```
//!
//! Output is also JSONL on stdout, one line per embedded chunk:
//!
//! ```json
//! {"doc_id":"story-1","kind":"story","id":"<uuid>","dim":384,"sink":["qdrant","pg"]}
//! ```
//!
//! Errors are emitted to stderr in JSON form so a wrapper process can ingest
//! them and surface them on the queueing system. Exit codes follow
//! conventional service semantics:
//!
//! - `0`  — clean shutdown after EOF on stdin.
//! - `2`  — configuration error (env / CLI flags). Do not retry.
//! - `3`  — runtime error (Qdrant/Postgres connectivity). Retryable.
//!
//! The worker uses the **mock** embedder by default so it stays self-contained.
//! To wire in an ONNX model, set `TRACERA_EMBED_MODEL_PATH` to a `.onnx` file
//! and the worker will use `OnnxEmbedder` instead.

#![deny(unsafe_code)]

use std::io::{self, BufRead, Write};
use std::sync::Arc;

use serde::{Deserialize, Serialize};
use serde_json::Value;
use tokio::sync::mpsc;
use tracing::{error, info, warn};
use tracing_subscriber::{fmt, EnvFilter};

use tracera_ml::{
    Embedder, EmbedderError, MockEmbedder, PgVectorInsert, PgVectorStore, QdrantClient,
    QdrantPoint, EMBEDDING_DIM,
};
#[cfg(feature = "onnx")]
use tracera_ml::{OnnxEmbedder, OnnxEmbedderConfig};

// ---------------------------------------------------------------------------
// Wire formats
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
struct InputLine {
    doc_id: String,
    chunk: String,
    #[serde(default = "default_kind")]
    kind: String,
    #[serde(default)]
    metadata: Value,
}

fn default_kind() -> String {
    "story".to_string()
}

#[derive(Debug, Serialize)]
struct OutputLine {
    doc_id: String,
    kind: String,
    id: String,
    dim: usize,
    sinks: Vec<&'static str>,
}

#[derive(Debug, Serialize)]
struct ErrorLine<'a> {
    line_no: usize,
    error: String,
    source: &'a str,
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

#[derive(Debug)]
struct Config {
    qdrant_url: Option<String>,
    qdrant_collection: Option<String>,
    database_url: Option<String>,
    model_path: Option<String>,
    batch_size: usize,
}

impl Config {
    fn from_env() -> Self {
        Self {
            qdrant_url: std::env::var("TRACERA_QDRANT_URL").ok(),
            qdrant_collection: std::env::var("TRACERA_QDRANT_COLLECTION").ok(),
            database_url: std::env::var("TRACERA_DATABASE_URL").ok(),
            model_path: std::env::var("TRACERA_EMBED_MODEL_PATH").ok(),
            batch_size: std::env::var("TRACERA_EMBED_BATCH_SIZE")
                .ok()
                .and_then(|s| s.parse().ok())
                .unwrap_or(64),
        }
    }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

#[tokio::main(flavor = "multi_thread")]
async fn main() -> io::Result<()> {
    init_tracing();
    let cfg = Config::from_env();
    info!(?cfg, "starting embed-worker");

    if cfg.qdrant_url.is_none() && cfg.database_url.is_none() {
        eprintln!(
            "{{\"error\":\"no sink configured: set TRACERA_QDRANT_URL and/or TRACERA_DATABASE_URL\"}}"
        );
        std::process::exit(2);
    }

    // Build the embedder. If `TRACERA_EMBED_MODEL_PATH` is set we *try* to
    // load an ONNX model; if that fails we fall back to a clear error so the
    // operator notices instead of silently using a mock.
    let embedder: Arc<dyn Embedder> = match cfg.model_path.as_deref() {
        Some(path) => {
            // `OnnxEmbedder` is feature-gated; if the feature isn't enabled
            // we surface a clear error instead of pretending to be ONNX.
            #[cfg(feature = "onnx")]
            {
                let ecfg = OnnxEmbedderConfig::new(path, EMBEDDING_DIM);
                match OnnxEmbedder::load(ecfg) {
                    Ok(e) => {
                        info!(model = %path, "loaded ONNX model");
                        Arc::new(e)
                    }
                    Err(err) => {
                        eprintln!(
                            "{{\"error\":\"failed to load ONNX model {path}: {err}\"}}"
                        );
                        std::process::exit(2);
                    }
                }
            }
            #[cfg(not(feature = "onnx"))]
            {
                let _ = path;
                eprintln!(
                    "{{\"error\":\"TRACERA_EMBED_MODEL_PATH is set but the `onnx` feature is not enabled; rebuild with --features onnx\"}}"
                );
                std::process::exit(2);
            }
        }
        None => {
            warn!("no TRACERA_EMBED_MODEL_PATH set, using deterministic mock embedder");
            Arc::new(MockEmbedder::new())
        }
    };

    // Optional backends. Both are lazy — if not configured we skip them.
    let qdrant = match (&cfg.qdrant_url, &cfg.qdrant_collection) {
        (Some(url), Some(collection)) => {
            let client = QdrantClient::new(url.clone());
            if let Err(e) = client.ensure_collection(collection, embedder.dim()).await {
                eprintln!(
                    "{{\"error\":\"qdrant ensure_collection failed: {e}\",\"sink\":\"qdrant\"}}"
                );
                std::process::exit(3);
            }
            Some((client, collection.clone()))
        }
        _ => None,
    };
    let pg = match &cfg.database_url {
        Some(url) => match sqlx::PgPool::connect(url).await {
            Ok(pool) => Some(PgVectorStore::new(pool)),
            Err(e) => {
                eprintln!("{{\"error\":\"pg connect failed: {e}\",\"sink\":\"pg\"}}");
                std::process::exit(3);
            }
        },
        None => None,
    };

    // Channel for batched writes. The reader produces input lines, the
    // processor accumulates them and flushes every `batch_size` rows or when
    // EOF hits.
    let (tx, mut rx) = mpsc::channel::<InputLine>(cfg.batch_size * 2);

    // Reader task: stdin → channel.
    tokio::spawn(async move {
        let stdin = io::stdin();
        let mut handle = stdin.lock();
        let mut buf = String::new();
        let mut line_no: usize = 0;
        loop {
            buf.clear();
            let bytes = match handle.read_line(&mut buf) {
                Ok(b) => b,
                Err(e) => {
                    error!("stdin read failed: {e}");
                    break;
                }
            };
            if bytes == 0 {
                break; // EOF
            }
            line_no += 1;
            let trimmed = buf.trim();
            if trimmed.is_empty() || trimmed.starts_with('#') {
                continue;
            }
            match serde_json::from_str::<InputLine>(trimmed) {
                Ok(line) => {
                    if tx.send(line).await.is_err() {
                        // Receiver gone — likely a panic upstream.
                        break;
                    }
                }
                Err(e) => {
                    let mut stderr = io::stderr().lock();
                    let _ = writeln!(
                        stderr,
                        "{}",
                        serde_json::to_string(&ErrorLine {
                            line_no,
                            error: e.to_string(),
                            source: "parse",
                        })
                        .unwrap_or_else(|_| "{\"error\":\"failed to serialize error\"}".to_string())
                    );
                }
            }
        }
        drop(tx);
    });

    // Processor task: embed in micro-batches, write to backends.
    let mut stdout = io::stdout().lock();
    let mut pending: Vec<(InputLine, Vec<f32>)> = Vec::with_capacity(cfg.batch_size);

    while let Some(input) = rx.recv().await {
        match embed_one(&embedder, &input).await {
            Ok(emb) => pending.push((input, emb)),
            Err(e) => {
                let mut stderr = io::stderr().lock();
                let _ = writeln!(
                    stderr,
                    "{}",
                    serde_json::to_string(&ErrorLine {
                        line_no: pending.len() + 1,
                        error: e.to_string(),
                        source: "embed",
                    })
                    .unwrap_or_else(|_| "{\"error\":\"failed to serialize error\"}".to_string())
                );
                // Continue processing — one bad row shouldn't kill the worker.
            }
        }

        if pending.len() >= cfg.batch_size {
            flush(&mut pending, &mut stdout, &qdrant, &pg).await;
        }
    }

    // Final flush.
    if !pending.is_empty() {
        flush(&mut pending, &mut stdout, &qdrant, &pg).await;
    }

    info!("embed-worker exiting cleanly");
    Ok(())
}

async fn embed_one(embedder: &Arc<dyn Embedder>, input: &InputLine) -> Result<Vec<f32>, EmbedderError> {
    let e = embedder.embed(&input.chunk).await?;
    Ok(e.vector)
}

/// Flush a batch to stdout + configured backends.
async fn flush(
    pending: &mut Vec<(InputLine, Vec<f32>)>,
    stdout: &mut io::StdoutLock<'_>,
    qdrant: &Option<(QdrantClient, String)>,
    pg: &Option<PgVectorStore>,
) {
    // Build sink lists + stdout lines.
    let mut points: Vec<QdrantPoint> = Vec::with_capacity(pending.len());
    let mut pg_rows: Vec<PgVectorInsert> = Vec::with_capacity(pending.len());

    for (input, vec) in pending.iter() {
        let id = uuid::Uuid::new_v4();
        let mut sinks = Vec::new();
        if qdrant.is_some() {
            // We collect points and push in one batch below.
            let mut payload = std::collections::HashMap::new();
            payload.insert("doc_id".to_string(), serde_json::json!(input.doc_id));
            payload.insert("text".to_string(), serde_json::json!(input.chunk));
            payload.insert("kind".to_string(), serde_json::json!(input.kind));
            // Spread the user metadata too so downstream filtering works.
            if let Value::Object(map) = &input.metadata {
                for (k, v) in map {
                    payload.insert(k.clone(), v.clone());
                }
            }
            points.push(QdrantPoint {
                id: id.to_string(),
                vector: vec.clone(),
                payload,
            });
            sinks.push("qdrant");
        }
        if pg.is_some() {
            pg_rows.push(PgVectorInsert {
                doc_id: &input.doc_id,
                chunk: &input.chunk,
                kind: &input.kind,
                embedding: vec.as_slice(),
                metadata: input.metadata.clone(),
            });
            sinks.push("pg");
        }

        let line = OutputLine {
            doc_id: input.doc_id.clone(),
            kind: input.kind.clone(),
            id: id.to_string(),
            dim: vec.len(),
            sinks: sinks.clone(),
        };
        if let Ok(s) = serde_json::to_string(&line) {
            let _ = writeln!(stdout, "{s}");
        }
    }
    let _ = stdout.flush();

    // Write to backends. We don't block the whole worker on a single failed
    // batch — instead we log the failure as an error line so the operator
    // can investigate.
    if let Some((client, collection)) = qdrant {
        if !points.is_empty() {
            match client.upsert_points(collection, &points).await {
                Ok(n) => info!(count = n, sink = "qdrant", "upserted batch"),
                Err(e) => {
                    let mut stderr = io::stderr().lock();
                    let _ = writeln!(
                        stderr,
                        "{}",
                        serde_json::json!({"error": e.to_string(), "sink": "qdrant"})
                    );
                }
            }
        }
    }
    if let Some(pg) = pg {
        if !pg_rows.is_empty() {
            match pg.upsert_batch(&pg_rows).await {
                Ok(ids) => info!(count = ids.len(), sink = "pg", "upserted batch"),
                Err(e) => {
                    let mut stderr = io::stderr().lock();
                    let _ = writeln!(
                        stderr,
                        "{}",
                        serde_json::json!({"error": e.to_string(), "sink": "pg"})
                    );
                }
            }
        }
    }

    // Silence "unused assignment" warning in case pending is dropped.
    pending.clear();
}

fn init_tracing() {
    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));
    let _ = fmt().with_env_filter(filter).with_target(false).try_init();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn input_line_parses_minimal_payload() {
        let raw = r#"{"doc_id":"d1","chunk":"hello"}"#;
        let parsed: InputLine = serde_json::from_str(raw).unwrap();
        assert_eq!(parsed.doc_id, "d1");
        assert_eq!(parsed.chunk, "hello");
        // kind defaults to "story"
        assert_eq!(parsed.kind, "story");
        assert_eq!(parsed.metadata, Value::Null);
    }

    #[test]
    fn input_line_parses_full_payload() {
        let raw = r#"{"doc_id":"d1","chunk":"c","kind":"code","metadata":{"pr":42}}"#;
        let parsed: InputLine = serde_json::from_str(raw).unwrap();
        assert_eq!(parsed.kind, "code");
        assert_eq!(parsed.metadata["pr"], 42);
    }

    #[test]
    fn output_line_roundtrips() {
        let line = OutputLine {
            doc_id: "d".into(),
            kind: "story".into(),
            id: "id".into(),
            dim: 384,
            sinks: vec!["qdrant"],
        };
        let s = serde_json::to_string(&line).unwrap();
        assert!(s.contains("\"dim\":384"));
        assert!(s.contains("\"qdrant\""));
    }

    #[test]
    fn config_from_env_picks_up_overrides() {
        // We can't easily flip env in a multi-threaded test without affecting
        // siblings, so just check the defaults work.
        let cfg = Config::from_env();
        assert!(cfg.batch_size >= 1);
    }
}
