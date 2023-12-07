from dataclasses import field
import dataclasses
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import validator
from pydantic.dataclasses import dataclass

from edea.kicad.base import ParsedKwargs
from edea.kicad.common import Effects, Pts, Stroke
from edea.kicad.config import PydanticConfig
from edea.kicad.meta import make_meta as m
from edea.kicad.s_expr import SExprList
from edea.kicad.str_enum import StrEnum

from .base import KicadPcbExpr
from .layer import CanonicalLayerName


@dataclass(config=PydanticConfig, eq=False)
class Property(KicadPcbExpr):
    key: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    value: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))


@dataclass(config=PydanticConfig, eq=False)
class PositionIdentifier(KicadPcbExpr):
    x: float = field(default=0, metadata=m("kicad_no_kw"))
    y: float = field(default=0, metadata=m("kicad_no_kw"))
    angle: float = field(default=0, metadata=m("kicad_no_kw", "kicad_omits_default"))
    unlocked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    kicad_expr_tag_name: Literal["at"] = "at"

    @classmethod
    def from_list(cls, expr: SExprList) -> "PositionIdentifier":
        if len(expr) < 2 or len(expr) > 4:
            raise ValueError(
                f"Expecting expression of length 2-4 got: {len(expr)=} {expr=}"
            )

        if (
            not isinstance(expr[0], str)
            or not isinstance(expr[1], str)
            or (len(expr) > 2 and not isinstance(expr[2], str))
            or (len(expr) > 3 and not isinstance(expr[3], str))
        ):
            raise ValueError(f"Expecting only atoms in expression got: {expr}")

        x = float(expr[0])
        y = float(expr[1])

        angle = 0
        if len(expr) > 2 and expr[2] != "unlocked":
            # the raise is unreachable, it's just a type assertion to keep the
            # typechecker happy
            if not isinstance(expr[2], str):
                raise ValueError
            angle = float(expr[2])

        unlocked = "unlocked" in expr

        return cls(x, y, angle, unlocked)


@dataclass(config=PydanticConfig, eq=False)
class ConnectionPads(KicadPcbExpr):
    type: Literal["yes", "no", "full", "thru_hole_only", None] = field(
        default=None, metadata=m("kicad_no_kw")
    )
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
    mode: Literal["hatch", "solid"] = field(
        default="solid", metadata=m("kicad_omits_default")
    )
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
    island: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    pts: Pts = field(default_factory=Pts)
    kicad_expr_tag_name: Literal["filled_polygon"] = "filled_polygon"


@dataclass(config=PydanticConfig, eq=False)
class ZoneFillSegment(KicadPcbExpr):
    layer: CanonicalLayerName
    pts: Pts
    kicad_expr_tag_name: Literal["filled_segments"] = "filled_segments"


@dataclass(config=PydanticConfig, eq=False)
class Polygon(KicadPcbExpr):
    pts: list[Pts] = field(default_factory=list)
    kicad_expr_tag_name: Literal["polygon"] = "polygon"


class Hatch(StrEnum):
    Edge = "edge"
    Full = "full"
    None_ = "none"


@dataclass(config=PydanticConfig, eq=False)
class ZoneAttrTearDrop(KicadPcbExpr):
    type: Literal["padvia", "track_end"] = "padvia"


@dataclass(config=PydanticConfig, eq=False)
class ZoneAttr(KicadPcbExpr):
    teardrop: ZoneAttrTearDrop


@dataclass(config=PydanticConfig, eq=False)
class Zone(KicadPcbExpr):
    """
    layers: some zones have `layers` instead of `layer`.
        But it's always guaranteed to have all the layers in the `layers` list
        after initialization.
    """

    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    net: int = 0
    net_name: str = ""
    layer: Optional[str] = None
    tstamp: UUID = field(default_factory=uuid4)
    name: Optional[str] = None
    hatch: tuple[Hatch, float] = (Hatch.None_, 0)
    priority: int = 0
    attr: Optional[ZoneAttr] = None
    connect_pads: ConnectionPads = field(default_factory=ConnectionPads)
    min_thickness: float = 0
    fill: ZoneFillSettings = field(default_factory=ZoneFillSettings)
    layers: list[str] = field(default_factory=list)
    polygon: list[Polygon] = field(default_factory=list)
    keepout: Optional[ZoneKeepOutSettings] = None
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
    name: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    id: UUID = field(default_factory=uuid4)
    members: list[UUID] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class RenderCache(KicadPcbExpr):
    name: str = field(metadata=m("kicad_no_kw"))
    number: float = field(metadata=m("kicad_no_kw"))
    polygon: list[Polygon] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class BaseTextBox(KicadPcbExpr):
    text: str = field(metadata=m("kicad_no_kw"))
    start: Optional[tuple[float, float]] = None
    end: Optional[tuple[float, float]] = None
    pts: Optional[Pts] = None
    layer: CanonicalLayerName = "F.Cu"
    tstamp: UUID = field(default_factory=uuid4)
    effects: Effects = field(default_factory=Effects)
    render_cache: Optional[RenderCache] = None
    angle: Optional[float] = None
    stroke: Optional[Stroke] = None
    hide: bool = field(default=False, metadata=m("kicad_kw_bool"))
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))

    # pylint: disable=duplicate-code
    @classmethod
    def _process_args_for_parsing(
        cls, args: list[str], kwargs: ParsedKwargs
    ) -> tuple[list[str], ParsedKwargs]:
        if len(args) == 2 and args[0] == "locked":
            args = [args[1]]
            kwargs = {**kwargs, "locked": [["true"]]}
        return args, kwargs

    # pylint: disable=duplicate-code
    def _process_fields_for_serialization(
        self, fields: tuple[dataclasses.Field, ...]
    ) -> tuple[dataclasses.Field, ...]:
        # move locked back to the front
        locked = None
        for f in fields:
            if f.name == "locked":
                locked = f
        if locked is None:
            raise Exception('Expecting a "locked" field.')
        rest = [f for f in fields if f.name != "locked"]
        return tuple([locked] + rest)


@dataclass(config=PydanticConfig, eq=False)
class Net(KicadPcbExpr):
    number: int = field(metadata=m("kicad_no_kw"))
    name: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))


@dataclass(config=PydanticConfig, eq=False)
class Image(KicadPcbExpr):
    at: tuple[float, float]
    layer: CanonicalLayerName = "F.Cu"
    scale: Optional[float] = None
    data: list[str] = field(default_factory=list)
