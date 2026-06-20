use tauri::{App, Manager, menu::{MenuBuilder, MenuItemBuilder, SubmenuBuilder, PredefinedMenuItem}};
use anyhow::Result;

pub fn create_menu(app: &App) -> Result<tauri::menu::Menu<tauri::Wry>> {
    let app_menu = SubmenuBuilder::new(app, "TraceRTM")
        .item(&PredefinedMenuItem::about(app, None, None)?)
        .separator()
        .item(&PredefinedMenuItem::services(app, None)?)
        .separator()
        .item(&PredefinedMenuItem::hide(app, None)?)
        .item(&PredefinedMenuItem::hide_others(app, None)?)
        .item(&PredefinedMenuItem::show_all(app, None)?)
        .separator()
        .item(&PredefinedMenuItem::quit(app, None)?)
        .build()?;

    let file_menu = SubmenuBuilder::new(app, "File")
        .item(&MenuItemBuilder::new("New Requirement")
            .id("new_requirement")
            .accelerator("CmdOrCtrl+N")
            .build(app)?)
        .item(&MenuItemBuilder::new("New Test")
            .id("new_test")
            .accelerator("CmdOrCtrl+Shift+N")
            .build(app)?)
        .separator()
        .item(&MenuItemBuilder::new("Open Project")
            .id("open_project")
            .accelerator("CmdOrCtrl+O")
            .build(app)?)
        .item(&MenuItemBuilder::new("Save")
            .id("save")
            .accelerator("CmdOrCtrl+S")
            .build(app)?)
        .separator()
        .item(&PredefinedMenuItem::close_window(app, None)?)
        .build()?;

    let edit_menu = SubmenuBuilder::new(app, "Edit")
        .item(&PredefinedMenuItem::undo(app, None)?)
        .item(&PredefinedMenuItem::redo(app, None)?)
        .separator()
        .item(&PredefinedMenuItem::cut(app, None)?)
        .item(&PredefinedMenuItem::copy(app, None)?)
        .item(&PredefinedMenuItem::paste(app, None)?)
        .item(&PredefinedMenuItem::select_all(app, None)?)
        .build()?;

    let view_menu = SubmenuBuilder::new(app, "View")
        .item(&MenuItemBuilder::new("Reload")
            .id("reload")
            .accelerator("CmdOrCtrl+R")
            .build(app)?)
        .item(&MenuItemBuilder::new("Toggle Developer Tools")
            .id("dev_tools")
            .accelerator("CmdOrCtrl+Alt+I")
            .build(app)?)
        .separator()
        .item(&PredefinedMenuItem::fullscreen(app, None)?)
        .build()?;

    let sync_menu = SubmenuBuilder::new(app, "Sync")
        .item(&MenuItemBuilder::new("Sync Now")
            .id("sync_now")
            .accelerator("CmdOrCtrl+Shift+S")
            .build(app)?)
        .item(&MenuItemBuilder::new("View Sync Status")
            .id("sync_status")
            .build(app)?)
        .separator()
        .item(&MenuItemBuilder::new("Work Offline")
            .id("toggle_offline")
            .build(app)?)
        .build()?;

    let window_menu = SubmenuBuilder::new(app, "Window")
        .item(&PredefinedMenuItem::minimize(app, None)?)
        .item(&PredefinedMenuItem::maximize(app, None)?)
        .separator()
        .item(&MenuItemBuilder::new("Bring All to Front")
            .id("bring_all_to_front")
            .build(app)?)
        .build()?;

    let help_menu = SubmenuBuilder::new(app, "Help")
        .item(&MenuItemBuilder::new("Documentation")
            .id("documentation")
            .build(app)?)
        .item(&MenuItemBuilder::new("Report Issue")
            .id("report_issue")
            .build(app)?)
        .separator()
        .item(&MenuItemBuilder::new("Check for Updates")
            .id("check_updates")
            .build(app)?)
        .build()?;

    let menu = MenuBuilder::new(app)
        .item(&app_menu)
        .item(&file_menu)
        .item(&edit_menu)
        .item(&view_menu)
        .item(&sync_menu)
        .item(&window_menu)
        .item(&help_menu)
        .build()?;

    // Handle menu events
    let app_handle = app.handle().clone();
    menu.on_menu_event(move |app, event| {
        match event.id().as_ref() {
            "new_requirement" => {
                let _ = app.emit("menu:new-requirement", ());
            }
            "new_test" => {
                let _ = app.emit("menu:new-test", ());
            }
            "open_project" => {
                let _ = app.emit("menu:open-project", ());
            }
            "save" => {
                let _ = app.emit("menu:save", ());
            }
            "reload" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.eval("location.reload()");
                }
            }
            "dev_tools" => {
                if let Some(window) = app.get_webview_window("main") {
                    if window.is_devtools_open() {
                        window.close_devtools();
                    } else {
                        window.open_devtools();
                    }
                }
            }
            "sync_now" => {
                let app_handle = app_handle.clone();
                tauri::async_runtime::spawn(async move {
                    if let Err(e) = crate::commands::force_sync(app_handle).await {
                        log::error!("Sync failed: {}", e);
                    }
                });
            }
            "sync_status" => {
                let _ = app.emit("menu:sync-status", ());
            }
            "toggle_offline" => {
                let _ = app.emit("menu:toggle-offline", ());
            }
            "documentation" => {
                let _ = tauri_plugin_shell::ShellExt::shell(app)
                    .open("https://tracertm.dev/docs", None);
            }
            "report_issue" => {
                let _ = tauri_plugin_shell::ShellExt::shell(app)
                    .open("https://github.com/tracertm/tracertm/issues/new", None);
            }
            "check_updates" => {
                let app_handle = app_handle.clone();
                tauri::async_runtime::spawn(async move {
                    #[cfg(not(debug_assertions))]
                    {
                        use tauri_plugin_updater::UpdaterExt;
                        if let Ok(Some(update)) = app_handle.updater().unwrap().check().await {
                            log::info!("Update available: {}", update.version);
                        }
                    }
                });
            }
            _ => {}
        }
    });

    Ok(menu)
}
