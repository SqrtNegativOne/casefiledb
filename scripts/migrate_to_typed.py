"""Migrate site_data.json from a flat array to typed entity collections."""
import json
from pathlib import Path

TYPE_TO_KEY: dict[str, str] = {
    "book": "books",
    "game": "games",
    "movie": "movies",
    "tv_episode": "tv_episodes",
    "tv_show": "tv_shows",
    "short_story": "short_stories",
    "play": "plays",
    "podcast": "podcasts",
}


def migrate(path: Path) -> None:
    """Read the flat array and write a typed-collections object."""
    raw = path.read_text(encoding="utf-8")
    items: list[dict] = json.loads(raw)

    result: dict[str, list] = {key: [] for key in TYPE_TO_KEY.values()}
    for item in items:
        media_type = item.get("media_type")
        key = TYPE_TO_KEY.get(media_type)
        if key is None:
            raise ValueError(
                f"Unknown media_type {media_type!r} in item {item.get('slug')!r}"
            )
        result[key].append(item)

    out = json.dumps(result, ensure_ascii=False, indent=2)
    path.write_text(out, encoding="utf-8")

    totals = {k: len(v) for k, v in result.items() if v}
    print("Migration complete:", totals)


if __name__ == "__main__":
    migrate(Path("public/site_data.json"))
