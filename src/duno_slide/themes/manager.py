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


def get_available_themes() -> list[str]:
    """Return a list of all available theme names."""
    return _pm.hook.duno_slide_get_theme_name()


def get_theme_templates_dir(theme_name: str) -> Path:
    """Return the templates directory for the given theme."""
    names = _pm.hook.duno_slide_get_theme_name()
    templates_dirs = _pm.hook.duno_slide_get_templates_dir()

    for name, templates_dir in zip(names, templates_dirs):
        if name == theme_name:
            return templates_dir

    available = ", ".join(names)
    raise ValueError(f"Theme '{theme_name}' not found. Available themes: {available}")


def get_theme_static_dir(theme_name: str) -> Path:
    """Return the static directory for the given theme."""
    names = _pm.hook.duno_slide_get_theme_name()
    static_dirs = _pm.hook.duno_slide_get_static_dir()

    for name, static_dir in zip(names, static_dirs):
        if name == theme_name:
            return static_dir

    available = ", ".join(names)
    raise ValueError(f"Theme '{theme_name}' not found. Available themes: {available}")
