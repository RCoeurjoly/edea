from dataclasses import field
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import root_validator, validator
from pydantic.dataclasses import dataclass

from edea.types.common import Effects, Pts, Stroke
from edea.types.config import PydanticConfig
from edea.types.meta import make_meta as m
from edea.types.str_enum import StrEnum

from .common import (
    BaseTextBox,
    Group,
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
    GraphicalLine,
    GraphicalPolygon,
    GraphicalRectangle,
    GraphicalText,
    GraphicalTextBox,
)
from .layer import CanonicalLayerName, Layer


@dataclass(config=PydanticConfig, eq=False)
class FootprintAttributes(KicadPcbExpr):
    type: Literal["smd", "through_hole"] | None = field(
        default=None, metadata=m("kicad_no_kw")
    )
    board_only: bool = field(default=False, metadata=m("kicad_kw_bool"))
    exclude_from_pos_files: bool = field(default=False, metadata=m("kicad_kw_bool"))
    exclude_from_bom: bool = field(default=False, metadata=m("kicad_kw_bool"))
    kicad_expr_tag_name: Literal["attr"] = "attr"

    @classmethod
    def from_list(cls, expr):
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
        self = cls()

        if len(expr) == 0:
            return self

        if expr[0] == "smd":
            self.type = "smd"
        elif expr[0] == "through_hole":
            self.type = "through_hole"

        for key in ["board_only", "exclude_from_pos_files", "exclude_from_bom"]:
            setattr(self, key, key in expr)

        return self


class ZoneConnection(StrEnum):
    NoConnection = "0"
    ThermalRelief = "1"
    SolidFill = "2"


@dataclass(config=PydanticConfig, eq=False)
class FootprintText(KicadPcbExpr):
    type: Literal["reference", "value", "user"] = field(
        default="user", metadata=m("kicad_no_kw")
    )
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    text: str = field(default="", metadata=m("kicad_always_quotes", "kicad_no_kw"))
    at: PositionIdentifier = field(default_factory=PositionIdentifier)
    layer: CanonicalLayerName = field(default="F.Cu", metadata=m("kicad_always_quotes"))
    hide: bool = field(default=False, metadata=m("kicad_kw_bool"))
    effects: Effects = field(default_factory=Effects)
    tstamp: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: Literal["fp_text"] = "fp_text"

    @root_validator(pre=True)
    def validate(cls, fields):
        if fields["locked"] != "locked":
            fields["text"] = fields["locked"]
            fields["locked"] = False
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
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
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
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
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
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
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
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    kicad_expr_tag_name: Literal["fp_arc"] = "fp_arc"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPolygon(KicadPcbExpr):
    pts: Pts
    layer: CanonicalLayerName
    width: float
    stroke: Optional[Stroke] = None
    fill: Optional[Literal["solid", "none"]] = None
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    kicad_expr_tag_name: Literal["fp_poly"] = "fp_poly"
    tstamp: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class FootprintCurve(KicadPcbExpr):
    pts: Pts
    layer: CanonicalLayerName
    width: float
    tstamp: UUID
    stroke: Optional[Stroke] = None
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    kicad_expr_tag_name: Literal["fp_curve"] = "fp_curve"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillOval(KicadPcbExpr):
    oval: Literal["oval"] = field(default="oval", metadata=m("kicad_no_kw"))
    diameter: float = field(default=0, metadata=m("kicad_no_kw"))
    width: float = field(default=0, metadata=m("kicad_no_kw"))
    offset: tuple[float, float] = field(
        default=(0, 0), metadata=m("kicad_omits_default")
    )
    kicad_expr_tag_name: Literal["drill"] = "drill"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadDrillRound(KicadPcbExpr):
    diameter: float = field(default=0, metadata=m("kicad_no_kw"))
    offset: tuple[float, float] = field(
        default=(0, 0), metadata=m("kicad_omits_default")
    )
    kicad_expr_tag_name: Literal["drill"] = "drill"


FootprintPadDrill = FootprintPadDrillOval | FootprintPadDrillRound


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadOptions(KicadPcbExpr):
    clearance: Literal["outline", "convexhull"]
    anchor: Literal["rect", "circle"]


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadPrimitives(KicadPcbExpr):
    gr_poly: list[GraphicalPolygon] = field(default_factory=list)
    gr_line: list[GraphicalLine] = field(default_factory=list)
    gr_rect: list[GraphicalRectangle] = field(default_factory=list)
    gr_circle: list[GraphicalCircle] = field(default_factory=list)
    gr_arc: list[GraphicalArc] = field(default_factory=list)
    gr_text: list[GraphicalText] = field(default_factory=list)
    bezier_to: list[GraphicalBezier] = field(default_factory=list)
    gr_bbox: list[GraphicalBoundingBox] = field(default_factory=list)
    gr_text_box: list[GraphicalTextBox] = field(default_factory=list)
    width: Optional[float] = None
    fill: bool = field(
        default=False, metadata=m("kicad_bool_yes_no", "kicad_omits_default")
    )

    kicad_expr_tag_name: Literal["primitives"] = "primitives"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPadRectDelta(KicadPcbExpr):
    x: float = field(metadata=m("kicad_no_kw"))
    y: float = field(metadata=m("kicad_no_kw"))
    kicad_expr_tag_name: Literal["rect_delta"] = "rect_delta"


@dataclass(config=PydanticConfig, eq=False)
class FootprintPad(KicadPcbExpr):
    number: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    type: Literal["thru_hole", "smd", "connect", "connect", "np_thru_hole"] = field(
        metadata=m("kicad_no_kw")
    )
    shape: Literal[
        "rect", "circle", "oval", "trapezoid", "roundrect", "custom"
    ] = field(metadata=m("kicad_no_kw"))
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    size: tuple[float, float] = (0, 0)
    tstamp: UUID = field(default_factory=uuid4)
    at: PositionIdentifier = field(default_factory=PositionIdentifier)
    drill: Optional[FootprintPadDrill] = None
    layers: list[str] = field(default_factory=list)
    property: list[str] = field(default_factory=list)
    remove_unused_layers: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    keep_end_layers: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    roundrect_rratio: Optional[float] = None
    chamfer: list[
        Literal["top_left", "top_right", "bottom_left", "bottom_right"]
    ] = field(default_factory=list, metadata=m("kicad_omits_default"))
    chamfer_ratio: Optional[float] = None
    net: Optional[Net] = None
    pinfunction: Optional[str] = field(default=None, metadata=m("kicad_always_quotes"))
    pintype: Optional[str] = field(default=None, metadata=m("kicad_always_quotes"))
    die_length: Optional[float] = None
    solder_mask_margin: Optional[float] = None
    solder_paste_margin: Optional[float] = None
    solder_paste_margin_ratio: Optional[float] = None
    clearance: Optional[float] = None
    zone_connect: Optional[Literal[0, 1, 2]] = None
    thermal_width: Optional[float] = None
    thermal_gap: Optional[float] = None
    options: Optional[FootprintPadOptions] = None
    primitives: FootprintPadPrimitives = field(
        default_factory=FootprintPadPrimitives, metadata=m("kicad_omits_default")
    )
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
    file: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    hide: bool = field(default=False, metadata=m("kicad_kw_bool"))
    # UNDOCUMENTED: `offset`
    offset: FootprintModelCoord = field(
        default_factory=FootprintModelCoord, metadata=m("kicad_omits_default")
    )
    scale: FootprintModelCoord = field(
        default_factory=FootprintModelCoord, metadata=m("kicad_omits_default")
    )
    rotate: FootprintModelCoord = field(
        default_factory=FootprintModelCoord, metadata=m("kicad_omits_default")
    )
    # UNDOCUMENTED: `opacity`
    opacity: Optional[float] = None

    @validator("hide", pre=True)
    def _hide(cls, v):
        return v == "hide"


AutoplaceCost = Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


@dataclass(config=PydanticConfig, eq=False)
class Footprint(KicadPcbExpr):
    library_link: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    placed: bool = field(default=False, metadata=m("kicad_kw_bool"))
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
