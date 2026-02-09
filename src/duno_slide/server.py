from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

from duno_slide.layout import Presentation
from duno_slide.themes.manager import get_theme_static_dir, get_theme_templates_dir

ASPECT_RATIOS = {
    "16:9": {"width": 1280, "height": 720},
    "4:3": {"width": 1024, "height": 768},
}


def _load_css(aspect_ratio: str, theme: str, static_url: str = "/static") -> str:
    static_dir = get_theme_static_dir(theme)
    css_path = static_dir / "styles.css"
    css = css_path.read_text(encoding="utf-8")

    dims = ASPECT_RATIOS[aspect_ratio]
    w, h = dims["width"], dims["height"]

    # Replace fixed slide dimensions with aspect ratio values
    css = css.replace("width: 1024px;", f"width: {w}px;")
    css = css.replace("height: 768px;", f"height: {h}px;")
    css = css.replace("size: 1024px 768px;", f"size: {w}px {h}px;")

    # Rewrite relative url() references to use the static URL prefix
    css = css.replace("url('vendor/", f"url('{static_url}/vendor/")

    return css


def render_presentation(presentation: Presentation, static_url: str = "/static") -> str:
    templates_dir = get_theme_templates_dir(presentation.theme)
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,
    )
    template = env.get_template("base.html")

    inline_css = _load_css(presentation.aspect_ratio, presentation.theme, static_url)
    dims = ASPECT_RATIOS[presentation.aspect_ratio]

    return template.render(
        title=presentation.title,
        slides=presentation.slides,
        inline_css=inline_css,
        static_url=static_url,
        aspect_ratio=presentation.aspect_ratio,
        slide_width=dims["width"],
        slide_height=dims["height"],
    )


def create_app(
    file: Path,
    theme_override: str | None = None,
) -> FastAPI:
    app = FastAPI()

    from duno_slide.loader import load_presentation

    presentation = load_presentation(file)
    if theme_override:
        presentation = presentation.model_copy(update={"theme": theme_override})

    static_dir = get_theme_static_dir(presentation.theme)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def index():
        reloaded = load_presentation(file)
        if theme_override:
            current = reloaded.model_copy(update={"theme": theme_override})
        else:
            current = reloaded
        return render_presentation(presentation=current, static_url="/static")

    return app


def serve(
    file: Path,
    host: str = "localhost",
    port: int = 8765,
    theme_override: str | None = None,
):
    app = create_app(file, theme_override=theme_override)
    print(f"Serving presentation at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    uvicorn.run(app, host=host, port=port, log_level="warning")
