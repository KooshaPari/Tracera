use tauri::AppHandle;
use anyhow::Result;
use serde_json::json;
use std::fs::File;
use std::io::Write;
use crate::db_ops::Database;
use crate::models::*;

pub struct Exporter {
    db: Database,
}

impl Exporter {
    pub fn new(app_handle: &AppHandle) -> Result<Self> {
        Ok(Self {
            db: Database::new(app_handle)?,
        })
    }

    pub fn export_project_json(&self, project_id: &str, output_path: &str) -> Result<()> {
        let project = self.db.get_project(project_id)?
            .ok_or_else(|| anyhow::anyhow!("Project not found"))?;

        let items = self.db.list_items(project_id, None)?;
        let links = self.db.list_links(project_id)?;

        let export_data = json!({
            "project": project,
            "items": items,
            "links": links,
            "exported_at": chrono::Utc::now().to_rfc3339(),
            "format_version": "1.0"
        });

        let mut file = File::create(output_path)?;
        file.write_all(serde_json::to_string_pretty(&export_data)?.as_bytes())?;

        log::info!("Project exported to JSON: {}", output_path);
        Ok(())
    }

    pub fn export_project_csv(&self, project_id: &str, output_path: &str) -> Result<()> {
        let items = self.db.list_items(project_id, None)?;

        let mut file = File::create(output_path)?;

        // Write CSV header
        writeln!(file, "ID,Type,Title,Status,Priority,Created,Updated")?;

        // Write data rows
        for item in items {
            writeln!(
                file,
                "{},{},{},{},{},{},{}",
                item.id,
                item.item_type.as_str(),
                escape_csv(&item.title),
                item.status,
                item.priority.as_deref().unwrap_or(""),
                item.created_at.format("%Y-%m-%d %H:%M:%S"),
                item.updated_at.format("%Y-%m-%d %H:%M:%S"),
            )?;
        }

        log::info!("Project exported to CSV: {}", output_path);
        Ok(())
    }

    pub fn export_traceability_matrix_csv(&self, project_id: &str, output_path: &str) -> Result<()> {
        let items = self.db.list_items(project_id, None)?;
        let links = self.db.list_links(project_id)?;

        let mut file = File::create(output_path)?;

        // Write CSV header
        writeln!(file, "Source ID,Source Title,Source Type,Target ID,Target Title,Target Type,Link Type")?;

        // Create a map for quick item lookup
        let item_map: std::collections::HashMap<_, _> = items.iter()
            .map(|item| (item.id.clone(), item))
            .collect();

        // Write traceability links
        for link in links {
            if let (Some(source), Some(target)) = (
                item_map.get(&link.source_id),
                item_map.get(&link.target_id)
            ) {
                writeln!(
                    file,
                    "{},{},{},{},{},{},{}",
                    source.id,
                    escape_csv(&source.title),
                    source.item_type.as_str(),
                    target.id,
                    escape_csv(&target.title),
                    target.item_type.as_str(),
                    link.link_type,
                )?;
            }
        }

        log::info!("Traceability matrix exported to CSV: {}", output_path);
        Ok(())
    }

    pub fn export_project_markdown(&self, project_id: &str, output_path: &str) -> Result<()> {
        let project = self.db.get_project(project_id)?
            .ok_or_else(|| anyhow::anyhow!("Project not found"))?;

        let items = self.db.list_items(project_id, None)?;
        let links = self.db.list_links(project_id)?;

        let mut file = File::create(output_path)?;

        // Write project header
        writeln!(file, "# {}", project.name)?;
        if let Some(desc) = &project.description {
            writeln!(file, "\n{}\n", desc)?;
        }

        // Group items by type
        let mut items_by_type: std::collections::HashMap<ItemType, Vec<&Item>> = std::collections::HashMap::new();
        for item in &items {
            items_by_type.entry(item.item_type.clone()).or_insert_with(Vec::new).push(item);
        }

        // Write sections for each item type
        for (item_type, type_items) in items_by_type {
            writeln!(file, "\n## {}s\n", capitalize(item_type.as_str()))?;

            for item in type_items {
                writeln!(file, "### {}", item.title)?;
                writeln!(file, "**Status:** {} | **Priority:** {}\n", item.status, item.priority.as_deref().unwrap_or("N/A"))?;
                writeln!(file, "{}\n", item.content)?;
            }
        }

        // Write traceability section
        if !links.is_empty() {
            writeln!(file, "\n## Traceability Links\n")?;

            let item_map: std::collections::HashMap<_, _> = items.iter()
                .map(|item| (item.id.clone(), item))
                .collect();

            for link in &links {
                if let (Some(source), Some(target)) = (
                    item_map.get(&link.source_id),
                    item_map.get(&link.target_id)
                ) {
                    writeln!(
                        file,
                        "- **{}** ({}) → **{}** ({})",
                        source.title,
                        source.item_type.as_str(),
                        target.title,
                        target.item_type.as_str()
                    )?;
                }
            }
        }

        // Write metadata
        writeln!(file, "\n---\n")?;
        writeln!(file, "*Exported: {}*", chrono::Utc::now().format("%Y-%m-%d %H:%M:%S"))?;

        log::info!("Project exported to Markdown: {}", output_path);
        Ok(())
    }
}

fn escape_csv(s: &str) -> String {
    if s.contains(',') || s.contains('"') || s.contains('\n') {
        format!("\"{}\"", s.replace('"', "\"\""))
    } else {
        s.to_string()
    }
}

fn capitalize(s: &str) -> String {
    let mut chars = s.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => first.to_uppercase().collect::<String>() + chars.as_str(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_csv_escape() {
        assert_eq!(escape_csv("simple"), "simple");
        assert_eq!(escape_csv("with,comma"), "\"with,comma\"");
        assert_eq!(escape_csv("with\"quote"), "\"with\"\"quote\"");
    }

    #[test]
    fn test_capitalize() {
        assert_eq!(capitalize("feature"), "Feature");
        assert_eq!(capitalize("test"), "Test");
    }
}
