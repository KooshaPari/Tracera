use crate::store::{CanonicalExport, CanonicalItem, CanonicalLink, CanonicalProject, StoreResult};
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
