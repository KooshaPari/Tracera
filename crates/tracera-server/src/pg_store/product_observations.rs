//! PostgreSQL backend for durable product observations.
//!
//! Only the SQL differs from the SQLite backend: `$1`-style placeholders, the
//! `FOR UPDATE` row lock on the baseline read, and an `ON CONFLICT DO NOTHING`
//! insert whose `rows_affected()` check turns a lost insert race into
//! [`StoreError::Conflict`]. All control flow lives in
//! [`crate::observation_store`].

use crate::observation_store as shared;
use crate::{observation_store::ObservationSql, product::persistence::*, store::StoreResult};
use sqlx::PgPool;

const SQL: ObservationSql = ObservationSql {
    upsert_baseline: "INSERT INTO product_observation_baselines (product_id, baseline, intents) VALUES ($1,$2,$3) ON CONFLICT(product_id,baseline) DO NOTHING",
    select_baseline_intents: "SELECT intents FROM product_observation_baselines WHERE product_id=$1 AND baseline=$2 FOR UPDATE",
    select_batch: "SELECT payload FROM product_observation_batches WHERE product_id=$1 AND baseline=$2 AND batch_key=$3",
    select_observation: "SELECT payload FROM product_observations WHERE product_id=$1 AND observation_id=$2",
    insert_observation: "INSERT INTO product_observations (product_id,observation_id,baseline,capability_id,payload) VALUES ($1,$2,$3,$4,$5) ON CONFLICT (product_id, observation_id) DO NOTHING",
    count_observations: "SELECT COUNT(*) FROM product_observations WHERE product_id=$1 AND baseline=$2",
    insert_batch: "INSERT INTO product_observation_batches (product_id,baseline,batch_key,payload) VALUES ($1,$2,$3,$4)",
    read_intents: "SELECT intents FROM product_observation_baselines WHERE product_id=$1 AND baseline=$2",
    read_rows: "SELECT payload FROM product_observations WHERE product_id=$1 AND baseline=$2 ORDER BY observation_id LIMIT 5001",
};

pub async fn ingest(
    pool: &PgPool,
    batch: ProductObservationBatch,
) -> StoreResult<ProductIngestReceipt> {
    shared::ingest(pool, SQL, batch).await
}

pub async fn read(
    pool: &PgPool,
    product: String,
    baseline: u64,
) -> StoreResult<Option<ProductObservationModel>> {
    shared::read(pool, SQL, product, baseline).await
}
