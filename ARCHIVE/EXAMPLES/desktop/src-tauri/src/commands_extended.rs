use tauri::AppHandle;
use serde::{Deserialize, Serialize};
use crate::models::*;
use crate::db_ops::Database;
use crate::export::Exporter;
use crate::notifications::NotificationManager;
use chrono::Utc;
use uuid::Uuid;

// Project Commands
#[tauri::command]
pub async fn create_project(
    app: AppHandle,
    name: String,
    description: Option<String>,
) -> Result<Project, String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;

    let project = Project {
        id: Uuid::new_v4().to_string(),
        name,
        description,
        created_at: Utc::now(),
        updated_at: Utc::now(),
        synced_at: None,
        is_deleted: false,
    };

    db.create_project(&project).map_err(|e| e.to_string())?;

    // Add to sync queue
    let payload = serde_json::to_string(&project).map_err(|e| e.to_string())?;
    db.add_to_sync_queue("project", &project.id, OperationType::Create, &payload)
        .map_err(|e| e.to_string())?;

    log::info!("Project created: {} ({})", project.name, project.id);

    Ok(project)
}

#[tauri::command]
pub async fn get_project(app: AppHandle, id: String) -> Result<Option<Project>, String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;
    db.get_project(&id).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn list_projects(app: AppHandle) -> Result<Vec<Project>, String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;
    db.list_projects().map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn update_project(
    app: AppHandle,
    project: Project,
) -> Result<(), String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;
    db.update_project(&project).map_err(|e| e.to_string())?;

    // Add to sync queue
    let payload = serde_json::to_string(&project).map_err(|e| e.to_string())?;
    db.add_to_sync_queue("project", &project.id, OperationType::Update, &payload)
        .map_err(|e| e.to_string())?;

    log::info!("Project updated: {}", project.id);

    Ok(())
}

#[tauri::command]
pub async fn delete_project(app: AppHandle, id: String) -> Result<(), String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;
    db.delete_project(&id).map_err(|e| e.to_string())?;

    // Add to sync queue
    db.add_to_sync_queue("project", &id, OperationType::Delete, "{}")
        .map_err(|e| e.to_string())?;

    log::info!("Project deleted: {}", id);

    Ok(())
}

// Item Commands
#[tauri::command]
pub async fn create_item(
    app: AppHandle,
    project_id: String,
    item_type: String,
    title: String,
    content: String,
    status: String,
    priority: Option<String>,
) -> Result<Item, String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;

    let item_type_enum = ItemType::from_str(&item_type)
        .ok_or_else(|| format!("Invalid item type: {}", item_type))?;

    let item = Item {
        id: Uuid::new_v4().to_string(),
        project_id,
        item_type: item_type_enum,
        title,
        content,
        status,
        priority,
        version: 1,
        created_at: Utc::now(),
        updated_at: Utc::now(),
        synced_at: None,
        is_deleted: false,
    };

    db.create_item(&item).map_err(|e| e.to_string())?;

    // Add to sync queue
    let payload = serde_json::to_string(&item).map_err(|e| e.to_string())?;
    db.add_to_sync_queue("item", &item.id, OperationType::Create, &payload)
        .map_err(|e| e.to_string())?;

    log::info!("Item created: {} ({})", item.title, item.id);

    Ok(item)
}

#[tauri::command]
pub async fn get_item(app: AppHandle, id: String) -> Result<Option<Item>, String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;
    db.get_item(&id).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn list_items(
    app: AppHandle,
    project_id: String,
    item_type: Option<String>,
) -> Result<Vec<Item>, String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;

    let item_type_enum = item_type
        .map(|t| ItemType::from_str(&t))
        .transpose()
        .ok_or_else(|| "Invalid item type".to_string())?;

    db.list_items(&project_id, item_type_enum).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn update_item(app: AppHandle, item: Item) -> Result<(), String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;
    db.update_item(&item).map_err(|e| e.to_string())?;

    // Add to sync queue
    let payload = serde_json::to_string(&item).map_err(|e| e.to_string())?;
    db.add_to_sync_queue("item", &item.id, OperationType::Update, &payload)
        .map_err(|e| e.to_string())?;

    log::info!("Item updated: {}", item.id);

    Ok(())
}

#[tauri::command]
pub async fn delete_item(app: AppHandle, id: String) -> Result<(), String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;
    db.delete_item(&id).map_err(|e| e.to_string())?;

    // Add to sync queue
    db.add_to_sync_queue("item", &id, OperationType::Delete, "{}")
        .map_err(|e| e.to_string())?;

    log::info!("Item deleted: {}", id);

    Ok(())
}

// Link Commands
#[tauri::command]
pub async fn create_link(
    app: AppHandle,
    project_id: String,
    source_id: String,
    target_id: String,
    link_type: String,
    metadata: Option<String>,
) -> Result<Link, String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;

    let link = Link {
        id: Uuid::new_v4().to_string(),
        project_id,
        source_id,
        target_id,
        link_type,
        metadata,
        created_at: Utc::now(),
        is_deleted: false,
    };

    db.create_link(&link).map_err(|e| e.to_string())?;

    // Add to sync queue
    let payload = serde_json::to_string(&link).map_err(|e| e.to_string())?;
    db.add_to_sync_queue("link", &link.id, OperationType::Create, &payload)
        .map_err(|e| e.to_string())?;

    log::info!("Link created: {}", link.id);

    Ok(link)
}

#[tauri::command]
pub async fn list_links(app: AppHandle, project_id: String) -> Result<Vec<Link>, String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;
    db.list_links(&project_id).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn delete_link(app: AppHandle, id: String) -> Result<(), String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;
    db.delete_link(&id).map_err(|e| e.to_string())?;

    // Add to sync queue
    db.add_to_sync_queue("link", &id, OperationType::Delete, "{}")
        .map_err(|e| e.to_string())?;

    log::info!("Link deleted: {}", id);

    Ok(())
}

// Export Commands
#[tauri::command]
pub async fn export_project_json(
    app: AppHandle,
    project_id: String,
    output_path: String,
) -> Result<(), String> {
    let exporter = Exporter::new(&app).map_err(|e| e.to_string())?;
    exporter.export_project_json(&project_id, &output_path).map_err(|e| e.to_string())?;

    let notif = NotificationManager::new(app);
    let _ = notif.send_custom("Export Complete", "Project exported to JSON successfully");

    Ok(())
}

#[tauri::command]
pub async fn export_project_csv(
    app: AppHandle,
    project_id: String,
    output_path: String,
) -> Result<(), String> {
    let exporter = Exporter::new(&app).map_err(|e| e.to_string())?;
    exporter.export_project_csv(&project_id, &output_path).map_err(|e| e.to_string())?;

    let notif = NotificationManager::new(app);
    let _ = notif.send_custom("Export Complete", "Project exported to CSV successfully");

    Ok(())
}

#[tauri::command]
pub async fn export_traceability_matrix(
    app: AppHandle,
    project_id: String,
    output_path: String,
) -> Result<(), String> {
    let exporter = Exporter::new(&app).map_err(|e| e.to_string())?;
    exporter.export_traceability_matrix_csv(&project_id, &output_path).map_err(|e| e.to_string())?;

    let notif = NotificationManager::new(app);
    let _ = notif.send_custom("Export Complete", "Traceability matrix exported successfully");

    Ok(())
}

#[tauri::command]
pub async fn export_project_markdown(
    app: AppHandle,
    project_id: String,
    output_path: String,
) -> Result<(), String> {
    let exporter = Exporter::new(&app).map_err(|e| e.to_string())?;
    exporter.export_project_markdown(&project_id, &output_path).map_err(|e| e.to_string())?;

    let notif = NotificationManager::new(app);
    let _ = notif.send_custom("Export Complete", "Project exported to Markdown successfully");

    Ok(())
}

// Sync Queue Commands
#[tauri::command]
pub async fn get_pending_sync_count(app: AppHandle) -> Result<usize, String> {
    let db = Database::new(&app).map_err(|e| e.to_string())?;
    let items = db.get_pending_sync_items().map_err(|e| e.to_string())?;
    Ok(items.len())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_command_structure() {
        // Test that commands compile correctly
        assert!(true);
    }
}
