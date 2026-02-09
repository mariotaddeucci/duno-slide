from pathlib import Path

from duno_slide.themes.hookspecs import hookimpl

THEME_DIR = Path(__file__).parent


class DunossauroTheme:
    """Built-in 'dunossauro' theme for duno-slide."""

    @hookimpl
    def duno_slide_get_theme_name(self) -> str:
        return "dunossauro"

    @hookimpl
    def duno_slide_get_templates_dir(self) -> Path:
        return THEME_DIR / "templates"

    @hookimpl
    def duno_slide_get_static_dir(self) -> Path:
        return THEME_DIR / "templates" / "static"
