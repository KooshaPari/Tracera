//! Tauri 2 entry point for the Tracera desktop shell.
//!
//! The desktop shell hosts the Svelte web UI built by `npm run build` and
//! adds:
//!
//!   * a system tray icon with quick actions (open, hide, quit),
//!   * a native application menu with platform-appropriate items,
//!   * graceful lifecycle handling so the app stays in the tray when the
//!     main window is closed.
//!
//! The Rust side stays thin — it does not reimplement Tracera business
//! logic. It exists to give the web UI a native container and to manage the
//! process lifecycle of the optional `tracera-os-service` companion daemon
//! (see `frontend/apps/os-service`).

#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::sync::Mutex;

use tauri::{
    menu::{MenuBuilder, MenuItemBuilder, PredefinedMenuItem, SubmenuBuilder},
    tray::TrayIconBuilder,
    AppHandle, Emitter, Manager, WindowEvent,
};

mod tray;

use tray::{build_tray_menu, TrayState};

// -----------------------------------------------------------------------------
// Logging — minimal stderr writer (avoids the env_logger dependency).
// -----------------------------------------------------------------------------

#[derive(Copy, Clone, PartialEq, Eq)]
enum LogLevel {
    Error,
    Warn,
    Info,
    Debug,
    Trace,
}

impl LogLevel {
    fn from_env() -> Self {
        let raw = std::env::var("RUST_LOG").unwrap_or_else(|_| "info".to_string());
        // Pick the most permissive level mentioned so that
        // ``RUST_LOG=info,tracera_desktop=debug`` resolves to ``Debug``.
        raw.split(',')
            .filter_map(|tok| match tok.trim() {
                "error" => Some(LogLevel::Error),
                "warn" => Some(LogLevel::Warn),
                "info" => Some(LogLevel::Info),
                "debug" => Some(LogLevel::Debug),
                "trace" => Some(LogLevel::Trace),
                _ => None,
            })
            .max_by_key(|l| *l as u32)
            .unwrap_or(LogLevel::Info)
    }

    fn as_str(self) -> &'static str {
        match self {
            LogLevel::Error => "ERROR",
            LogLevel::Warn => "WARN",
            LogLevel::Info => "INFO",
            LogLevel::Debug => "DEBUG",
            LogLevel::Trace => "TRACE",
        }
    }
}

fn log(level: LogLevel, target: &str, msg: &str) {
    eprintln!(
        "[{}] [{}] [{}] {}",
        chrono_lite_timestamp(),
        level.as_str(),
        target,
        msg,
    );
}

// -----------------------------------------------------------------------------
// Application state
// -----------------------------------------------------------------------------

/// Application-wide state held inside Tauri's managed state container.
///
/// `service_pid` is a placeholder used by the companion ``os-service`` crate
/// to record the PID of the backend it spawned. The web frontend reads this
/// value via a Tauri command to display service status.
#[derive(Default)]
struct AppState {
    /// PID of the spawned ``tracera-os-service`` companion, if any.
    service_pid: Mutex<Option<u32>>,
}

/// Returns the PID of the spawned companion service, if any.
///
/// The frontend calls this on startup to render a status badge.
#[tauri::command]
fn service_pid(state: tauri::State<'_, AppState>) -> Option<u32> {
    state.service_pid.lock().ok().and_then(|g| *g)
}

/// Tells the webview to focus the in-app command palette.
///
/// Hooked into the tray "Search" item so users get keyboard-driven access
/// without having to bring the main window to the foreground first.
#[tauri::command]
fn focus_search(app: AppHandle) -> Result<(), tauri::Error> {
    app.emit("tracera://focus-search", ())
}

/// Restore + focus the main window, creating it on first launch.
fn show_main_window(app: &AppHandle) {
    if let Some(win) = app.get_webview_window("main") {
        let _ = win.show();
        let _ = win.unminimize();
        let _ = win.set_focus();
    } else {
        log(LogLevel::Warn, "tracera_desktop", "main window not yet created; skipping show");
    }
}

/// Hide the main window and fall back to the tray.
fn hide_main_window(app: &AppHandle) {
    if let Some(win) = app.get_webview_window("main") {
        let _ = win.hide();
    }
}

// -----------------------------------------------------------------------------
// Native menu
// -----------------------------------------------------------------------------

/// Build the platform-appropriate application menu.
///
/// On macOS we contribute the standard Apple submenus (App, File, Edit,
/// View, Window). On Windows / Linux we contribute a leaner set focused
/// on the file/edit/view menus plus a "Tracera" app submenu.
fn build_app_menu(app: &AppHandle) -> tauri::Result<tauri::menu::Menu<tauri::Wry>> {
    let handle = app.handle();

    // Common items.
    let open = MenuItemBuilder::with_id("open_main", "Open Tracera").build(handle)?;
    let quit = MenuItemBuilder::with_id("quit", "Quit")
        .accelerator("CmdOrCtrl+Q")
        .build(handle)?;
    let hide = MenuItemBuilder::with_id("hide_main", "Hide to tray")
        .accelerator("CmdOrCtrl+H")
        .build(handle)?;
    let search = MenuItemBuilder::with_id("search", "Search")
        .accelerator("CmdOrCtrl+K")
        .build(handle)?;

    // File submenu.
    let file_menu = SubmenuBuilder::new(handle, "File")
        .item(&open)
        .item(&hide)
        .separator()
        .item(&quit)
        .build()?;

    // Edit submenu (standard items provided by Tauri).
    let edit_menu = SubmenuBuilder::new(handle, "Edit")
        .item(&PredefinedMenuItem::undo(handle, None)?)
        .item(&PredefinedMenuItem::redo(handle, None)?)
        .separator()
        .item(&PredefinedMenuItem::cut(handle, None)?)
        .item(&PredefinedMenuItem::copy(handle, None)?)
        .item(&PredefinedMenuItem::paste(handle, None)?)
        .item(&PredefinedMenuItem::select_all(handle, None)?)
        .build()?;

    // View submenu.
    let view_menu = SubmenuBuilder::new(handle, "View")
        .item(&search)
        .item(&PredefinedMenuItem::fullscreen(handle, None)?)
        .build()?;

    // Tracera submenu (app-level commands).
    let tracera_menu = SubmenuBuilder::new(handle, "Tracera")
        .item(&open)
        .item(&hide)
        .separator()
        .item(&search)
        .build()?;

    let menu = if cfg!(target_os = "macos") {
        MenuBuilder::new(handle)
            .items(&[
                &tracera_menu, // becomes the App menu on macOS
                &file_menu,
                &edit_menu,
                &view_menu,
                &SubmenuBuilder::new(handle, "Window").build()?,
            ])
            .build()?
    } else {
        MenuBuilder::new(handle)
            .items(&[&tracera_menu, &file_menu, &edit_menu, &view_menu])
            .build()?
    };

    Ok(menu)
}

// -----------------------------------------------------------------------------
// Builder
// -----------------------------------------------------------------------------

/// Wire up tray, menu, and lifecycle for the desktop shell.
pub fn build_app() -> tauri::Builder<tauri::Wry> {
    tauri::Builder::default()
        .manage(AppState::default())
        .invoke_handler(tauri::generate_handler![service_pid, focus_search])
        .on_menu_event(|app, event| match event.id().as_ref() {
            "open_main" => show_main_window(app),
            "hide_main" => hide_main_window(app),
            "search" => {
                show_main_window(app);
                if let Err(err) = app.emit("tracera://focus-search", ()) {
                    log(LogLevel::Error, "tracera_desktop", &format!("failed to emit focus-search event: {err}"));
                }
            }
            "quit" => app.exit(0),
            other => log(LogLevel::Info, "tracera_desktop", &format!("unhandled menu id: {other}")),
        })
        .setup(|app| {
            // App menu.
            let menu = build_app_menu(&app.handle())?;
            app.set_menu(menu)?;

            // Tray.
            let tray_state = TrayState::new(app.handle().clone());
            let tray_menu = build_tray_menu(&app.handle(), tray_state.clone())?;
            let _tray = TrayIconBuilder::with_id("main-tray")
                .tooltip("Tracera Desktop")
                .menu(&tray_menu)
                .show_menu_on_left_click(false)
                .on_menu_event(move |app, event| {
                    tray_state.handle_event(app, event.id().as_ref());
                })
                .on_tray_icon_event(|tray, event| {
                    if let tauri::tray::TrayIconEvent::DoubleClick { .. } = event {
                        show_main_window(tray.app_handle());
                    }
                })
                .build(app)?;

            log(LogLevel::Info, "tracera_desktop", "tray + menu initialized");
            Ok(())
        })
        .on_window_event(|window, event| {
            // Hide-to-tray when the user closes the main window.
            if let WindowEvent::CloseRequested { api, .. } = event {
                if window.label() == "main" {
                    api.prevent_close();
                    if let Err(err) = window.hide() {
                        log(
                            LogLevel::Warn,
                            "tracera_desktop",
                            &format!("failed to hide main window: {err}"),
                        );
                    }
                    log(
                        LogLevel::Info,
                        "tracera_desktop",
                        "main window hidden to tray",
                    );
                }
            }
        })
}

/// Programmatic entry point. Public so an integration test or alternative
/// binary can call it directly.
pub fn run() {
    if let Err(err) = build_app().run(tauri::generate_context!()) {
        eprintln!("tracera-desktop: fatal error: {err}");
        std::process::exit(1);
    }
}

/// Tauri commands exported for the web frontend.
///
/// Kept in a single slice so the file is easy to scan.
pub fn exported_commands() -> &'static [&'static str] {
    &["service_pid", "focus_search"]
}

// -----------------------------------------------------------------------------
// Timestamp helper — keeps the dependency tree small.
// -----------------------------------------------------------------------------

fn chrono_lite_timestamp() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let dur = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default();
    let secs = dur.as_secs();
    let (year, month, day, hour, minute, second) = epoch_to_ymdhms(secs);
    format!(
        "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z",
        year, month, day, hour, minute, second,
    )
}

fn epoch_to_ymdhms(secs: u64) -> (i32, u32, u32, u32, u32, u32) {
    let s = (secs % 60) as u32;
    let m = ((secs / 60) % 60) as u32;
    let h = ((secs / 3600) % 24) as u32;
    let mut days = (secs / 86_400) as i64;
    let mut year: i32 = 1970;
    loop {
        let leap = is_leap(year);
        let yd = if leap { 366 } else { 365 };
        if days >= yd {
            days -= yd;
            year += 1;
        } else {
            break;
        }
    }
    let mdays = if is_leap(year) {
        [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    } else {
        [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    };
    let mut month = 1u32;
    for &dm in &mdays {
        if days >= dm {
            days -= dm;
            month += 1;
        } else {
            break;
        }
    }
    (year, month, (days as u32) + 1, h, m, s)
}

fn is_leap(y: i32) -> bool {
    (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0)
}

// -----------------------------------------------------------------------------
// Entry point
// -----------------------------------------------------------------------------

fn main() {
    // Default to ``info`` if RUST_LOG is unset.
    if std::env::var_os("RUST_LOG").is_none() {
        std::env::set_var("RUST_LOG", "info,tracera_desktop=debug");
    }
    log(
        LogLevel::from_env(),
        "tracera_desktop",
        "tracera-desktop: starting",
    );
    run();
}