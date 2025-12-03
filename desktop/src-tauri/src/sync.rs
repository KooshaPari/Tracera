use tauri::{AppHandle, Emitter, Manager};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;
use chrono::{DateTime, Utc};
use anyhow::Result;

const SYNC_INTERVAL_SECONDS: u64 = 300; // 5 minutes
const API_BASE_URL: &str = "http://localhost:8000/api"; // Configure as needed

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncStatus {
    pub is_syncing: bool,
    pub last_sync: Option<DateTime<Utc>>,
    pub sync_error: Option<String>,
    pub pending_changes: usize,
    pub online: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SyncPayload {
    requirements: Vec<Requirement>,
    tests: Vec<Test>,
    timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Requirement {
    id: String,
    content: String,
    status: String,
    updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Test {
    id: String,
    requirement_id: String,
    content: String,
    status: String,
    updated_at: DateTime<Utc>,
}

pub struct SyncManager {
    status: Arc<Mutex<SyncStatus>>,
    app_handle: AppHandle,
}

impl SyncManager {
    pub fn new(app_handle: AppHandle) -> Self {
        Self {
            status: Arc::new(Mutex::new(SyncStatus {
                is_syncing: false,
                last_sync: None,
                sync_error: None,
                pending_changes: 0,
                online: false,
            })),
            app_handle,
        }
    }

    pub async fn get_status(&self) -> SyncStatus {
        self.status.lock().await.clone()
    }

    pub async fn sync(&self) -> Result<()> {
        let mut status = self.status.lock().await;

        if status.is_syncing {
            return Ok(());
        }

        status.is_syncing = true;
        status.sync_error = None;
        drop(status);

        // Emit sync started event
        let _ = self.app_handle.emit("sync-started", ());

        let result = self.perform_sync().await;

        let mut status = self.status.lock().await;
        status.is_syncing = false;

        match result {
            Ok(_) => {
                status.last_sync = Some(Utc::now());
                status.pending_changes = 0;
                status.sync_error = None;
                log::info!("Sync completed successfully");

                // Emit sync completed event
                let _ = self.app_handle.emit("sync-completed", status.clone());
            }
            Err(e) => {
                let error_msg = e.to_string();
                status.sync_error = Some(error_msg.clone());
                log::error!("Sync failed: {}", error_msg);

                // Emit sync error event
                let _ = self.app_handle.emit("sync-error", error_msg);
            }
        }

        Ok(())
    }

    async fn perform_sync(&self) -> Result<()> {
        // Check network connectivity
        let online = self.check_network().await;
        {
            let mut status = self.status.lock().await;
            status.online = online;
        }

        if !online {
            log::warn!("Offline mode - sync skipped");
            return Ok(());
        }

        // 1. Upload local changes
        self.upload_local_changes().await?;

        // 2. Download remote changes
        self.download_remote_changes().await?;

        // 3. Resolve conflicts (last-write-wins for now)
        self.resolve_conflicts().await?;

        Ok(())
    }

    async fn check_network(&self) -> bool {
        let client = reqwest::Client::new();
        match client
            .get(format!("{}/health", API_BASE_URL))
            .timeout(std::time::Duration::from_secs(5))
            .send()
            .await
        {
            Ok(response) => response.status().is_success(),
            Err(_) => false,
        }
    }

    async fn upload_local_changes(&self) -> Result<()> {
        log::info!("Uploading local changes...");

        let store = self.app_handle.state::<tauri_plugin_store::StoreCollection<tauri::Wry>>();
        let path = std::path::PathBuf::from("local_changes.json");

        let changes = if let Some(store) = store.get_store(&path) {
            let store = store.lock().await;
            store.get("pending_changes")
                .and_then(|v| serde_json::from_value::<Vec<serde_json::Value>>(v.clone()).ok())
                .unwrap_or_default()
        } else {
            Vec::new()
        };

        if changes.is_empty() {
            log::info!("No local changes to upload");
            return Ok(());
        }

        let client = reqwest::Client::new();
        let response = client
            .post(format!("{}/sync/upload", API_BASE_URL))
            .json(&changes)
            .send()
            .await?;

        if response.status().is_success() {
            // Clear pending changes
            if let Some(store) = store.get_store(&path) {
                let mut store = store.lock().await;
                store.set("pending_changes", serde_json::json!([]));
                store.save().await?;
            }
            log::info!("Local changes uploaded successfully");
        } else {
            anyhow::bail!("Upload failed with status: {}", response.status());
        }

        Ok(())
    }

    async fn download_remote_changes(&self) -> Result<()> {
        log::info!("Downloading remote changes...");

        let store = self.app_handle.state::<tauri_plugin_store::StoreCollection<tauri::Wry>>();
        let path = std::path::PathBuf::from("app_data.json");

        let last_sync = if let Some(store) = store.get_store(&path) {
            let store = store.lock().await;
            store.get("last_sync_timestamp")
                .and_then(|v| serde_json::from_value::<String>(v.clone()).ok())
        } else {
            None
        };

        let client = reqwest::Client::new();
        let mut request = client.get(format!("{}/sync/download", API_BASE_URL));

        if let Some(timestamp) = last_sync {
            request = request.query(&[("since", timestamp)]);
        }

        let response = request.send().await?;

        if response.status().is_success() {
            let data: SyncPayload = response.json().await?;

            // Store downloaded data
            if let Some(store) = store.get_store(&path) {
                let mut store = store.lock().await;
                store.set("requirements", serde_json::to_value(&data.requirements)?);
                store.set("tests", serde_json::to_value(&data.tests)?);
                store.set("last_sync_timestamp", serde_json::to_value(data.timestamp.to_rfc3339())?);
                store.save().await?;
            }

            log::info!("Remote changes downloaded successfully");
        } else {
            anyhow::bail!("Download failed with status: {}", response.status());
        }

        Ok(())
    }

    async fn resolve_conflicts(&self) -> Result<()> {
        log::info!("Resolving conflicts (last-write-wins)...");
        // Simple conflict resolution: last write wins
        // In a production app, you might want more sophisticated conflict resolution
        Ok(())
    }
}

pub async fn start_background_sync(app_handle: AppHandle) {
    let manager = SyncManager::new(app_handle);

    loop {
        if let Err(e) = manager.sync().await {
            log::error!("Background sync error: {}", e);
        }

        tokio::time::sleep(tokio::time::Duration::from_secs(SYNC_INTERVAL_SECONDS)).await;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_sync_status() {
        // Test sync status initialization
        let status = SyncStatus {
            is_syncing: false,
            last_sync: None,
            sync_error: None,
            pending_changes: 0,
            online: false,
        };

        assert!(!status.is_syncing);
        assert_eq!(status.pending_changes, 0);
    }
}
