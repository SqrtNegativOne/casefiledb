use std::collections::HashSet;
use std::path::Path;

use anyhow::{Context, Result};

mod models;
use models::MediaItem;

const TEMP_DIR: &str = "temp";
const SITE_DATA: &str = "public/site_data.json";

fn ingest() -> Result<()> {
    let temp_dir = Path::new(TEMP_DIR);
    let mut temp_files: Vec<_> = std::fs::read_dir(temp_dir)
        .context("cannot open temp/")?
        .filter_map(|e| e.ok())
        .filter(|e| e.path().extension().and_then(|s| s.to_str()) == Some("json"))
        .map(|e| e.path())
        .collect();
    temp_files.sort();

    if temp_files.is_empty() {
        println!("Nothing in temp/ to ingest.");
        return Ok(());
    }

    let mut incoming: Vec<serde_json::Value> = Vec::new();
    for path in &temp_files {
        let content = std::fs::read_to_string(path)
            .with_context(|| format!("reading {}", path.display()))?;
        let raw: serde_json::Value =
            serde_json::from_str(&content).with_context(|| format!("parsing {}", path.display()))?;
        match raw {
            serde_json::Value::Array(arr) => incoming.extend(arr),
            v => incoming.push(v),
        }
    }

    println!(
        "Validating {} item(s) from {} file(s)...",
        incoming.len(),
        temp_files.len()
    );

    let mut errors: Vec<String> = Vec::new();
    let mut validated: Vec<serde_json::Value> = Vec::new();

    for item in incoming {
        let title = item
            .get("title")
            .and_then(|v| v.as_str())
            .or_else(|| item.get("wikidata_id").and_then(|v| v.as_str()))
            .unwrap_or("<unknown>")
            .to_string();

        match serde_json::from_value::<MediaItem>(item) {
            Ok(media) => {
                validated.push(serde_json::to_value(&media).expect("re-serialize failed"));
            }
            Err(e) => {
                errors.push(format!("  {title}: {e}"));
            }
        }
    }

    if !errors.is_empty() {
        eprintln!("Validation failed — temp/ not cleared:\n");
        for err in &errors {
            eprintln!("{err}");
        }
        std::process::exit(1);
    }

    let site_data_path = Path::new(SITE_DATA);
    let mut existing: Vec<serde_json::Value> = if site_data_path.exists() {
        let content = std::fs::read_to_string(site_data_path)
            .context("reading site_data.json")?;
        serde_json::from_str(&content).context("parsing site_data.json")?
    } else {
        Vec::new()
    };

    let existing_slugs: HashSet<String> = existing
        .iter()
        .filter_map(|v| v.get("slug").and_then(|s| s.as_str()).map(str::to_string))
        .collect();

    let mut added = 0usize;
    let mut skipped = 0usize;

    for item in validated {
        let slug = item
            .get("slug")
            .and_then(|s| s.as_str())
            .unwrap_or("")
            .to_string();
        let title = item
            .get("title")
            .and_then(|s| s.as_str())
            .unwrap_or("")
            .to_string();

        if existing_slugs.contains(&slug) {
            println!("  SKIP (already exists): {title} ({slug})");
            skipped += 1;
        } else {
            existing.push(item);
            added += 1;
        }
    }

    std::fs::write(
        site_data_path,
        serde_json::to_string_pretty(&existing).context("serialising site_data.json")?,
    )
    .context("writing site_data.json")?;

    for path in &temp_files {
        std::fs::remove_file(path)?;
    }

    println!("\nDone: {added} added, {skipped} skipped. temp/ cleared.");
    Ok(())
}

fn main() {
    if let Err(e) = ingest() {
        eprintln!("Error: {e:#}");
        std::process::exit(1);
    }
}
