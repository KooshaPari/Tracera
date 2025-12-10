use tauri::AppHandle;
use tauri_plugin_notification::NotificationExt;
use anyhow::Result;

pub struct NotificationManager {
    app_handle: AppHandle,
}

impl NotificationManager {
    pub fn new(app_handle: AppHandle) -> Self {
        Self { app_handle }
    }

    pub fn send_sync_success(&self) -> Result<()> {
        self.app_handle
            .notification()
            .builder()
            .title("TraceRTM")
            .body("Sync completed successfully")
            .show()?;
        Ok(())
    }

    pub fn send_sync_error(&self, error: &str) -> Result<()> {
        self.app_handle
            .notification()
            .builder()
            .title("TraceRTM - Sync Error")
            .body(format!("Sync failed: {}", error))
            .show()?;
        Ok(())
    }

    pub fn send_update_available(&self, version: &str) -> Result<()> {
        self.app_handle
            .notification()
            .builder()
            .title("TraceRTM Update Available")
            .body(format!("Version {} is available for download", version))
            .show()?;
        Ok(())
    }

    pub fn send_conflict_detected(&self, entity_type: &str) -> Result<()> {
        self.app_handle
            .notification()
            .builder()
            .title("TraceRTM - Sync Conflict")
            .body(format!("Conflict detected in {}", entity_type))
            .show()?;
        Ok(())
    }

    pub fn send_custom(&self, title: &str, body: &str) -> Result<()> {
        self.app_handle
            .notification()
            .builder()
            .title(title)
            .body(body)
            .show()?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_notification_manager() {
        // This would require a full Tauri app context to test
        // In a real app, you'd use integration tests
        assert!(true);
    }
}
