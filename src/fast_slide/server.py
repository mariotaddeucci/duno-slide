import base64
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from fast_slide.layout import Presentation

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = TEMPLATES_DIR / "static"
FONTS_DIR = STATIC_DIR / "fonts"
VENDOR_DIR = STATIC_DIR / "vendor"

ASPECT_RATIOS = {
    "16:9": {"width": 1280, "height": 720},
    "4:3": {"width": 1024, "height": 768},
}


def _load_font_base64(filename: str) -> str:
    font_path = FONTS_DIR / filename
    if font_path.exists():
        return base64.b64encode(font_path.read_bytes()).decode("ascii")
    return ""


def _load_css_with_inlined_fonts(aspect_ratio: str) -> str:
    css_path = STATIC_DIR / "styles.css"
    css = css_path.read_text(encoding="utf-8")

    # Remove the Google Fonts import (we inline fonts)
    css = css.replace(
        "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');",
        "",
    )

    inter_b64 = _load_font_base64("inter-latin.woff2")
    jetbrains_b64 = _load_font_base64("jetbrains-mono-latin.woff2")

    font_faces = ""
    if inter_b64:
        font_faces += (
            "@font-face {\n"
            "  font-family: 'Inter';\n"
            "  font-style: normal;\n"
            "  font-weight: 100 900;\n"
            "  font-display: swap;\n"
            f"  src: url(data:font/woff2;base64,{inter_b64}) format('woff2');\n"
            "}\n"
        )
    if jetbrains_b64:
        font_faces += (
            "@font-face {\n"
            "  font-family: 'JetBrains Mono';\n"
            "  font-style: normal;\n"
            "  font-weight: 400 700;\n"
            "  font-display: swap;\n"
            f"  src: url(data:font/woff2;base64,{jetbrains_b64}) format('woff2');\n"
            "}\n"
        )

    dims = ASPECT_RATIOS[aspect_ratio]
    w, h = dims["width"], dims["height"]

    # Replace fixed slide dimensions with aspect ratio values
    css = css.replace("width: 1024px;", f"width: {w}px;")
    css = css.replace("height: 768px;", f"height: {h}px;")
    css = css.replace("size: 1024px 768px;", f"size: {w}px {h}px;")

    return font_faces + "\n" + css


def _load_highlight_css() -> str:
    """Load highlight.js CSS from vendor directory."""
    hljs_css_path = VENDOR_DIR / "github-dark.min.css"
    if hljs_css_path.exists():
        return hljs_css_path.read_text(encoding="utf-8")
    return ""


def _load_highlight_js() -> str:
    """Load highlight.js JavaScript from vendor directory."""
    hljs_js_path = VENDOR_DIR / "all-hljs.js"
    if hljs_js_path.exists():
        return hljs_js_path.read_text(encoding="utf-8")
    return ""


def render_presentation(presentation: Presentation) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )
    template = env.get_template("base.html")

    inline_css = _load_css_with_inlined_fonts(presentation.aspect_ratio)
    highlight_css = _load_highlight_css()
    highlight_js = _load_highlight_js()
    dims = ASPECT_RATIOS[presentation.aspect_ratio]

    return template.render(
        title=presentation.title,
        slides=presentation.slides,
        inline_css=inline_css,
        highlight_css=highlight_css,
        highlight_js=highlight_js,
        aspect_ratio=presentation.aspect_ratio,
        slide_width=dims["width"],
        slide_height=dims["height"],
    )


class SlideHTTPHandler(SimpleHTTPRequestHandler):
    html_content: str = ""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self.html_content.encode("utf-8"))


def serve(
    presentation: Presentation,
    host: str = "localhost",
    port: int = 8765,
):
    html = render_presentation(presentation=presentation)
    SlideHTTPHandler.html_content = html

    server = HTTPServer((host, port), SlideHTTPHandler)
    print(f"Serving presentation at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
