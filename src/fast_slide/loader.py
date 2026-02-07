import tomllib
from pathlib import Path

from fast_slide.layout import Presentation


def load_presentation(file_path: str | Path) -> Presentation:
    """Load a presentation from a TOML file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Presentation file not found: {path}")

    with open(path, "rb") as f:
        data = tomllib.load(f)

    title = data.get("title", "Untitled Presentation")
    aspect_ratio = data.get("aspect_ratio", "16:9")
    raw_slides = data.get("slides", [])

    slides = []
    for raw in raw_slides:
        slides.append(raw)

    return Presentation(title=title, aspect_ratio=aspect_ratio, slides=slides)
