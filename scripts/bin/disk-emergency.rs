// disk-emergency: automated crisis disk-recovery playbook for 100% full situations.
// Rust per scripting hierarchy (faster execution, no external deps for simple file ops).

use std::fs;
use std::path::Path;
use std::process::Command;

fn main() {
    let report = std::env::args().any(|arg| arg == "--report");
    let dry_run = std::env::args().any(|arg| arg == "--dry-run");

    println!("disk-emergency: starting crisis playbook");
    println!("dry-run: {}", dry_run);
    println!();

    let mut total_bytes = 0u64;

    // Phase 1: Homebrew cache (5-10 GB typical)
    println!("[1/5] Homebrew cache (~/Library/Caches/Homebrew)");
    let brew_cache = format!(
        "{}/.Caches/Homebrew",
        std::env::var("HOME").unwrap_or_else(|_| "/tmp".to_string())
    );
    if Path::new(&format!("{}/..", brew_cache)).exists() {
        let bytes = purge_dir(&brew_cache, dry_run);
        total_bytes += bytes;
        if report {
            println!("  -> {}", format_bytes(bytes));
        }
    }
    println!();

    // Phase 2: npm cache (3-8 GB typical)
    println!("[2/5] npm cache (~/.npm/_cacache)");
    if !dry_run {
        let _ = Command::new("npm")
            .args(&["cache", "clean", "--force"])
            .output();
    } else {
        println!("  dry-run: would run 'npm cache clean --force'");
    }
    println!();

    // Phase 3: Cargo worktree targets (6-8 GB per orphaned build)
    println!("[3/5] Worktree targets (repos/.worktrees/*/target)");
    let repo_root = "/Users/kooshapari/CodeProjects/Phenotype/repos";
    let worktree_base = format!("{}/.worktrees", repo_root);
    if Path::new(&worktree_base).exists() {
        if let Ok(entries) = fs::read_dir(&worktree_base) {
            for entry in entries.flatten() {
                let target_path = entry.path().join("target");
                if target_path.exists() {
                    let bytes = purge_dir(target_path.to_str().unwrap_or(""), dry_run);
                    total_bytes += bytes;
                    if report {
                        println!("  -> {} removed", format_bytes(bytes));
                    }
                }
            }
        }
    }
    println!();

    // Phase 4: Xcode cache (2-5 GB)
    println!("[4/5] Xcode cache (~/Library/Caches/com.apple.dt.Xcode)");
    let xcode_cache = format!(
        "{}/.Caches/com.apple.dt.Xcode",
        std::env::var("HOME").unwrap_or_else(|_| "/tmp".to_string())
    );
    if Path::new(&format!("{}/..", xcode_cache)).exists() {
        let bytes = purge_dir(&xcode_cache, dry_run);
        total_bytes += bytes;
        if report {
            println!("  -> {}", format_bytes(bytes));
        }
    }
    println!();

    // Phase 5: Cargo registry cache (~300 MB)
    println!("[5/5] Cargo registry (~/.cargo/registry/cache)");
    let cargo_registry = format!(
        "{}/.cargo/registry/cache",
        std::env::var("HOME").unwrap_or_else(|_| "/tmp".to_string())
    );
    if Path::new(&cargo_registry).exists() {
        let bytes = purge_dir(&cargo_registry, dry_run);
        total_bytes += bytes;
        if report {
            println!("  -> {}", format_bytes(bytes));
        }
    }
    println!();

    if report {
        println!("=== TOTAL RECLAIMED ===");
        println!("{}", format_bytes(total_bytes));
    }

    if !dry_run {
        println!("crisis playbook complete. run 'df -h /System/Volumes/Data | tail -1' to verify.");
    }
}

fn purge_dir(path: &str, dry_run: bool) -> u64 {
    if path.is_empty() {
        return 0;
    }

    // Estimate size before deletion
    let size_before = estimate_dir_size(path);

    if !dry_run {
        let _ = Command::new("rm")
            .args(&["-rf", path])
            .output();
    } else {
        println!("  dry-run: would remove {}", path);
    }

    size_before
}

fn estimate_dir_size(path: &str) -> u64 {
    let output = Command::new("du")
        .args(&["-sb", path])
        .output();

    match output {
        Ok(out) => {
            let stdout = String::from_utf8_lossy(&out.stdout);
            stdout
                .split_whitespace()
                .next()
                .and_then(|s| s.parse::<u64>().ok())
                .unwrap_or(0)
        }
        Err(_) => 0,
    }
}

fn format_bytes(bytes: u64) -> String {
    let units = ["B", "KB", "MB", "GB", "TB"];
    let mut size = bytes as f64;
    let mut unit_idx = 0;

    while size >= 1024.0 && unit_idx < units.len() - 1 {
        size /= 1024.0;
        unit_idx += 1;
    }

    format!("{:.2} {}", size, units[unit_idx])
}
