//! SQLite backend for durable product observations.
//!
//! Only the SQL differs from the PostgreSQL backend: `?` placeholders, no row
//! locking clause, and a plain `INSERT` (a unique violation therefore surfaces
//! as [`StoreError::Database`], exactly as this module behaved before the
//! shared implementation in [`crate::observation_store`] existed).
//! All control flow lives there.

use crate::observation_store as shared;
use crate::{observation_store::ObservationSql, product::persistence::*, store::StoreResult};
use sqlx::SqlitePool;

const SQL: ObservationSql = ObservationSql {
    upsert_baseline: "INSERT INTO product_observation_baselines (product_id, baseline, intents) VALUES (?,?,?) ON CONFLICT(product_id,baseline) DO NOTHING",
    select_baseline_intents: "SELECT intents FROM product_observation_baselines WHERE product_id=? AND baseline=? ",
    select_batch: "SELECT payload FROM product_observation_batches WHERE product_id=? AND baseline=? AND batch_key=?",
    select_observation: "SELECT payload FROM product_observations WHERE product_id=? AND observation_id=?",
    insert_observation: "INSERT INTO product_observations (product_id,observation_id,baseline,capability_id,payload) VALUES (?,?,?,?,?)",
    count_observations: "SELECT COUNT(*) FROM product_observations WHERE product_id=? AND baseline=?",
    insert_batch: "INSERT INTO product_observation_batches (product_id,baseline,batch_key,payload) VALUES (?,?,?,?)",
    read_intents: "SELECT intents FROM product_observation_baselines WHERE product_id=? AND baseline=?",
    read_rows: "SELECT payload FROM product_observations WHERE product_id=? AND baseline=? ORDER BY observation_id LIMIT 5001",
};

pub async fn ingest(
    pool: &SqlitePool,
    batch: ProductObservationBatch,
) -> StoreResult<ProductIngestReceipt> {
    shared::ingest(pool, SQL, batch).await
}

pub async fn read(
    pool: &SqlitePool,
    product: String,
    baseline: u64,
) -> StoreResult<Option<ProductObservationModel>> {
    shared::read(pool, SQL, product, baseline).await
}
