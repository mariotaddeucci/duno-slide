import threading
from pathlib import Path

from duno_slide.loader import load_presentation
from duno_slide.server import ASPECT_RATIOS, create_app


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

    import uvicorn

    presentation = load_presentation(file)

    dims = ASPECT_RATIOS[presentation.aspect_ratio]
    vw = width or dims["width"]
    vh = height or dims["height"]

    # Serve temporarily using FastAPI
    app = create_app(file)
    config = uvicorn.Config(app, host="127.0.0.1", port=0, log_level="error")
    server = uvicorn.Server(config)

    # Use a thread to run the server
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for server to start
    import time

    while not server.started:
        time.sleep(0.1)

    # Get the actual port
    port = server.servers[0].sockets[0].getsockname()[1]

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
        server.should_exit = True
