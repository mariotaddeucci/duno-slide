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
    "extra",
]

MD_EXTENSION_CONFIGS = {}


def _convert_mermaid_blocks(html_str: str) -> str:
    """Convert fenced mermaid code blocks into Mermaid.js-compatible elements."""
    pattern = r'<pre><code class="language-mermaid">(.*?)</code></pre>'

    def _unescape(match: re.Match) -> str:
        content = html.unescape(match.group(1))
        return f'<pre class="mermaid">{content}</pre>'

    return re.sub(pattern, _unescape, html_str, flags=re.DOTALL)


def _process_grid_syntax(text: str) -> str:
    """
    Process custom grid syntax in markdown.

    Converts:
    ::: grid
    ::: card
    Content
    :::
    ::: card
    Content
    :::
    :::

    Into HTML with grid classes.
    """
    lines = text.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a grid start
        if line.strip().startswith("::: grid"):
            # Extract column count if specified
            cols_match = re.search(r"cols-(\d+)", line)
            cols = cols_match.group(1) if cols_match else "2"

            # Find the matching end :::
            grid_lines = []
            i += 1
            depth = 1

            while i < len(lines) and depth > 0:
                current = lines[i]
                if current.strip() == ":::":
                    depth -= 1
                    if depth == 0:
                        break
                elif current.strip().startswith("::: "):
                    depth += 1
                grid_lines.append(current)
                i += 1

            # Now process cards within grid_lines
            cards = []
            card_content = []
            in_card = False

            for grid_line in grid_lines:
                if grid_line.strip() == "::: card":
                    if in_card and card_content:
                        cards.append("\n".join(card_content))
                        card_content = []
                    in_card = True
                elif grid_line.strip() == ":::" and in_card:
                    if card_content:
                        cards.append("\n".join(card_content))
                        card_content = []
                    in_card = False
                elif in_card:
                    card_content.append(grid_line)

            # Add any remaining card content
            if card_content:
                cards.append("\n".join(card_content))

            # Build the grid HTML
            result.append(f'<div class="grid grid-cols-{cols}">')
            for card in cards:
                result.append('<div class="grid-card">')
                result.append(card)
                result.append("</div>")
            result.append("</div>")
        else:
            result.append(line)

        i += 1

    return "\n".join(result)


def _render_markdown(text: str) -> str:
    """Convert a markdown string to HTML."""
    # First, process custom grid syntax before markdown conversion
    text = _process_grid_syntax(text)

    md = markdown.Markdown(
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
    )
    html_result = md.convert(text)

    # Post-process: convert markdown inside grid cards
    html_result = _process_grid_card_markdown(html_result)

    return _convert_mermaid_blocks(html_result)


def _process_grid_card_markdown(html: str) -> str:
    """Process markdown content inside grid cards."""
    # Find all grid-card divs and convert their markdown content
    pattern = r'<div class="grid-card">\s*(.*?)\s*</div>'

    # Create a single markdown instance to reuse
    md = markdown.Markdown(
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
    )

    def convert_card_content(match: re.Match) -> str:
        content = match.group(1)
        # If content doesn't contain HTML tags, it's likely markdown
        if not re.search(r"<[^>]+>", content):
            md.reset()  # Reset the parser state
            converted = md.convert(content)
            return f'<div class="grid-card">{converted}</div>'
        return match.group(0)

    return re.sub(pattern, convert_card_content, html, flags=re.DOTALL)


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
