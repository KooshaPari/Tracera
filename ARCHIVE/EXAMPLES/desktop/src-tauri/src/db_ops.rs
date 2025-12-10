use tauri::AppHandle;
use anyhow::Result;
use rusqlite::{Connection, params};
use crate::models::*;
use crate::db::get_db_path;
use chrono::Utc;

pub struct Database {
    conn: Connection,
}

impl Database {
    pub fn new(app_handle: &AppHandle) -> Result<Self> {
        let db_path = get_db_path(app_handle)?;
        let conn = Connection::open(db_path)?;
        Ok(Self { conn })
    }

    // Project operations
    pub fn create_project(&self, project: &Project) -> Result<()> {
        self.conn.execute(
            "INSERT INTO projects (id, name, description, created_at, updated_at, synced_at, is_deleted)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            params![
                &project.id,
                &project.name,
                &project.description,
                &project.created_at.to_rfc3339(),
                &project.updated_at.to_rfc3339(),
                project.synced_at.map(|dt| dt.to_rfc3339()),
                project.is_deleted,
            ],
        )?;
        Ok(())
    }

    pub fn get_project(&self, id: &str) -> Result<Option<Project>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, name, description, created_at, updated_at, synced_at, is_deleted
             FROM projects WHERE id = ?1 AND is_deleted = 0"
        )?;

        let project = stmt.query_row(params![id], |row| {
            Ok(Project {
                id: row.get(0)?,
                name: row.get(1)?,
                description: row.get(2)?,
                created_at: row.get::<_, String>(3)?.parse().unwrap(),
                updated_at: row.get::<_, String>(4)?.parse().unwrap(),
                synced_at: row.get::<_, Option<String>>(5)?.map(|s| s.parse().unwrap()),
                is_deleted: row.get(6)?,
            })
        }).optional()?;

        Ok(project)
    }

    pub fn list_projects(&self) -> Result<Vec<Project>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, name, description, created_at, updated_at, synced_at, is_deleted
             FROM projects WHERE is_deleted = 0 ORDER BY updated_at DESC"
        )?;

        let projects = stmt.query_map([], |row| {
            Ok(Project {
                id: row.get(0)?,
                name: row.get(1)?,
                description: row.get(2)?,
                created_at: row.get::<_, String>(3)?.parse().unwrap(),
                updated_at: row.get::<_, String>(4)?.parse().unwrap(),
                synced_at: row.get::<_, Option<String>>(5)?.map(|s| s.parse().unwrap()),
                is_deleted: row.get(6)?,
            })
        })?.collect::<Result<Vec<_>, _>>()?;

        Ok(projects)
    }

    pub fn update_project(&self, project: &Project) -> Result<()> {
        self.conn.execute(
            "UPDATE projects SET name = ?1, description = ?2, updated_at = ?3 WHERE id = ?4",
            params![
                &project.name,
                &project.description,
                &Utc::now().to_rfc3339(),
                &project.id,
            ],
        )?;
        Ok(())
    }

    pub fn delete_project(&self, id: &str) -> Result<()> {
        self.conn.execute(
            "UPDATE projects SET is_deleted = 1, updated_at = ?1 WHERE id = ?2",
            params![&Utc::now().to_rfc3339(), id],
        )?;
        Ok(())
    }

    // Item operations
    pub fn create_item(&self, item: &Item) -> Result<()> {
        self.conn.execute(
            "INSERT INTO items (id, project_id, item_type, title, content, status, priority, version, created_at, updated_at, synced_at, is_deleted)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12)",
            params![
                &item.id,
                &item.project_id,
                item.item_type.as_str(),
                &item.title,
                &item.content,
                &item.status,
                &item.priority,
                &item.version,
                &item.created_at.to_rfc3339(),
                &item.updated_at.to_rfc3339(),
                item.synced_at.map(|dt| dt.to_rfc3339()),
                item.is_deleted,
            ],
        )?;
        Ok(())
    }

    pub fn get_item(&self, id: &str) -> Result<Option<Item>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, project_id, item_type, title, content, status, priority, version, created_at, updated_at, synced_at, is_deleted
             FROM items WHERE id = ?1 AND is_deleted = 0"
        )?;

        let item = stmt.query_row(params![id], |row| {
            let item_type_str: String = row.get(2)?;
            Ok(Item {
                id: row.get(0)?,
                project_id: row.get(1)?,
                item_type: ItemType::from_str(&item_type_str).unwrap(),
                title: row.get(3)?,
                content: row.get(4)?,
                status: row.get(5)?,
                priority: row.get(6)?,
                version: row.get(7)?,
                created_at: row.get::<_, String>(8)?.parse().unwrap(),
                updated_at: row.get::<_, String>(9)?.parse().unwrap(),
                synced_at: row.get::<_, Option<String>>(10)?.map(|s| s.parse().unwrap()),
                is_deleted: row.get(11)?,
            })
        }).optional()?;

        Ok(item)
    }

    pub fn list_items(&self, project_id: &str, item_type: Option<ItemType>) -> Result<Vec<Item>> {
        let query = if let Some(it) = item_type {
            format!(
                "SELECT id, project_id, item_type, title, content, status, priority, version, created_at, updated_at, synced_at, is_deleted
                 FROM items WHERE project_id = ?1 AND item_type = ?2 AND is_deleted = 0 ORDER BY updated_at DESC"
            )
        } else {
            format!(
                "SELECT id, project_id, item_type, title, content, status, priority, version, created_at, updated_at, synced_at, is_deleted
                 FROM items WHERE project_id = ?1 AND is_deleted = 0 ORDER BY updated_at DESC"
            )
        };

        let mut stmt = self.conn.prepare(&query)?;

        let items = if let Some(it) = item_type {
            stmt.query_map(params![project_id, it.as_str()], |row| {
                let item_type_str: String = row.get(2)?;
                Ok(Item {
                    id: row.get(0)?,
                    project_id: row.get(1)?,
                    item_type: ItemType::from_str(&item_type_str).unwrap(),
                    title: row.get(3)?,
                    content: row.get(4)?,
                    status: row.get(5)?,
                    priority: row.get(6)?,
                    version: row.get(7)?,
                    created_at: row.get::<_, String>(8)?.parse().unwrap(),
                    updated_at: row.get::<_, String>(9)?.parse().unwrap(),
                    synced_at: row.get::<_, Option<String>>(10)?.map(|s| s.parse().unwrap()),
                    is_deleted: row.get(11)?,
                })
            })?
        } else {
            stmt.query_map(params![project_id], |row| {
                let item_type_str: String = row.get(2)?;
                Ok(Item {
                    id: row.get(0)?,
                    project_id: row.get(1)?,
                    item_type: ItemType::from_str(&item_type_str).unwrap(),
                    title: row.get(3)?,
                    content: row.get(4)?,
                    status: row.get(5)?,
                    priority: row.get(6)?,
                    version: row.get(7)?,
                    created_at: row.get::<_, String>(8)?.parse().unwrap(),
                    updated_at: row.get::<_, String>(9)?.parse().unwrap(),
                    synced_at: row.get::<_, Option<String>>(10)?.map(|s| s.parse().unwrap()),
                    is_deleted: row.get(11)?,
                })
            })?
        }.collect::<Result<Vec<_>, _>>()?;

        Ok(items)
    }

    pub fn update_item(&self, item: &Item) -> Result<()> {
        self.conn.execute(
            "UPDATE items SET title = ?1, content = ?2, status = ?3, priority = ?4, version = version + 1, updated_at = ?5 WHERE id = ?6",
            params![
                &item.title,
                &item.content,
                &item.status,
                &item.priority,
                &Utc::now().to_rfc3339(),
                &item.id,
            ],
        )?;
        Ok(())
    }

    pub fn delete_item(&self, id: &str) -> Result<()> {
        self.conn.execute(
            "UPDATE items SET is_deleted = 1, updated_at = ?1 WHERE id = ?2",
            params![&Utc::now().to_rfc3339(), id],
        )?;
        Ok(())
    }

    // Link operations
    pub fn create_link(&self, link: &Link) -> Result<()> {
        self.conn.execute(
            "INSERT INTO links (id, project_id, source_id, target_id, link_type, metadata, created_at, is_deleted)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![
                &link.id,
                &link.project_id,
                &link.source_id,
                &link.target_id,
                &link.link_type,
                &link.metadata,
                &link.created_at.to_rfc3339(),
                link.is_deleted,
            ],
        )?;
        Ok(())
    }

    pub fn list_links(&self, project_id: &str) -> Result<Vec<Link>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, project_id, source_id, target_id, link_type, metadata, created_at, is_deleted
             FROM links WHERE project_id = ?1 AND is_deleted = 0"
        )?;

        let links = stmt.query_map(params![project_id], |row| {
            Ok(Link {
                id: row.get(0)?,
                project_id: row.get(1)?,
                source_id: row.get(2)?,
                target_id: row.get(3)?,
                link_type: row.get(4)?,
                metadata: row.get(5)?,
                created_at: row.get::<_, String>(6)?.parse().unwrap(),
                is_deleted: row.get(7)?,
            })
        })?.collect::<Result<Vec<_>, _>>()?;

        Ok(links)
    }

    pub fn delete_link(&self, id: &str) -> Result<()> {
        self.conn.execute(
            "UPDATE links SET is_deleted = 1 WHERE id = ?1",
            params![id],
        )?;
        Ok(())
    }

    // Sync queue operations
    pub fn add_to_sync_queue(&self, entity_type: &str, entity_id: &str, operation: OperationType, payload: &str) -> Result<()> {
        self.conn.execute(
            "INSERT INTO sync_queue (entity_type, entity_id, operation, payload, created_at, retry_count)
             VALUES (?1, ?2, ?3, ?4, ?5, 0)",
            params![
                entity_type,
                entity_id,
                operation.as_str(),
                payload,
                &Utc::now().to_rfc3339(),
            ],
        )?;
        Ok(())
    }

    pub fn get_pending_sync_items(&self) -> Result<Vec<SyncQueueItem>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, entity_type, entity_id, operation, payload, created_at, retry_count
             FROM sync_queue ORDER BY created_at ASC LIMIT 100"
        )?;

        let items = stmt.query_map([], |row| {
            let operation_str: String = row.get(3)?;
            let operation = match operation_str.as_str() {
                "create" => OperationType::Create,
                "update" => OperationType::Update,
                "delete" => OperationType::Delete,
                _ => OperationType::Update,
            };

            Ok(SyncQueueItem {
                id: row.get(0)?,
                entity_type: row.get(1)?,
                entity_id: row.get(2)?,
                operation,
                payload: row.get(4)?,
                created_at: row.get::<_, String>(5)?.parse().unwrap(),
                retry_count: row.get(6)?,
            })
        })?.collect::<Result<Vec<_>, _>>()?;

        Ok(items)
    }

    pub fn remove_from_sync_queue(&self, id: i64) -> Result<()> {
        self.conn.execute("DELETE FROM sync_queue WHERE id = ?1", params![id])?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_database_operations() {
        let conn = Connection::open_in_memory().unwrap();

        conn.execute_batch(
            r#"
            CREATE TABLE projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                synced_at TEXT,
                is_deleted INTEGER DEFAULT 0
            );
            "#,
        ).unwrap();

        let now = Utc::now();
        conn.execute(
            "INSERT INTO projects (id, name, description, created_at, updated_at, is_deleted)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            params!["test-id", "Test Project", Some("Test Description"), now.to_rfc3339(), now.to_rfc3339(), 0],
        ).unwrap();

        let count: i64 = conn.query_row("SELECT COUNT(*) FROM projects", [], |row| row.get(0)).unwrap();
        assert_eq!(count, 1);
    }
}
