from collections import UserList
from dataclasses import field
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import validator
from pydantic.dataclasses import dataclass

from edea.types.common import Effects, Pts, Stroke
from edea.types.config import PydanticConfig
from edea.types.meta import make_meta as m
from edea.types.pcb_layers import CanonicalLayerName, LayerType
from edea.types.s_expr import SExprList
from edea.types.str_enum import StrEnum

from .base import KicadPcbExpr


@dataclass(config=PydanticConfig, eq=False)
class Property(KicadPcbExpr):
    key: str
    value: str = ""


@dataclass(config=PydanticConfig, eq=False)
class Layer(KicadPcbExpr):
    ordinal: int
    name: CanonicalLayerName
    type: LayerType = "user"
    user_name: Optional[str] = None


@dataclass(config=PydanticConfig, eq=False)
class Layers(KicadPcbExpr, UserList):
    """
     This is constructed differently to other KicadExpr which are lists.
     The `layers` field in the KiCad PCB file is as follows:

    .. code-block:: text

         (layers
             (0 "F.Cu" signal)
             (31 "B.Cu" signal)
             ...
         )


    We have two options either complicate the parser to handle this, or handle
    the construction of the list ourselves. We've chosen the latter.
    """

    data: list[Layer] = field(default_factory=list)

    def __init__(self, *args):
        super().__init__()
        # Setting the self.data to a list of Layer objects, will make instances
        # of this class act as a list of Layer objects without the need to
        # access the self.data attribute.
        self.data = [Layer(*a) for a in args]


@dataclass(config=PydanticConfig, eq=False)
class PositionIdentifier(KicadPcbExpr):
    x: float = field(default=0, metadata=m("kicad_no_kw"))
    y: float = field(default=0, metadata=m("kicad_no_kw"))
    angle: float = field(default=0, metadata=m("kicad_no_kw", "kicad_omits_default"))
    unlocked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    kicad_expr_tag_name: Literal["at"] = "at"

    @classmethod
    def from_list(cls, expr: SExprList) -> "PositionIdentifier":
        assert isinstance(expr[0], str)
        assert isinstance(expr[1], str)
        x = float(expr[0])
        y = float(expr[1])
        unlocked = "unlocked" in expr
        angle = 0
        if len(expr) > 2 and isinstance(expr[2], str) and expr[2] != "unlocked":
            angle = float(expr[2])
        return cls(x, y, angle, unlocked)


@dataclass(config=PydanticConfig, eq=False)
class ConnectionPads(KicadPcbExpr):
    type: Optional[Literal["yes", "no", "full", "thru_hole_only"]] = None
    clearance: float = 0


@dataclass(config=PydanticConfig, eq=False)
class ZoneKeepOutSettings(KicadPcbExpr):
    tracks: Literal["allowed", "not_allowed"]
    vias: Literal["allowed", "not_allowed"]
    pads: Literal["allowed", "not_allowed"]
    copperpour: Literal["allowed", "not_allowed"]
    footprints: Literal["allowed", "not_allowed"]
    kicad_expr_tag_name: Literal["keepout"] = "keepout"


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
    yes: bool = field(default=False, metadata=m("kicad_kw_bool"))
    island_removal_mode: Optional[ZoneFillIslandRemovalMode] = None
    mode: Literal["hatch", "solid"] = "solid"
    thermal_gap: Optional[float] = None
    thermal_bridge_width: Optional[float] = None
    smoothing: Optional[Literal["chamfer", "fillet"]] = None
    island_area_min: Optional[float] = None
    hatch_thickness: Optional[float] = None
    hatch_gap: Optional[float] = None
    hatch_orientation: Optional[float] = None
    hatch_smoothing_level: Optional[ZoneFillHatchSmoothingLevel] = None
    hatch_smoothing_value: Optional[float] = None
    hatch_border_algorithm: Optional[ZoneFillHatchBorderAlgorithm] = None
    hatch_min_hole_area: Optional[float] = None
    kicad_expr_tag_name: Literal["fill"] = "fill"
    # UNDOCUMENTED: `radius`
    radius: Optional[float] = None


@dataclass(config=PydanticConfig, eq=False)
class ZoneFillPolygon(KicadPcbExpr):
    layer: CanonicalLayerName
    pts: Pts = field(default_factory=Pts)
    island: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    kicad_expr_tag_name: Literal["filled_polygon"] = "filled_polygon"


@dataclass(config=PydanticConfig, eq=False)
class ZoneFillSegment(KicadPcbExpr):
    layer: CanonicalLayerName
    pts: Pts
    kicad_expr_tag_name: Literal["filled_segments"] = "filled_segments"


@dataclass(config=PydanticConfig, eq=False)
class ZonePolygon(KicadPcbExpr):
    pts: Pts = field(default_factory=Pts)
    kicad_expr_tag_name: Literal["polygon"] = "polygon"


class Hatch(StrEnum):
    Edge = "edge"
    Full = "full"
    None_ = "none"


@dataclass(config=PydanticConfig, eq=False)
class Zone(KicadPcbExpr):
    """
    layers: some zones have `layers` instead of `layer`.
        But it's always guaranteed to have all the layers in the `layers` list
        after initialization.
    """

    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    net: int = 0
    tstamp: UUID = field(default_factory=uuid4)
    hatch: tuple[Hatch, float] = (Hatch.None_, 0)
    connect_pads: ConnectionPads = field(default_factory=ConnectionPads)
    min_thickness: float = 0
    fill: ZoneFillSettings = field(default_factory=ZoneFillSettings)
    layer: Optional[str] = None
    layers: list[str] = field(default_factory=list)
    polygon: list[ZonePolygon] = field(default_factory=list)
    keepout: Optional[ZoneKeepOutSettings] = None
    name: Optional[str] = None
    priority: int = 0
    net_name: str = ""
    filled_areas_thickness: bool = field(
        default=True, metadata=m("kicad_bool_yes_no", "kicad_omits_default")
    )
    filled_polygon: list[ZoneFillPolygon] = field(default_factory=list)
    fill_segments: list[ZoneFillSegment] = field(default_factory=list)

    @validator("layers", pre=True)
    def _layers(cls, v):
        if isinstance(v, str):
            return [v]
        return v

    def __post_init__(self):
        if self.layer is not None:
            self.layers = [self.layer]


@dataclass(config=PydanticConfig, eq=False)
class Group(KicadPcbExpr):
    name: str
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    id: UUID = field(default_factory=uuid4)
    members: list[UUID] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class BaseTextBox(KicadPcbExpr):
    text: str
    layer: CanonicalLayerName
    tstmap: UUID
    effects: Effects
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    start: Optional[tuple[float, float]] = None
    end: Optional[tuple[float, float]] = None
    pts: Optional[Pts] = None
    angle: Optional[float] = None
    stroke: Optional[Stroke] = None
    hide: bool = field(default=False, metadata=m("kicad_kw_bool"))
