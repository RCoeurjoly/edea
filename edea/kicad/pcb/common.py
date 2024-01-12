from dataclasses import field
from typing import Annotated, ClassVar, Literal, Optional
from uuid import UUID, uuid4

from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.common import Effects, Pts, Stroke

from .base import KicadPcbExpr
from .layer import CanonicalLayerName, WildCardLayerName


@dataclass(config=PydanticConfig, eq=False)
class Property(KicadPcbExpr):
    key: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    value: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]


@dataclass(config=PydanticConfig, eq=False)
class Position(KicadPcbExpr):
    x: Annotated[float, m("kicad_no_kw")] = 0
    y: Annotated[float, m("kicad_no_kw")] = 0
    angle: Annotated[float, m("kicad_no_kw", "kicad_omits_default")] = 0
    unlocked: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["at"]] = "at"


@dataclass(config=PydanticConfig, eq=False)
class ConnectionPads(KicadPcbExpr):
    type: Annotated[
        Literal["yes", "no", "full", "thru_hole_only", None], m("kicad_no_kw")
    ] = None
    clearance: float = 0
    kicad_expr_tag_name: ClassVar[Literal["connect_pads"]] = "connect_pads"


@dataclass(config=PydanticConfig, eq=False)
class ZoneKeepOutSettings(KicadPcbExpr):
    tracks: Literal["allowed", "not_allowed"]
    vias: Literal["allowed", "not_allowed"]
    pads: Literal["allowed", "not_allowed"]
    copperpour: Literal["allowed", "not_allowed"]
    footprints: Literal["allowed", "not_allowed"]
    kicad_expr_tag_name: ClassVar[Literal["keepout"]] = "keepout"


class ZoneFillIslandRemovalMode(StrEnum):
    Always = "0"
    Never = "1"
    MinimumArea = "2"


class ZoneFillHatchSmoothingLevel(StrEnum):
    No = "0"
    Fillet = "1"
    ArcMinimum = "2"
    ArcMaximum = "3"


class ZoneFillHatchBorderAlgorithm(StrEnum):
    ZoneMinimumThickness = "zone_min_thickness"
    HatchThickness = "hatch_thickness"


@dataclass(config=PydanticConfig, eq=False)
class ZoneFillSettings(KicadPcbExpr):
    yes: Annotated[bool, m("kicad_kw_bool")] = False
    mode: Annotated[Literal["hatch", "solid"], m("kicad_omits_default")] = "solid"
    thermal_gap: Optional[float] = None
    thermal_bridge_width: Optional[float] = None
    smoothing: Literal["chamfer", "fillet", None] = None
    # UNDOCUMENTED: `radius`
    radius: Optional[float] = None
    island_removal_mode: Optional[ZoneFillIslandRemovalMode] = None
    island_area_min: Optional[float] = None
    hatch_thickness: Optional[float] = None
    hatch_gap: Optional[float] = None
    hatch_orientation: Optional[float] = None
    hatch_smoothing_level: Optional[ZoneFillHatchSmoothingLevel] = None
    hatch_smoothing_value: Optional[float] = None
    hatch_border_algorithm: Optional[ZoneFillHatchBorderAlgorithm] = None
    hatch_min_hole_area: Optional[float] = None
    kicad_expr_tag_name: ClassVar[Literal["fill"]] = "fill"


@dataclass(config=PydanticConfig, eq=False)
class ZoneFillPolygon(KicadPcbExpr):
    layer: CanonicalLayerName
    island: Annotated[bool, m("kicad_kw_bool_empty")] = False
    pts: Pts = field(default_factory=Pts)
    kicad_expr_tag_name: ClassVar[Literal["filled_polygon"]] = "filled_polygon"


@dataclass(config=PydanticConfig, eq=False)
class Polygon(KicadPcbExpr):
    pts: list[Pts] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["polygon"]] = "polygon"


class Hatch(StrEnum):
    Edge = "edge"
    Full = "full"
    None_ = "none"


@dataclass(config=PydanticConfig, eq=False)
class ZoneAttrTearDrop(KicadPcbExpr):
    type: Literal["padvia", "track_end"] = "padvia"
    kicad_expr_tag_name: ClassVar[Literal["teardrop"]] = "teardrop"


@dataclass(config=PydanticConfig, eq=False)
class ZoneAttr(KicadPcbExpr):
    teardrop: ZoneAttrTearDrop
    kicad_expr_tag_name: ClassVar[Literal["attr"]] = "attr"


@dataclass(config=PydanticConfig, eq=False)
class Zone(KicadPcbExpr):
    """
    layers: some zones have `layers` instead of `layer`.
        But it's always guaranteed to have all the layers in the `layers` list
        after initialization.
    """

    locked: Annotated[bool, m("kicad_kw_bool")] = False
    net: int = 0
    net_name: str = ""
    layer: Optional[CanonicalLayerName] = None
    layers: Annotated[
        list[CanonicalLayerName | WildCardLayerName], m("kicad_always_quotes")
    ] = field(
        default_factory=list,
    )
    tstamp: UUID = field(default_factory=uuid4)
    name: Optional[str] = None
    hatch: tuple[Hatch, float] = (Hatch.None_, 0)
    priority: int | None = None
    attr: Optional[ZoneAttr] = None
    connect_pads: ConnectionPads = field(default_factory=ConnectionPads)
    min_thickness: float = 0
    filled_areas_thickness: Annotated[
        bool, m("kicad_bool_yes_no", "kicad_omits_default")
    ] = True
    keepout: Optional[ZoneKeepOutSettings] = None
    fill: Annotated[ZoneFillSettings, m("kicad_omits_default")] = field(
        default_factory=ZoneFillSettings,
    )
    polygons: list[Polygon] = field(default_factory=list)
    filled_polygons: list[ZoneFillPolygon] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class Group(KicadPcbExpr):
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    id: UUID = field(default_factory=uuid4)
    members: list[UUID] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class RenderCache(KicadPcbExpr):
    name: Annotated[str, m("kicad_no_kw")]
    number: Annotated[float, m("kicad_no_kw")]
    polygons: list[Polygon] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class BaseTextBox(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    text: Annotated[str, m("kicad_no_kw")] = ""
    start: Optional[tuple[float, float]] = None
    end: Optional[tuple[float, float]] = None
    pts: Optional[Pts] = None
    layer: CanonicalLayerName = "F.Cu"
    tstamp: UUID = field(default_factory=uuid4)
    effects: Effects = field(default_factory=Effects)
    render_cache: Optional[RenderCache] = None
    angle: Optional[float] = None
    stroke: Optional[Stroke] = None
    hide: Annotated[bool, m("kicad_kw_bool")] = False


@dataclass(config=PydanticConfig, eq=False)
class Net(KicadPcbExpr):
    number: Annotated[int, m("kicad_no_kw")]
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]


@dataclass(config=PydanticConfig, eq=False)
class Image(KicadPcbExpr):
    at: tuple[float, float]
    layer: CanonicalLayerName = "F.Cu"
    scale: Optional[float] = None
    data: list[str] = field(default_factory=list)
