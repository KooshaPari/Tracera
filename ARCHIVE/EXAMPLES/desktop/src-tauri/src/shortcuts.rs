use tauri::{App, Manager, Emitter};
use anyhow::Result;

pub fn register_shortcuts(app: &App) -> Result<()> {
    // Global shortcuts are handled via the menu system in menu.rs
    // This module handles custom keyboard events that aren't menu items

    let app_handle = app.handle().clone();

    // Listen for custom keyboard events from the frontend
    app.listen("register-shortcut", move |event| {
        if let Some(payload) = event.payload() {
            log::debug!("Custom shortcut registered: {}", payload);
        }
    });

    // Setup window-level keyboard handling
    if let Some(window) = app.get_webview_window("main") {
        window.on_window_event(move |event| {
            if let tauri::WindowEvent::Focused(focused) = event {
                log::debug!("Window focus changed: {}", focused);
            }
        });
    }

    Ok(())
}

// Common keyboard shortcuts
pub const SHORTCUTS: &[(&str, &str)] = &[
    // File operations
    ("new_requirement", "CmdOrCtrl+N"),
    ("new_test", "CmdOrCtrl+Shift+N"),
    ("open_project", "CmdOrCtrl+O"),
    ("save", "CmdOrCtrl+S"),
    ("save_all", "CmdOrCtrl+Shift+S"),

    // Edit operations
    ("undo", "CmdOrCtrl+Z"),
    ("redo", "CmdOrCtrl+Shift+Z"),
    ("cut", "CmdOrCtrl+X"),
    ("copy", "CmdOrCtrl+C"),
    ("paste", "CmdOrCtrl+V"),
    ("select_all", "CmdOrCtrl+A"),
    ("find", "CmdOrCtrl+F"),
    ("find_replace", "CmdOrCtrl+H"),

    // Navigation
    ("go_back", "CmdOrCtrl+["),
    ("go_forward", "CmdOrCtrl+]"),
    ("quick_open", "CmdOrCtrl+P"),
    ("command_palette", "CmdOrCtrl+Shift+P"),

    // View
    ("zoom_in", "CmdOrCtrl+Plus"),
    ("zoom_out", "CmdOrCtrl+Minus"),
    ("zoom_reset", "CmdOrCtrl+0"),
    ("toggle_sidebar", "CmdOrCtrl+B"),
    ("toggle_terminal", "CmdOrCtrl+`"),

    // Sync
    ("sync_now", "CmdOrCtrl+Shift+S"),
    ("refresh", "CmdOrCtrl+R"),
    ("hard_refresh", "CmdOrCtrl+Shift+R"),

    // Development
    ("dev_tools", "CmdOrCtrl+Alt+I"),
    ("reload", "CmdOrCtrl+R"),
];

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_shortcuts_defined() {
        assert!(!SHORTCUTS.is_empty());
        assert!(SHORTCUTS.len() > 10);
    }
}
