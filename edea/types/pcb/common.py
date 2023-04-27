from collections import UserList
from dataclasses import field
from enum import Enum
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import root_validator, validator
from pydantic.dataclasses import dataclass

from edea.types.common import Effects, Pts
from edea.types.config import PydanticConfig

from edea.types.pcb_layers import CanonicalLayerName, LayerType
from .base import KicadPcbExpr


@dataclass(config=PydanticConfig)
class Property(KicadPcbExpr):
    key: str
    value: str = ""


@dataclass(config=PydanticConfig)
class Layer(KicadPcbExpr):
    ordinal: int
    name: CanonicalLayerName
    type: LayerType = "user"
    user_name: Optional[str] = None


@dataclass(config=PydanticConfig)
class Layers(KicadPcbExpr, UserList):
    """
    This is constructed differently to other KicadExpr which are lists.
    The `layers` field in the KiCad PCB file is as follows:
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


@dataclass(config=PydanticConfig)
class PositionIdentifier(KicadPcbExpr):
    x: float = 0
    y: float = 0
    angle: Optional[float] = None
    unlocked: bool = False
    kicad_expr_tag_name: Literal["at"] = "at"

    def __len__(self):
        return 3 if self.angle is not None else 2

    def __getitem__(self, index: int) -> Optional[float]:
        return [self.x, self.y, self.angle][index]

    @root_validator(pre=True)
    def validate(cls, args):
        """If unlocked is passed to angle, set angle to None and unlocked to True."""
        if "unlocked" in args.values() and args.get("angle", None) is not None:
            args["angle"] = None
            args["unlocked"] = True
        return args


@dataclass(config=PydanticConfig)
class TextStroke(KicadPcbExpr):
    width: float
    type: Literal["dash", "dash_dot", "dash_dot_dot", "dot", "default", "solid"]
    color: tuple[float, float, float, float]
    kicad_expr_tag_name: Literal["stroke"] = "stroke"


@dataclass(config=PydanticConfig)
class ConnectionPads(KicadPcbExpr):
    type: Optional[Literal["yes", "no", "full", "thru_hole_only"]] = None
    clearance: float = 0


@dataclass(config=PydanticConfig)
class FilledAreaThickness(KicadPcbExpr):
    no: bool


@dataclass(config=PydanticConfig)
class ZoneKeepOutSettings(KicadPcbExpr):
    tracks: Literal["allowed", "not_allowed"]
    vias: Literal["allowed", "not_allowed"]
    pads: Literal["allowed", "not_allowed"]
    copperpour: Literal["allowed", "not_allowed"]
    footprints: Literal["allowed", "not_allowed"]
    kicad_expr_tag_name: Literal["keepout"] = "keepout"


class ZoneFillIslandRemovalMode(str, Enum):
    Always = "0"
    Never = "1"
    MinimumArea = "2"


class ZoneFillHatchSmoothingLevel(str, Enum):
    No = "0"
    Fillet = "1"
    ArcMinimum = "2"
    ArcMaximum = "3"


class ZoneFillHatchBorderAlgorithm(str, Enum):
    ZoneMinimumThickness = "zone_min_thickness"
    HatchThickness = "hatch_thickness"


@dataclass(config=PydanticConfig)
class ZoneFillSettings(KicadPcbExpr):
    yes: bool = False
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


@dataclass(config=PydanticConfig)
class IsIsland(KicadPcbExpr):
    kicad_expr_tag_name: Literal["island"] = "island"
    # holds no data, appears simply as "(island)" with parens.
    # maybe there is a less ugly solution to this?


@dataclass(config=PydanticConfig)
class ZoneFillPolygon(KicadPcbExpr):
    layer: CanonicalLayerName
    pts: Pts = field(default_factory=Pts)
    island: Optional[IsIsland] = None
    kicad_expr_tag_name: Literal["filled_polygon"] = "filled_polygon"


@dataclass(config=PydanticConfig)
class ZoneFillSegment(KicadPcbExpr):
    layer: CanonicalLayerName
    pts: Pts
    kicad_expr_tag_name: Literal["filled_segments"] = "filled_segments"


@dataclass(config=PydanticConfig)
class ZonePolygon(KicadPcbExpr):
    pts: Pts = field(default_factory=Pts)
    kicad_expr_tag_name: Literal["polygon"] = "polygon"


class Hatch(str, Enum):
    Edge = "edge"
    Full = "full"
    None_ = "none"


@dataclass(config=PydanticConfig)
class Zone(KicadPcbExpr):
    """
    :param layers: some zones have `layers` instead of `layer`.
        But it's always guaranteed to have all the layers in the `layers` list
        after initialization.
    """

    locked: bool = False
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
    filled_areas_thickness: Optional[FilledAreaThickness] = None
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


@dataclass(config=PydanticConfig)
class Group(KicadPcbExpr):
    name: str
    locked: bool = False
    id: UUID = field(default_factory=uuid4)
    members: list[UUID] = field(default_factory=list)


@dataclass(config=PydanticConfig)
class IsRemoveUnusedLayers(KicadPcbExpr):
    kicad_expr_tag_name: Literal["remove_unused_layers"] = "remove_unused_layers"
    # holds no data, appears simply as "(remove_unused_layers)" with parens.
    # maybe there is a less ugly solution to this?


@dataclass(config=PydanticConfig)
class IsKeepEndLayers(KicadPcbExpr):
    kicad_expr_tag_name: Literal["keep_end_layers"] = "keep_end_layers"
    # holds no data, appears simply as "(keep_end_layers)" with parens.
    # maybe there is a less ugly solution to this?


@dataclass(config=PydanticConfig)
class BaseTextBox(KicadPcbExpr):
    text: str
    layer: CanonicalLayerName
    tstmap: UUID
    effects: Effects
    locked: bool = False
    start: Optional[tuple[float, float]] = None
    end: Optional[tuple[float, float]] = None
    pts: Optional[Pts] = None
    angle: Optional[float] = None
    stroke: Optional[TextStroke] = None
    hide: bool = False
