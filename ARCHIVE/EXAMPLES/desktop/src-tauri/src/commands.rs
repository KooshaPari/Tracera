use tauri::{AppHandle, State};
use serde::{Deserialize, Serialize};
use crate::sync::SyncStatus;

#[derive(Debug, Serialize, Deserialize)]
pub struct AppInfo {
    pub version: String,
    pub platform: String,
    pub arch: String,
}

#[tauri::command]
pub async fn sync_data(app: AppHandle) -> Result<(), String> {
    log::info!("Manual sync triggered");

    let manager = crate::sync::SyncManager::new(app);
    manager.sync().await.map_err(|e| e.to_string())?;

    Ok(())
}

#[tauri::command]
pub async fn get_sync_status(app: AppHandle) -> Result<SyncStatus, String> {
    let manager = crate::sync::SyncManager::new(app);
    Ok(manager.get_status().await)
}

#[tauri::command]
pub async fn force_sync(app: AppHandle) -> Result<(), String> {
    log::info!("Force sync triggered");

    let manager = crate::sync::SyncManager::new(app);
    manager.sync().await.map_err(|e| e.to_string())?;

    Ok(())
}

#[tauri::command]
pub async fn get_local_data(
    app: AppHandle,
    key: String,
) -> Result<Option<serde_json::Value>, String> {
    log::debug!("Getting local data for key: {}", key);

    let store = app.state::<tauri_plugin_store::StoreCollection<tauri::Wry>>();
    let path = std::path::PathBuf::from("app_data.json");

    if let Some(store) = store.get_store(&path) {
        let store = store.lock().await;
        Ok(store.get(&key).cloned())
    } else {
        Ok(None)
    }
}

#[tauri::command]
pub async fn save_local_data(
    app: AppHandle,
    key: String,
    value: serde_json::Value,
) -> Result<(), String> {
    log::debug!("Saving local data for key: {}", key);

    let store = app.state::<tauri_plugin_store::StoreCollection<tauri::Wry>>();
    let path = std::path::PathBuf::from("app_data.json");

    if let Some(store) = store.get_store(&path) {
        let mut store = store.lock().await;
        store.set(key, value);
        store.save().await.map_err(|e| e.to_string())?;
    }

    // Mark as pending change
    let changes_path = std::path::PathBuf::from("local_changes.json");
    if let Some(changes_store) = store.get_store(&changes_path) {
        let mut changes_store = changes_store.lock().await;
        let mut pending = changes_store
            .get("pending_changes")
            .and_then(|v| serde_json::from_value::<Vec<String>>(v.clone()).ok())
            .unwrap_or_default();

        if !pending.contains(&key) {
            pending.push(key);
            changes_store.set("pending_changes", serde_json::to_value(pending).unwrap());
            changes_store.save().await.map_err(|e| e.to_string())?;
        }
    }

    Ok(())
}

#[tauri::command]
pub async fn clear_cache(app: AppHandle) -> Result<(), String> {
    log::info!("Clearing cache");

    let store = app.state::<tauri_plugin_store::StoreCollection<tauri::Wry>>();
    let path = std::path::PathBuf::from("app_data.json");

    if let Some(store) = store.get_store(&path) {
        let mut store = store.lock().await;
        store.clear();
        store.save().await.map_err(|e| e.to_string())?;
    }

    Ok(())
}

#[tauri::command]
pub async fn get_app_info() -> Result<AppInfo, String> {
    Ok(AppInfo {
        version: env!("CARGO_PKG_VERSION").to_string(),
        platform: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_app_info() {
        let info = get_app_info().await.unwrap();
        assert!(!info.version.is_empty());
        assert!(!info.platform.is_empty());
        assert!(!info.arch.is_empty());
    }
}
