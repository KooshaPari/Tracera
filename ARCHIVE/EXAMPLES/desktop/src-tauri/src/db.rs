use tauri::AppHandle;
use anyhow::Result;
use std::path::PathBuf;
use rusqlite::{Connection, params};
use crate::models::*;

pub fn init_db(app_handle: &AppHandle) -> Result<()> {
    let app_dir = app_handle.path().app_data_dir()?;
    let db_path = app_dir.join("tracertm.db");

    log::info!("Initializing database at: {:?}", db_path);

    // Create app data directory if it doesn't exist
    if !app_dir.exists() {
        std::fs::create_dir_all(&app_dir)?;
    }

    // Initialize SQLite database
    let conn = Connection::open(&db_path)?;

    // Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON", [])?;

    // Create tables
    conn.execute_batch(
        r#"
        -- Projects table
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            synced_at TEXT,
            is_deleted INTEGER DEFAULT 0
        );

        -- Items table (unified for all item types)
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT,
            version INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            synced_at TEXT,
            is_deleted INTEGER DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        -- Links table (traceability relationships)
        CREATE TABLE IF NOT EXISTS links (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            link_type TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT NOT NULL,
            is_deleted INTEGER DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (source_id) REFERENCES items(id) ON DELETE CASCADE,
            FOREIGN KEY (target_id) REFERENCES items(id) ON DELETE CASCADE
        );

        -- Agents table
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            config TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            synced_at TEXT,
            is_deleted INTEGER DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        -- Sync queue for offline changes
        CREATE TABLE IF NOT EXISTS sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            operation TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL,
            retry_count INTEGER DEFAULT 0
        );

        -- Attachments table
        CREATE TABLE IF NOT EXISTS attachments (
            id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            mime_type TEXT,
            created_at TEXT NOT NULL,
            synced_at TEXT,
            is_deleted INTEGER DEFAULT 0
        );

        -- Conflict resolution table
        CREATE TABLE IF NOT EXISTS conflicts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            local_version TEXT NOT NULL,
            remote_version TEXT NOT NULL,
            created_at TEXT NOT NULL,
            resolved INTEGER DEFAULT 0
        );

        -- Create indices for performance
        CREATE INDEX IF NOT EXISTS idx_projects_updated ON projects(updated_at);
        CREATE INDEX IF NOT EXISTS idx_items_project ON items(project_id);
        CREATE INDEX IF NOT EXISTS idx_items_type ON items(item_type);
        CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
        CREATE INDEX IF NOT EXISTS idx_items_updated ON items(updated_at);
        CREATE INDEX IF NOT EXISTS idx_links_project ON links(project_id);
        CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_id);
        CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_id);
        CREATE INDEX IF NOT EXISTS idx_agents_project ON agents(project_id);
        CREATE INDEX IF NOT EXISTS idx_sync_queue_created ON sync_queue(created_at);
        CREATE INDEX IF NOT EXISTS idx_attachments_entity ON attachments(entity_type, entity_id);
        CREATE INDEX IF NOT EXISTS idx_conflicts_entity ON conflicts(entity_type, entity_id);
        "#,
    )?;

    log::info!("Database initialized successfully");

    Ok(())
}

pub fn get_db_path(app_handle: &AppHandle) -> Result<PathBuf> {
    let app_dir = app_handle.path().app_data_dir()?;
    Ok(app_dir.join("tracertm.db"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_db_schema() {
        let conn = rusqlite::Connection::open_in_memory().unwrap();

        let result = conn.execute_batch(
            r#"
            CREATE TABLE requirements (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                status TEXT NOT NULL
            );
            "#,
        );

        assert!(result.is_ok());
    }
}
