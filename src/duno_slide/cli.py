from pathlib import Path
from typing import Annotated, Optional

import typer


def _version_callback(value: bool) -> None:
    if value:
        from duno_slide import __version__

        typer.echo(f"duno-slide {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="duno-slide",
    help="Fast presentations from TOML files.",
    add_completion=False,
)


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Show the version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    pass


@app.command()
def host(
    file: Annotated[Path, typer.Argument(help="Path to the presentation TOML file.")],
    port: Annotated[int, typer.Option(help="Port to serve on.")] = 8765,
    bind: Annotated[str, typer.Option(help="Address to bind to.")] = "localhost",
):
    """Serve the presentation in the browser."""
    from duno_slide.server import serve

    serve(file, host=bind, port=port)


@app.command()
def export(
    file: Annotated[Path, typer.Argument(help="Path to the presentation TOML file.")],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output file path.")
    ] = Path("presentation.pdf"),
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Export format: pdf or png.",
        ),
    ] = "pdf",
    width: Annotated[
        Optional[int], typer.Option(help="Override viewport width.")
    ] = None,
    height: Annotated[
        Optional[int], typer.Option(help="Override viewport height.")
    ] = None,
):
    """Export the presentation to PDF or PNG images using Playwright."""
    from duno_slide.exporter import export_presentation

    export_presentation(
        file=file,
        output=output,
        format=format,
        width=width,
        height=height,
    )


@app.command()
def render(
    file: Annotated[Path, typer.Argument(help="Path to the presentation TOML file.")],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output HTML file path.")
    ] = Path("presentation.html"),
):
    """Render the presentation to a single HTML file."""
    from duno_slide.loader import load_presentation
    from duno_slide.server import render_presentation

    presentation = load_presentation(file)
    html = render_presentation(presentation)
    output.write_text(html, encoding="utf-8")
    typer.echo(f"Saved to {output}")
