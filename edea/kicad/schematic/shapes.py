"""
Dataclasses describing the graphic items found in .kicad_sch files.
"""

from dataclasses import field
from typing import Annotated, ClassVar, Literal, Optional
from uuid import UUID

from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.common import Pts, Stroke
from edea.kicad.schematic.base import KicadSchExpr


class FillType(StrEnum):
    """
    Different types of fills.
    """

    NONE = "none"
    """
    No fill.
    """
    OUTLINE = "outline"
    """
    Fill the outline of the object.
    """
    BACKGROUND = "background"
    """
    Fill the background of the object.
    """


@dataclass(config=PydanticConfig, eq=False)
class FillSimple(KicadSchExpr):
    """
    A simple fill style.

    `KiCad fill <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_fill_definition>`_

    :param type: How the object is filled.
    :cvar kicad_expr_tag_name: The tag name for KiCad expression.
    """

    type: FillType = FillType.BACKGROUND
    kicad_expr_tag_name: ClassVar[Literal["fill"]] = "fill"


@dataclass(config=PydanticConfig, eq=False)
class FillColor(KicadSchExpr):
    """
    A fill style with a specific color.

    `KiCad fill <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_fill_definition>`_

    :param color: The RGBA color value for the fill.
    :cvar kicad_expr_tag_name: The tag name for KiCad expression.
    """

    color: tuple[int, int, int, float] = (0, 0, 0, 0)
    kicad_expr_tag_name: ClassVar[Literal["fill"]] = "fill"


@dataclass(config=PydanticConfig, eq=False)
class FillTypeColor(KicadSchExpr):
    """
    A color fill style with a specific color.

    `KiCad fill <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_fill_definition>`_

    :param type: The type of fill.
    :param color: The RGBA color value for the fill.
    :cvar kicad_expr_tag_name: The tag name for KiCad expression.
    """

    type: Literal["color"] = "color"
    color: tuple[int, int, int, float] = (0, 0, 0, 0)
    kicad_expr_tag_name: ClassVar[Literal["fill"]] = "fill"


Fill = FillSimple | FillColor | FillTypeColor


@dataclass(config=PydanticConfig, eq=False)
class Polyline(KicadSchExpr):
    """
    A polyline that defines one or more
    graphical lines that may or may not define a polygon.

    `KiCad polyline <https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/index.html#_graphical_line_section>`_

    :param pts: The list of X-Y coordinates of the line(s).
    :param stroke: The stroke style of the polygon formed by the lines.
    :param fill: How the polygon is filled.
    :param uuid: The unique identifier of the polyline.

    .. note::
        The `uuid` field was added in 20231120 (KiCad 8).

    .. note::
        The `fill` field became optional in 20231120 (KiCad 8).

    """

    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Annotated[Optional[Fill], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[Literal["polyline"]] = "polyline"


@dataclass(config=PydanticConfig, eq=False)
class Bezier(KicadSchExpr):
    """
    A graphic cubic bezier curve.

    `KiCad bezier <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_symbol_curve>`_

    :param pts: The list of X-Y coordinates of each point of the curve.
    :param stroke: The stroke style of the curve outline.
    :param fill: How the curve is filled.
    """

    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)
    kicad_expr_tag_name: ClassVar[Literal["bezier"]] = "bezier"


@dataclass(config=PydanticConfig, eq=False)
class Rectangle(KicadSchExpr):
    """
    A rectangle.

    `KiCad rectangle <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_symbol_rectangle>`_

    :param start: The X-Y coordinates of the upper left corner of the rectangle.
    :param end: The X-Y coordinates of the low right corner of the rectangle.
    :param stroke: The line width and style of the rectangle.
    :param fill: How the rectangle is filled.
    :param uuid: The unique identifier of the rectangle.

    .. note::
        The `uuid` field was added in 20231120 (KiCad 8).
    """

    start: tuple[float, float]
    end: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[Literal["rectangle"]] = "rectangle"


@dataclass(config=PydanticConfig, eq=False)
class Circle(KicadSchExpr):
    """
    A circle.

    `KiCad circle <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_symbol_circle>`_

    :param center: The coordinates of the center of the circle.
    :param radius: The radius of the circle.
    :param stroke: The line width and style of the circle.
    :param fill: How the circle is filled.
    :param uuid: The unique identifier of the rectangle.

    .. note::
        The `uuid` field was added in 20231120 (KiCad 8).

    """

    center: tuple[float, float]
    radius: float
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[Literal["circle"]] = "circle"


@dataclass(config=PydanticConfig, eq=False)
class Radius(KicadSchExpr):
    """
    A radius.

    :param at: The X-Y coordinates of the radius.
    :param length: The length of the radius.
    :param angles: The rotation angle of the radius.
    """

    at: tuple[float, float]
    length: float
    angles: tuple[float, float]
    kicad_expr_tag_name: ClassVar[Literal["radius"]] = "radius"


@dataclass(config=PydanticConfig, eq=False)
class Arc(KicadSchExpr):
    """
    An arc.

    `KiCad arc <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_symbol_arc>`_

    :param start: The X-Y coordinates of the start position of the arc radius.
    :param mid: The X-Y coordinates of the midpoint along the arc.
    :param end: The X-Y coordinates of the end position of the arc radius.
    :param radius: The radius of the arc.
    :param stroke: The stroke style of the arc.
    :param fill: How the arc is filled.
    :param uuid: The unique identifier of the rectangle.

    .. note::
        The `uuid` field was added in 20231120 (KiCad 8).

    """

    start: tuple[float, float]
    mid: tuple[float, float]
    end: tuple[float, float]
    radius: Optional[Radius] = None
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[Literal["arc"]] = "arc"
