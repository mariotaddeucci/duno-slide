import html
import re
import tomllib
from pathlib import Path

import markdown

from duno_slide.layout import Presentation

MD_EXTENSIONS = [
    "fenced_code",
    "tables",
    "nl2br",
    "sane_lists",
]

MD_EXTENSION_CONFIGS = {}


def _convert_mermaid_blocks(html_str: str) -> str:
    """Convert fenced mermaid code blocks into Mermaid.js-compatible elements."""
    pattern = r'<pre><code class="language-mermaid">(.*?)</code></pre>'

    def _unescape(match: re.Match) -> str:
        content = html.unescape(match.group(1))
        return f'<pre class="mermaid">{content}</pre>'

    return re.sub(pattern, _unescape, html_str, flags=re.DOTALL)


def _render_markdown(text: str) -> str:
    """Convert a markdown string to HTML."""
    md = markdown.Markdown(
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
    )
    html_result = md.convert(text)
    return _convert_mermaid_blocks(html_result)


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
