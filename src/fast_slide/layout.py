from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

TBackgroundColors = Literal["white", "black", "red", "green", "yellow", "blue"]
TLayout = TypeVar("TLayout")


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


SlideLayout = Annotated[
    CoverTitleRightSlideLayout
    | CoverTitleLeftSlideLayout
    | DefaultSlideLayout,
    Field(discriminator="layout"),
]
