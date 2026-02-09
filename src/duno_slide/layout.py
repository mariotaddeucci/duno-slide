from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

TBackgroundColors = Literal[
    "red",
    "green",
    "yellow",
    "blue",
    "lavender",
    "pink",
]
TLayout = TypeVar("TLayout")
TAspectRatio = Literal["16:9", "4:3"]


class BaseSlideLayout(BaseModel, Generic[TLayout]):
    layout: TLayout = Field(description="Tipo de layout do slide (cover_title_right, cover_title_left, default, summary).")
    background: TBackgroundColors = Field(description="Cor de fundo do slide. Valores aceitos: red, green, yellow, blue, lavender, pink.")


class CoverTitleRightSlideLayout(BaseSlideLayout[Literal["cover_title_right"]]):
    title: str = Field(description="Título principal exibido na capa.")
    subtitle: str | None = Field(default=None, description="Subtítulo opcional exibido abaixo do título.")


class CoverTitleLeftSlideLayout(BaseSlideLayout[Literal["cover_title_left"]]):
    title: str = Field(description="Título principal exibido na capa.")
    subtitle: str | None = Field(default=None, description="Subtítulo opcional exibido abaixo do título.")


class DefaultSlideLayout(BaseSlideLayout[Literal["default"]]):
    title: str | None = Field(default=None, description="Título do slide.")
    content: str | None = Field(default=None, description="Conteúdo do slide em formato Markdown.")
    vertical_align: Literal["top", "center", "bottom"] = Field(default="top", description="Alinhamento vertical do conteúdo. Valores aceitos: top, center, bottom.")
    footer: str | None = Field(default=None, description="Texto de rodapé do slide.")


class SummaryItem(BaseModel):
    title: str = Field(default="", description="Título do item do sumário.")
    description: str | None = Field(default=None, description="Descrição do item do sumário.")
    empty: bool = Field(default=False, description="Indica se o item é um espaço vazio para balanceamento de colunas.")


class SummarySlideLayout(BaseSlideLayout[Literal["summary"]]):
    title: str | None = Field(default=None, description="Título do slide de sumário.")
    items: list[SummaryItem] = Field(description="Lista de itens do sumário.")
    footer: str | None = Field(default=None, description="Texto de rodapé do slide.")

    @property
    def _balanced_items(self) -> list[SummaryItem]:
        """Return items padded to an even count for balanced 2-column grid."""
        items = list(self.items)
        if len(items) % 2 != 0:
            items.append(SummaryItem(empty=True))
        return items

    @property
    def left_column_items(self) -> list[SummaryItem]:
        balanced = self._balanced_items
        return balanced[: len(balanced) // 2]

    @property
    def right_column_items(self) -> list[SummaryItem]:
        balanced = self._balanced_items
        return balanced[len(balanced) // 2 :]


SlideLayout = Annotated[
    CoverTitleRightSlideLayout
    | CoverTitleLeftSlideLayout
    | DefaultSlideLayout
    | SummarySlideLayout,
    Field(discriminator="layout"),
]


class Presentation(BaseModel):
    title: str = Field(description="Título da apresentação.")
    slides: list[SlideLayout] = Field(description="Lista de slides da apresentação.")
    aspect_ratio: TAspectRatio = Field(default="16:9", description="Proporção de tela da apresentação. Valores aceitos: 16:9, 4:3.")
    theme: str = Field(default="dunossauro", description="Nome do tema utilizado na apresentação.")
