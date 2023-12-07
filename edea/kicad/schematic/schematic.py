"""
Dataclasses describing the contents of .kicad_sch files.

SPDX-License-Identifier: EUPL-1.2
"""
from dataclasses import field
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import validator
from pydantic.dataclasses import dataclass

from edea.kicad.color import Color
from edea.kicad.common import Image, Paper, PaperStandard, TitleBlock, VersionError
from edea.kicad.config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad.schematic.base import KicadSchExpr
from edea.kicad.schematic.shapes import (
    Arc,
    Fill,
    FillSimple,
    FillColor,
    Pts,
    Stroke,
)
from edea.kicad.schematic.symbol import Effects, LibSymbol, Property
from edea.kicad.str_enum import StrEnum


@dataclass(config=PydanticConfig, eq=False)
class PinAssignment(KicadSchExpr):
    number: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    uuid: UUID = field(default_factory=uuid4)
    alternate: Optional[str] = None
    kicad_expr_tag_name: Literal["pin"] = "pin"


@dataclass(config=PydanticConfig, eq=False)
class DefaultInstance(KicadSchExpr):
    reference: str = field(metadata=m("kicad_always_quotes"))
    unit: int = 1
    value: str = field(default="", metadata=m("kicad_always_quotes"))
    footprint: str = field(default="", metadata=m("kicad_always_quotes"))


@dataclass(config=PydanticConfig, eq=False)
class SymbolUseInstancePath(KicadSchExpr):
    name: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    reference: str = field(metadata=m("kicad_always_quotes"))
    unit: int = 1
    value: str | None = field(default=None, metadata=m("kicad_always_quotes"))
    footprint: str | None = field(default=None, metadata=m("kicad_always_quotes"))
    kicad_expr_tag_name: Literal["path"] = "path"


@dataclass(config=PydanticConfig, eq=False)
class SymbolUseInstanceProject(KicadSchExpr):
    name: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    path: list[SymbolUseInstancePath] = field(default_factory=list)
    kicad_expr_tag_name: Literal["project"] = "project"


@dataclass(config=PydanticConfig, eq=False)
class SymbolUseInstances(KicadSchExpr):
    project: list[SymbolUseInstanceProject] = field(default_factory=list)
    kicad_expr_tag_name: Literal["instances"] = "instances"


@dataclass(config=PydanticConfig, eq=False)
class SymbolUse(KicadSchExpr):
    lib_name: Optional[str] = None
    lib_id: str = field(default="", metadata=m("kicad_always_quotes"))
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    mirror: Literal["x", "y", None] = None
    unit: int = 1
    convert: Optional[int] = None
    in_bom: bool = field(default=True, metadata=m("kicad_bool_yes_no"))
    on_board: bool = field(default=True, metadata=m("kicad_bool_yes_no"))
    dnp: bool = field(default=False, metadata=m("kicad_bool_yes_no"))
    fields_autoplaced: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    uuid: UUID = field(default_factory=uuid4)
    default_instance: Optional[DefaultInstance] = None
    property: list[Property] = field(default_factory=list)
    pin: list[PinAssignment] = field(default_factory=list)
    instances: SymbolUseInstances | None = field(default=None)
    kicad_expr_tag_name: Literal["symbol"] = "symbol"


@dataclass(config=PydanticConfig, eq=False)
class Wire(KicadSchExpr):
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class Junction(KicadSchExpr):
    at: tuple[float, float]
    diameter: float = 0
    color: Color = (0, 0, 0, 0.0)
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class NoConnect(KicadSchExpr):
    at: tuple[float, float]
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class LocalLabel(KicadSchExpr):
    text: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    fields_autoplaced: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    property: list[Property] = field(default_factory=list)
    kicad_expr_tag_name: Literal["label"] = "label"


@dataclass(config=PydanticConfig, eq=False)
class Text(LocalLabel):
    kicad_expr_tag_name: Literal["text"] = "text"


@dataclass(config=PydanticConfig, eq=False)
class TextBox(KicadSchExpr):
    text: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    size: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["text_box"] = "text_box"


class LabelShape(StrEnum):
    # pylint: disable=duplicate-code
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    TRI_STATE = "tri_state"
    PASSIVE = "passive"


@dataclass(config=PydanticConfig, eq=False)
class GlobalLabel(KicadSchExpr):
    text: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    shape: LabelShape = LabelShape.BIDIRECTIONAL
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    fields_autoplaced: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    property: list[Property] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class HierarchicalLabel(KicadSchExpr):
    text: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    shape: LabelShape = LabelShape.BIDIRECTIONAL
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    fields_autoplaced: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    property: list[Property] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class NetclassFlag(KicadSchExpr):
    text: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    length: float
    shape: Literal["rectangle", "round", "diamond", "dot"]
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    fields_autoplaced: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    property: list[Property] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class LibSymbols(KicadSchExpr):
    symbol: list[LibSymbol] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class SymbolInstancesPath(KicadSchExpr):
    path: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    reference: str = field(metadata=m("kicad_always_quotes"))
    unit: int
    value: str = field(metadata=m("kicad_always_quotes"))
    footprint: str = field(metadata=m("kicad_always_quotes"))
    kicad_expr_tag_name: Literal["path"] = "path"


@dataclass(config=PydanticConfig, eq=False)
class SymbolInstances(KicadSchExpr):
    path: list[SymbolInstancesPath] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class PolylineTopLevel(KicadSchExpr):
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill | None = field(default=None)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["polyline"] = "polyline"


@dataclass(config=PydanticConfig, eq=False)
class RectangleTopLevel(KicadSchExpr):
    start: tuple[float, float]
    end: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["rectangle"] = "rectangle"


@dataclass(config=PydanticConfig, eq=False)
class ArcTopLevel(Arc):
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["arc"] = "arc"


@dataclass(config=PydanticConfig, eq=False)
class CircleTopLevel(KicadSchExpr):
    center: tuple[float, float]
    radius: float
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["circle"] = "circle"


@dataclass(config=PydanticConfig, eq=False)
class SheetPin(KicadSchExpr):
    name: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    shape: LabelShape = field(
        default=LabelShape.BIDIRECTIONAL, metadata=m("kicad_no_kw")
    )
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["pin"] = "pin"


@dataclass(config=PydanticConfig, eq=False)
class SheetInstancePath(KicadSchExpr):
    name: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    page: str = field(metadata=m("kicad_always_quotes"))
    kicad_expr_tag_name: Literal["path"] = "path"


@dataclass(config=PydanticConfig, eq=False)
class SheetInstanceProject(KicadSchExpr):
    name: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    kicad_expr_tag_name: Literal["project"] = "project"


@dataclass(config=PydanticConfig, eq=False)
class SheetInstances(KicadSchExpr):
    path: list[SheetInstancePath] = field(default_factory=list)
    kicad_expr_tag_name: Literal["sheet_instances"] = "sheet_instances"


@dataclass(config=PydanticConfig, eq=False)
class SubSheetInstancePath(KicadSchExpr):
    name: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    page: str = field(metadata=m("kicad_always_quotes"))
    kicad_expr_tag_name: Literal["path"] = "path"


@dataclass(config=PydanticConfig, eq=False)
class SubSheetInstanceProject(KicadSchExpr):
    name: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    path: list[SubSheetInstancePath] = field(default_factory=list)
    kicad_expr_tag_name: Literal["project"] = "project"


@dataclass(config=PydanticConfig, eq=False)
class SubSheetInstances(KicadSchExpr):
    project: list[SubSheetInstanceProject] = field(default_factory=list)
    kicad_expr_tag_name: Literal["instances"] = "instances"


@dataclass(config=PydanticConfig, eq=False)
class Sheet(KicadSchExpr):
    at: tuple[float, float]
    size: tuple[float, float]
    fields_autoplaced: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    stroke: Stroke = field(default_factory=Stroke)
    fill: FillColor = field(default_factory=FillColor)
    uuid: UUID = field(default_factory=uuid4)
    property: list[Property] = field(default_factory=list)
    pin: list[SheetPin] = field(default_factory=list)
    instances: SubSheetInstances | None = field(default=None)


@dataclass(config=PydanticConfig, eq=False)
class BusEntry(KicadSchExpr):
    at: tuple[float, float]
    size: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class Bus(KicadSchExpr):
    pts: Pts = field(default_factory=Pts, metadata=m("kicad_omits_default"))
    stroke: Stroke = field(default_factory=Stroke)
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class BusAlias(KicadSchExpr):
    name: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    members: list[str] = field(default_factory=list, metadata=m("kicad_always_quotes"))


@dataclass(config=PydanticConfig, eq=False)
class Schematic(KicadSchExpr):
    version: Literal["20230121"] = "20230121"

    @validator("version")
    @classmethod
    def check_version(cls, v) -> Literal["20230121"]:
        if v == "20230121":
            return v
        raise VersionError(
            "Only the stable KiCad 7 schematic file format i.e. '20230121' is"
            f" supported. Got '{v}'. Please open and re-save the file with"
            " KiCad 7 if you can."
        )

    generator: str = "edea"
    uuid: UUID = field(default_factory=uuid4)
    paper: Paper = field(default_factory=PaperStandard)
    title_block: Optional[TitleBlock] = None
    lib_symbols: LibSymbols = field(default_factory=LibSymbols)
    arc: list[ArcTopLevel] = field(default_factory=list)
    circle: list[CircleTopLevel] = field(default_factory=list)
    sheet: list[Sheet] = field(default_factory=list)
    symbol: list[SymbolUse] = field(default_factory=list)
    rectangle: list[RectangleTopLevel] = field(default_factory=list)
    wire: list[Wire] = field(default_factory=list)
    polyline: list[PolylineTopLevel] = field(default_factory=list)
    bus: list[Bus] = field(default_factory=list)
    image: list[Image] = field(default_factory=list)
    junction: list[Junction] = field(default_factory=list)
    no_connect: list[NoConnect] = field(default_factory=list)
    bus_entry: list[BusEntry] = field(default_factory=list)
    text: list[Text] = field(default_factory=list)
    text_box: list[TextBox] = field(default_factory=list)
    label: list[LocalLabel] = field(default_factory=list)
    hierarchical_label: list[HierarchicalLabel] = field(default_factory=list)
    global_label: list[GlobalLabel] = field(default_factory=list)
    netclass_flag: list[NetclassFlag] = field(default_factory=list)
    bus_alias: list[BusAlias] = field(default_factory=list)
    sheet_instances: SheetInstances | None = field(default=None)
    symbol_instances: SymbolInstances = field(
        default_factory=SymbolInstances, metadata=m("kicad_omits_default")
    )

    kicad_expr_tag_name: Literal["kicad_sch"] = "kicad_sch"
