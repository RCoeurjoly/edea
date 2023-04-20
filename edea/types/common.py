from dataclasses import field
from enum import Enum
from typing import Literal, Optional, Union
from uuid import UUID, uuid4

from pydantic import root_validator
from pydantic.dataclasses import dataclass

from edea.types.base import KicadExpr
from edea.types.config import PydanticConfig


class PaperFormat(str, Enum):
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


class PaperOrientation(str, Enum):
    LANDSCAPE = ""
    PORTRAIT = "portrait"


@dataclass(config=PydanticConfig)
class PaperUser(KicadExpr):
    format: Literal["User"] = "User"
    width: float = 0
    height: float = 0
    kicad_expr_tag_name: Literal["paper"] = "paper"

    def as_dimensions_mm(self) -> tuple[float, float]:
        return (self.width, self.height)


@dataclass(config=PydanticConfig)
class PaperStandard(KicadExpr):
    format: PaperFormat = PaperFormat.A4
    orientation: PaperOrientation = PaperOrientation.LANDSCAPE

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


@dataclass(config=PydanticConfig)
class PolygonArc(KicadExpr):
    start: tuple[float, float]
    mid: tuple[float, float]
    end: tuple[float, float]

    kicad_expr_tag_name: Literal["arc"] = "arc"


@dataclass(config=PydanticConfig)
class XY(KicadExpr):
    x: float
    y: float


@dataclass(config=PydanticConfig)
class Pts(KicadExpr):
    xy: list[XY] = field(default_factory=list)
    arc: list[PolygonArc] = field(default_factory=list)


@dataclass(config=PydanticConfig)
class Image(KicadExpr):
    at: tuple[float, float]
    scale: Optional[float] = None
    uuid: UUID = field(default_factory=uuid4)
    data: list[str] = field(default_factory=list)


@dataclass(config=PydanticConfig)
class TitleBlockComment(KicadExpr):
    number: int = 1
    text: str = ""
    kicad_expr_tag_name: Literal["comment"] = "comment"


@dataclass(config=PydanticConfig)
class TitleBlock(KicadExpr):
    title: str = ""
    date: str = ""
    rev: str = ""
    company: str = ""
    comment: list[TitleBlockComment] = field(default_factory=list)


class JustifyHoriz(str, Enum):
    LEFT = "left"
    CENTER = ""
    RIGHT = "right"


class JustifyVert(str, Enum):
    TOP = "top"
    CENTER = ""
    BOTTOM = "bottom"


@dataclass(config=PydanticConfig)
class Justify(KicadExpr):
    horizontal: JustifyHoriz = JustifyHoriz.CENTER
    vertical: JustifyVert = JustifyVert.CENTER
    mirror: bool = False

    @root_validator(pre=True)
    def validate(cls, fields: dict):
        """
        The values can be passed in any order so we have to find the right
        field for them.
        """
        correct_fields = {}
        for v in fields.values():
            if v in (JustifyHoriz.LEFT, JustifyHoriz.RIGHT):
                correct_fields["horizontal"] = v
            elif v in (JustifyVert.TOP, JustifyVert.BOTTOM):
                correct_fields["vertical"] = v
            elif v == "mirror":
                correct_fields["mirror"] = True

        return correct_fields


@dataclass(config=PydanticConfig)
class Font(KicadExpr):
    size: tuple[float, float] = (1.27, 1.27)
    thickness: Optional[float] = None
    italic: bool = False
    bold: bool = False


@dataclass(config=PydanticConfig)
class Effects(KicadExpr):
    font: Font = field(default_factory=Font)
    justify: Justify = field(default_factory=Justify)
    hide: bool = False


class VersionError(ValueError):
    """
    Source file was produced with an unsupported KiCad version.
    """
