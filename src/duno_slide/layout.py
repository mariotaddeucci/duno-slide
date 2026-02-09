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
    layout: TLayout
    background: TBackgroundColors


class CoverTitleRightSlideLayout(BaseSlideLayout[Literal["cover_title_right"]]):
    title: str
    subtitle: str | None = None


class CoverTitleLeftSlideLayout(BaseSlideLayout[Literal["cover_title_left"]]):
    title: str
    subtitle: str | None = None


class DefaultSlideLayout(BaseSlideLayout[Literal["default"]]):
    title: str | None = None
    content: str | None = None
    vertical_align: Literal["top", "center", "bottom"] = "top"
    footer: str | None = None


class SummaryItem(BaseModel):
    title: str = ""
    description: str | None = None
    empty: bool = False


class SummarySlideLayout(BaseSlideLayout[Literal["summary"]]):
    title: str | None = None
    items: list[SummaryItem]
    footer: str | None = None

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
    title: str
    slides: list[SlideLayout]
    aspect_ratio: TAspectRatio = "16:9"
    theme: str = "dunossauro"
