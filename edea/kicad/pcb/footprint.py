from dataclasses import field
from typing import Annotated, ClassVar, Literal, Optional
from uuid import UUID

from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.common import Effects, Pts, Stroke

from .common import (
    BaseTextBox,
    Group,
    Image,
    KicadPcbExpr,
    Net,
    Position,
    Property,
    TearDrops,
    Zone,
)
from .graphics import (
    GraphicalArc,
    GraphicalBezier,
    GraphicalBoundingBox,
    GraphicalCircle,
    GraphicalDimension,
    GraphicalLine,
    GraphicalPolygon,
    GraphicalRectangle,
    GraphicalText,
    GraphicalTextBox,
    LayerKnockout,
    RenderCache,
)
from .layer import CanonicalLayerName


@dataclass(config=PydanticConfig, eq=False)
class FootprintAttributes(KicadPcbExpr):
    """
    The footprint attributes for KiCad PCB expressions.

    :param type: The footprint type (SMD or through-hole).
    :param board_only: The footprint is only defined in the board and has no reference to any schematic symbol.
    :param exclude_from_pos_files: The footprint position information should not be included when creating position files.
    :param exclude_from_bom: The footprint should be excluded when creating bill of materials (BOM) files.
    :param allow_missing_courtyard: Whether to allow missing courtyard or not.
    :param allow_soldermask_bridges: Whether to allow soldermask bridges or not.
    :param dnp: The footprint is marked as "do not populate".
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("attr").

    .. note::
        The `dnp` field was added in 20240108 (KiCad 8).

    """

    type: Annotated[Literal["smd", "through_hole", None], m("kicad_no_kw")] = None
    board_only: Annotated[bool, m("kicad_kw_bool")] = False
    exclude_from_pos_files: Annotated[bool, m("kicad_kw_bool")] = False
    exclude_from_bom: Annotated[bool, m("kicad_kw_bool")] = False
    allow_missing_courtyard: Annotated[bool, m("kicad_kw_bool")] = False
    allow_soldermask_bridges: Annotated[bool, m("kicad_kw_bool")] = False
    dnp: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["attr"]] = "attr"


class ZoneConnection(StrEnum):
    """
    Used to select zone connection types for KiCad PCB expressions.
    """

    NoConnection = "0"
    """
    The zone has no connection.
    """
    ThermalRelief = "1"
    """
    The zone is used for thermal relief.
    """
    SolidFill = "2"
    """
    The zone is filled with solid copper.
    """


@dataclass(config=PydanticConfig, eq=False)
class FootprintText(KicadPcbExpr):
    """
    The text elements associated with footprints in KiCad PCB expressions.

    :param type: The text type (reference, value, or user-defined).
    :param locked: Whether the text is locked or not.
    :param text: The text content.
    :param at: The X-Y coordinates of the text element.
    :param layer: The canonical layer the text resides on.
    :param hide: Whether to hide the text element or not.
    :param effects: How the text is displayed.
    :param tstamp: The unique identifier of the text object.
    :param uuid: The unique identifier of the text object.
    :param unlocked: Whether the text is unlocked or not.
    :param render_cache: A `RenderCache` object .
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("fp_text").

    .. note::
        The `unlocked` field was added in 20240108 (KiCad 8).

    .. note::
        The `tstamp` field got renamed to `uuid` in 20240108 (KiCad 8).

    """

    type: Annotated[Literal["reference", "value", "user"], m("kicad_no_kw")] = "user"
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    text: Annotated[str, m("kicad_always_quotes", "kicad_no_kw")] = ""
    at: Position = field(default_factory=Position)
    layer: LayerKnockout = field(default_factory=LayerKnockout)
    hide: Annotated[bool, m("kicad_kw_bool")] = False
    effects: Effects = field(default_factory=Effects)
    tstamp: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    unlocked: Annotated[
        Optional[bool], m("kicad_bool_yes_no", "kicad_omits_default")
    ] = None
    render_cache: Optional[RenderCache] = None
    kicad_expr_tag_name: ClassVar[Literal["fp_text"]] = "fp_text"


@dataclass(config=PydanticConfig, eq=False)
class FootprintTextBox(BaseTextBox):
    """
    The text box associated with footprints in KiCad PCB expressions.

    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("fp_text_box").
    """

    kicad_expr_tag_name = "fp_text_box"


@dataclass(config=PydanticConfig, eq=False)
class FootprintLine(KicadPcbExpr):
    """
    A footprint line element in KiCad PCB expressions.

    :param start: The starting X-Y coordinates of the line.
    :param end: The ending X-Y coordinates of the line.
    :param stroke: A `Stroke` object defining line style.
    :param layer: The canonical layer the line resides on.
    :param width: The line width.
    :param tstamp: The unique identifier of the line object.
    :param uuid: The unique identifier of the line object.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("fp_line").

    .. note::
        The `tstamp` field got renamed to `uuid` in 20240108 (KiCad 8).

    """

    start: tuple[float, float]
    end: tuple[float, float]
    stroke: Optional[Stroke] = None
    layer: CanonicalLayerName = "F.Cu"
    width: Optional[float] = None
    tstamp: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[Literal["fp_line"]] = "fp_line"


@dataclass(config=PydanticConfig, eq=False)
class FootprintRectangle(KicadPcbExpr):
    """
    A footprint rectangle element in KiCad PCB expressions.

    :param start: The coordinates of the upper left corner of the rectangle.
    :param end: The coordinates of the low right corner of the rectangle.
    :param stroke: A `Stroke` object defining outline style.
    :param fill: How the rectangle is filled.
    :param layer: The canonical layer the rectangle resides on.
    :param width: The line width of the rectangle.
    :param locked: Whether the rectangle cannot be edited.
    :param tstamp: The unique identifierث of the rectangle object.
    :param uuid: The unique identifier of the rectangle object.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("fp_rect").

    .. note::
        The `tstamp` field got renamed to `uuid` in 20240108 (KiCad 8).

    """

    start: tuple[float, float]
    end: tuple[float, float]
    stroke: Optional[Stroke] = None
    fill: Literal["solid", "none", None] = None
    layer: CanonicalLayerName = "F.Cu"
    width: Optional[float] = None
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    tstamp: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[Literal["fp_rect"]] = "fp_rect"


@dataclass(config=PydanticConfig, eq=False)
class FootprintCircle(KicadPcbExpr):
    """
    A footprint circle element in KiCad PCB expressions.

    :param center: The X-Y coordinates of the center of the circle.
    :param end: The coordinates of the end of the radius of the circle.
    :param stroke: A `Stroke` object defining outline style.
    :param fill: How the circle is filled.
    :param layer: The canonical layer the circle resides on.
    :param width: The line width of the circle.
    :param locked: Whether the circle can be edited or not.
    :param tstamp: The unique identifier of the circle object.
    :param uuid: The unique identifier of the circle object.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("fp_circle").

    .. note::
        The `tstamp` field got renamed to `uuid` in 20240108 (KiCad 8).

    """

    center: tuple[float, float]
    end: tuple[float, float]
    stroke: Optional[Stroke] = None
    fill: Optional[Literal["solid", "none"]] = None
    layer: CanonicalLayerName = "F.Cu"
    width: Optional[float] = None
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    tstamp: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[Literal["fp_circle"]] = "fp_circle"


@dataclass(config=PydanticConfig, eq=False)
class FootprintArc(KicadPcbExpr):
    """
    A footprint arc element in KiCad PCB expressions.

    :param start: The X-Y coordinates of the start position of the arc radius.
    :param mid: The X-Y coordinates of the midpoint along the arc.
    :param end: The X-Y coordinates of the end position of the arc radius.
    :param stroke: Reference to a `Stroke` object defining the line style of the arc's edge.
    :param layer: The canonical layer the arc resides on.
    :param width: The line width of the arc.
    :param locked: Whether the arc can be edited or not.
    :param tstamp: The unique identifier of the arc object.
    :param uuid: The unique identifier of the arc object.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("fp_arc").

    .. note::
        The `tstamp` field got renamed to `uuid` in 20240108 (KiCad 8).

    """

    start: tuple[float, float]
    mid: tuple[float, float]
    end: tuple[float, float]
    stroke: Optional[Stroke] = None
    layer: CanonicalLayerName = "F.Cu"
    width: Optional[float] = None
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    tstamp: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[Literal["fp_arc"]] = "fp_arc"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPolygon(KicadPcbExpr):
    """
    A footprint polygon element in KiCad PCB expressions.

    :param pts: A list of (X, Y) coordinates of the polygon outline.
    :param stroke: Reference to a `Stroke` object defining the line style of the polygon's edge.
    :param width: The width of the polygon.
    :param fill: How the polygon is filled.
    :param layer: The canonical layer the polygon resides on.
    :param locked: Whether the polygon can be edited or not.
    :param tstamp: The unique identifier of the polygon object.
    :param uuid: The unique identifier of the polygon object.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("fp_poly").

    .. note::
        The `tstamp` field got renamed to `uuid` in 20240108 (KiCad 8).

    """

    pts: Pts
    stroke: Stroke = field(default_factory=Stroke)
    width: Optional[float] = None
    fill: Optional[Literal["solid", "none"]] = None
    layer: CanonicalLayerName = "F.Cu"
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    tstamp: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[Literal["fp_poly"]] = "fp_poly"


@dataclass(config=PydanticConfig, eq=False)
class FootprintCurve(KicadPcbExpr):
    """
    A footprint curve element in KiCad PCB expressions.

    :param pts: A list of the four X/Y coordinates of each point of the curve.
    :param layer: The canonical layer the curve resides on.
    :param stroke: Reference to a `Stroke` object defining the line style of the curve's edge.
    :param locked: Whether the curve is locked for editing or not.
    :param tstamp: The unique identifier of the curve object.
    :param uuid: The unique identifier of the curve object.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("fp_curve").

    .. note::
        The `tstamp` field got renamed to `uuid` in 20240108 (KiCad 8).

    """

    pts: Pts
    layer: CanonicalLayerName
    stroke: Optional[Stroke] = None
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    tstamp: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[Literal["fp_curve"]] = "fp_curve"


# the drill oval expression can be can be e.g. `(drill oval 1.0 1.0 (offset ...))`
# or `(drill oval (offest ...))` or `(drill oval 1.0 1.0)` or just
# `(drill oval 1.0)` or `(drill oval 1.0 (offset ...))`. so everything
# is seemingly optional


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillOval1(KicadPcbExpr):
    """
    An oval drill footprint pad in KiCad PCB expressions.

    :param oval: The drill is oval instead of round.
    :param size: The size of the oval drill pad.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("drill").
    """

    oval: Annotated[Literal["oval"], m("kicad_no_kw")] = "oval"
    size: Annotated[float, m("kicad_no_kw")] = 0
    kicad_expr_tag_name: ClassVar[Literal["drill"]] = "drill"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillOval2(KicadPcbExpr):
    """
    An oval drill footprint pad in KiCad PCB expressions.

    :param oval: The drill is oval instead of round.
    :param size_x: The size in X direction of the oval drill pad.
    :param size_y: The size in Y direction of the oval drill pad.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("drill").
    """

    oval: Annotated[Literal["oval"], m("kicad_no_kw")] = "oval"
    size_x: Annotated[float, m("kicad_no_kw")] = 0
    size_y: Annotated[float, m("kicad_no_kw")] = 0
    kicad_expr_tag_name: ClassVar[Literal["drill"]] = "drill"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillOval3(KicadPcbExpr):
    """
    An oval drill footprint pad with offset in KiCad PCB expressions.

    :param oval: The drill is oval instead of round.
    :param offset: The drill offset coordinates from the center of the pad.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("drill").
    """

    oval: Annotated[Literal["oval"], m("kicad_no_kw")] = "oval"
    offset: tuple[float, float] = (0, 0)
    kicad_expr_tag_name: ClassVar[Literal["drill"]] = "drill"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillOval4(KicadPcbExpr):
    """
    An oval drill footprint pad with size and offset in KiCad PCB expressions.

    :param oval: The drill is oval instead of round.
    :param size: The size of the oval drill pad.
    :param offset: The drill offset coordinates from the center of the pad.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("drill").
    """

    oval: Annotated[Literal["oval"], m("kicad_no_kw")] = "oval"
    size: Annotated[float, m("kicad_no_kw")] = 0
    offset: tuple[float, float] = (0, 0)
    kicad_expr_tag_name: ClassVar[Literal["drill"]] = "drill"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillOval5(KicadPcbExpr):
    """
    An oval drill footprint pad with size, offset, and individual X/Y sizes
    in KiCad PCB expressions.

    :param oval: The drill is oval instead of round.
    :param size_x: The size in X direction of the oval drill pad.
    :param size_y: The size in Y direction of the oval drill pad.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("drill").
    """

    oval: Annotated[Literal["oval"], m("kicad_no_kw")] = "oval"
    size_x: Annotated[float, m("kicad_no_kw")] = 0
    size_y: Annotated[float, m("kicad_no_kw")] = 0
    offset: tuple[float, float] = (0, 0)
    kicad_expr_tag_name: ClassVar[Literal["drill"]] = "drill"


FootprintPadDrillOval = (
    FootprintPadDrillOval1
    | FootprintPadDrillOval2
    | FootprintPadDrillOval3
    | FootprintPadDrillOval4
    | FootprintPadDrillOval5
)


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillRound(KicadPcbExpr):
    """
    A round drill footprint pad in KiCad PCB expressions.

    :param diameter: The diameter of the round drill pad.
    :param offset:The drill offset coordinates from the center of the pad.

    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("drill").

    """

    diameter: Annotated[float | None, m("kicad_no_kw")] = None
    offset: Annotated[tuple[float, float], m("kicad_omits_default")] = (0, 0)
    kicad_expr_tag_name: ClassVar[Literal["drill"]] = "drill"


FootprintPadDrill = FootprintPadDrillOval | FootprintPadDrillRound


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadOptions(KicadPcbExpr):
    """
    The options for footprint pads in KiCad PCB expressions.

    :param clearance: The type of clearance used for a custom pad.
    :param anchor: The anchor pad shape of a custom pad.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("options").

    """

    clearance: Literal["outline", "convexhull"]
    anchor: Literal["rect", "circle"]
    kicad_expr_tag_name: ClassVar[Literal["options"]] = "options"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadPrimitives(KicadPcbExpr):
    """
    The primitive graphical elements for footprint pads in KiCad PCB expressions.

    :param gr_polys: A list of graphical polygons for the pad.
    :param gr_lines: A list of graphical lines for the pad.
    :param gr_rects: A list of graphical rectangles for the pad.
    :param gr_circles: A list of graphical circles for the pad.
    :param gr_arcs: A list of graphical arcs for the pad.
    :param gr_text_items: A list of graphical text elements for the pad.
    :param beziers: A list of graphical bezier curves for the pad.
    :param gr_bboxes: A list of graphical bounding boxes for the pad.
    :param gr_text_boxes: A list of graphical text boxes for the pad.
    :param width: The line width applied to graphical elements within the pad.
    :param fill: Whether to fill closed graphical elements within the pad or not.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("primitives").

    """

    gr_polys: list[GraphicalPolygon] = field(default_factory=list)
    gr_lines: list[GraphicalLine] = field(default_factory=list)
    gr_rects: list[GraphicalRectangle] = field(default_factory=list)
    gr_circles: list[GraphicalCircle] = field(default_factory=list)
    gr_arcs: list[GraphicalArc] = field(default_factory=list)
    gr_text_items: list[GraphicalText] = field(default_factory=list)
    beziers: list[GraphicalBezier] = field(default_factory=list)
    gr_bboxes: list[GraphicalBoundingBox] = field(default_factory=list)
    gr_text_boxes: list[GraphicalTextBox] = field(default_factory=list)
    width: Optional[float] = None
    fill: Annotated[bool, m("kicad_bool_yes_no", "kicad_omits_default")] = False

    kicad_expr_tag_name: ClassVar[Literal["primitives"]] = "primitives"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadRectDelta(KicadPcbExpr):
    """
    A rectangle pad delta in KiCad PCB expressions (undocumented).

    :param x: The delta value in X direction for the rectangle pad.
    :param y: The delta value in Y direction for the rectangle pad.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("rect_delta").
    """

    x: Annotated[float, m("kicad_no_kw")]
    y: Annotated[float, m("kicad_no_kw")]
    kicad_expr_tag_name: ClassVar[Literal["rect_delta"]] = "rect_delta"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPad(KicadPcbExpr):
    """
    A footprint pad in KiCad PCB expressions.

    `KiCad pad <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_footprint_pad>`_

    :param number: The pad number.
    :param type: The pad type (thru_hole, smd, connect, or np_thru_hole).
    :param shape: The pad shape (circle, rect, oval, trapezoid, roundrect, or custom).
    :param locked: Whether the footprint pad can be edited or not.
    :param at: The X-Y coordinates of the pad center.
    :param size: The size of the pad.
    :param drill: The pad drill requirements.
    :param property: Any special properties for the pad.
    :param layers: The layer or layers the pad reside on.
    :param remove_unused_layers: It specifies that the copper should be removed from any layers the pad is not connected to.
    :param keep_end_layers: It specifies that the top and bottom layers should be retained when removing the copper from unused layers.
    :param zone_layer_connections: List of zone layers connected to the pad.
    :param roundrect_rratio: The scaling factor of the pad to corner radius for rounded rectangular and chamfered corner rectangular pads.
    :param chamfer_ratio: The scaling factor of the pad to chamfer size.
    :param chamfer: A list of one or more rectangular pad corners that get chamfered.
    :param net: The integer number and name string of the net connection for the pad.
    :param pinfunction: The associated schematic symbol pin name.
    :param pintype: The associated schematic pin electrical type.
    :param solder_mask_margin: The distance between the pad and the solder mask for the pad.
    :param solder_paste_margin: The distance the solder paste should be changed for the pad.
    :param solder_paste_margin_ratio: The percentage to reduce the pad outline by to generate the solder paste size.
    :param clearance: The clearance from all copper to the pad.
    :param zone_connect: The type of zone connect for the pad.
    :param die_length: The die length between the component pad and physical chip inside the component package.
    :param thermal_bridge_width: The width of the thermal bridge for thermal pads.
    :param thermal_bridge_angle: The angle of the thermal bridge for thermal pads.
    :param thermal_width: The thermal relief spoke width used for zone connection for the pad.
    :param thermal_gap: The distance from the pad to the zone of the thermal relief connection for the pad.
    :param options: The options when a custom pad is defined.
    :param primitives: The drawing objects and options used to define a custom pad.
    :param rect_delta: (Undocumented field) The rectangle pad deltas.
    :param tstamp: The unique identifier of the pad object.
    :param uuid: The unique identifier of the pad object.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("pad").

    .. warning::
        The `rect_delta` field is undocumented in the KiCad file format documentation.

    .. note::
        The `tstamp` field got renamed to `uuid` in 20240108 (KiCad 8).

    """

    number: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    type: Annotated[
        Literal["thru_hole", "smd", "connect", "connect", "np_thru_hole"],
        m("kicad_no_kw"),
    ]
    shape: Annotated[
        Literal["rect", "circle", "oval", "trapezoid", "roundrect", "custom"],
        m("kicad_no_kw"),
    ]
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    at: Position = field(default_factory=Position)
    size: tuple[float, float] = (0, 0)
    drill: Optional[FootprintPadDrill] = None
    property: list[str] = field(default_factory=list)
    layers: Annotated[list[str], m("kicad_always_quotes")] = field(
        default_factory=list,
    )
    remove_unused_layers: Annotated[bool, m("kicad_kw_bool_empty")] = False
    keep_end_layers: Annotated[bool, m("kicad_kw_bool_empty")] = False
    zone_layer_connections: list[CanonicalLayerName] = field(default_factory=list)
    roundrect_rratio: Optional[float] = None
    chamfer_ratio: Optional[float] = None
    chamfer: Annotated[
        list[Literal["top_left", "top_right", "bottom_left", "bottom_right"]],
        m("kicad_omits_default"),
    ] = field(default_factory=list)
    net: Optional[Net] = None
    pinfunction: Annotated[Optional[str], m("kicad_always_quotes")] = None
    pintype: Annotated[Optional[str], m("kicad_always_quotes")] = None
    solder_mask_margin: Optional[float] = None
    solder_paste_margin: Optional[float] = None
    solder_paste_margin_ratio: Optional[float] = None
    clearance: Optional[float] = None
    zone_connect: Literal[0, 1, 2, None] = None
    die_length: Optional[float] = None
    thermal_bridge_width: Annotated[float, m("kicad_omits_default")] = 0
    thermal_bridge_angle: Annotated[int, m("kicad_omits_default")] = 0
    thermal_width: Optional[float] = None
    thermal_gap: Optional[float] = None
    options: Optional[FootprintPadOptions] = None
    primitives: Annotated[FootprintPadPrimitives, m("kicad_omits_default")] = field(
        default_factory=FootprintPadPrimitives,
    )
    # UNDOCUMENTED: `rect_delta`
    rect_delta: Optional[FootprintPadRectDelta] = None
    teardrops: Optional[TearDrops] = None
    tstamp: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[Literal["pad"]] = "pad"


@dataclass(config=PydanticConfig, eq=False)
class FootprintModelCoord(KicadPcbExpr):
    """
    Footprint model coordinate related elements in KiCad PCB expressions.

    :param xyz: A tuple of the model coordinates.
    """

    xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)
    kicad_expr_tag_name: ClassVar[Literal["xyz", "offset", "scale", "rotate"]] = "xyz"


class FootprintModelOffset(FootprintModelCoord):
    """
    A model offset in KiCad PCB expressions.

    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("offset").
    """

    kicad_expr_tag_name = "offset"


class FootprintModelScale(FootprintModelCoord):
    """
    A model scale in KiCad PCB expressions.

    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("scale").
    """

    kicad_expr_tag_name = "scale"


class FootprintModelRotate(FootprintModelCoord):
    """
    A model rotation in KiCad PCB expressions.

    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("rotate").
    """

    kicad_expr_tag_name = "rotate"


@dataclass(config=PydanticConfig, eq=False)
class Footprint3dModel(KicadPcbExpr):
    """
    A 3D model element for footprints in KiCad PCB expressions.


    `KiCad 3d model <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_footprint_3d_model>`_

    :param file: The path to the 3D model file.
    :param hide: Whether to hide the 3D model in the viewer.
    :param opacity: (Undocumented field) The opacity of the 3D model (0.0 to 1.0).
    :param offset: (Undocumented field) The offset of the 3D model placement.
    :param scale: The model scale factor for each 3D axis.
    :param rotate: The model rotation for each 3D axis relative to the footprint.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("model").
    """

    file: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    hide: Annotated[bool, m("kicad_kw_bool")] = False
    # UNDOCUMENTED: `opacity`
    opacity: Optional[float] = None
    # UNDOCUMENTED: `offset`
    offset: Annotated[FootprintModelOffset, m("kicad_omits_default")] = field(
        default_factory=FootprintModelOffset,
    )
    scale: Annotated[FootprintModelScale, m("kicad_omits_default")] = field(
        default_factory=FootprintModelScale,
    )
    rotate: Annotated[FootprintModelRotate, m("kicad_omits_default")] = field(
        default_factory=FootprintModelRotate,
    )
    kicad_expr_tag_name: ClassVar[Literal["model"]] = "model"


AutoplaceCost = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


@dataclass(config=PydanticConfig, eq=False)
class Footprint(KicadPcbExpr):
    """
    A footprint in KiCad PCB expressions.


    `KiCad footprint <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_footprint>`_

    :param library_link: The library reference of the footprint.
    :param locked: A flag to indicate the footprint cannot be edited.
    :param placed: A flag to indicate that the footprint has not been placed.
    :param layer: The canonical layer the footprint is placed.
    :param tedit: The last time the footprint was edited.
    :param tstamp: The unique identifier for the footprint.
    :param uuid: The unique identifier for the footprint.
    :param at: The X-Y coordinates of the footprint placement.
    :param descr: The description of the footprint.
    :param tags: Search tags for the footprint.
    :param properties: List of key-value property strings for the footprint.
    :param path: The hierarchical path of the schematic symbol linked to the footprint.
    :param autoplace_cost90: The vertical cost of when using the automatic footprint placement tool.
    :param autoplace_cost180: The horizontal cost of when using the automatic footprint placement tool.
    :param solder_mask_margin: The solder mask distance from all pads in the footprint.
    :param solder_paste_margin: The solder paste distance from all pads in the footprint.
    :param solder_paste_ratio: The percentage of the pad size used to define the solder paste for all pads in the footprint.
    :param clearance: The clearance to all board copper objects for all pads in the footprint.
    :param zone_connect: How all pads are connected to filled zone.
    :param thermal_width: The thermal relief spoke width used for zone connections for all pads in the footprint.
    :param thermal_gap: The distance from the pad to the zone of thermal relief connections for all pads in the footprint.
    :param sheetname: The name of the sheet the footprint is associated with.
    :param sheetfile: The file path of the sheet the footprint is associated with.
    :param attr: The attributes of the footprint.
    :param net_tie_pad_groups: An optional list of net-tie pad groups.
    :param fp_text_items: A list of footprint text elements.
    :param images: A list of image references for the footprint.
    :param fp_text_boxes: A list of footprint text box elements.
    :param fp_lines: A list of footprint line elements.
    :param fp_rects: A list of footprint rectangle elements.
    :param fp_circles: A list of footprint circle elements.
    :param fp_arcs: A list of footprint arc elements.
    :param fp_polys: A list of footprint polygon elements.
    :param fp_curves: A list of footprint curve elements.
    :param dimensions: A list of graphical dimension elements associated with the footprint.
    :param pads: A list of footprint pad elements. Defines the electrical connections of the footprint.
    :param groups: A list of groups associated with the footprint (for organization purposes).
    :param zones: (Undocumented field) List of zones associated with the footprint.
    :param models: A list of 3D models attached to the footprint.

    .. note::
        The `tstamp` field got renamed to `uuid` in 20240108 (KiCad 8).

    .. note::
        The fields `sheetname` and `sheetfile` were added in 20240108 (KiCad 8).

    """

    library_link: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    placed: Annotated[bool, m("kicad_kw_bool")] = False
    layer: CanonicalLayerName = "F.Cu"
    tedit: Optional[str] = None
    tstamp: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    at: Position = field(default_factory=Position)
    descr: Optional[str] = None
    tags: Optional[str] = None
    properties: list[Property] = field(default_factory=list)
    path: Optional[str] = None
    autoplace_cost90: Optional[AutoplaceCost] = None
    autoplace_cost180: Optional[AutoplaceCost] = None
    solder_mask_margin: Optional[float] = None
    solder_paste_margin: Optional[float] = None
    solder_paste_ratio: Optional[float] = None
    clearance: Optional[float] = None
    zone_connect: Optional[ZoneConnection] = None
    thermal_width: Optional[float] = None
    thermal_gap: Optional[float] = None
    sheetname: Optional[str] = None
    sheetfile: Optional[str] = None
    attr: Optional[FootprintAttributes] = None
    net_tie_pad_groups: Annotated[list[str], m("kicad_omits_default")] = field(
        default_factory=list,
    )
    fp_text_items: list[FootprintText] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)
    fp_text_boxes: list[FootprintTextBox] = field(default_factory=list)
    fp_lines: list[FootprintLine] = field(default_factory=list)
    fp_rects: list[FootprintRectangle] = field(default_factory=list)
    fp_circles: list[FootprintCircle] = field(default_factory=list)
    fp_arcs: list[FootprintArc] = field(default_factory=list)
    fp_polys: list[FootprintPolygon] = field(default_factory=list)
    fp_curves: list[FootprintCurve] = field(default_factory=list)
    dimensions: list[GraphicalDimension] = field(default_factory=list)
    pads: list[FootprintPad] = field(default_factory=list)
    groups: list[Group] = field(default_factory=list)

    # UNDOCUMENTED: `zone`
    zones: list[Zone] = field(default_factory=list)
    models: list[Footprint3dModel] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["footprint"]] = "footprint"
