"""
Dataclasses describing the contents of .kicad_sch files.

SPDX-License-Identifier: EUPL-1.2
"""
import pathlib
from dataclasses import field
from typing import Annotated, ClassVar, Literal, Optional
from uuid import UUID, uuid4

from pydantic import validator
from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.color import Color
from edea.kicad.common import Image, Paper, PaperStandard, TitleBlock, VersionError
from edea.kicad.schematic.base import KicadSchExpr
from edea.kicad.schematic.shapes import Arc, Fill, FillColor, FillSimple, Pts, Stroke
from edea.kicad.schematic.symbol import Effects, LibSymbol, Property


@dataclass(config=PydanticConfig, eq=False)
class PinAssignment(KicadSchExpr):
    number: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    uuid: UUID = field(default_factory=uuid4)
    alternate: Optional[str] = None
    kicad_expr_tag_name: ClassVar[Literal["pin"]] = "pin"


@dataclass(config=PydanticConfig, eq=False)
class DefaultInstance(KicadSchExpr):
    reference: Annotated[str, m("kicad_always_quotes")]
    unit: int = 1
    value: Annotated[str, m("kicad_always_quotes")] = ""
    footprint: Annotated[str, m("kicad_always_quotes")] = ""


@dataclass(config=PydanticConfig, eq=False)
class SymbolUseInstancePath(KicadSchExpr):
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    reference: Annotated[str, m("kicad_always_quotes")]
    unit: int
    kicad_expr_tag_name: ClassVar[Literal["path"]] = "path"


@dataclass(config=PydanticConfig, eq=False)
class SymbolUseInstanceProject(KicadSchExpr):
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    paths: list[SymbolUseInstancePath] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["project"]] = "project"


@dataclass(config=PydanticConfig, eq=False)
class SymbolUseInstances(KicadSchExpr):
    projects: list[SymbolUseInstanceProject] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["instances"]] = "instances"


@dataclass(config=PydanticConfig, eq=False)
class SymbolUse(KicadSchExpr):
    lib_name: Optional[str] = None
    lib_id: Annotated[str, m("kicad_always_quotes")] = ""
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    mirror: Literal["x", "y", None] = None
    unit: int = 1
    convert: Optional[int] = None
    in_bom: Annotated[bool, m("kicad_bool_yes_no")] = True
    on_board: Annotated[bool, m("kicad_bool_yes_no")] = True
    dnp: Annotated[bool, m("kicad_bool_yes_no")] = False
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = False
    uuid: UUID = field(default_factory=uuid4)
    default_instance: Optional[DefaultInstance] = None
    properties: list[Property] = field(default_factory=list)
    pins: list[PinAssignment] = field(default_factory=list)
    instances: Optional[SymbolUseInstances] = None
    kicad_expr_tag_name: ClassVar[Literal["symbol"]] = "symbol"

    @validator("properties")
    @classmethod
    def _validate_properties(cls, properties):
        keys = [prop.key for prop in properties]
        if "Reference" not in keys:
            raise ValueError(
                '"reference" (Reference) is missing from symbol properties'
            )
        if "Value" not in keys:
            raise ValueError('"value" (Value) is missing from symbol properties')
        return properties

    reference: Annotated[str, m("exclude_from_files")]  # type: ignore
    value: Annotated[str, m("exclude_from_files")]  # type: ignore

    @property
    def reference(self) -> str:
        for prop in self.properties:
            if prop.key == "Reference":
                return prop.value
        raise KeyError("Reference not found")

    @reference.setter
    def reference(self, value: str):
        # when it's missing in __init__ it's a "property" object, we just
        # ignore that
        if isinstance(value, property):
            return
        for prop in self.properties:
            if prop.key == "Reference":
                prop.value = value
                break
        else:
            self.properties.append(
                Property(
                    key="Reference",
                    value=value,
                )
            )

    @property
    def value(self) -> str:
        for prop in self.properties:
            if prop.key == "Value":
                return prop.value
        raise KeyError("Value not found")

    @value.setter
    def value(self, value: str):
        # when it's missing in __init__ it's a "property" object, we just
        # ignore that
        if isinstance(value, property):
            return
        for prop in self.properties:
            if prop.key == "Value":
                prop.value = value
                break
        else:
            self.properties.append(
                Property(
                    key="Value",
                    value=value,
                )
            )


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
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = False
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    properties: list[Property] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["label"]] = "label"


@dataclass(config=PydanticConfig, eq=False)
class Text(LocalLabel):
    kicad_expr_tag_name: ClassVar[Literal["text"]] = "text"


@dataclass(config=PydanticConfig, eq=False)
class TextBox(KicadSchExpr):
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    size: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["text_box"]] = "text_box"


class LabelShape(StrEnum):
    # pylint: disable=duplicate-code
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    TRI_STATE = "tri_state"
    PASSIVE = "passive"


@dataclass(config=PydanticConfig, eq=False)
class GlobalLabel(KicadSchExpr):
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    shape: LabelShape = LabelShape.BIDIRECTIONAL
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = False
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    properties: list[Property] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class HierarchicalLabel(KicadSchExpr):
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    shape: LabelShape = LabelShape.BIDIRECTIONAL
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = False
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    properties: list[Property] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class NetclassFlag(KicadSchExpr):
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    length: float
    shape: Literal["rectangle", "round", "diamond", "dot"]
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = False
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    properties: list[Property] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class LibSymbols(KicadSchExpr):
    symbols: list[LibSymbol] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class SymbolInstancesPath(KicadSchExpr):
    path: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    reference: Annotated[str, m("kicad_always_quotes")]
    unit: int
    value: Annotated[str, m("kicad_always_quotes")]
    footprint: Annotated[str, m("kicad_always_quotes")]
    kicad_expr_tag_name: ClassVar[Literal["path"]] = "path"


@dataclass(config=PydanticConfig, eq=False)
class SymbolInstances(KicadSchExpr):
    paths: list[SymbolInstancesPath] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class PolylineTopLevel(KicadSchExpr):
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill | None = field(default=None)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["polyline"]] = "polyline"


@dataclass(config=PydanticConfig, eq=False)
class RectangleTopLevel(KicadSchExpr):
    start: tuple[float, float]
    end: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["rectangle"]] = "rectangle"


@dataclass(config=PydanticConfig, eq=False)
class ArcTopLevel(Arc):
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["arc"]] = "arc"


@dataclass(config=PydanticConfig, eq=False)
class CircleTopLevel(KicadSchExpr):
    center: tuple[float, float]
    radius: float
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["circle"]] = "circle"


@dataclass(config=PydanticConfig, eq=False)
class SheetPin(KicadSchExpr):
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    shape: Annotated[LabelShape, m("kicad_no_kw")] = LabelShape.BIDIRECTIONAL
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["pin"]] = "pin"


@dataclass(config=PydanticConfig, eq=False)
class SheetInstancesPath(KicadSchExpr):
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    page: Annotated[str, m("kicad_always_quotes")]
    kicad_expr_tag_name: ClassVar[Literal["path"]] = "path"


@dataclass(config=PydanticConfig, eq=False)
class SheetInstances(KicadSchExpr):
    paths: list[SheetInstancesPath] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["sheet_instances"]] = "sheet_instances"


@dataclass(config=PydanticConfig, eq=False)
class SubSheetInstanceProject(KicadSchExpr):
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    paths: list[SheetInstancesPath] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["project"]] = "project"


@dataclass(config=PydanticConfig, eq=False)
class SubSheetInstances(KicadSchExpr):
    projects: list[SubSheetInstanceProject] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["instances"]] = "instances"


@dataclass(config=PydanticConfig, eq=False, kw_only=True)
class Sheet(KicadSchExpr):
    at: tuple[float, float] = (15.24, 15.24)
    size: tuple[float, float] = (15.24, 15.24)
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = True
    stroke: Stroke = field(default_factory=Stroke)
    fill: FillColor = field(default_factory=FillColor)
    uuid: UUID = field(default_factory=uuid4)
    properties: list[Property] = field(default_factory=list)
    pins: list[SheetPin] = field(default_factory=list)
    instances: Optional[SubSheetInstances] = None

    @validator("properties")
    @classmethod
    def _validate_properties(cls, properties):
        keys = [prop.key for prop in properties]
        if "Sheetname" not in keys:
            raise ValueError('"name" (Sheetname) is missing from sheet properties')
        if "Sheetfile" not in keys:
            raise ValueError('"file" (Sheetfile) is missing from sheet properties')
        return properties

    name: Annotated[str, m("exclude_from_files")]  # type: ignore
    file: Annotated[pathlib.Path, m("exclude_from_files")]  # type: ignore

    @property
    def name(self) -> str:
        for prop in self.properties:
            if prop.key == "Sheetname":
                return prop.value
        raise KeyError("Sheetname not found")

    @name.setter
    def name(self, value: str):
        # when it's missing in __init__ it's a "property" object, we just
        # ignore that
        if isinstance(value, property):
            return
        for prop in self.properties:
            if prop.key == "Sheetname":
                prop.value = value
                break
        else:
            self.properties.append(
                Property(
                    key="Sheetname",
                    value=value,
                    at=(self.at[0], self.at[1] - 0.7116, 0),
                    effects=Effects(justify=["left", "bottom"]),
                )
            )

    @property
    def file(self) -> pathlib.Path:
        for prop in self.properties:
            if prop.key == "Sheetfile":
                return pathlib.Path(prop.value)
        raise KeyError("Sheetfile not found")

    @file.setter
    def file(self, value: pathlib.Path):
        # when it's missing in __init__ it's a "property" object, we just
        # ignore that
        if isinstance(value, property):
            return
        for prop in self.properties:
            if prop.key == "Sheetfile":
                prop.value = str(value)
                break
        else:
            self.properties.append(
                Property(
                    key="Sheetfile",
                    value=str(value),
                    at=(self.at[0], self.at[1] + self.size[1] + 0.5846, 0),
                    effects=Effects(justify=["left", "top"]),
                )
            )


@dataclass(config=PydanticConfig, eq=False)
class BusEntry(KicadSchExpr):
    at: tuple[float, float]
    size: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class Bus(KicadSchExpr):
    pts: Annotated[Pts, m("kicad_omits_default")] = field(
        default_factory=Pts,
    )
    stroke: Stroke = field(default_factory=Stroke)
    uuid: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class BusAlias(KicadSchExpr):
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    members: Annotated[list[str], m("kicad_always_quotes")] = field(
        default_factory=list,
    )


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
    arcs: list[ArcTopLevel] = field(default_factory=list)
    circles: list[CircleTopLevel] = field(default_factory=list)
    sheets: list[Sheet] = field(default_factory=list)
    symbols: list[SymbolUse] = field(default_factory=list)
    rectangles: list[RectangleTopLevel] = field(default_factory=list)
    wires: list[Wire] = field(default_factory=list)
    polylines: list[PolylineTopLevel] = field(default_factory=list)
    buses: list[Bus] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)
    junctions: list[Junction] = field(default_factory=list)
    no_connects: list[NoConnect] = field(default_factory=list)
    bus_entries: list[BusEntry] = field(default_factory=list)
    text_items: list[Text] = field(default_factory=list)
    text_boxes: list[TextBox] = field(default_factory=list)
    labels: list[LocalLabel] = field(default_factory=list)
    hierarchical_labels: list[HierarchicalLabel] = field(default_factory=list)
    global_labels: list[GlobalLabel] = field(default_factory=list)
    netclass_flags: list[NetclassFlag] = field(default_factory=list)
    bus_aliases: list[BusAlias] = field(default_factory=list)
    sheet_instances: SheetInstances | None = field(default=None)
    symbol_instances: Annotated[SymbolInstances, m("kicad_omits_default")] = field(
        default_factory=SymbolInstances,
    )

    kicad_expr_tag_name: ClassVar[Literal["kicad_sch"]] = "kicad_sch"
