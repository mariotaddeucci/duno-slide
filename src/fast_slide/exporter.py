import threading
from http.server import HTTPServer
from pathlib import Path

from fast_slide.loader import load_presentation
from fast_slide.server import ASPECT_RATIOS, SlideHTTPHandler, render_presentation


def export_presentation(
    file: Path,
    output: Path,
    format: str = "pdf",
    width: int | None = None,
    height: int | None = None,
):
    """Export a presentation to PDF or PNG using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit(
            "Playwright is required for export.\n"
            "Install it with: pip install playwright && playwright install chromium"
        )

    presentation = load_presentation(file)
    html = render_presentation(presentation)

    dims = ASPECT_RATIOS[presentation.aspect_ratio]
    vw = width or dims["width"]
    vh = height or dims["height"]

    # Serve temporarily on a random port
    SlideHTTPHandler.html_content = html
    server = HTTPServer(("127.0.0.1", 0), SlideHTTPHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": vw, "height": vh})
            page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")

            if format == "pdf":
                output_path = output.with_suffix(".pdf")
                page.pdf(
                    path=str(output_path),
                    width=f"{vw}px",
                    height=f"{vh}px",
                    print_background=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                )
                print(f"PDF exported to {output_path}")

            elif format == "png":
                # Export each slide as a separate PNG
                slides = page.query_selector_all(".slide")
                output_dir = output.parent / output.stem
                output_dir.mkdir(parents=True, exist_ok=True)

                for i, slide in enumerate(slides, 1):
                    slide_path = output_dir / f"slide_{i:03d}.png"
                    slide.screenshot(path=str(slide_path))
                    print(f"Slide {i} exported to {slide_path}")

                print(f"All slides exported to {output_dir}/")
            else:
                raise ValueError(f"Unsupported format: {format}. Use 'pdf' or 'png'.")

            browser.close()
    finally:
        server.shutdown()
