"""
Dataclasses describing the contents of .kicad_sch files.

SPDX-License-Identifier: EUPL-1.2
"""
from dataclasses import field
from enum import Enum
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import validator
from pydantic.color import Color
from pydantic.dataclasses import dataclass

from edea.types.common import Image, Paper, PaperStandard, TitleBlock, VersionError
from edea.types.config import PydanticConfig
from edea.types.schematic.base import KicadSchExpr
from edea.types.schematic.shapes import Fill, Pts, Stroke
from edea.types.schematic.symbol import Effects, LibSymbol, SymbolProperty


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
    # pylint: disable=duplicate-code
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
class BusAlias(KicadSchExpr):
    name: str
    members: list[str] = field(default_factory=list)


@dataclass(config=PydanticConfig)
class Schematic(KicadSchExpr):
    version: Literal["20211123"] = "20211123"

    @validator("version")
    @classmethod
    def check_version(cls, v) -> Literal["20211123"]:
        v = str(v)
        if v != "20211123":
            raise VersionError(
                "Only the stable KiCad 6 schematic file format, i.e. version"
                f" '20211123', is supported. Got '{v}'."
            )
        return v

    generator: str = "edea"
    uuid: UUID = field(default_factory=uuid4)
    title_block: Optional[TitleBlock] = None
    paper: Paper = field(default_factory=PaperStandard)
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
