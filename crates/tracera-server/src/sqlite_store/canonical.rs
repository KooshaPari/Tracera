use crate::store::{
    CanonicalExport, CanonicalItem, CanonicalLink, CanonicalMutation, CanonicalProject, StoreResult,
};
use sqlx::{Row, SqlitePool};

pub(super) async fn import(pool: &SqlitePool, export: CanonicalExport) -> StoreResult<()> {
    let mut tx = pool.begin().await?;
    let created_at = export
        .project
        .created_at
        .as_deref()
        .and_then(|s| chrono::DateTime::parse_from_rfc3339(s).ok())
        .map(|d| d.to_rfc3339())
        .unwrap_or_else(|| chrono::Utc::now().to_rfc3339());
    sqlx::query("INSERT INTO canonical_projects (id,name,description,created_at,updated_at) VALUES (?1,?2,?3,?4,?4)")
        .bind(&export.project.id).bind(&export.project.name).bind(&export.project.description).bind(created_at)
        .execute(&mut *tx).await?;
    for item in &export.items {
        sqlx::query("INSERT INTO canonical_items (project_id,id,title,view,item_type,status,description,version,source_url,source_repo,source_kind) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11)")
            .bind(&export.project.id).bind(&item.id).bind(&item.title).bind(&item.view).bind(&item.item_type)
            .bind(&item.status).bind(&item.description).bind(item.version)
            .bind(&item.source_url).bind(&item.source_repo).bind(&item.source_kind)
            .execute(&mut *tx).await?;
    }
    for link in &export.links {
        sqlx::query("INSERT INTO canonical_links (project_id,source_id,target_id,link_type) VALUES (?1,?2,?3,?4)")
            .bind(&export.project.id).bind(&link.source_id).bind(&link.target_id).bind(&link.link_type)
            .execute(&mut *tx).await?;
    }
    tx.commit().await?;
    Ok(())
}

pub(super) async fn append(
    pool: &SqlitePool,
    project_id: &str,
    items: Vec<CanonicalItem>,
    links: Vec<CanonicalLink>,
) -> StoreResult<()> {
    let mut tx = pool.begin().await?;
    for item in &items {
        sqlx::query("INSERT INTO canonical_items (project_id,id,title,view,item_type,status,description,version,source_url,source_repo,source_kind) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11)")
            .bind(project_id).bind(&item.id).bind(&item.title).bind(&item.view).bind(&item.item_type)
            .bind(&item.status).bind(&item.description).bind(item.version)
            .bind(&item.source_url).bind(&item.source_repo).bind(&item.source_kind)
            .execute(&mut *tx).await?;
    }
    for link in &links {
        sqlx::query("INSERT INTO canonical_links (project_id,source_id,target_id,link_type) VALUES (?1,?2,?3,?4)")
            .bind(project_id).bind(&link.source_id).bind(&link.target_id).bind(&link.link_type)
            .execute(&mut *tx).await?;
    }
    tx.commit().await?;
    Ok(())
}

pub(super) async fn project(pool: &SqlitePool, id: &str) -> StoreResult<Option<CanonicalProject>> {
    let row =
        sqlx::query("SELECT id,name,description,created_at FROM canonical_projects WHERE id=?1")
            .bind(id)
            .fetch_optional(pool)
            .await?;
    Ok(row.map(|r| CanonicalProject {
        id: r.get("id"),
        name: r.get("name"),
        description: r.get("description"),
        created_at: Some(r.get("created_at")),
    }))
}

pub(super) async fn items(
    pool: &SqlitePool,
    id: &str,
    limit: i64,
    skip: i64,
) -> StoreResult<(Vec<CanonicalItem>, i64)> {
    let total: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM canonical_items WHERE project_id=?1")
        .bind(id)
        .fetch_one(pool)
        .await?;
    let rows = sqlx::query("SELECT id,title,view,item_type,status,description,version,source_url,source_repo,source_kind FROM canonical_items WHERE project_id=?1 ORDER BY id LIMIT ?2 OFFSET ?3")
        .bind(id).bind(limit).bind(skip).fetch_all(pool).await?;
    Ok((
        rows.into_iter()
            .map(|r| CanonicalItem {
                id: r.get("id"),
                title: r.get("title"),
                view: r.get("view"),
                item_type: r.get("item_type"),
                status: r.get("status"),
                description: r.get("description"),
                version: r.get("version"),
                source_url: r.get("source_url"),
                source_repo: r.get("source_repo"),
                source_kind: r.get("source_kind"),
            })
            .collect(),
        total,
    ))
}

pub(super) async fn item(
    pool: &SqlitePool,
    project_id: &str,
    item_id: &str,
) -> StoreResult<Option<CanonicalItem>> {
    let row = sqlx::query("SELECT id,title,view,item_type,status,description,version,source_url,source_repo,source_kind FROM canonical_items WHERE project_id=?1 AND id=?2")
        .bind(project_id)
        .bind(item_id)
        .fetch_optional(pool)
        .await?;
    Ok(row.map(|r| CanonicalItem {
        id: r.get("id"),
        title: r.get("title"),
        view: r.get("view"),
        item_type: r.get("item_type"),
        status: r.get("status"),
        description: r.get("description"),
        version: r.get("version"),
        source_url: r.get("source_url"),
        source_repo: r.get("source_repo"),
        source_kind: r.get("source_kind"),
    }))
}

pub(super) async fn links(
    pool: &SqlitePool,
    id: &str,
    limit: i64,
    skip: i64,
) -> StoreResult<(Vec<CanonicalLink>, i64)> {
    let total: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM canonical_links WHERE project_id=?1")
        .bind(id)
        .fetch_one(pool)
        .await?;
    let rows = sqlx::query("SELECT source_id,target_id,link_type FROM canonical_links WHERE project_id=?1 ORDER BY source_id,target_id,link_type LIMIT ?2 OFFSET ?3")
        .bind(id).bind(limit).bind(skip).fetch_all(pool).await?;
    Ok((
        rows.into_iter()
            .map(|r| CanonicalLink {
                source_id: r.get("source_id"),
                target_id: r.get("target_id"),
                link_type: r.get("link_type"),
            })
            .collect(),
        total,
    ))
}

pub(super) async fn export(pool: &SqlitePool, id: &str) -> StoreResult<Option<CanonicalExport>> {
    let Some(project) = project(pool, id).await? else {
        return Ok(None);
    };
    let (items, _) = items(pool, id, i64::MAX, 0).await?;
    let (links, _) = links(pool, id, i64::MAX, 0).await?;
    Ok(Some(CanonicalExport {
        project,
        items,
        links,
    }))
}

/// Lock the project before reading/updating an item. Concurrent edits to different
/// fields merge against the current row; missing fields retain source provenance.
pub(super) async fn mutate(
    pool: &SqlitePool,
    project_id: &str,
    mutation: CanonicalMutation,
) -> StoreResult<bool> {
    let mut tx = pool.begin().await?;
    let affected = sqlx::query("UPDATE canonical_projects SET updated_at=?2 WHERE id=?1")
        .bind(project_id)
        .bind(chrono::Utc::now().to_rfc3339())
        .execute(&mut *tx)
        .await?
        .rows_affected();
    if affected == 0 {
        return Ok(false);
    }
    let affected = match mutation {
        CanonicalMutation::CreateItem(item) => {
            sqlx::query("INSERT INTO canonical_items (project_id,id,title,view,item_type,status,description,version,source_url,source_repo,source_kind) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11)")
                .bind(project_id).bind(&item.id).bind(&item.title).bind(&item.view).bind(&item.item_type)
                .bind(&item.status).bind(&item.description).bind(item.version)
                .bind(&item.source_url).bind(&item.source_repo).bind(&item.source_kind)
                .execute(&mut *tx).await?.rows_affected()
        }
        CanonicalMutation::UpdateItem { id, patch } => {
            let row = sqlx::query("SELECT id,title,view,item_type,status,description,version,source_url,source_repo,source_kind FROM canonical_items WHERE project_id=?1 AND id=?2")
                .bind(project_id).bind(&id).fetch_optional(&mut *tx).await?;
            let Some(row) = row else { return Ok(false); };
            let item = CanonicalItem {
                id: row.get("id"), title: row.get("title"), view: row.get("view"),
                item_type: row.get("item_type"), status: row.get("status"),
                description: row.get("description"), version: row.get("version"),
                source_url: row.get("source_url"), source_repo: row.get("source_repo"), source_kind: row.get("source_kind"),
            };
            let mut merged = serde_json::to_value(item).map_err(|e| crate::store::StoreError::Database(e.to_string()))?;
            let fields = patch.as_object().ok_or_else(|| crate::store::StoreError::Database("invalid item patch".into()))?;
            for (key, value) in fields { merged[key] = value.clone(); }
            let item: CanonicalItem = serde_json::from_value(merged).map_err(|e| crate::store::StoreError::Database(e.to_string()))?;
            sqlx::query("UPDATE canonical_items SET title=?3,view=?4,item_type=?5,status=?6,description=?7,version=?8,source_url=?9,source_repo=?10,source_kind=?11 WHERE project_id=?1 AND id=?2")
                .bind(project_id).bind(&id).bind(&item.title).bind(&item.view).bind(&item.item_type)
                .bind(&item.status).bind(&item.description).bind(item.version)
                .bind(&item.source_url).bind(&item.source_repo).bind(&item.source_kind)
                .execute(&mut *tx).await?.rows_affected()
        }
        CanonicalMutation::DeleteItem(id) => {
            // ON DELETE CASCADE removes only this project's incident links.
            sqlx::query("DELETE FROM canonical_items WHERE project_id=?1 AND id=?2")
                .bind(project_id).bind(id).execute(&mut *tx).await?.rows_affected()
        }
        CanonicalMutation::CreateLink(link) => {
            sqlx::query("INSERT INTO canonical_links (project_id,source_id,target_id,link_type) VALUES (?1,?2,?3,?4)")
                .bind(project_id).bind(link.source_id).bind(link.target_id).bind(link.link_type)
                .execute(&mut *tx).await?.rows_affected()
        }
        CanonicalMutation::ReplaceLink { old, new } => {
            let removed = sqlx::query("DELETE FROM canonical_links WHERE project_id=?1 AND source_id=?2 AND target_id=?3 AND link_type=?4")
                .bind(project_id).bind(old.source_id).bind(old.target_id).bind(old.link_type)
                .execute(&mut *tx).await?.rows_affected();
            if removed == 0 { return Ok(false); }
            sqlx::query("INSERT INTO canonical_links (project_id,source_id,target_id,link_type) VALUES (?1,?2,?3,?4)")
                .bind(project_id).bind(new.source_id).bind(new.target_id).bind(new.link_type)
                .execute(&mut *tx).await?.rows_affected()
        }
        CanonicalMutation::DeleteLink(link) => {
            sqlx::query("DELETE FROM canonical_links WHERE project_id=?1 AND source_id=?2 AND target_id=?3 AND link_type=?4")
                .bind(project_id).bind(link.source_id).bind(link.target_id).bind(link.link_type)
                .execute(&mut *tx).await?.rows_affected()
        }
    };
    if affected == 0 {
        return Ok(false);
    }
    tx.commit().await?;
    Ok(true)
}
