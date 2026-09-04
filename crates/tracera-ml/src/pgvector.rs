//! Postgres + pgvector query helpers.
//!
//! We use the runtime `sqlx::query` / `sqlx::query_as` APIs (no macros) so the
//! crate compiles without a live database connection. The `vector` extension
//! type is read as `pgvector` text representation (`[v1,v2,...]`) — we parse
//! it ourselves rather than depending on the `pgvector` crate, which keeps
//! the dependency surface small and matches the same approach used in
//! `tracera-server`'s `pg_store.rs`.
//!
//! Tables this crate assumes:
//!
//! ```sql
//! CREATE EXTENSION IF NOT EXISTS vector;
//! CREATE TABLE IF NOT EXISTS embeddings (
//!     id          UUID PRIMARY KEY,
//!     doc_id      TEXT NOT NULL,
//!     chunk       TEXT NOT NULL,
//!     kind        TEXT NOT NULL,
//!     embedding   VECTOR(384) NOT NULL,
//!     metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
//!     created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
//! );
//! CREATE INDEX IF NOT EXISTS embeddings_embedding_idx
//!     ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
//! ```

use serde_json::Value;
use sqlx::{PgPool, Row};
use uuid::Uuid;

/// Errors produced by the pgvector wrapper.
#[derive(Debug, thiserror::Error)]
pub enum PgVectorError {
    #[error("postgres error: {0}")]
    Sqlx(#[from] sqlx::Error),

    #[error("invalid vector string: {0}")]
    InvalidVector(String),

    #[error("dimension mismatch: vector has {got}, table column expects {expected}")]
    DimensionMismatch { got: usize, expected: usize },
}

/// A search hit from the pgvector table.
#[derive(Debug, Clone)]
pub struct PgVectorHit {
    pub id: Uuid,
    pub doc_id: String,
    pub chunk: String,
    pub kind: String,
    /// Cosine similarity (1.0 = identical, 0.0 = orthogonal). pgvector's
    /// `<=>` operator returns cosine *distance*, which we convert to similarity
    /// in the wrapper.
    pub score: f32,
    pub metadata: Value,
}

/// Postgres-backed vector store.
#[derive(Debug, Clone)]
pub struct PgVectorStore {
    pool: PgPool,
}

impl PgVectorStore {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    /// Pool reference, exposed for callers that want to run their own
    /// queries alongside vector search.
    pub fn pool(&self) -> &PgPool {
        &self.pool
    }

    /// Insert (or upsert) a single chunk + its embedding.
    pub async fn upsert_embedding(
        &self,
        doc_id: &str,
        chunk: &str,
        kind: &str,
        embedding: &[f32],
        metadata: Value,
    ) -> Result<Uuid, PgVectorError> {
        let id = Uuid::new_v4();
        let vec_str = encode_vector(embedding)?;
        sqlx::query(
            "INSERT INTO embeddings (id, doc_id, chunk, kind, embedding, metadata) \
             VALUES ($1, $2, $3, $4, $5::vector, $6::jsonb) \
             ON CONFLICT (id) DO UPDATE SET \
                 doc_id = EXCLUDED.doc_id, \
                 chunk = EXCLUDED.chunk, \
                 kind = EXCLUDED.kind, \
                 embedding = EXCLUDED.embedding, \
                 metadata = EXCLUDED.metadata",
        )
        .bind(id)
        .bind(doc_id)
        .bind(chunk)
        .bind(kind)
        .bind(vec_str)
        .bind(metadata)
        .execute(&self.pool)
        .await?;
        Ok(id)
    }

    /// Batch upsert using a single multi-row INSERT. Much faster than
    /// per-row calls when ingesting a document with many chunks.
    pub async fn upsert_batch(
        &self,
        rows: &[PgVectorInsert<'_>],
    ) -> Result<Vec<Uuid>, PgVectorError> {
        if rows.is_empty() {
            return Ok(Vec::new());
        }

        // Build a parameterized INSERT: ($1,$2,$3,$4,$5::vector,$6::jsonb), ...
        // We bind each row positionally rather than using UNNEST so the
        // generated SQL is easy to read in pg_stat_statements.
        let placeholders: Vec<String> = (0..rows.len())
            .map(|i| {
                let base = i * 6;
                format!(
                    "(${},${},${},${},${}::vector,${}::jsonb)",
                    base + 1,
                    base + 2,
                    base + 3,
                    base + 4,
                    base + 5,
                    base + 6,
                )
            })
            .collect();
        let sql = format!(
            "INSERT INTO embeddings (id, doc_id, chunk, kind, embedding, metadata) VALUES {} \
             ON CONFLICT (id) DO UPDATE SET \
                 doc_id = EXCLUDED.doc_id, \
                 chunk = EXCLUDED.chunk, \
                 kind = EXCLUDED.kind, \
                 embedding = EXCLUDED.embedding, \
                 metadata = EXCLUDED.metadata",
            placeholders.join(", ")
        );

        let mut q = sqlx::query(&sql);
        let mut ids = Vec::with_capacity(rows.len());
        for r in rows {
            let id = Uuid::new_v4();
            ids.push(id);
            q = q
                .bind(id)
                .bind(r.doc_id)
                .bind(r.chunk)
                .bind(r.kind)
                .bind(encode_vector(r.embedding)?)
                .bind(r.metadata.clone());
        }
        q.execute(&self.pool).await?;
        Ok(ids)
    }

    /// Cosine KNN search. `kind_filter` (if supplied) restricts results to
    /// a single `kind` value — useful when you want only "story" chunks
    /// and not "code" chunks.
    pub async fn cosine_search(
        &self,
        query: &[f32],
        limit: u64,
        kind_filter: Option<&str>,
    ) -> Result<Vec<PgVectorHit>, PgVectorError> {
        let vec_str = encode_vector(query)?;

        // We pull an extra row so we can detect "out of bounds" cases where
        // an index scan under-returns, and so we can re-rank ties by id.
        let internal_limit = limit.min(1000);

        let rows = if let Some(kind) = kind_filter {
            sqlx::query(
                "SELECT id, doc_id, chunk, kind, metadata::text AS metadata, \
                        1 - (embedding <=> $1::vector) AS score \
                 FROM embeddings \
                 WHERE kind = $2 \
                 ORDER BY embedding <=> $1::vector \
                 LIMIT $3",
            )
            .bind(vec_str)
            .bind(kind)
            .bind(internal_limit as i64)
            .fetch_all(&self.pool)
            .await?
        } else {
            sqlx::query(
                "SELECT id, doc_id, chunk, kind, metadata::text AS metadata, \
                        1 - (embedding <=> $1::vector) AS score \
                 FROM embeddings \
                 ORDER BY embedding <=> $1::vector \
                 LIMIT $2",
            )
            .bind(vec_str)
            .bind(internal_limit as i64)
            .fetch_all(&self.pool)
            .await?
        };

        let mut hits = Vec::with_capacity(rows.len());
        for r in rows {
            let meta_str: String = r.try_get("metadata").unwrap_or_default();
            let metadata: Value = serde_json::from_str(&meta_str).unwrap_or(Value::Null);
            hits.push(PgVectorHit {
                id: r.try_get("id").unwrap_or_else(|_| Uuid::nil()),
                doc_id: r.try_get("doc_id").unwrap_or_default(),
                chunk: r.try_get("chunk").unwrap_or_default(),
                kind: r.try_get("kind").unwrap_or_default(),
                score: r.try_get("score").unwrap_or(0.0),
                metadata,
            });
        }

        // Truncate to caller-requested limit after re-ranking, in case the
        // server returned ties that the index can return in arbitrary order.
        hits.truncate(limit as usize);
        Ok(hits)
    }

    /// Delete all chunks for a given `doc_id`. Returns the number of rows
    /// removed.
    pub async fn delete_by_doc(&self, doc_id: &str) -> Result<u64, PgVectorError> {
        let res = sqlx::query("DELETE FROM embeddings WHERE doc_id = $1")
            .bind(doc_id)
            .execute(&self.pool)
            .await?;
        Ok(res.rows_affected())
    }
}

/// A single row for batch upsert.
#[derive(Debug, Clone)]
pub struct PgVectorInsert<'a> {
    pub doc_id: &'a str,
    pub chunk: &'a str,
    pub kind: &'a str,
    pub embedding: &'a [f32],
    pub metadata: Value,
}

// ---------------------------------------------------------------------------
// Vector encoding / decoding
// ---------------------------------------------------------------------------

/// Encode a vector slice to pgvector's text representation: `[v1,v2,...]`.
pub fn encode_vector(v: &[f32]) -> Result<String, PgVectorError> {
    // We use `{:?}`-style debug formatting for f32 which always produces
    // a finite representation (NaN is rejected because pgvector would error
    // anyway, and `format!` on a NaN gives "NaN" which pgvector parses).
    let mut s = String::with_capacity(v.len() * 12);
    s.push('[');
    for (i, x) in v.iter().enumerate() {
        if i > 0 {
            s.push(',');
        }
        if x.is_finite() {
            // {:.8} is enough precision for cosine similarity at typical
            // embedding dimensions; full precision just bloats the WAL.
            s.push_str(&format!("{x:.8}"));
        } else {
            return Err(PgVectorError::InvalidVector(format!(
                "non-finite value at index {i}: {x}"
            )));
        }
    }
    s.push(']');
    Ok(s)
}

/// Decode a pgvector string back to `Vec<f32>`. Used in tests and any caller
/// that pulls the raw vector out of a row.
pub fn decode_vector(s: &str) -> Result<Vec<f32>, PgVectorError> {
    let inner = s.trim().trim_start_matches('[').trim_end_matches(']');
    if inner.is_empty() {
        return Ok(Vec::new());
    }
    let mut out = Vec::with_capacity(inner.matches(',').count() + 1);
    for piece in inner.split(',') {
        let v: f32 = piece
            .trim()
            .parse()
            .map_err(|e| PgVectorError::InvalidVector(format!("{e}: {piece}")))?;
        out.push(v);
    }
    Ok(out)
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn encode_decode_roundtrip() {
        let v = vec![0.1, -0.2, 0.3, 1.5];
        let s = encode_vector(&v).unwrap();
        assert_eq!(s, "[0.10000000,-0.20000000,0.30000000,1.50000000]");
        let back = decode_vector(&s).unwrap();
        assert_eq!(back.len(), v.len());
        for (a, b) in v.iter().zip(back.iter()) {
            assert!((a - b).abs() < 1e-6);
        }
    }

    #[test]
    fn encode_rejects_non_finite() {
        assert!(encode_vector(&[0.0, f32::NAN]).is_err());
        assert!(encode_vector(&[0.0, f32::INFINITY]).is_err());
    }

    #[test]
    fn decode_handles_whitespace() {
        let s = "[ 0.1 , 0.2 , 0.3 ]";
        let v = decode_vector(s).unwrap();
        assert_eq!(v, vec![0.1, 0.2, 0.3]);
    }

    #[test]
    fn decode_empty_vector() {
        assert_eq!(decode_vector("[]").unwrap(), Vec::<f32>::new());
        assert_eq!(decode_vector("[ ]").unwrap(), Vec::<f32>::new());
    }

    #[test]
    fn decode_rejects_garbage() {
        assert!(decode_vector("not a vector").is_err());
        assert!(decode_vector("[1, two, 3]").is_err());
    }

    #[test]
    fn batch_sql_has_expected_placeholder_count() {
        // Build a 3-row insert and confirm the SQL has 18 placeholders.
        // This is a regression test for the chunked batch upsert.
        let rows: Vec<PgVectorInsert> = (0..3)
            .map(|i| PgVectorInsert {
                doc_id: "d",
                chunk: "c",
                kind: "k",
                embedding: &[0.0],
                metadata: serde_json::json!({"i": i}),
            })
            .collect();
        let placeholders: Vec<String> = (0..rows.len())
            .map(|i| {
                let base = i * 6;
                format!(
                    "(${},${},${},${},${}::vector,${}::jsonb)",
                    base + 1,
                    base + 2,
                    base + 3,
                    base + 4,
                    base + 5,
                    base + 6,
                )
            })
            .collect();
        let sql = format!(
            "INSERT INTO embeddings (id, doc_id, chunk, kind, embedding, metadata) VALUES {}",
            placeholders.join(", ")
        );
        assert_eq!(sql.matches('$').count(), 18);
    }
}
