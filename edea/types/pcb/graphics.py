from dataclasses import field
from enum import Enum
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic.dataclasses import dataclass

from edea.types.common import Effects, Pts
from edea.types.config import PydanticConfig

from .base import KicadPcbExpr
from .common import BaseTextBox, CanonicalLayerName, PositionIdentifier


@dataclass(config=PydanticConfig)
class GraphicalText(KicadPcbExpr):
    text: str = ""
    locked: bool = False
    at: PositionIdentifier = field(default_factory=PositionIdentifier)
    effects: Effects = field(default_factory=Effects)
    layer: Optional[CanonicalLayerName] = None
    tstamp: Optional[UUID] = None
    kicad_expr_tag_name: Literal["gr_text"] = "gr_text"


@dataclass(config=PydanticConfig)
class GraphicalTextBox(BaseTextBox):
    kicad_expr_tag_name: Literal["gr_text_box"] = "gr_text_box"


@dataclass(config=PydanticConfig)
class GraphicalLine(KicadPcbExpr):
    locked: bool = False
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: float = 0
    layer: Optional[CanonicalLayerName] = None
    tstamp: Optional[UUID] = None
    locked: bool = False
    angle: Optional[float] = None
    kicad_expr_tag_name: Literal["gr_line"] = "gr_line"


@dataclass(config=PydanticConfig)
class GraphicalRectangle(KicadPcbExpr):
    locked: bool = False
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: float = 0
    tstamp: Optional[UUID] = None
    layer: Optional[CanonicalLayerName] = None
    fill: Optional[Literal["solid", "yes", "none"]] = None
    kicad_expr_tag_name: Literal["gr_rect"] = "gr_rect"


@dataclass(config=PydanticConfig)
class GraphicalCircle(KicadPcbExpr):
    locked: bool = False
    center: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: float = 0
    layer: Optional[CanonicalLayerName] = None
    tstamp: Optional[UUID] = None
    locked: bool = False
    fill: Optional[Literal["solid", "yes", "none"]] = None
    kicad_expr_tag_name: Literal["gr_circle"] = "gr_circle"


@dataclass(config=PydanticConfig)
class GraphicalArc(KicadPcbExpr):
    locked: bool = False
    start: tuple[float, float] = (0, 0)
    mid: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: float = 0
    layer: Optional[CanonicalLayerName] = None
    tstamp: Optional[UUID] = None
    locked: bool = False
    kicad_expr_tag_name: Literal["gr_arc"] = "gr_arc"


@dataclass(config=PydanticConfig)
class GraphicalPolygon(KicadPcbExpr):
    locked: bool = False
    width: float = 0
    layer: Optional[CanonicalLayerName] = None
    tstamp: Optional[UUID] = None
    locked: bool = False
    pts: Pts = field(default_factory=Pts)
    fill: Optional[Literal["solid", "yes", "none"]] = None
    kicad_expr_tag_name: Literal["gr_poly"] = "gr_poly"


@dataclass(config=PydanticConfig)
class GraphicalBezier(KicadPcbExpr):
    locked: bool = False
    width: float = 0
    pts: Pts = field(default_factory=Pts)
    layer: Optional[CanonicalLayerName] = None
    tstamp: Optional[UUID] = None
    kicad_expr_tag_name: Literal["bezier"] = "bezier"


@dataclass(config=PydanticConfig)
class GraphicalCurve(GraphicalBezier):
    """
    This isn't documented in the Kicad docs, but it is in some files.
    This is what bezier was called before KiCad 7.
    """

    kicad_expr_tag_name: Literal["gr_curve"] = "gr_curve"


@dataclass(config=PydanticConfig)
class GraphicalBoundingBox(KicadPcbExpr):
    locked: bool = False
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    kicad_expr_tag_name: Literal["gr_bbox"] = "gr_bbox"


class DimensionFormatUnits(str, Enum):
    Inches = "0"
    Mils = "1"
    Millimeters = "2"
    Automatic = "3"


class DimensionFormatUnitsFormat(str, Enum):
    NoSuffix = "0"
    BareSuffix = "1"
    WrapSuffix = "2"


@dataclass(config=PydanticConfig)
class DimensionFormat(KicadPcbExpr):
    units: DimensionFormatUnits
    units_format: DimensionFormatUnitsFormat
    precision: int
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    override_value: Optional[str] = None
    suppress_zeroes: bool = False
    kicad_expr_tag_name: Literal["format"] = "format"


class DimensionStyleTextPositionMode(str, Enum):
    Outside = "0"
    InLine = "1"
    Manual = "2"


class DimensionStyleTextFrame(str, Enum):
    NoFrame = "0"
    Rectangle = "1"
    Circle = "2"
    RoundedRectangle = "3"


@dataclass(config=PydanticConfig)
class DimensionStyle(KicadPcbExpr):
    thickness: float = 0.0
    arrow_length: float = 0.0
    text_position_mode: DimensionStyleTextPositionMode = (
        DimensionStyleTextPositionMode.Outside
    )
    extension_height: Optional[float] = None
    extension_offset: Optional[float] = None
    text_frame: Optional[DimensionStyleTextFrame] = None
    keep_text_aligned: bool = False
    kicad_expr_tag_name: Literal["style"] = "style"


@dataclass(config=PydanticConfig)
class GraphicalDimension(KicadPcbExpr):
    locked: bool = False
    type: Literal["aligned", "leader", "center", "orthogonal", "radial"] = "aligned"
    layer: CanonicalLayerName = "F.Cu"
    tstamp: UUID = field(default_factory=uuid4)
    style: DimensionStyle = field(default_factory=DimensionStyle)
    pts: Pts = field(default_factory=Pts)
    height: Optional[float] = None
    orientation: Optional[float] = None
    leader_length: Optional[float] = None
    gr_text: Optional[GraphicalText] = None
    format: Optional[DimensionFormat] = None
    kicad_expr_tag_name: Literal["dimension"] = "dimension"
