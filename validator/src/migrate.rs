/// One-shot migration: reads public/site_data.json, assigns person IDs to every
/// person record that lacks one, and writes the file back in place.
use anyhow::{Context, Result};

mod models;
use models::{MediaItem, MediaItemWire, SiteData};

const SITE_DATA: &str = "public/site_data.json";

fn run() -> Result<()> {
    let content = std::fs::read_to_string(SITE_DATA).context("reading site_data.json")?;
    let data: SiteData = serde_json::from_str(&content).context("parsing site_data.json")?;

    let mut migrated = SiteData::default();
    let mut count = 0usize;

    for wire in data.all_items() {
        let item = MediaItem::try_from(wire.clone())
            .with_context(|| format!("migrating '{}'", wire.title))?;
        migrated.push(MediaItemWire::from(item));
        count += 1;
    }

    std::fs::write(
        SITE_DATA,
        serde_json::to_string_pretty(&migrated).context("serialising")?,
    )
    .context("writing site_data.json")?;

    println!("Migrated {count} items — person IDs assigned.");
    Ok(())
}

fn main() {
    if let Err(e) = run() {
        eprintln!("Error: {e:#}");
        std::process::exit(1);
    }
}
