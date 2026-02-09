from pathlib import Path

import pluggy

from duno_slide.themes.dunossauro import DunossauroTheme
from duno_slide.themes.hookspecs import ThemeSpec


def _create_plugin_manager() -> pluggy.PluginManager:
    """Create and configure the pluggy plugin manager."""
    pm = pluggy.PluginManager("duno_slide")
    pm.add_hookspecs(ThemeSpec)
    pm.register(DunossauroTheme())
    pm.load_setuptools_entrypoints("duno_slide")
    return pm


_pm = _create_plugin_manager()


def _build_theme_map() -> dict[str, int]:
    """Build a mapping of theme name to its index in the hook results."""
    names = _pm.hook.duno_slide_get_theme_name()
    return {name: idx for idx, name in enumerate(names)}


def get_available_themes() -> list[str]:
    """Return a list of all available theme names."""
    return _pm.hook.duno_slide_get_theme_name()


def _get_theme_index(theme_name: str) -> int:
    """Return the index for the given theme, raising ValueError if not found."""
    theme_map = _build_theme_map()
    if theme_name not in theme_map:
        available = ", ".join(theme_map.keys())
        raise ValueError(
            f"Theme '{theme_name}' not found. Available themes: {available}"
        )
    return theme_map[theme_name]


def get_theme_templates_dir(theme_name: str) -> Path:
    """Return the templates directory for the given theme."""
    idx = _get_theme_index(theme_name)
    return _pm.hook.duno_slide_get_templates_dir()[idx]


def get_theme_static_dir(theme_name: str) -> Path:
    """Return the static directory for the given theme."""
    idx = _get_theme_index(theme_name)
    return _pm.hook.duno_slide_get_static_dir()[idx]
