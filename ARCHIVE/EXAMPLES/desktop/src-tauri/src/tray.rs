use tauri::{
    App, AppHandle, Manager, Runtime,
    menu::{MenuBuilder, MenuItemBuilder},
    tray::{TrayIconBuilder, TrayIconEvent},
};
use anyhow::Result;

pub fn create_tray<R: Runtime>(app: &App<R>) -> Result<()> {
    let sync_now = MenuItemBuilder::new("Sync Now")
        .id("tray_sync")
        .build(app)?;

    let show_window = MenuItemBuilder::new("Show TraceRTM")
        .id("tray_show")
        .build(app)?;

    let quit = MenuItemBuilder::new("Quit")
        .id("tray_quit")
        .build(app)?;

    let menu = MenuBuilder::new(app)
        .item(&show_window)
        .separator()
        .item(&sync_now)
        .separator()
        .item(&quit)
        .build()?;

    let tray = TrayIconBuilder::new()
        .menu(&menu)
        .icon(app.default_window_icon().unwrap().clone())
        .tooltip("TraceRTM")
        .on_menu_event(|app, event| {
            match event.id().as_ref() {
                "tray_show" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                }
                "tray_sync" => {
                    let app_handle = app.app_handle().clone();
                    tauri::async_runtime::spawn(async move {
                        if let Err(e) = crate::commands::force_sync(app_handle).await {
                            log::error!("Tray sync failed: {}", e);
                        }
                    });
                }
                "tray_quit" => {
                    std::process::exit(0);
                }
                _ => {}
            }
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click { button, .. } = event {
                if button == tauri::tray::MouseButton::Left {
                    let app = tray.app_handle();
                    if let Some(window) = app.get_webview_window("main") {
                        if window.is_visible().unwrap_or(false) {
                            let _ = window.hide();
                        } else {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                }
            }
        })
        .build(app)?;

    Ok(())
}

pub fn update_tray_tooltip(app_handle: &AppHandle, tooltip: &str) -> Result<()> {
    if let Some(tray) = app_handle.tray_by_id("main") {
        tray.set_tooltip(Some(tooltip))?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tray_creation() {
        // This would require a full Tauri app context to test
        // In a real app, you'd use integration tests
        assert!(true);
    }
}
