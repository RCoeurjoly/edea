from dataclasses import field
from typing import Annotated, ClassVar, Literal, Optional, Union
from uuid import UUID, uuid4

from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.base import KicadExpr
from edea.kicad.color import Color


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
    color: Annotated[Color, m("kicad_omits_default")] = (0, 0, 0, 0.0)


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
    format: Annotated[Literal["User"], m("kicad_no_kw", "kicad_always_quotes")] = "User"
    width: Annotated[float, m("kicad_no_kw")] = 0
    height: Annotated[float, m("kicad_no_kw")] = 0
    kicad_expr_tag_name: ClassVar[Literal["paper"]] = "paper"

    def as_dimensions_mm(self) -> tuple[float, float]:
        return (self.width, self.height)


@dataclass(config=PydanticConfig, eq=False)
class PaperStandard(KicadExpr):
    format: Annotated[
        PaperFormat, m("kicad_no_kw", "kicad_always_quotes")
    ] = PaperFormat.A4
    orientation: Annotated[
        PaperOrientation, m("kicad_no_kw", "kicad_omits_default")
    ] = PaperOrientation.LANDSCAPE
    kicad_expr_tag_name: ClassVar[Literal["paper"]] = "paper"

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

    kicad_expr_tag_name: ClassVar[Literal["arc"]] = "arc"


@dataclass(config=PydanticConfig, eq=False)
class XY(KicadExpr):
    x: Annotated[float, m("kicad_no_kw")]
    y: Annotated[float, m("kicad_no_kw")]


@dataclass(config=PydanticConfig, eq=False)
class Pts(KicadExpr):
    xys: list[XY] = field(default_factory=list)
    arcs: list[PolygonArc] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class Image(KicadExpr):
    at: tuple[float, float]
    scale: Optional[float] = None
    uuid: UUID = field(default_factory=uuid4)
    data: list[str] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class TitleBlockComment(KicadExpr):
    number: Annotated[int, m("kicad_no_kw")] = 1
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    kicad_expr_tag_name: ClassVar[Literal["comment"]] = "comment"


@dataclass(config=PydanticConfig, eq=False)
class TitleBlock(KicadExpr):
    title: Annotated[str, m("kicad_omits_default")] = ""
    date: Annotated[str, m("kicad_omits_default")] = ""
    rev: Annotated[str, m("kicad_omits_default")] = ""
    company: Annotated[str, m("kicad_omits_default")] = ""
    comments: Annotated[list[TitleBlockComment], m("kicad_omits_default")] = field(
        default_factory=list,
    )


@dataclass(config=PydanticConfig, eq=False)
class Font(KicadExpr):
    face: Optional[str] = None
    size: tuple[float, float] = (1.27, 1.27)
    thickness: Annotated[Optional[float], m("kicad_omits_default")] = None
    bold: Annotated[bool, m("kicad_kw_bool")] = False
    italic: Annotated[bool, m("kicad_kw_bool")] = False
    color: Annotated[tuple[int, int, int, float], m("kicad_omits_default")] = (
        0,
        0,
        0,
        1.0,
    )


@dataclass(config=PydanticConfig, eq=False)
class Effects(KicadExpr):
    font: Font = field(default_factory=Font)
    justify: Annotated[
        list[Literal["left", "right", "top", "bottom", "mirror"]],
        m("kicad_omits_default"),
    ] = field(
        default_factory=list,
    )
    hide: Annotated[bool, m("kicad_kw_bool")] = False
    href: Annotated[Optional[str], m("kicad_always_quotes")] = None


class VersionError(ValueError):
    """
    Source file was produced with an unsupported KiCad version.
    """
