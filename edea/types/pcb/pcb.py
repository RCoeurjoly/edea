"""
Dataclasses describing the contents of .kicad_sch files.

SPDX-License-Identifier: EUPL-1.2
"""
from dataclasses import field
from enum import Enum
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import root_validator, validator
from pydantic.dataclasses import dataclass

from edea.types.common import (
    Image as BaseImage,
    Paper,
    PaperStandard,
    TitleBlock,
    VersionError,
)
from edea.types.config import PydanticConfig
from edea.types.pcb_layers import CanonicalLayerName

from .base import KicadPcbExpr
from .common import (
    Group,
    IsKeepEndLayers,
    IsRemoveUnusedLayers,
    Layers,
    PositionIdentifier,
    Property,
    Zone,
)
from .footprint import Footprint
from .graphics import (
    GraphicalArc,
    GraphicalBezier,
    GraphicalBoundingBox,
    GraphicalCircle,
    GraphicalCurve,
    GraphicalDimension,
    GraphicalLine,
    GraphicalPolygon,
    GraphicalRectangle,
    GraphicalText,
    GraphicalTextBox,
)


@dataclass(config=PydanticConfig)
class General(KicadPcbExpr):
    thickness: float = 0


@dataclass(config=PydanticConfig)
class StackUpLayerThickness(KicadPcbExpr):
    value: float
    locked: bool = False


@dataclass(config=PydanticConfig)
class StackUpLayer(KicadPcbExpr):
    name: Optional[str]
    # This is an arbitrary string, not a `CanonicalLayer`.
    type: str
    color: Optional[str] = None
    thickness: Optional[StackUpLayerThickness] = None
    material: Optional[str] = None
    epsilon_r: Optional[float] = None
    loss_tangent: Optional[float] = None
    kicad_expr_tag_name: Literal["layer"] = "layer"

    @validator("name", pre=True)
    def validate_name(cls, v):
        if v is None:
            return "dielectric"
        return None


@dataclass(config=PydanticConfig)
class Stackup(KicadPcbExpr):
    layer: list[StackUpLayer] = field(default_factory=list)
    copper_finish: Optional[str] = "None"
    dielectric_constraints: Optional[Literal["yes", "no"]] = None
    edge_connector: Optional[Literal["yes", "bevelled"]] = None
    castellated_pads: Optional[Literal["yes"]] = None
    edge_plating: Optional[Literal["yes"]] = None


class PlotOutputFormat(str, Enum):
    GERBER = "0"
    POSTSCRIPT = "1"
    SVG = "2"
    DXF = "3"
    HPGL = "4"
    PDF = "5"


@dataclass(config=PydanticConfig)
class PlotSettings(KicadPcbExpr):
    layerselection: str
    disableapertmacros: bool
    usegerberextensions: bool
    usegerberattributes: bool
    usegerberadvancedattributes: bool
    creategerberjobfile: bool
    svgprecision: int
    excludeedgelayer: bool
    plotframeref: bool
    viasonmask: bool
    mode: Literal[1, 2]
    useauxorigin: bool
    hpglpennumber: int
    hpglpenspeed: int
    hpglpendiameter: float
    dxfpolygonmode: bool
    dxfimperialunits: bool
    dxfusepcbnewfont: bool
    psnegative: bool
    psa4output: bool
    plotreference: bool
    plotvalue: bool
    plotinvisibletext: bool
    sketchpadsonfab: bool
    subtractmaskfromsilk: bool
    outputformat: PlotOutputFormat = PlotOutputFormat.GERBER
    svguseinch: bool = False
    mirror: bool = False
    drillshape: int = 0
    scaleselection: int = 0
    outputdirectory: str = ""
    gerberprecision: Optional[int] = None
    # UNDOCUMENTED: `dashed_line_dash_ratio`, `dashed_line_gap_ratio`
    dashed_line_dash_ratio: Optional[float] = None
    dashed_line_gap_ratio: Optional[float] = None

    @validator("mode", pre=True)
    def parse_mode(cls, v):
        if isinstance(v, str):
            return int(v)
        return v

    kicad_expr_tag_name: Literal["pcbplotparams"] = "pcbplotparams"


@dataclass(config=PydanticConfig)
class Setup(KicadPcbExpr):
    pcbplotparams: PlotSettings
    stackup: Optional[Stackup] = None
    pad_to_mask_clearance: float = 0.0
    solder_mask_min_width: Optional[float] = 0.0
    pad_to_paste_clearance: Optional[float] = 0.0
    pad_to_paste_clearance_ratio: Optional[float] = 100.0
    aux_axis_origin: Optional[tuple[float, float]] = (0.0, 0.0)
    grid_origin: Optional[tuple[float, float]] = (0.0, 0.0)


@dataclass(config=PydanticConfig)
class Net(KicadPcbExpr):
    oridinal: int
    name: str


@dataclass(config=PydanticConfig)
class Segment(KicadPcbExpr):
    locked: bool = False
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: float = 0.0
    layer: CanonicalLayerName = "F.Cu"
    net: int = 0
    tstamp: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig)
class IsFreeVia(KicadPcbExpr):
    kicad_expr_tag_name: Literal["free"] = "free"
    # holds no data, appears simply as "(free)" with parens.
    # maybe there is a less ugly solution to this?


@dataclass(config=PydanticConfig)
class Via(KicadPcbExpr):
    type: Optional[Literal["blind", "micro", "through"]] = "through"
    locked: bool = False
    at: tuple[float, float] = (0, 0)
    size: float = 0
    drill: float = 0
    net: int = 0
    tstamp: UUID = field(default_factory=uuid4)
    layers: list[str] = field(default_factory=list)
    remove_unused_layers: Optional[IsRemoveUnusedLayers] = None
    keep_end_layers: Optional[IsKeepEndLayers] = None
    free: Optional[IsFreeVia] = None

    @root_validator(pre=True)
    def validate(cls, fields):
        values = list(fields.values())
        if values[0] == "locked":
            fields["locked"] = "locked"
            fields["type"] = "through"
        return fields


@dataclass(config=PydanticConfig)
class Arc(KicadPcbExpr):
    locked: bool = False
    start: tuple[float, float] = (0, 0)
    mid: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: float = 0.0
    net: int = 0
    tstamp: UUID = field(default_factory=uuid4)
    layer: CanonicalLayerName = "F.Cu"


@dataclass(config=PydanticConfig)
class Target(KicadPcbExpr):
    type: str
    at: PositionIdentifier
    size: float
    width: float
    layer: CanonicalLayerName
    tstamp: Optional[UUID] = None


@dataclass(config=PydanticConfig)
class Image(BaseImage, KicadPcbExpr):
    layer: CanonicalLayerName = "F.Cu"


@dataclass(config=PydanticConfig)
class Pcb(KicadPcbExpr):
    setup: Setup
    version: Literal["20211014"] = "20211014"
    generator: str = "edea"
    general: General = field(default_factory=General)
    title_block: Optional[TitleBlock] = None
    paper: Paper = field(default_factory=PaperStandard)
    layers: Layers = field(default_factory=Layers)
    property: list[Property] = field(default_factory=list)
    net: list[Net] = field(default_factory=list)
    footprint: list[Footprint] = field(default_factory=list)
    zone: list[Zone] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)

    # Graphics
    gr_line: list[GraphicalLine] = field(default_factory=list)
    gr_text: list[GraphicalText] = field(default_factory=list)
    gr_text_box: list[GraphicalTextBox] = field(default_factory=list)
    gr_line: list[GraphicalLine] = field(default_factory=list)
    gr_rect: list[GraphicalRectangle] = field(default_factory=list)
    gr_circle: list[GraphicalCircle] = field(default_factory=list)
    gr_curve: list[GraphicalCurve] = field(default_factory=list)
    gr_arc: list[GraphicalArc] = field(default_factory=list)
    gr_poly: list[GraphicalPolygon] = field(default_factory=list)
    bezier: list[GraphicalBezier] = field(default_factory=list)
    gr_bbox: list[GraphicalBoundingBox] = field(default_factory=list)
    dimension: list[GraphicalDimension] = field(default_factory=list)
    # end Graphics

    # Tracks
    segment: list[Segment] = field(default_factory=list)
    via: list[Via] = field(default_factory=list)
    arc: list[Arc] = field(default_factory=list)
    # end Tracks
    group: list[Group] = field(default_factory=list)

    # UNDOCUMENTED: `target`
    target: list[Target] = field(default_factory=list)

    @validator("version")
    @classmethod
    def check_version(cls, v) -> Literal["20211014"]:
        v = str(v)
        if v != "20211014":
            raise VersionError(
                f"Only the stable KiCad 6 pcb file format, i.e. version '20211014', "
                f"is supported. Got '{v}'."
            )
        return v

    kicad_expr_tag_name: Literal["kicad_pcb"] = "kicad_pcb"
