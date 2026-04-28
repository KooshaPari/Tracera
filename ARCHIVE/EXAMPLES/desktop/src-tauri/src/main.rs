// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod commands_extended;
mod menu;
mod sync;
mod db;
mod db_ops;
mod models;
mod shortcuts;
mod tray;
mod notifications;
mod export;

use tauri::{
    AppHandle, Manager, Runtime, WebviewUrl, WebviewWindowBuilder,
    menu::{MenuBuilder, SubmenuBuilder},
};
use tauri_plugin_deep_link::DeepLinkExt;

#[derive(Clone, serde::Serialize)]
struct DeepLinkPayload {
    url: String,
}

fn main() {
    env_logger::init();

    tauri::Builder::default()
        // Register plugins
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_sql::Builder::default().build())
        .plugin(tauri_plugin_updater::Builder::default().build())
        .plugin(tauri_plugin_deep_link::init())

        // Setup handler
        .setup(|app| {
            #[cfg(debug_assertions)]
            {
                let window = app.get_webview_window("main").unwrap();
                window.open_devtools();
            }

            // Initialize database
            db::init_db(&app.handle())?;

            // Setup menu
            let menu = menu::create_menu(app)?;
            app.set_menu(menu)?;

            // Setup system tray
            tray::create_tray(app)?;

            // Register keyboard shortcuts
            shortcuts::register_shortcuts(app)?;

            // Setup deep link handler
            app.deep_link().register("tracertm")
                .map_err(|e| anyhow::anyhow!("Failed to register deep link: {}", e))?;

            app.deep_link().on_open_url(move |event| {
                log::info!("Deep link opened: {}", event.urls().join(", "));
                // Handle deep link navigation
                if let Some(url) = event.urls().first() {
                    let _ = event.app_handle().emit("deep-link", DeepLinkPayload {
                        url: url.to_string(),
                    });
                }
            });

            // Check for updates on startup
            #[cfg(not(debug_assertions))]
            {
                let app_handle = app.handle().clone();
                tauri::async_runtime::spawn(async move {
                    if let Err(e) = check_for_updates(app_handle).await {
                        log::error!("Update check failed: {}", e);
                    }
                });
            }

            // Start background sync
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                sync::start_background_sync(app_handle).await;
            });

            Ok(())
        })

        // Register commands
        .invoke_handler(tauri::generate_handler![
            // Sync commands
            commands::sync_data,
            commands::get_sync_status,
            commands::force_sync,
            commands::get_local_data,
            commands::save_local_data,
            commands::clear_cache,
            commands::get_app_info,
            // Project commands
            commands_extended::create_project,
            commands_extended::get_project,
            commands_extended::list_projects,
            commands_extended::update_project,
            commands_extended::delete_project,
            // Item commands
            commands_extended::create_item,
            commands_extended::get_item,
            commands_extended::list_items,
            commands_extended::update_item,
            commands_extended::delete_item,
            // Link commands
            commands_extended::create_link,
            commands_extended::list_links,
            commands_extended::delete_link,
            // Export commands
            commands_extended::export_project_json,
            commands_extended::export_project_csv,
            commands_extended::export_traceability_matrix,
            commands_extended::export_project_markdown,
            // Sync queue commands
            commands_extended::get_pending_sync_count,
        ])

        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[cfg(not(debug_assertions))]
async fn check_for_updates(app: AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    use tauri_plugin_updater::UpdaterExt;

    log::info!("Checking for updates...");

    if let Some(update) = app.updater()?.check().await? {
        log::info!("Update available: {}", update.version);

        let answer = tauri_plugin_dialog::MessageDialogBuilder::new(
            "Update Available",
            format!(
                "Version {} is available. Current version is {}.\n\nWould you like to update now?",
                update.version,
                update.current_version
            )
        )
        .buttons(tauri_plugin_dialog::MessageDialogButtons::YesNo)
        .kind(tauri_plugin_dialog::MessageDialogKind::Info)
        .blocking_show();

        if answer {
            log::info!("User accepted update, downloading...");
            update.download_and_install(|_, _| {}, || {
                log::info!("Update installed, restarting...");
            }).await?;
        }
    } else {
        log::info!("No updates available");
    }

    Ok(())
}
