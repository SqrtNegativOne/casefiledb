"""CLI tool for AI agents to validate and import new works into the database."""

import json
import sys
from pathlib import Path
from typing import Any, List

from schema.database import init_db
from ingestion.importer import import_json

# Allowed values from models.py
ALLOWED_MEDIA_TYPES = {'book', 'movie', 'tv_show', 'tv_episode', 'game', 'short_story', 'play', 'podcast'}
ALLOWED_ROLES = {'protagonist', 'antagonist', 'victim', 'detective', 'bystander', 'unknown'}
ALLOWED_CAUSES = {
    'POISONED', 'SHOT', 'STABBED', 'CLUBBED', 'STRANGLED', 'DROWNED', 'BURNED', 'HANGED', 'FELL', 
    'CRUSHED', 'SUFFOCATED', 'EXPLODED', 'ELECTROCUTED', 'FROZEN', 'ILLNESS', 'EATEN', 'TORN_APART', 'OTHER'
}
ALLOWED_DEATH_TYPES = {'murder', 'attempted_murder', 'manslaughter', 'suicide', 'accident', 'natural_death', 'execution', 'unknown'}
ALLOWED_MOTIVES = {'greed_inheritance', 'greed_financial', 'blackmail', 'jealousy', 'revenge', 'ideology', 'self_defense', 'concealment', 'passion', 'unknown', 'other'}

def validate_data(data: List[dict]) -> List[str]:
    errors = []
    for i, item in enumerate(data):
        prefix = f"Item {i} ({item.get('title', 'Unknown')})"
        
        # Check required media fields
        for field in ['wikidata_id', 'title', 'media_type', 'persons', 'deaths']:
            if field not in item:
                errors.append(f"{prefix}: Missing required field '{field}'")
        
        if item.get('media_type') not in ALLOWED_MEDIA_TYPES:
            errors.append(f"{prefix}: Invalid media_type '{item.get('media_type')}'. Must be one of {ALLOWED_MEDIA_TYPES}")

        # Check persons
        person_names = set()
        for p in item.get('persons', []):
            name = p.get('name')
            if not name:
                errors.append(f"{prefix}: Person missing 'name'")
                continue
            person_names.add(name)
            if p.get('role_in_story') and p.get('role_in_story') not in ALLOWED_ROLES:
                errors.append(f"{prefix}: Invalid role '{p.get('role_in_story')}' for person '{name}'")

        # Check deaths
        for d in item.get('deaths', []):
            if d.get('cause') not in ALLOWED_CAUSES:
                errors.append(f"{prefix}: Invalid cause '{d.get('cause')}' in death record")
            if d.get('death_type') not in ALLOWED_DEATH_TYPES:
                errors.append(f"{prefix}: Invalid death_type '{d.get('death_type')}'")
            if d.get('motive') and d.get('motive') not in ALLOWED_MOTIVES:
                errors.append(f"{prefix}: Invalid motive '{d.get('motive')}'")
            
            # Link check
            for link_field in ['victim_name', 'killer_name']:
                name = d.get(link_field)
                if name and name not in person_names:
                    errors.append(f"{prefix}: '{link_field}' '{name}' not found in persons list")
                    
    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: python import_work.py <json_file_path>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"Error: File {json_path} not found.")
        sys.exit(1)

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            data = [data]
    except Exception as e:
        print(f"Error: Failed to parse JSON: {e}")
        sys.exit(1)

    print(f"Validating {len(data)} work(s)...")
    errors = validate_data(data)
    
    if errors:
        print("\nVALIDATION FAILED:")
        for err in errors:
            print(f" - {err}")
        print("\nPlease fix these errors and try again.")
        sys.exit(1)
    
    print("Validation successful. Importing to database...")
    init_db()
    results = import_json(str(json_path))
    
    print(f"\nIMPORT COMPLETE:")
    print(f" - Inserted: {results['inserted']}")
    print(f" - Updated:  {results['updated']}")
    print(f" - Skipped:  {results['skipped']}")
    
    if results['errors']:
        print("\nImport Errors occurred:")
        for err in results['errors']:
            print(f" - {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
