from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from fast_slide.layout import Presentation

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = TEMPLATES_DIR / "static"

ASPECT_RATIOS = {
    "16:9": {"width": 1280, "height": 720},
    "4:3": {"width": 1024, "height": 768},
}


def _load_css(aspect_ratio: str) -> str:
    css_path = STATIC_DIR / "styles.css"
    css = css_path.read_text(encoding="utf-8")

    dims = ASPECT_RATIOS[aspect_ratio]
    w, h = dims["width"], dims["height"]

    # Replace fixed slide dimensions with aspect ratio values
    css = css.replace("width: 1024px;", f"width: {w}px;")
    css = css.replace("height: 768px;", f"height: {h}px;")
    css = css.replace("size: 1024px 768px;", f"size: {w}px {h}px;")

    return css


def render_presentation(presentation: Presentation) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )
    template = env.get_template("base.html")

    inline_css = _load_css(presentation.aspect_ratio)
    highlight_css_url = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css"
    highlight_js_url = (
        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"
    )
    dims = ASPECT_RATIOS[presentation.aspect_ratio]

    return template.render(
        title=presentation.title,
        slides=presentation.slides,
        inline_css=inline_css,
        highlight_css_url=highlight_css_url,
        highlight_js_url=highlight_js_url,
        aspect_ratio=presentation.aspect_ratio,
        slide_width=dims["width"],
        slide_height=dims["height"],
    )


class SlideHTTPHandler(SimpleHTTPRequestHandler):
    presentation_path: Path | None = None

    def do_GET(self):
        if self.presentation_path is None:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Presentation path not configured.")
            return

        try:
            from fast_slide.loader import load_presentation

            presentation = load_presentation(self.presentation_path)
            html = render_presentation(presentation=presentation)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        except Exception as exc:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            message = f"Failed to load presentation: {exc}"
            self.wfile.write(message.encode("utf-8"))


def serve(
    file: Path,
    host: str = "localhost",
    port: int = 8765,
):
    SlideHTTPHandler.presentation_path = file

    server = HTTPServer((host, port), SlideHTTPHandler)
    print(f"Serving presentation at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
