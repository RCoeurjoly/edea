from dataclasses import field
from typing import Annotated, Literal, Optional
from uuid import UUID, uuid4

from pydantic.dataclasses import dataclass

from edea.kicad._fields import make_meta as m
from edea.kicad.common import Effects, Pts, Stroke
from edea.kicad.config import PydanticConfig
from edea.kicad.str_enum import StrEnum

from .common import (
    BaseTextBox,
    Group,
    Image,
    KicadPcbExpr,
    Net,
    PositionIdentifier,
    Property,
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
    type: Annotated[Literal["smd", "through_hole", None], m("kicad_no_kw")] = None
    board_only: Annotated[bool, m("kicad_kw_bool")] = False
    exclude_from_pos_files: Annotated[bool, m("kicad_kw_bool")] = False
    exclude_from_bom: Annotated[bool, m("kicad_kw_bool")] = False
    allow_missing_courtyard: Annotated[bool, m("kicad_kw_bool")] = False
    allow_soldermask_bridges: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: Literal["attr"] = "attr"


class ZoneConnection(StrEnum):
    NoConnection = "0"
    ThermalRelief = "1"
    SolidFill = "2"


@dataclass(config=PydanticConfig, eq=False)
class FootprintText(KicadPcbExpr):
    type: Annotated[Literal["reference", "value", "user"], m("kicad_no_kw")] = "user"
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    text: Annotated[str, m("kicad_always_quotes", "kicad_no_kw")] = ""
    at: PositionIdentifier = field(default_factory=PositionIdentifier)
    layer: LayerKnockout = field(default_factory=LayerKnockout)
    hide: Annotated[bool, m("kicad_kw_bool")] = False
    effects: Effects = field(default_factory=Effects)
    tstamp: UUID = field(default_factory=uuid4)
    render_cache: Optional[RenderCache] = None
    kicad_expr_tag_name: Literal["fp_text"] = "fp_text"


@dataclass(config=PydanticConfig, eq=False)
class FootprintTextBox(BaseTextBox):
    kicad_expr_tag_name: Literal["fp_text_box"] = "fp_text_box"


@dataclass(config=PydanticConfig, eq=False)
class FootprintLine(KicadPcbExpr):
    start: tuple[float, float]
    end: tuple[float, float]
    stroke: Optional[Stroke] = None
    layer: CanonicalLayerName = "F.Cu"
    width: Optional[float] = None
    tstamp: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["fp_line"] = "fp_line"


@dataclass(config=PydanticConfig, eq=False)
class FootprintRectangle(KicadPcbExpr):
    start: tuple[float, float]
    end: tuple[float, float]
    stroke: Optional[Stroke] = None
    fill: Literal["solid", "none", None] = None
    layer: CanonicalLayerName = "F.Cu"
    tstamp: UUID = field(default_factory=uuid4)
    width: Optional[float] = None
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: Literal["fp_rect"] = "fp_rect"


@dataclass(config=PydanticConfig, eq=False)
class FootprintCircle(KicadPcbExpr):
    center: tuple[float, float]
    end: tuple[float, float]
    stroke: Optional[Stroke] = None
    fill: Optional[Literal["solid", "none"]] = None
    layer: CanonicalLayerName = "F.Cu"
    width: Optional[float] = None
    tstamp: UUID = field(default_factory=uuid4)
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: Literal["fp_circle"] = "fp_circle"


@dataclass(config=PydanticConfig, eq=False)
class FootprintArc(KicadPcbExpr):
    start: tuple[float, float]
    mid: tuple[float, float]
    end: tuple[float, float]
    stroke: Optional[Stroke] = None
    layer: CanonicalLayerName = "F.Cu"
    tstamp: UUID = field(default_factory=uuid4)
    width: Optional[float] = None
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: Literal["fp_arc"] = "fp_arc"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPolygon(KicadPcbExpr):
    pts: Pts
    stroke: Stroke = field(default_factory=Stroke)
    width: Optional[float] = None
    fill: Optional[Literal["solid", "none"]] = None
    layer: CanonicalLayerName = "F.Cu"
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: Literal["fp_poly"] = "fp_poly"
    tstamp: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class FootprintCurve(KicadPcbExpr):
    pts: Pts
    layer: CanonicalLayerName
    tstamp: UUID
    stroke: Optional[Stroke] = None
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: Literal["fp_curve"] = "fp_curve"


# the drill oval expression can be can be e.g. `(drill oval 1.0 1.0 (offset ...))`
# or `(drill oval (offest ...))` or `(drill oval 1.0 1.0)` or just
# `(drill oval 1.0)` or `(drill oval 1.0 (offset ...))`. so everything
# is seemingly optional


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillOval1(KicadPcbExpr):
    oval: Annotated[Literal["oval"], m("kicad_no_kw")] = "oval"
    size: Annotated[float, m("kicad_no_kw")] = 0
    kicad_expr_tag_name: Literal["drill"] = "drill"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillOval2(KicadPcbExpr):
    oval: Annotated[Literal["oval"], m("kicad_no_kw")] = "oval"
    size_x: Annotated[float, m("kicad_no_kw")] = 0
    size_y: Annotated[float, m("kicad_no_kw")] = 0
    kicad_expr_tag_name: Literal["drill"] = "drill"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillOval3(KicadPcbExpr):
    oval: Annotated[Literal["oval"], m("kicad_no_kw")] = "oval"
    offset: tuple[float, float] = (0, 0)
    kicad_expr_tag_name: Literal["drill"] = "drill"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillOval4(KicadPcbExpr):
    oval: Annotated[Literal["oval"], m("kicad_no_kw")] = "oval"
    size: Annotated[float, m("kicad_no_kw")] = 0
    offset: tuple[float, float] = (0, 0)
    kicad_expr_tag_name: Literal["drill"] = "drill"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillOval5(KicadPcbExpr):
    oval: Annotated[Literal["oval"], m("kicad_no_kw")] = "oval"
    size_x: Annotated[float, m("kicad_no_kw")] = 0
    size_y: Annotated[float, m("kicad_no_kw")] = 0
    offset: tuple[float, float] = (0, 0)
    kicad_expr_tag_name: Literal["drill"] = "drill"


FootprintPadDrillOval = (
    FootprintPadDrillOval1
    | FootprintPadDrillOval2
    | FootprintPadDrillOval3
    | FootprintPadDrillOval4
    | FootprintPadDrillOval5
)


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillRound(KicadPcbExpr):
    diameter: Annotated[float | None, m("kicad_no_kw")] = None
    offset: Annotated[tuple[float, float], m("kicad_omits_default")] = (0, 0)
    kicad_expr_tag_name: Literal["drill"] = "drill"


FootprintPadDrill = FootprintPadDrillOval | FootprintPadDrillRound


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadOptions(KicadPcbExpr):
    clearance: Literal["outline", "convexhull"]
    anchor: Literal["rect", "circle"]
    kicad_expr_tag_name: Literal["options"] = "options"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadPrimitives(KicadPcbExpr):
    gr_poly: list[GraphicalPolygon] = field(default_factory=list)
    gr_line: list[GraphicalLine] = field(default_factory=list)
    gr_rect: list[GraphicalRectangle] = field(default_factory=list)
    gr_circle: list[GraphicalCircle] = field(default_factory=list)
    gr_arc: list[GraphicalArc] = field(default_factory=list)
    gr_text: list[GraphicalText] = field(default_factory=list)
    bezier: list[GraphicalBezier] = field(default_factory=list)
    gr_bbox: list[GraphicalBoundingBox] = field(default_factory=list)
    gr_text_box: list[GraphicalTextBox] = field(default_factory=list)
    width: Optional[float] = None
    fill: Annotated[bool, m("kicad_bool_yes_no", "kicad_omits_default")] = False

    kicad_expr_tag_name: Literal["primitives"] = "primitives"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadRectDelta(KicadPcbExpr):
    x: Annotated[float, m("kicad_no_kw")]
    y: Annotated[float, m("kicad_no_kw")]
    kicad_expr_tag_name: Literal["rect_delta"] = "rect_delta"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPad(KicadPcbExpr):
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
    at: PositionIdentifier = field(default_factory=PositionIdentifier)
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
    tstamp: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["pad"] = "pad"


@dataclass(config=PydanticConfig, eq=False)
class FootprintModelCoord(KicadPcbExpr):
    xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)


class FootprintModelOffset(FootprintModelCoord):
    kicad_expr_tag_name: Literal["offset"] = "offset"


class FootprintModelScale(FootprintModelCoord):
    kicad_expr_tag_name: Literal["scale"] = "scale"


class FootprintModelRotate(FootprintModelCoord):
    kicad_expr_tag_name: Literal["rotate"] = "rotate"


@dataclass(config=PydanticConfig, eq=False)
class Footprint3dModel(KicadPcbExpr):
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
    kicad_expr_tag_name: Literal["model"] = "model"


AutoplaceCost = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


@dataclass(config=PydanticConfig, eq=False)
class Footprint(KicadPcbExpr):
    library_link: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    placed: Annotated[bool, m("kicad_kw_bool")] = False
    layer: CanonicalLayerName = "F.Cu"
    tedit: Optional[str] = None
    tstamp: Optional[UUID] = None
    at: Optional[PositionIdentifier] = None
    descr: Optional[str] = None
    tags: Optional[str] = None
    property: list[Property] = field(default_factory=list)
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
    attr: Optional[FootprintAttributes] = None
    net_tie_pad_groups: Annotated[list[str], m("kicad_omits_default")] = field(
        default_factory=list,
    )
    fp_text: list[FootprintText] = field(default_factory=list)
    image: list[Image] = field(default_factory=list)
    fp_text_box: list[FootprintTextBox] = field(default_factory=list)
    fp_line: list[FootprintLine] = field(default_factory=list)
    fp_rect: list[FootprintRectangle] = field(default_factory=list)
    fp_circle: list[FootprintCircle] = field(default_factory=list)
    fp_arc: list[FootprintArc] = field(default_factory=list)
    fp_poly: list[FootprintPolygon] = field(default_factory=list)
    fp_curve: list[FootprintCurve] = field(default_factory=list)
    dimension: list[GraphicalDimension] = field(default_factory=list)
    pad: list[FootprintPad] = field(default_factory=list)
    group: list[Group] = field(default_factory=list)

    # UNDOCUMENTED: `zone`
    zone: list[Zone] = field(default_factory=list)
    model: list[Footprint3dModel] = field(default_factory=list)
