use crate::{
    item::{Item, ItemFilter, ItemPage},
    store::{StoreError, StoreResult},
};
use sqlx::{QueryBuilder, Sqlite, SqlitePool};

fn filtered(prefix: &'static str, filter: &ItemFilter) -> QueryBuilder<Sqlite> {
    let mut query = QueryBuilder::new(prefix);
    query.push(" WHERE 1=1");
    for (column, value) in [
        ("project_id", &filter.project_id),
        ("status", &filter.status),
        ("view", &filter.view),
        ("priority", &filter.priority),
    ] {
        if let Some(value) = value {
            query
                .push(" AND ")
                .push(column)
                .push(" = ")
                .push_bind(value);
        }
    }
    query
}

pub(super) async fn list(
    pool: &SqlitePool,
    filter: ItemFilter,
    limit: i64,
    offset: i64,
) -> StoreResult<ItemPage> {
    let mut transaction = pool.begin().await?;
    let total = filtered("SELECT COUNT(*) FROM items", &filter)
        .build_query_scalar::<i64>()
        .fetch_one(&mut *transaction)
        .await?;
    let mut query = filtered("SELECT document FROM items", &filter);
    query
        .push(" ORDER BY id ASC LIMIT ")
        .push_bind(limit)
        .push(" OFFSET ")
        .push_bind(offset);
    let documents = query
        .build_query_scalar::<String>()
        .fetch_all(&mut *transaction)
        .await?;
    transaction.commit().await?;
    let items = documents
        .into_iter()
        .map(|document| decode(&document))
        .collect::<StoreResult<_>>()?;
    Ok(ItemPage { items, total })
}

fn decode(document: &str) -> StoreResult<Item> {
    serde_json::from_str(document).map_err(|e| StoreError::Database(e.to_string()))
}

pub(super) async fn get(pool: &SqlitePool, id: String) -> StoreResult<Option<Item>> {
    let mut query = QueryBuilder::<Sqlite>::new("SELECT document FROM items WHERE id = ");
    query.push_bind(id);
    query
        .build_query_scalar::<String>()
        .fetch_optional(pool)
        .await?
        .map(|document| decode(&document))
        .transpose()
}

pub(super) async fn create(pool: &SqlitePool, item: Item) -> StoreResult<()> {
    let document = serde_json::to_string(&item).map_err(|e| StoreError::Database(e.to_string()))?;
    let mut query = QueryBuilder::<Sqlite>::new(
        "INSERT INTO items (id, project_id, status, view, priority, document) VALUES (",
    );
    let mut values = query.separated(", ");
    values
        .push_bind(item.id)
        .push_bind(item.project_id)
        .push_bind(item.status)
        .push_bind(item.view)
        .push_bind(item.priority)
        .push_bind(document);
    query.push(")");
    query.build().execute(pool).await?;
    Ok(())
}
