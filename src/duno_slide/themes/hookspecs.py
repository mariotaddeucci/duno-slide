from pathlib import Path

import pluggy

hookspec = pluggy.HookspecMarker("duno_slide")
hookimpl = pluggy.HookimplMarker("duno_slide")


class ThemeSpec:
    """Hook specifications for duno-slide themes."""

    @hookspec
    def duno_slide_get_theme_name(self) -> str:  # type: ignore[bad-return]
        """Return the name of this theme."""

    @hookspec
    def duno_slide_get_templates_dir(self) -> Path:  # type: ignore[bad-return]
        """Return the path to the Jinja2 templates directory for this theme."""

    @hookspec
    def duno_slide_get_static_dir(self) -> Path:  # type: ignore[bad-return]
        """Return the path to the static files directory for this theme."""
