//! System tray construction and event handling.
//!
//!
// The tray exposes a small menu of actions that map onto the application
//! menu (open, search, settings, about, quit). The struct keeps the
//! ``AppHandle`` so the callbacks can fan out to whatever owns the menu
//! and the main window.

use std::sync::Arc;

use tauri::menu::{CheckMenuItemBuilder, MenuBuilder, MenuItemBuilder, PredefinedMenuItem};
use tauri::{AppHandle, Manager};

/// Shared tray state passed between Tauri callbacks.
///
/// Holds an :class:`AppHandle` clone (cheap) so the menu callbacks can
/// reach back into the Tauri runtime to focus windows, open the in-app
/// settings panel, or quit the app. ``Arc<…>`` lets us clone into multiple
/// closures (the menu and the tray icon).
#[derive(Clone)]
pub struct TrayState {
    /// Tauri runtime handle, cloned for each callback that needs it.
    #[allow(dead_code)]
    pub handle: AppHandle,
    /// Whether the desktop should auto-launch the search palette on next
    /// show. Set by the ``Search`` tray item, consumed on the next focus
    /// event from the webview.
    pub pending_search: Arc<std::sync::atomic::AtomicBool>,
}

impl TrayState {
    /// Create a new tray state bound to the given app handle.
    pub fn new(handle: AppHandle) -> Self {
        Self {
            handle,
            pending_search: Arc::new(std::sync::atomic::AtomicBool::new(false)),
        }
    }

    /// Dispatch a tray menu event by id.
    ///
    /// Mirrors the menu event handler in :mod:`main` so the tray and the
    /// native menu stay in lockstep.
    pub fn handle_event(&self, app: &AppHandle, id: &str) {
        match id {
            "tray_open" | "open_main" => {
                if let Some(win) = app.get_webview_window("main") {
                    let _ = win.show();
                    let _ = win.unminimize();
                    let _ = win.set_focus();
                }
            }
            "tray_search" => {
                if let Some(win) = app.get_webview_window("main") {
                    let _ = win.show();
                    let _ = win.unminimize();
                    let _ = win.set_focus();
                }
                self.pending_search.store(true, std::sync::atomic::Ordering::SeqCst);
                let _ = tauri::Emitter::emit(app, "tracera://focus-search", ());
            }
            "tray_hide" | "hide_main" => {
                if let Some(win) = app.get_webview_window("main") {
                    let _ = win.hide();
                }
            }
            "tray_settings" => {
                if let Some(win) = app.get_webview_window("main") {
                    let _ = win.show();
                    let _ = win.unminimize();
                    let _ = win.set_focus();
                }
                let _ = tauri::Emitter::emit(app, "tracera://open-settings", ());
            }
            "tray_quit" | "quit" => app.exit(0),
            other => {
                eprintln!("[tracera_desktop] unhandled tray menu id: {other}");
            }
        }
    }
}

/// Build the tray context menu.
///
/// The menu is intentionally short — system tray menus on Windows and
/// macOS are best kept to ~5 items so they fit comfortably on small
/// displays. Settings is the only "advanced" item; everything else is a
/// one-click action.
pub fn build_tray_menu(
    app: &AppHandle,
    _state: TrayState,
) -> tauri::Result<tauri::menu::Menu<tauri::Wry>> {
    let handle = app.handle();

    let open = MenuItemBuilder::with_id("tray_open", "Open Tracera")
        .accelerator("CmdOrCtrl+1")
        .build(handle)?;
    let search = MenuItemBuilder::with_id("tray_search", "Search…")
        .accelerator("CmdOrCtrl+K")
        .build(handle)?;
    let settings = CheckMenuItemBuilder::with_id("tray_settings", "Settings")
        .build(handle)?;
    // Cast the check item back to a MenuItem so it can be embedded in a
    // plain menu — Tauri 2 has two parallel builders (item vs check) and
    // the SubmenuBuilder accepts both via the ``IsMenuItem`` trait, so
    // adding the check item directly also works.

    let separator = PredefinedMenuItem::separator(handle)?;
    let quit = MenuItemBuilder::with_id("tray_quit", "Quit Tracera")
        .accelerator("CmdOrCtrl+Q")
        .build(handle)?;
    let hide = MenuItemBuilder::with_id("tray_hide", "Hide to tray")
        .accelerator("CmdOrCtrl+H")
        .build(handle)?;

    let menu = MenuBuilder::new(handle)
        .item(&open)
        .item(&search)
        .item(&settings)
        .item(&separator)
        .item(&hide)
        .item(&quit)
        .build()?;

    Ok(menu)
}