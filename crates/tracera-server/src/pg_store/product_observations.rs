use crate::{
    product::persistence::*,
    store::{StoreError, StoreResult},
};
use sqlx::{PgPool, Row};
fn invalid(message: impl Into<String>) -> StoreError {
    StoreError::Database(message.into())
}
fn encoded<T: serde::Serialize>(value: &T) -> StoreResult<String> {
    serde_json::to_string(value).map_err(|e| invalid(e.to_string()))
}
pub async fn ingest(
    pool: &PgPool,
    mut batch: ProductObservationBatch,
) -> StoreResult<ProductIngestReceipt> {
    batch.validate().map_err(invalid)?;
    batch.intents.sort_by(|a, b| a.id.cmp(&b.id));
    batch.observations.sort_by(|a, b| a.id.cmp(&b.id));
    let product = batch.product_id.as_str();
    let baseline = batch.baseline.number() as i64;
    let payload = encoded(&batch)?;
    let intents = encoded(&batch.intents)?;
    let mut tx = pool.begin().await?;
    // Serialize writers on this product baseline, including first creation.
    sqlx::query("INSERT INTO product_observation_baselines (product_id, baseline, intents) VALUES ($1,$2,$3) ON CONFLICT(product_id,baseline) DO NOTHING")
        .bind(product).bind(baseline).bind(&intents).execute(&mut *tx).await?;
    let existing: String = sqlx::query_scalar("SELECT intents FROM product_observation_baselines WHERE product_id=$1 AND baseline=$2 FOR UPDATE")
        .bind(product).bind(baseline).fetch_one(&mut *tx).await?;
    if existing != intents {
        return Err(StoreError::Conflict(
            "accepted baseline intents are immutable".into(),
        ));
    }
    let replay: Option<String> = sqlx::query_scalar("SELECT payload FROM product_observation_batches WHERE product_id=$1 AND baseline=$2 AND batch_key=$3")
        .bind(product).bind(baseline).bind(&batch.idempotency_key).fetch_optional(&mut *tx).await?;
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
        let previous: Option<String> = sqlx::query_scalar(
            "SELECT payload FROM product_observations WHERE product_id=$1 AND observation_id=$2",
        )
        .bind(product)
        .bind(&observation.id)
        .fetch_optional(&mut *tx)
        .await?;
        if let Some(previous) = previous {
            if previous != value {
                return Err(StoreError::Conflict(
                    "observation identity conflicts with immutable evidence".into(),
                ));
            }
        } else {
            sqlx::query("INSERT INTO product_observations (product_id,observation_id,baseline,capability_id,payload) VALUES ($1,$2,$3,$4,$5)")
                .bind(product).bind(&observation.id).bind(baseline).bind(&observation.capability_id).bind(value).execute(&mut *tx).await?;
            accepted += 1;
        }
    }
    let count: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM product_observations WHERE product_id=$1 AND baseline=$2",
    )
    .bind(product)
    .bind(baseline)
    .fetch_one(&mut *tx)
    .await?;
    if count > 5000 {
        return Err(StoreError::Conflict(
            "baseline observation limit exceeded (5000)".into(),
        ));
    }
    sqlx::query("INSERT INTO product_observation_batches (product_id,baseline,batch_key,payload) VALUES ($1,$2,$3,$4)")
        .bind(product).bind(baseline).bind(batch.idempotency_key).bind(payload).execute(&mut *tx).await?;
    tx.commit().await?;
    Ok(ProductIngestReceipt {
        accepted,
        replayed: false,
    })
}
pub async fn read(
    pool: &PgPool,
    product: String,
    baseline: u64,
) -> StoreResult<Option<ProductObservationModel>> {
    if baseline > i64::MAX as u64 {
        return Err(invalid("baseline exceeds supported range"));
    }
    let intents: Option<String> = sqlx::query_scalar(
        "SELECT intents FROM product_observation_baselines WHERE product_id=$1 AND baseline=$2",
    )
    .bind(&product)
    .bind(baseline as i64)
    .fetch_optional(pool)
    .await?;
    let Some(intents) = intents else {
        return Ok(None);
    };
    let rows = sqlx::query("SELECT payload FROM product_observations WHERE product_id=$1 AND baseline=$2 ORDER BY observation_id LIMIT 5001")
        .bind(&product).bind(baseline as i64).fetch_all(pool).await?;
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
