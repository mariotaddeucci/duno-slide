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
    file: Annotated[
        Path, typer.Argument(help="Caminho do arquivo TOML da apresentação.")
    ],
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
    theme: Annotated[
        Optional[str],
        typer.Option(help="Tema da apresentação de exemplo."),
    ] = None,
):
    """Serve a apresentação de exemplo embutida."""
    from duno_slide.server import serve

    sample_file = Path(__file__).parent / "sample.toml"
    serve(sample_file, host=bind, port=port, theme_override=theme)


@app.command()
def export(
    file: Annotated[
        Path, typer.Argument(help="Caminho do arquivo TOML da apresentação.")
    ],
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
    file: Annotated[
        Path, typer.Argument(help="Caminho do arquivo TOML da apresentação.")
    ],
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


@app.command()
def validate(
    file: Annotated[
        Path, typer.Argument(help="Caminho do arquivo TOML da apresentação.")
    ],
):
    """Valida a estrutura de um arquivo TOML de apresentação."""
    import tomllib

    from pydantic import ValidationError

    from duno_slide.layout import Presentation

    if not file.exists():
        typer.echo(f"✗ Arquivo não encontrado: {file}", err=True)
        raise typer.Exit(1)

    try:
        with open(file, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        typer.echo(f"✗ Erro de sintaxe no TOML: {e}", err=True)
        raise typer.Exit(1)

    try:
        Presentation.model_validate(data)
    except ValidationError as e:
        typer.echo(f"✗ Arquivo inválido: {file}\n", err=True)
        for error in e.errors():
            loc = " → ".join(str(part) for part in error["loc"])
            msg = error["msg"]

            # Build context with field description if available
            ctx = error.get("ctx", {})
            lines = [f"  Campo: {loc}", f"  Erro:  {msg}"]

            if "expected" in ctx:
                lines.append(f"  Esperado: {ctx['expected']}")

            if "given" in ctx:
                lines.append(f"  Recebido: {ctx['given']}")

            # Try to get field description from the model schema
            field_description = _get_field_description(
                Presentation, error["loc"]
            )
            if field_description:
                lines.append(f"  Dica:  {field_description}")

            typer.echo("\n".join(lines), err=True)
            typer.echo("", err=True)

        raise typer.Exit(1)

    slide_count = len(data.get("slides", []))
    typer.echo(f"✓ Arquivo válido: {file} ({slide_count} slides)")


def _get_field_description(
    model: type, loc: tuple[int | str, ...]
) -> str | None:
    """Walk through nested Pydantic model schemas to find a field description."""
    from pydantic import BaseModel

    current_schema = model.model_json_schema(
        ref_template="{model}"
    )
    defs = current_schema.get("$defs", {})

    for i, part in enumerate(loc):
        if isinstance(part, int):
            # list index — dive into items schema
            items = current_schema.get("items")
            if isinstance(items, dict):
                current_schema = _resolve_ref(items, defs)
            continue

        # Discriminated union: resolve via anyOf / oneOf
        if "anyOf" in current_schema or "oneOf" in current_schema:
            variants = current_schema.get(
                "anyOf", current_schema.get("oneOf", [])
            )
            found = False
            for variant in variants:
                resolved = _resolve_ref(variant, defs)
                props = resolved.get("properties", {})
                if part in props:
                    current_schema = resolved
                    found = True
                    break
            if not found:
                return None

        props = current_schema.get("properties", {})
        if part not in props:
            return None

        field_schema = props[part]
        field_schema = _resolve_ref(field_schema, defs)

        # last part — return description
        if i == len(loc) - 1:
            return field_schema.get("description")

        current_schema = field_schema

    return None


def _resolve_ref(schema: dict, defs: dict) -> dict:
    """Resolve a $ref in a JSON schema."""
    if "$ref" in schema:
        ref_name = schema["$ref"]
        return defs.get(ref_name, schema)

    # Handle anyOf with a single $ref (common for Optional fields)
    if "anyOf" in schema:
        for option in schema["anyOf"]:
            if "$ref" in option:
                return defs.get(option["$ref"], schema)

    return schema
