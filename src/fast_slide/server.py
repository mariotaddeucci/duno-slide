from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from fast_slide.layout import SlideLayout

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = TEMPLATES_DIR / "static"


def render_presentation(
    slides: list[SlideLayout],
    title: str = "Fast Slide",
) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )
    template = env.get_template("base.html")
    return template.render(title=title, slides=slides)


class SlideHTTPHandler(SimpleHTTPRequestHandler):
    html_content: str = ""

    def do_GET(self):
        if self.path.startswith("/static/"):
            file_path = STATIC_DIR / self.path.removeprefix("/static/")
            if file_path.exists():
                self.send_response(200)
                if file_path.suffix == ".css":
                    self.send_header("Content-Type", "text/css; charset=utf-8")
                elif file_path.suffix == ".js":
                    self.send_header(
                        "Content-Type", "application/javascript; charset=utf-8"
                    )
                else:
                    self.send_header("Content-Type", "application/octet-stream")
                self.end_headers()
                self.wfile.write(file_path.read_bytes())
            else:
                self.send_error(404, "File not found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self.html_content.encode("utf-8"))


def serve(
    slides: list[SlideLayout],
    title: str = "Fast Slide",
    host: str = "localhost",
    port: int = 8765,
):
    html = render_presentation(slides, title)
    SlideHTTPHandler.html_content = html

    server = HTTPServer((host, port), SlideHTTPHandler)
    print(f"Serving presentation at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
