"""
Dataclasses describing the symbols found in "lib_symbols" of .kicad_sch files.

SPDX-License-Identifier: EUPL-1.2
"""

from dataclasses import field
from typing import Annotated, ClassVar, Literal

from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.common import Effects, Stroke
from edea.kicad.schematic.base import KicadSchExpr
from edea.kicad.schematic.shapes import (
    Arc,
    Bezier,
    Circle,
    Fill,
    FillColor,
    Polyline,
    Rectangle,
)


class PinElectricalType(StrEnum):
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    TRI_STATE = "tri_state"
    PASSIVE = "passive"
    FREE = "free"
    UNSPECIFIED = "unspecified"
    POWER_IN = "power_in"
    POWER_OUT = "power_out"
    OPEN_COLLECTOR = "open_collector"
    OPEN_EMITTER = "open_emitter"
    NO_CONNECT = "no_connect"


class PinGraphicStyle(StrEnum):
    LINE = "line"
    INVERTED = "inverted"
    CLOCK = "clock"
    INVERTED_CLOCK = "inverted_clock"
    INPUT_LOW = "input_low"
    CLOCK_LOW = "clock_low"
    OUTPUT_LOW = "output_low"
    EDGE_CLOCK_HIGH = "edge_clock_high"
    NON_LOGIC = "non_logic"


@dataclass(config=PydanticConfig, eq=False)
class PinNumber(KicadSchExpr):
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    effects: Effects = field(default_factory=Effects)
    kicad_expr_tag_name: ClassVar[Literal["number"]] = "number"


@dataclass(config=PydanticConfig, eq=False)
class PinName(KicadSchExpr):
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    effects: Effects = field(default_factory=Effects)
    kicad_expr_tag_name: ClassVar[Literal["name"]] = "name"


@dataclass(config=PydanticConfig, eq=False)
class Property(KicadSchExpr):
    key: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    value: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    do_not_autoplace: Annotated[bool, m("kicad_kw_bool_empty")] = False
    show_name: Annotated[bool, m("kicad_kw_bool_empty")] = False
    effects: Effects = field(default_factory=Effects)
    kicad_expr_tag_name: ClassVar[Literal["property"]] = "property"


@dataclass(config=PydanticConfig, eq=False)
class PinAlternate(KicadSchExpr):
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    electrical_type: Annotated[
        PinElectricalType, m("kicad_no_kw")
    ] = PinElectricalType.UNSPECIFIED
    graphic_style: Annotated[PinGraphicStyle, m("kicad_no_kw")] = PinGraphicStyle.LINE
    kicad_expr_tag_name: ClassVar[Literal["alternate"]] = "alternate"


@dataclass(config=PydanticConfig, eq=False)
class Pin(KicadSchExpr):
    electrical_type: Annotated[
        PinElectricalType, m("kicad_no_kw")
    ] = PinElectricalType.UNSPECIFIED
    graphic_style: Annotated[PinGraphicStyle, m("kicad_no_kw")] = PinGraphicStyle.LINE
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    length: float = 0
    hide: Annotated[bool, m("kicad_kw_bool")] = False
    name: PinName = field(default_factory=PinName)
    number: PinNumber = field(default_factory=PinNumber)
    alternates: list[PinAlternate] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class PinNameSettings(KicadSchExpr):
    offset: Annotated[float, m("kicad_omits_default")] = 0
    hide: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["pin_names"]] = "pin_names"


@dataclass(config=PydanticConfig, eq=False)
class PinNumberSettings(KicadSchExpr):
    hide: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["pin_numbers"]] = "pin_numbers"


@dataclass(config=PydanticConfig, eq=False)
class SymbolGraphicText(KicadSchExpr):
    private: Annotated[bool, m("kicad_kw_bool")] = False
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    at: tuple[float, float, int] = (0, 0, 0)
    effects: Effects = field(default_factory=Effects)
    kicad_expr_tag_name: ClassVar[Literal["text"]] = "text"


@dataclass(config=PydanticConfig, eq=False)
class SymbolGraphicTextBox(KicadSchExpr):
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    size: tuple[float, float] = (0, 0)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillColor)
    effects: Effects = field(default_factory=Effects)
    kicad_expr_tag_name: ClassVar[Literal["text_box"]] = "text_box"


@dataclass(config=PydanticConfig, eq=False)
class SubSymbol(KicadSchExpr):
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    polylines: list[Polyline] = field(default_factory=list)
    text_items: list[SymbolGraphicText] = field(default_factory=list)
    rectangles: list[Rectangle] = field(default_factory=list)
    text_boxes: list[SymbolGraphicTextBox] = field(default_factory=list)
    circles: list[Circle] = field(default_factory=list)
    arcs: list[Arc] = field(default_factory=list)
    pins: list[Pin] = field(default_factory=list)
    beziers: list[Bezier] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["symbol"]] = "symbol"


@dataclass(config=PydanticConfig, eq=False)
class LibSymbol(KicadSchExpr):
    name: Annotated[str, m("kicad_no_kw")]
    properties: list[Property] = field(default_factory=list)
    power: Annotated[bool, m("kicad_kw_bool_empty")] = False
    pin_numbers: Annotated[PinNumberSettings, m("kicad_omits_default")] = field(
        default_factory=PinNumberSettings,
    )
    pin_names: Annotated[PinNameSettings, m("kicad_omits_default")] = field(
        default_factory=PinNameSettings,
    )
    in_bom: Annotated[bool, m("kicad_bool_yes_no")] = True
    on_board: Annotated[bool, m("kicad_bool_yes_no")] = True
    pins: list[Pin] = field(default_factory=list)
    symbols: list[SubSymbol] = field(default_factory=list)
    polylines: list[Polyline] = field(default_factory=list)
    text_items: list[SymbolGraphicText] = field(default_factory=list)
    rectangles: list[Rectangle] = field(default_factory=list)
    circles: list[Circle] = field(default_factory=list)
    arcs: list[Arc] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["symbol"]] = "symbol"
