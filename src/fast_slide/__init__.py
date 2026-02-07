from fast_slide.layout import (
    CoverTitleLeftSlideLayout,
    CoverTitleRightSlideLayout,
    DefaultSlideLayout,
)
from fast_slide.server import serve


def main() -> None:
    slides = [
        CoverTitleRightSlideLayout(
            layout="cover_title_right",
            background="red",
            title="A rede",
            subtitle="e as coisas dando errado!",
        ),
        CoverTitleLeftSlideLayout(
            layout="cover_title_left",
            background="yellow",
            title="Clientes",
            subtitle="Existem tantos...",
        ),
        DefaultSlideLayout(
            layout="default",
            background="yellow",
            vertical_align="center",
            content="<p>Esta aula <strong>não vai ensinar HTTP em si</strong>. Isso já foi abordado em lives anteriores.</p>",
            footer="Antes de tudo",
        ),
        DefaultSlideLayout(
            layout="default",
            background="red",
            title="Timeouts",
            vertical_align="top",
            content=(
                "<p>Vamos pensar em um exemplo extremamente simples:</p>"
                "<pre>import httpx\n\n"
                "def get_page_content():\n"
                "    return httpx.get('https://httpbin.org/delay/6').text\n\n"
                "get_page_content()</pre>"
                "<p>O que acontece se a resposta não voltar no tempo que esperamos?</p>"
                '<pre>File "live_http_client/.venv/.../httpx/_transports/default.py",\n'
                "    line 118, in map_httpcore_exceptions\n"
                "      raise mapped_exc(message) from exc\n"
                "httpx.ReadTimeout: timed out</pre>"
            ),
        ),
    ]

    serve(slides, title="Demo Presentation")
