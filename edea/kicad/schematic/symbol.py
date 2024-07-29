"""
Dataclasses describing the symbols found in "lib_symbols" of .kicad_sch files.
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
    """
    Different electrical types of a pin on a KiCad schematic.

    `KiCad hierarchical sheet pin \
        <https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/index.html#_hierarchical_sheet_pin_definition>`_
    """

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
    """
    Different graphical styles for pins on a KiCad schematic symbol.
    """

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
    """
    The number of the pin.

    :param text: The pin number as a text.
    :param effects: How the pin number is displayed.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("number").
    """

    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    effects: Effects = field(default_factory=Effects)
    kicad_expr_tag_name: ClassVar[Literal["number"]] = "number"


@dataclass(config=PydanticConfig, eq=False)
class PinName(KicadSchExpr):
    """
    The name of the pin.

    :param text: The pin name.
    :param effects: How the pin name is displayed.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("name").
    """

    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    effects: Effects = field(default_factory=Effects)
    kicad_expr_tag_name: ClassVar[Literal["name"]] = "name"


@dataclass(config=PydanticConfig, eq=False)
class Property(KicadSchExpr):
    """
    A key value pair for storing user defined information.

    :param key: The name of the property.
    :param value: The value of the property.
    :param at: The X-Y coordinates of the property.
    :param do_not_autoplace: Whether the autoplace of the key is allowed or not.
    :param show_name: Whether the key is shown or not.
    :param effects: How the text is displayed.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("property").
    """

    key: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    value: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    do_not_autoplace: Annotated[bool, m("kicad_kw_bool_empty")] = False
    show_name: Annotated[bool, m("kicad_kw_bool_empty")] = False
    effects: Effects = field(default_factory=Effects)
    kicad_expr_tag_name: ClassVar[Literal["property"]] = "property"


@dataclass(config=PydanticConfig, eq=False)
class PinAlternate(KicadSchExpr):
    """
    An alternate pin.

    :param name:
    :param electrical_type:
    :param graphic_style:
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("alternate").
    """

    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    electrical_type: Annotated[
        PinElectricalType, m("kicad_no_kw")
    ] = PinElectricalType.UNSPECIFIED
    graphic_style: Annotated[PinGraphicStyle, m("kicad_no_kw")] = PinGraphicStyle.LINE
    kicad_expr_tag_name: ClassVar[Literal["alternate"]] = "alternate"


@dataclass(config=PydanticConfig, eq=False)
class Pin(KicadSchExpr):
    """
    A pin.

    :param at: The X-Y coordinates and the rotation degree of the pin
    :param length: The length of the pin.
    :param hide: Whether the pin's text is hidden or not.
    :param name: The name of the pin.
    :param number: The number of the pin.
    :param alternates: A list of :py:class:`PinAlternate`.
    """

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
    """
    Pin's name settings.

     :param offset: The pin name offset for all pin names of the symbol. If not defined, the pin name offset is 0.508mm (0.020").
     :param hide: Whether the pin's name is hidden or not.
     :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("pin_names").
    """

    offset: Annotated[float, m("kicad_omits_default")] = 0
    hide: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["pin_names"]] = "pin_names"


@dataclass(config=PydanticConfig, eq=False)
class PinNumberSettings(KicadSchExpr):
    """
    Pins' numbers settings.

    :param hide: Whether the pin's number is hidden or not.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("pin_numbers").
    """

    hide: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["pin_numbers"]] = "pin_numbers"


@dataclass(config=PydanticConfig, eq=False)
class SymbolGraphicText(KicadSchExpr):
    """
    A graphic text element in a KiCad symbol.

    :param private: Whether the text is private or public.
    :param text: The text content.
    :param at: The X-Y coordinates and rotation angle of the text.
    :param effects: How the text is displayed.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("text").
    """

    private: Annotated[bool, m("kicad_kw_bool")] = False
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    at: tuple[float, float, int] = (0, 0, 0)
    effects: Effects = field(default_factory=Effects)
    kicad_expr_tag_name: ClassVar[Literal["text"]] = "text"


@dataclass(config=PydanticConfig, eq=False)
class SymbolGraphicTextBox(KicadSchExpr):
    """
    A graphic text box element in a KiCad symbol.

    :param text: The text content.
    :param at: The X-Y coordinates and rotation angle of the text box.
    :param size: The size of the text box.
    :param stroke: The stroke style of the text box.
    :param fill: The fill style of the text box.
    :param effects: How the text box is displayed.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("text_box").
    """

    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    size: tuple[float, float] = (0, 0)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillColor)
    effects: Effects = field(default_factory=Effects)
    kicad_expr_tag_name: ClassVar[Literal["text_box"]] = "text_box"


@dataclass(config=PydanticConfig, eq=False)
class SubSymbol(KicadSchExpr):
    """
    A sub-symbol within a KiCad symbol.

    :param name: The name of the sub-symbol.
    :param polylines: A list of :py:class:`Polyline` in the sub-symbol.
    :param text_items: A list of :py:class:`SymbolGraphicText` in the sub-symbol.
    :param rectangles: A list of :py:class:`~edea.kicad.schematic.shapes.Rectangle` in the sub-symbol.
    :param text_boxes: A list of :py:class:`SymbolGraphicTextBox`  in the sub-symbol.
    :param circles: A list of :py:class:`~edea.kicad.schematic.shapes.Circle` in the sub-symbol.
    :param arcs: A list of :py:class:`~edea.kicad.schematic.shapes.Arc` in the sub-symbol.
    :param pins: A list of :py:class:`Pin` in the sub-symbol.
    :param beziers: A list of :py:class:`~edea.kicad.schematic.shapes.Bezier` s in the sub-symbol.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("symbol").
    """

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
    """
    A library symbol in KiCad.

    `kiCad library symbol <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_symbols>`_

    :param name: The name of the library symbol.
    :param properties: A list of properties of the library symbol.
    :param power: Whether the symbol represents power or not.
    :param pin_numbers: The settings for pin numbers in the symbol.
    :param pin_names: The settings for pin names in the symbol.
    :param in_bom: Whether the symbol is included in the BOM or not.
    :param on_board: Whether the symbol is on the board or not.
    :param pins: A list of pins in the symbol.
    :param symbols: A list of sub-symbols in the symbol.
    :param polylines: A lst of polylines in the symbol.
    :param text_items: A list of graphic text items in the symbol.
    :param rectangles: A list of rectangles in the symbol.
    :param circles: A list of circles in the symbol.
    :param arcs: A list of arcs in the symbol.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("symbol").
    """

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
