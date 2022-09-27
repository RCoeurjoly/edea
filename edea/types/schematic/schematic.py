"""
Dataclasses describing the contents of .kicad_sch files.

SPDX-License-Identifier: EUPL-1.2
"""
from dataclasses import field
from enum import Enum
from typing import Optional, Literal, Union
from uuid import UUID, uuid4

from pydantic import validator
from pydantic.color import Color
from pydantic.dataclasses import dataclass

from edea.types.config import PydanticConfig
from edea.types.schematic.base import KicadSchExpr
from edea.types.schematic.shapes import Pts, Stroke, Fill
from edea.types.schematic.symbol import Effects, LibSymbol, SymbolProperty


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
class PaperUser(KicadSchExpr):
    format: Literal["User"] = "User"
    width: float = 0
    height: float = 0
    kicad_expr_tag_name: Literal["paper"] = "paper"

    def as_dimensions_mm(self) -> tuple[float, float]:
        return (self.width, self.height)


@dataclass(config=PydanticConfig)
class Paper(KicadSchExpr):
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


@dataclass(config=PydanticConfig)
class PinAssignment(KicadSchExpr):
    number: str
    uuid: UUID = field(default_factory=uuid4)
    alternate: Optional[str] = None
    kicad_expr_tag_name: Literal["pin"] = "pin"


@dataclass(config=PydanticConfig)
class DefaultInstance(KicadSchExpr):
    reference: str
    unit: int = 1
    value: str = ""
    footprint: str = ""


@dataclass(config=PydanticConfig)
class IsFieldsAutoplaced(KicadSchExpr):
    kicad_expr_tag_name: Literal["fields_autoplaced"] = "fields_autoplaced"
    # holds no data, appears simply as "(fields_autoplaced)" with parens.
    # maybe there is a less ugly solution to this?


@dataclass(config=PydanticConfig)
class SymbolUse(KicadSchExpr):
    lib_id: str
    lib_name: Optional[str] = None
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    unit: int = 1
    convert: Optional[int] = None
    in_bom: bool = True
    on_board: bool = True
    mirror: Literal["x", "y", None] = None
    uuid: UUID = field(default_factory=uuid4)
    default_instance: Optional[DefaultInstance] = None
    property: list[SymbolProperty] = field(default_factory=list)
    pin: list[PinAssignment] = field(default_factory=list)
    fields_autoplaced: Optional[IsFieldsAutoplaced] = None
    kicad_expr_tag_name: Literal["symbol"] = "symbol"


@dataclass(config=PydanticConfig)
class Wire(KicadSchExpr):
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig)
class Junction(KicadSchExpr):
    at: tuple[float, float]
    diameter: float = 0
    color: Color = Color((0, 0, 0, 0))
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig)
class NoConnect(KicadSchExpr):
    at: tuple[float, float]
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig)
class LocalLabel(KicadSchExpr):
    text: str
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    fields_autoplaced: Optional[IsFieldsAutoplaced] = None
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["label"] = "label"


class LabelShape(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    TRI_STATE = "tri_state"
    PASSIVE = "passive"


@dataclass(config=PydanticConfig)
class GlobalLabel(KicadSchExpr):
    text: str
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    shape: LabelShape = LabelShape.BIDIRECTIONAL
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    property: list[SymbolProperty] = field(default_factory=list)
    fields_autoplaced: Optional[IsFieldsAutoplaced] = None


@dataclass(config=PydanticConfig)
class HierarchicalLabel(KicadSchExpr):
    text: str
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    shape: LabelShape = LabelShape.BIDIRECTIONAL
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    fields_autoplaced: Optional[IsFieldsAutoplaced] = None


@dataclass(config=PydanticConfig)
class LibSymbols(KicadSchExpr):
    symbol: list[LibSymbol] = field(default_factory=list)


@dataclass(config=PydanticConfig)
class TitleBlockComment(KicadSchExpr):
    number: int = 1
    text: str = ""
    kicad_expr_tag_name: Literal["comment"] = "comment"


@dataclass(config=PydanticConfig)
class TitleBlock(KicadSchExpr):
    title: str = ""
    date: str = ""
    rev: str = ""
    company: str = ""
    comment: list[TitleBlockComment] = field(default_factory=list)


@dataclass(config=PydanticConfig)
class SheetPath(KicadSchExpr):
    path: str = "/"
    page: str = "1"
    kicad_expr_tag_name: Literal["path"] = "path"


@dataclass(config=PydanticConfig)
class SheetInstances(KicadSchExpr):
    path: list[SheetPath] = field(default_factory=list)


@dataclass(config=PydanticConfig)
class SymbolInstancesPath(KicadSchExpr):
    path: str
    reference: str
    unit: int
    value: str
    footprint: str = ""
    kicad_expr_tag_name: Literal["path"] = "path"


@dataclass(config=PydanticConfig)
class SymbolInstances(KicadSchExpr):
    path: list[SymbolInstancesPath] = field(default_factory=list)


@dataclass(config=PydanticConfig)
class PolyLineTopLevel(KicadSchExpr):
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=Fill)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["polyline"] = "polyline"


@dataclass(config=PydanticConfig)
class FillColor(KicadSchExpr):
    color: Color = Color((0, 0, 0, 0))
    kicad_expr_tag_name: Literal["fill"] = "fill"


@dataclass(config=PydanticConfig)
class SheetPin(KicadSchExpr):
    name: str
    shape: LabelShape = LabelShape.BIDIRECTIONAL
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["pin"] = "pin"


@dataclass(config=PydanticConfig)
class Sheet(KicadSchExpr):
    at: tuple[float, float]
    size: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    fill: FillColor = field(default_factory=FillColor)
    uuid: UUID = field(default_factory=uuid4)
    property: list[SymbolProperty] = field(default_factory=list)
    pin: list[SheetPin] = field(default_factory=list)
    fields_autoplaced: Optional[IsFieldsAutoplaced] = None


@dataclass(config=PydanticConfig)
class BusEntry(KicadSchExpr):
    at: tuple[float, float]
    size: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig)
class Bus(KicadSchExpr):
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig)
class Image(KicadSchExpr):
    at: tuple[float, float]
    scale: Optional[float] = None
    uuid: UUID = field(default_factory=uuid4)
    data: list[str] = field(default_factory=list)


@dataclass(config=PydanticConfig)
class BusAlias(KicadSchExpr):
    name: str
    members: list[str] = field(default_factory=list)


@dataclass(config=PydanticConfig)
class Schematic(KicadSchExpr):
    version: int = 20211123

    @validator("version")
    def check_version(cls, v):
        if v != 20211123:
            raise ValueError(
                f"Only the stable KiCad 6 schematic file format, i.e. version '20211123', "
                f"is supported. Got '{v}'."
            )
        return v

    generator: str = "edea"
    uuid: UUID = field(default_factory=uuid4)
    title_block: Optional[TitleBlock] = None
    paper: Union[Paper, PaperUser] = field(default_factory=Paper)
    lib_symbols: LibSymbols = field(default_factory=LibSymbols)
    sheet: list[Sheet] = field(default_factory=list)
    symbol: list[SymbolUse] = field(default_factory=list)
    polyline: list[PolyLineTopLevel] = field(default_factory=list)
    wire: list[Wire] = field(default_factory=list)
    bus: list[Bus] = field(default_factory=list)
    image: list[Image] = field(default_factory=list)
    junction: list[Junction] = field(default_factory=list)
    no_connect: list[NoConnect] = field(default_factory=list)
    bus_entry: list[BusEntry] = field(default_factory=list)
    text: list[LocalLabel] = field(default_factory=list)
    label: list[LocalLabel] = field(default_factory=list)
    hierarchical_label: list[HierarchicalLabel] = field(default_factory=list)
    global_label: list[GlobalLabel] = field(default_factory=list)
    sheet_instances: SheetInstances = field(default_factory=SheetInstances)
    symbol_instances: SymbolInstances = field(default_factory=SymbolInstances)
    bus_alias: list[BusAlias] = field(default_factory=list)

    kicad_expr_tag_name: Literal["kicad_sch"] = "kicad_sch"
