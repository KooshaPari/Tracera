//! Backend-agnostic persistence for durable product observations.
//!
//! The SQLite and PostgreSQL stores previously carried byte-for-byte near
//! copies of the same ingest and read logic (131 lines each, 36 differing).
//! This module holds that logic once. Each backend supplies only the SQL text
//! it needs, because the placeholder style (`?` vs `$1`), the locking clause
//! (`FOR UPDATE`), and the upsert form differ per database.
//!
//! Behaviour is preserved exactly: every backend keeps its own SQL, so
//! SQLite still issues a plain `INSERT` (whose unique violation surfaces as
//! [`StoreError::Database`] exactly as before) while PostgreSQL keeps
//! `ON CONFLICT DO NOTHING` plus the `rows_affected()` check that turns a
//! lost insert race into [`StoreError::Conflict`].

use crate::{
    product::persistence::*,
    store::{StoreError, StoreResult},
};
use sqlx::{Database, Row};

/// Every statement the shared ingest and read paths need, written for one
/// specific database.
#[derive(Clone, Copy)]
pub(crate) struct ObservationSql {
    pub upsert_baseline: &'static str,
    pub select_baseline_intents: &'static str,
    pub select_batch: &'static str,
    pub select_observation: &'static str,
    pub insert_observation: &'static str,
    pub count_observations: &'static str,
    pub insert_batch: &'static str,
    pub read_intents: &'static str,
    pub read_rows: &'static str,
}

fn invalid(message: impl Into<String>) -> StoreError {
    StoreError::Database(message.into())
}

fn encoded<T: serde::Serialize>(value: &T) -> StoreResult<String> {
    serde_json::to_string(value).map_err(|e| invalid(e.to_string()))
}

/// Number of rows a write touched.
///
/// sqlx 0.9 exposes `rows_affected` only as an inherent method on each
/// driver's own result type — there is no generic trait — so this adapts the
/// two backends to one bound the shared code can require.
pub(crate) trait AffectedRows {
    fn affected_rows(&self) -> u64;
}

impl AffectedRows for sqlx::postgres::PgQueryResult {
    fn affected_rows(&self) -> u64 {
        sqlx::postgres::PgQueryResult::rows_affected(self)
    }
}

impl AffectedRows for sqlx::sqlite::SqliteQueryResult {
    fn affected_rows(&self) -> u64 {
        sqlx::sqlite::SqliteQueryResult::rows_affected(self)
    }
}

/// Atomically persist one observation batch, honouring idempotency keys and
/// immutable evidence.
pub(crate) async fn ingest<DB>(
    pool: &sqlx::Pool<DB>,
    sql: ObservationSql,
    mut batch: ProductObservationBatch,
) -> StoreResult<ProductIngestReceipt>
where
    DB: Database,
    for<'c> &'c mut DB::Connection: sqlx::Executor<'c, Database = DB>,
    for<'c> &'c sqlx::Pool<DB>: sqlx::Executor<'c, Database = DB>,
    DB::Arguments: sqlx::IntoArguments<DB>,
    DB::QueryResult: AffectedRows,
    for<'r> usize: sqlx::ColumnIndex<DB::Row>,
    for<'r> String: sqlx::Decode<'r, DB> + sqlx::Encode<'r, DB> + sqlx::Type<DB>,
    for<'r> Option<String>: sqlx::Encode<'r, DB> + sqlx::Type<DB>,
    for<'r> i64: sqlx::Decode<'r, DB> + sqlx::Encode<'r, DB> + sqlx::Type<DB>,
    for<'r> i32: sqlx::Decode<'r, DB> + sqlx::Encode<'r, DB> + sqlx::Type<DB>,
    for<'r> &'r str: sqlx::Encode<'r, DB> + sqlx::Type<DB> + sqlx::ColumnIndex<DB::Row>,
{
    batch.validate().map_err(invalid)?;
    batch.intents.sort_by(|a, b| a.id.cmp(&b.id));
    batch.observations.sort_by(|a, b| a.id.cmp(&b.id));
    let product = batch.product_id.as_str();
    let baseline = batch.baseline.number() as i64;
    let payload = encoded(&batch)?;
    let intents = encoded(&batch.intents)?;
    let mut tx = pool.begin().await?;
    // Serialize writers on this product baseline, including first creation.
    sqlx::query::<DB>(sql.upsert_baseline)
        .bind(product)
        .bind(baseline)
        .bind(&intents)
        .execute(&mut *tx)
        .await?;
    let existing: String = sqlx::query_scalar::<DB, String>(sql.select_baseline_intents)
        .bind(product)
        .bind(baseline)
        .fetch_one(&mut *tx)
        .await?;
    if existing != intents {
        return Err(StoreError::Conflict(
            "accepted baseline intents are immutable".into(),
        ));
    }
    let replay: Option<String> = sqlx::query_scalar::<DB, String>(sql.select_batch)
        .bind(product)
        .bind(baseline)
        .bind(batch.idempotency_key.clone())
        .fetch_optional(&mut *tx)
        .await?;
    if let Some(previous) = replay {
        if previous != payload {
            return Err(StoreError::Conflict(
                "idempotency key conflicts with stored batch".into(),
            ));
        }
        tx.commit().await?;
        return Ok(ProductIngestReceipt {
            accepted: 0,
            replayed: true,
        });
    }
    let mut accepted = 0;
    for observation in &batch.observations {
        let value = encoded(observation)?;
        let previous: Option<String> = sqlx::query_scalar::<DB, String>(sql.select_observation)
            .bind(product)
            .bind(observation.id.clone())
            .fetch_optional(&mut *tx)
            .await?;
        if let Some(previous) = previous {
            if previous != value {
                return Err(StoreError::Conflict(
                    "observation identity conflicts with immutable evidence".into(),
                ));
            }
        } else {
            let inserted = sqlx::query::<DB>(sql.insert_observation)
                .bind(product)
                .bind(observation.id.clone())
                .bind(baseline)
                .bind(observation.capability_id.clone())
                .bind(value)
                .execute(&mut *tx)
                .await?;
            if inserted.affected_rows() == 0 {
                return Err(StoreError::Conflict(
                    "observation identity conflicts with immutable evidence".into(),
                ));
            }
            accepted += 1;
        }
    }
    let count: i64 = sqlx::query_scalar::<DB, i64>(sql.count_observations)
        .bind(product)
        .bind(baseline)
        .fetch_one(&mut *tx)
        .await?;
    if count > 5000 {
        return Err(StoreError::Conflict(
            "baseline observation limit exceeded (5000)".into(),
        ));
    }
    sqlx::query::<DB>(sql.insert_batch)
        .bind(product)
        .bind(baseline)
        .bind(batch.idempotency_key)
        .bind(payload)
        .execute(&mut *tx)
        .await?;
    tx.commit().await?;
    Ok(ProductIngestReceipt {
        accepted,
        replayed: false,
    })
}

/// Read one bounded observation model, or `None` when the baseline is absent.
pub(crate) async fn read<DB>(
    pool: &sqlx::Pool<DB>,
    sql: ObservationSql,
    product: String,
    baseline: u64,
) -> StoreResult<Option<ProductObservationModel>>
where
    DB: Database,
    for<'c> &'c sqlx::Pool<DB>: sqlx::Executor<'c, Database = DB>,
    DB::Arguments: sqlx::IntoArguments<DB>,
    for<'r> usize: sqlx::ColumnIndex<DB::Row>,
    for<'r> String: sqlx::Decode<'r, DB> + sqlx::Encode<'r, DB> + sqlx::Type<DB>,
    for<'r> i64: sqlx::Decode<'r, DB> + sqlx::Encode<'r, DB> + sqlx::Type<DB>,
    for<'r> &'r str: sqlx::Encode<'r, DB> + sqlx::Type<DB> + sqlx::ColumnIndex<DB::Row>,
{
    if baseline > i64::MAX as u64 {
        return Err(invalid("baseline exceeds supported range"));
    }
    let intents: Option<String> = sqlx::query_scalar::<DB, String>(sql.read_intents)
        .bind(&product)
        .bind(baseline as i64)
        .fetch_optional(pool)
        .await?;
    let Some(intents) = intents else {
        return Ok(None);
    };
    let rows = sqlx::query::<DB>(sql.read_rows)
        .bind(&product)
        .bind(baseline as i64)
        .fetch_all(pool)
        .await?;
    if rows.len() > 5000 {
        return Err(invalid("baseline exceeds supported bounded model size"));
    }
    let observations = rows
        .iter()
        .map(|row| {
            let payload: String = row.try_get("payload")?;
            serde_json::from_str(&payload).map_err(|e| invalid(e.to_string()))
        })
        .collect::<StoreResult<Vec<_>>>()?;
    Ok(Some(ProductObservationModel {
        product_id: crate::product::ProductId::new(product),
        baseline: crate::product::BaselineRevision(baseline),
        intents: serde_json::from_str(&intents).map_err(|e| invalid(e.to_string()))?,
        observations,
    }))
}
