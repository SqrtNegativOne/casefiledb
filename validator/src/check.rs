/// Validates every item in public/site_data.json against the Rust schema.
/// Prints a summary and exits non-zero on any error.
use anyhow::{Context, Result};

mod models;
use models::{MediaItem, SiteData};

fn run() -> Result<()> {
    let path = "public/site_data.json";
    let content = std::fs::read_to_string(path).context("reading site_data.json")?;
    let data: SiteData = serde_json::from_str(&content).context("parsing site_data.json")?;

    let mut errors: Vec<String> = Vec::new();
    let mut ok = 0usize;

    for item in data.all_items() {
        match MediaItem::try_from(item.clone()) {
            Ok(_) => ok += 1,
            Err(e) => errors.push(format!("  {}: {e}", item.title)),
        }
    }

    if errors.is_empty() {
        println!("All {ok} items valid.");
        Ok(())
    } else {
        for e in &errors {
            eprintln!("{e}");
        }
        anyhow::bail!("{} item(s) failed validation", errors.len());
    }
}

fn main() {
    if let Err(e) = run() {
        eprintln!("Error: {e:#}");
        std::process::exit(1);
    }
}
