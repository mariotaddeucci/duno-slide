import tomllib
from pathlib import Path

import markdown

from fast_slide.layout import Presentation

MD_EXTENSIONS = [
    "fenced_code",
    "tables",
    "nl2br",
    "sane_lists",
]

MD_EXTENSION_CONFIGS = {}


def _render_markdown(text: str) -> str:
    """Convert a markdown string to HTML."""
    md = markdown.Markdown(
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
    )
    return md.convert(text)


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
        if "content" in raw and raw["content"]:
            raw["content"] = _render_markdown(raw["content"])
        slides.append(raw)

    return Presentation(title=title, aspect_ratio=aspect_ratio, slides=slides)
