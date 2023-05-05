from dataclasses import field
from enum import Enum
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import root_validator, validator
from pydantic.dataclasses import dataclass

from edea.types.common import Effects, Pts, Stroke
from edea.types.meta import make_meta as m
from edea.types.config import PydanticConfig
from edea.types.pcb_layers import CanonicalLayerName

from .common import (
    BaseTextBox,
    Group,
    KicadPcbExpr,
    Layer,
    PositionIdentifier,
    Property,
    Zone,
)
from .graphics import (
    GraphicalArc,
    GraphicalBezier,
    GraphicalBoundingBox,
    GraphicalCircle,
    GraphicalLine,
    GraphicalPolygon,
    GraphicalRectangle,
    GraphicalText,
    GraphicalTextBox,
)


@dataclass(config=PydanticConfig, eq=False)
class FootprintAttributes(KicadPcbExpr):
    type: Optional[Literal["smd", "through_hole"]] = "smd"
    board_only: bool = False
    exclude_from_pos_files: bool = False
    exclude_from_bom: bool = False
    kicad_expr_tag_name: Literal["attr"] = "attr"

    @root_validator(pre=True)
    def _root(cls, fields):
        """All the fields are optional for example:
        ```kicad_pcb
        (attr smd board_only exclude_from_pos_files exclude_from_bom)
        (attr board_only exclude_from_pos_files exclude_from_bom)
        ```
        are both valid.
        And the fields gets passed as positional arguments so we need to
        to handle the case where the `type` field is omitted.
        Also, we handle the type conversion here for boolean fields.
        """
        values = list(fields.values())
        if values[0] in ["smd", "through_hole"]:
            fields["type"] = values[0]
        else:
            fields["type"] = None

        for key in ["board_only", "exclude_from_pos_files", "exclude_from_bom"]:
            if key in values:
                fields[key] = True
            else:
                fields[key] = False
        return fields


class ZoneConnection(str, Enum):
    NoConnection = "0"
    ThermalRelief = "1"
    SolidFill = "2"


@dataclass(config=PydanticConfig, eq=False)
class FootprintText(KicadPcbExpr):
    type: Literal["reference", "value", "user"] = "user"
    text: str = field(default_factory=str)
    locked: bool = False
    at: PositionIdentifier = field(default_factory=PositionIdentifier)
    layer: CanonicalLayerName = "F.Cu"
    effects: Effects = field(default_factory=Effects)
    tstamp: UUID = field(default_factory=uuid4)
    hide: bool = False
    kicad_expr_tag_name: Literal["fp_text"] = "fp_text"

    @root_validator(pre=True)
    def validate(cls, fields):
        values = list(fields.values())
        if "locked" in values and values[2] != "locked":
            # if locked and text passed in reverse order
            fields["locked"] = True
            fields["text"] = values[2]
        return fields


@dataclass(config=PydanticConfig, eq=False)
class FootprintTextBox(BaseTextBox):
    kicad_expr_tag_name: Literal["fp_text_box"] = "fp_text_box"


@dataclass(config=PydanticConfig, eq=False)
class FootprintLine(KicadPcbExpr):
    start: tuple[float, float]
    end: tuple[float, float]
    layer: CanonicalLayerName
    width: float
    tstamp: UUID
    stroke: Optional[Stroke] = None
    locked: bool = False
    kicad_expr_tag_name: Literal["fp_line"] = "fp_line"


@dataclass(config=PydanticConfig, eq=False)
class FootprintRectangle(KicadPcbExpr):
    start: tuple[float, float]
    end: tuple[float, float]
    layer: CanonicalLayerName
    width: float
    tstamp: UUID
    stroke: Optional[Stroke] = None
    fill: Optional[Literal["solid", "none"]] = None
    locked: bool = False
    kicad_expr_tag_name: Literal["fp_rect"] = "fp_rect"


@dataclass(config=PydanticConfig, eq=False)
class FootprintCircle(KicadPcbExpr):
    center: tuple[float, float]
    end: tuple[float, float]
    layer: CanonicalLayerName
    width: float
    tstamp: UUID
    stroke: Optional[Stroke] = None
    fill: Optional[Literal["solid", "none"]] = None
    locked: bool = False
    kicad_expr_tag_name: Literal["fp_circle"] = "fp_circle"


@dataclass(config=PydanticConfig, eq=False)
class FootprintArc(KicadPcbExpr):
    start: tuple[float, float]
    mid: tuple[float, float]
    end: tuple[float, float]
    layer: CanonicalLayerName
    width: float
    tstamp: UUID
    stroke: Optional[Stroke] = None
    locked: bool = False
    kicad_expr_tag_name: Literal["fp_arc"] = "fp_arc"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPolygon(KicadPcbExpr):
    layer: CanonicalLayerName
    width: float
    tstamp: UUID
    stroke: Optional[Stroke] = None
    pts: Pts = field(default_factory=Pts)
    fill: Optional[Literal["solid", "none"]] = None
    locked: bool = False
    kicad_expr_tag_name: Literal["fp_poly"] = "fp_poly"


@dataclass(config=PydanticConfig, eq=False)
class FootprintCurve(KicadPcbExpr):
    layer: CanonicalLayerName
    width: float
    tstamp: UUID
    pts: Pts
    stroke: Optional[Stroke] = None
    locked: bool = False
    kicad_expr_tag_name: Literal["fp_curve"] = "fp_curve"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrill(KicadPcbExpr):
    oval: bool = False
    diameter: Optional[float] = None
    width: Optional[float] = None
    offset: Optional[tuple[float, float]] = None
    kicad_expr_tag_name: Literal["drill"] = "drill"

    @validator("oval", pre=True)
    def validate_oval(cls, v):
        return v == "oval"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadOptions(KicadPcbExpr):
    clearance: Literal["outline", "convexhull"]
    anchor: Literal["rect", "circle"]


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadPrimitives(KicadPcbExpr):
    width: Optional[float] = None
    fill: bool = False
    gr_poly: list[GraphicalPolygon] = field(default_factory=list)
    gr_line: list[GraphicalLine] = field(default_factory=list)
    gr_rect: list[GraphicalRectangle] = field(default_factory=list)
    gr_circle: list[GraphicalCircle] = field(default_factory=list)
    gr_arc: list[GraphicalArc] = field(default_factory=list)
    gr_text: list[GraphicalText] = field(default_factory=list)
    bezier_to: list[GraphicalBezier] = field(default_factory=list)
    gr_bbox: list[GraphicalBoundingBox] = field(default_factory=list)
    gr_text_box: list[GraphicalTextBox] = field(default_factory=list)

    kicad_expr_tag_name: Literal["primitives"] = "primitives"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadRectDelta(KicadPcbExpr):
    x: float
    y: float
    kicad_expr_tag_name: Literal["rect_delta"] = "rect_delta"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPad(KicadPcbExpr):
    number: str
    type: Literal["thru_hole", "smd", "connect", "connect", "np_thru_hole"]
    shape: Literal["rect", "circle", "oval", "trapezoid", "roundrect", "custom"]
    locked: bool = False
    size: tuple[float, float] = (0, 0)
    tstamp: UUID = field(default_factory=uuid4)
    at: PositionIdentifier = field(default_factory=PositionIdentifier)
    drill: Optional[FootprintPadDrill] = None
    layers: list[str] = field(default_factory=list)
    property: list[Property] = field(default_factory=list)
    remove_unused_layers: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    keep_end_layers: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    roundrect_rratio: Optional[float] = None
    chamfer: Optional[
        list[Literal["top_left", "top_right", "bottom_left", "bottom_right"]]
    ] = None
    chamfer_ratio: Optional[float] = None
    net: Optional[tuple[int, str]] = None
    pinfunction: Optional[str] = None
    pintype: Optional[str] = None
    die_length: Optional[float] = None
    solder_mask_margin: Optional[float] = None
    solder_paste_margin: Optional[float] = None
    solder_paste_margin_ratio: Optional[float] = None
    clearance: Optional[float] = None
    zone_connect: Optional[Literal[0, 1, 2]] = None
    thermal_width: Optional[float] = None
    thermal_gap: Optional[float] = None
    options: Optional[FootprintPadOptions] = None
    primitives: Optional[FootprintPadPrimitives] = None
    kicad_expr_tag_name: Literal["pad"] = "pad"
    # UNDOCUMENTED: `rect_delta`
    rect_delta: Optional[FootprintPadRectDelta] = None

    @validator("zone_connect", pre=True)
    def validate_zone_connect(cls, v):
        if v is not None:
            return int(v)
        return None


@dataclass(config=PydanticConfig, eq=False)
class FootprintModelCoord(KicadPcbExpr):
    xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass(config=PydanticConfig, eq=False)
class Footprint3dModel(KicadPcbExpr):
    file: str
    hide: bool = False
    # UNDOCUMENTED: `offset`
    offset: Optional[FootprintModelCoord] = field(default_factory=FootprintModelCoord)
    scale: Optional[FootprintModelCoord] = field(default_factory=FootprintModelCoord)
    rotate: Optional[FootprintModelCoord] = field(default_factory=FootprintModelCoord)
    # UNDOCUMENTED: `opacity`
    opacity: Optional[float] = None

    @validator("hide", pre=True)
    def _hide(cls, v):
        return v == "hide"


AutoplaceCost = Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


@dataclass(config=PydanticConfig, eq=False)
class Footprint(KicadPcbExpr):
    library_link: str
    locked: bool = False
    placed: bool = False
    layer: CanonicalLayerName = "F.Cu"
    tedit: Optional[str] = None
    model: list[Footprint3dModel] = field(default_factory=list)
    tstamp: Optional[UUID] = None
    at: Optional[PositionIdentifier] = None
    tags: Optional[str] = None
    descr: Optional[str] = None
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
    private_layers: list[Layer] = field(default_factory=list)
    net_tie_pad_groups: list[str] = field(default_factory=list)
    fp_text: list[FootprintText] = field(default_factory=list)
    fp_line: list[FootprintLine] = field(default_factory=list)
    fp_rect: list[FootprintRectangle] = field(default_factory=list)
    fp_circle: list[FootprintCircle] = field(default_factory=list)
    fp_arc: list[FootprintArc] = field(default_factory=list)
    fp_poly: list[FootprintPolygon] = field(default_factory=list)
    fp_curve: list[FootprintCurve] = field(default_factory=list)
    pad: list[FootprintPad] = field(default_factory=list)
    group: list[Group] = field(default_factory=list)

    # UNDOCUMENTED: `zone`
    zone: list[Zone] = field(default_factory=list)

    @root_validator(pre=True)
    def validate(cls, fields):
        values = list(fields.values())
        if "locked" in values:
            fields["locked"] = True
        if "placed" in values:
            fields["placed"] = True

        # handle the case where they are reversed
        if values[1] == "placed" and "locked" not in values:
            fields["locked"] = False
        if values[2] == "locked" and "placed" not in values:
            fields["placed"] = False

        return fields
