from dataclasses import field
from typing import Literal, Optional, Union
from uuid import UUID, uuid4

from pydantic.dataclasses import dataclass

from edea.kicad.base import KicadExpr
from edea.kicad.color import Color
from edea.kicad.config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad.str_enum import StrEnum


class StrokeType(StrEnum):
    DEFAULT = "default"
    DASH = "dash"
    DASH_DOT = "dash_dot"
    DASH_DOT_DOT = "dash_dot_dot"
    DOT = "dot"
    SOLID = "solid"


@dataclass(config=PydanticConfig, eq=False)
class Stroke(KicadExpr):
    width: float = 0
    type: StrokeType = StrokeType.DEFAULT
    color: Color = field(default=(0, 0, 0, 0.0), metadata=m("kicad_omits_default"))


class PaperFormat(StrEnum):
    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    A4 = "A4"
    A5 = "A5"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    US_LETTER = "USLetter"
    US_LEGAL = "USLegal"
    US_LEDGER = "USLedger"


class PaperOrientation(StrEnum):
    LANDSCAPE = ""
    PORTRAIT = "portrait"


@dataclass(config=PydanticConfig, eq=False)
class PaperUser(KicadExpr):
    format: Literal["User"] = field(
        default="User", metadata=m("kicad_no_kw", "kicad_always_quotes")
    )
    width: float = field(default=0, metadata=m("kicad_no_kw"))
    height: float = field(default=0, metadata=m("kicad_no_kw"))
    kicad_expr_tag_name: Literal["paper"] = "paper"

    def as_dimensions_mm(self) -> tuple[float, float]:
        return (self.width, self.height)


@dataclass(config=PydanticConfig, eq=False)
class PaperStandard(KicadExpr):
    format: PaperFormat = field(
        default=PaperFormat.A4, metadata=m("kicad_no_kw", "kicad_always_quotes")
    )
    orientation: PaperOrientation = field(
        default=PaperOrientation.LANDSCAPE,
        metadata=m("kicad_no_kw", "kicad_omits_default"),
    )
    kicad_expr_tag_name: Literal["paper"] = "paper"

    def as_dimensions_mm(self) -> tuple[float, float]:
        lookup = {
            PaperFormat.A5: (148, 210),
            PaperFormat.A4: (210, 297),
            PaperFormat.A3: (297, 420),
            PaperFormat.A2: (420, 594),
            PaperFormat.A1: (594, 841),
            PaperFormat.A0: (841, 1189),
            PaperFormat.A: (8.5 * 25.4, 11 * 25.4),
            PaperFormat.B: (11 * 25.4, 17 * 25.4),
            PaperFormat.C: (17 * 25.4, 22 * 25.4),
            PaperFormat.D: (22 * 25.4, 34 * 25.4),
            PaperFormat.E: (34 * 25.4, 44 * 25.4),
            PaperFormat.US_LETTER: (8.5 * 25.4, 11 * 25.4),
            PaperFormat.US_LEGAL: (8.5 * 25.4, 14 * 25.4),
            PaperFormat.US_LEDGER: (11 * 25.4, 17 * 25.4),
        }
        width, height = lookup[self.format]
        if self.orientation == PaperOrientation.LANDSCAPE:
            width, height = (height, width)
        return (width, height)


Paper = Union[PaperUser, PaperStandard]


@dataclass(config=PydanticConfig, eq=False)
class PolygonArc(KicadExpr):
    start: tuple[float, float]
    mid: tuple[float, float]
    end: tuple[float, float]

    kicad_expr_tag_name: Literal["arc"] = "arc"


@dataclass(config=PydanticConfig, eq=False)
class XY(KicadExpr):
    x: float = field(metadata=m("kicad_no_kw"))
    y: float = field(metadata=m("kicad_no_kw"))


@dataclass(config=PydanticConfig, eq=False)
class Pts(KicadExpr):
    xy: list[XY] = field(default_factory=list)
    arc: list[PolygonArc] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class Image(KicadExpr):
    at: tuple[float, float]
    scale: Optional[float] = None
    uuid: UUID = field(default_factory=uuid4)
    data: list[str] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class TitleBlockComment(KicadExpr):
    number: int = field(default=1, metadata=m("kicad_no_kw"))
    text: str = field(default="", metadata=m("kicad_no_kw", "kicad_always_quotes"))
    kicad_expr_tag_name: Literal["comment"] = "comment"


@dataclass(config=PydanticConfig, eq=False)
class TitleBlock(KicadExpr):
    title: str = field(default="", metadata=m("kicad_omits_default"))
    date: str = field(default="", metadata=m("kicad_omits_default"))
    rev: str = field(default="", metadata=m("kicad_omits_default"))
    company: str = field(default="", metadata=m("kicad_omits_default"))
    comment: list[TitleBlockComment] = field(
        default_factory=list, metadata=m("kicad_omits_default")
    )


@dataclass(config=PydanticConfig, eq=False)
class Font(KicadExpr):
    face: Optional[str] = None
    size: tuple[float, float] = (1.27, 1.27)
    thickness: Optional[float] = field(default=None, metadata=m("kicad_omits_default"))
    bold: bool = field(default=False, metadata=m("kicad_kw_bool"))
    italic: bool = field(default=False, metadata=m("kicad_kw_bool"))
    color: tuple[int, int, int, float] = field(
        default=(0, 0, 0, 1.0), metadata=m("kicad_omits_default")
    )


@dataclass(config=PydanticConfig, eq=False)
class Effects(KicadExpr):
    font: Font = field(default_factory=Font)
    justify: list[Literal["left", "right", "top", "bottom", "mirror"]] = field(
        default_factory=list, metadata=m("kicad_omits_default")
    )
    hide: bool = field(default=False, metadata=m("kicad_kw_bool"))
    href: Optional[str] = field(default=None, metadata=m("kicad_always_quotes"))


class VersionError(ValueError):
    """
    Source file was produced with an unsupported KiCad version.
    """
