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
    help="Apresentações elegantes a partir de arquivos TOML.",
    add_completion=False,
    invoke_without_command=True,
)


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Mostra a versão e sai.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def host(
    file: Annotated[Path, typer.Argument(help="Caminho do arquivo TOML da apresentação.")],
    port: Annotated[int, typer.Option(help="Porta para servir.")] = 8765,
    bind: Annotated[str, typer.Option(help="Endereço para bind.")] = "localhost",
):
    """Serve a apresentação no navegador."""
    from duno_slide.server import serve

    serve(file, host=bind, port=port)


@app.command()
def sample(
    port: Annotated[int, typer.Option(help="Porta para servir.")] = 8765,
    bind: Annotated[str, typer.Option(help="Endereço para bind.")] = "localhost",
):
    """Serve a apresentação de exemplo embutida."""
    from duno_slide.server import serve

    sample_file = Path(__file__).parent / "sample.toml"
    serve(sample_file, host=bind, port=port)


@app.command()
def export(
    file: Annotated[Path, typer.Argument(help="Caminho do arquivo TOML da apresentação.")],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Caminho do arquivo de saída.")
    ] = Path("presentation.pdf"),
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Formato de exportação: pdf ou png.",
        ),
    ] = "pdf",
    width: Annotated[
        Optional[int], typer.Option(help="Largura customizada da viewport.")
    ] = None,
    height: Annotated[
        Optional[int], typer.Option(help="Altura customizada da viewport.")
    ] = None,
):
    """Exporta a apresentação para PDF ou imagens PNG usando Playwright."""
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
    file: Annotated[Path, typer.Argument(help="Caminho do arquivo TOML da apresentação.")],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Caminho do arquivo HTML de saída.")
    ] = Path("presentation.html"),
):
    """Renderiza a apresentação em um arquivo HTML único."""
    from duno_slide.loader import load_presentation
    from duno_slide.server import render_presentation

    presentation = load_presentation(file)
    html = render_presentation(presentation)
    output.write_text(html, encoding="utf-8")
    typer.echo(f"Salvo em {output}")
