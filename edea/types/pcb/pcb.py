"""
Dataclasses describing the contents of .kicad_pcb files.

SPDX-License-Identifier: EUPL-1.2
"""
import itertools
import math
from dataclasses import field
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import root_validator, validator
from pydantic.dataclasses import dataclass

from edea.types.base import custom_serializer
from edea.types.common import Image as BaseImage
from edea.types.common import Paper, PaperStandard, TitleBlock, VersionError
from edea.types.config import PydanticConfig
from edea.types.meta import make_meta as m
from edea.types.s_expr import SExprList
from edea.types.str_enum import StrEnum

from .base import KicadPcbExpr
from .common import Group, Net, PositionIdentifier, Property, Zone
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
from .layer import CanonicalLayerName, Layer, layer_to_list


@dataclass(config=PydanticConfig, eq=False)
class General(KicadPcbExpr):
    thickness: float = 0


@dataclass(config=PydanticConfig, eq=False)
class StackupLayerThickness(KicadPcbExpr):
    value: float = field(metadata=m("kicad_no_kw"))
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    kicad_expr_tag_name: Literal["thickness"] = "thickness"


@dataclass(config=PydanticConfig, eq=False)
class StackupLayer(KicadPcbExpr):
    name: str = field(metadata=m("kicad_no_kw", "kicad_always_quotes"))
    # This is an arbitrary string, not a `CanonicalLayer`.
    type: str
    color: Optional[str] = field(default=None, metadata=m("kicad_always_quotes"))
    thickness: Optional[StackupLayerThickness] = None
    material: Optional[str] = field(default=None, metadata=m("kicad_always_quotes"))
    epsilon_r: Optional[float] = None
    loss_tangent: Optional[float] = None
    kicad_expr_tag_name: Literal["layer"] = "layer"


@dataclass(config=PydanticConfig, eq=False)
class Stackup(KicadPcbExpr):
    layer: list[StackupLayer] = field(default_factory=list)
    copper_finish: Optional[str] = None
    dielectric_constraints: bool = field(
        default=False, metadata=m("kicad_bool_yes_no", "kicad_omits_default")
    )
    edge_connector: Literal["yes", "bevelled", None] = field(
        default=None, metadata=m("kicad_omits_default")
    )
    castellated_pads: bool = field(
        default=False, metadata=m("kicad_bool_yes_no", "kicad_omits_default")
    )
    edge_plating: bool = field(
        default=False, metadata=m("kicad_bool_yes_no", "kicad_omits_default")
    )


class PlotOutputFormat(StrEnum):
    GERBER = "0"
    POSTSCRIPT = "1"
    SVG = "2"
    DXF = "3"
    HPGL = "4"
    PDF = "5"


@dataclass(config=PydanticConfig, eq=False)
class PlotSettings(KicadPcbExpr):
    layerselection: str = "0x00010fc_ffffffff"
    disableapertmacros: bool = False
    usegerberextensions: bool = False
    usegerberattributes: bool = True
    usegerberadvancedattributes: bool = True
    creategerberjobfile: bool = True
    svgprecision: int = 4
    excludeedgelayer: bool = False
    plotframeref: bool = False
    viasonmask: bool = False
    mode: Literal[1, 2] = 1
    useauxorigin: bool = False
    hpglpennumber: int = 1
    hpglpenspeed: int = 20
    hpglpendiameter: float = 15.0
    dxfpolygonmode: bool = True
    dxfimperialunits: bool = True
    dxfusepcbnewfont: bool = True
    psnegative: bool = False
    psa4output: bool = False
    plotreference: bool = True
    plotvalue: bool = True
    plotinvisibletext: bool = False
    sketchpadsonfab: bool = False
    subtractmaskfromsilk: bool = False
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


@dataclass(config=PydanticConfig, eq=False)
class Setup(KicadPcbExpr):
    stackup: Optional[Stackup] = None
    pad_to_mask_clearance: float = 0.0
    solder_mask_min_width: float = field(default=0.0, metadata=m("kicad_omits_default"))
    pad_to_paste_clearance: float = field(
        default=0.0, metadata=m("kicad_omits_default")
    )
    pad_to_paste_clearance_ratio: float = field(
        default=100.0, metadata=m("kicad_omits_default")
    )
    aux_axis_origin: tuple[float, float] = field(
        default=(0.0, 0.0), metadata=m("kicad_omits_default")
    )
    grid_origin: tuple[float, float] = field(
        default=(0.0, 0.0), metadata=m("kicad_omits_default")
    )
    pcbplotparams: PlotSettings = field(default_factory=PlotSettings)


@dataclass(config=PydanticConfig, eq=False)
class Segment(KicadPcbExpr):
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: float = 0.0
    layer: CanonicalLayerName = "F.Cu"
    net: int = 0
    tstamp: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class Via(KicadPcbExpr):
    type: Literal["blind", "micro", "through"] = field(
        default="through", metadata=m("kicad_no_kw", "kicad_omits_default")
    )
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    at: tuple[float, float] = (0, 0)
    size: float = 0
    drill: float = 0
    net: int = 0
    tstamp: UUID = field(default_factory=uuid4)
    layers: list[str] = field(default_factory=list)
    remove_unused_layers: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    keep_end_layers: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))
    free: bool = field(default=False, metadata=m("kicad_kw_bool_empty"))

    @root_validator(pre=True)
    def validate(cls, fields):
        values = list(fields.values())
        if values[0] == "locked":
            fields["locked"] = "locked"
            fields["type"] = "through"
        return fields


@dataclass(config=PydanticConfig, eq=False)
class Arc(KicadPcbExpr):
    locked: bool = field(default=False, metadata=m("kicad_kw_bool"))
    start: tuple[float, float] = (0, 0)
    mid: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: float = 0.0
    net: int = 0
    tstamp: UUID = field(default_factory=uuid4)
    layer: CanonicalLayerName = "F.Cu"


@dataclass(config=PydanticConfig, eq=False)
class Target(KicadPcbExpr):
    type: str = field(metadata=m("kicad_no_kw"))
    at: PositionIdentifier
    size: float
    width: float
    layer: CanonicalLayerName
    tstamp: Optional[UUID] = None


@dataclass(config=PydanticConfig, eq=False)
class Image(BaseImage, KicadPcbExpr):
    layer: CanonicalLayerName = "F.Cu"


@dataclass(config=PydanticConfig)
class BoardSize:
    width_mm: float
    height_mm: float


@dataclass(config=PydanticConfig, eq=False)
class Pcb(KicadPcbExpr):
    version: Literal["20211014"] = "20211014"
    generator: str = "edea"
    general: General = field(default_factory=General)
    title_block: Optional[TitleBlock] = None
    paper: Paper = field(default_factory=PaperStandard)

    layers: list[Layer] = field(default_factory=list, metadata=m("kicad_always_quotes"))

    @custom_serializer("layers")
    def _layers_to_list(self, layers: list[Layer]) -> list[SExprList]:
        lst: SExprList = ["layers"]
        return [lst + [layer_to_list(layer) for layer in layers]]

    setup: Setup = field(default_factory=Setup)
    property: list[Property] = field(default_factory=list)
    net: list[Net] = field(default_factory=list)
    footprint: list[Footprint] = field(default_factory=list)
    zone: list[Zone] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)

    # Graphics
    gr_line: list[GraphicalLine] = field(default_factory=list)
    gr_text: list[GraphicalText] = field(default_factory=list)
    gr_text_box: list[GraphicalTextBox] = field(default_factory=list)
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

    def size(self):
        """Calculate the size (width, height) of the board"""
        # pylint: disable=too-many-branches
        min_x = min_y = float("inf")
        max_x = max_y = float("-inf")

        is_missing_board_outline = True

        for gr in itertools.chain(
            self.gr_line,
            self.gr_rect,
            self.gr_arc,
            self.gr_poly,
            self.gr_curve,
            self.gr_circle,
        ):
            if gr.layer == "Edge.Cuts":
                if is_missing_board_outline:
                    # found board outline
                    is_missing_board_outline = False
            else:
                # only calculate size from edge cuts
                continue
            min_x, max_x, min_y, max_y = gr.envelope(min_x, max_x, min_y, max_y)

        if is_missing_board_outline:
            raise MissingBoardOutlineError("Board outline is missing")

        if self._is_infinite_size(min_x, min_y, max_x, max_y):
            raise ValueError("Could not calculate board size")

        return BoardSize(
            width_mm=round(max_x - min_x, 2), height_mm=round(max_y - min_y, 2)
        )

    @staticmethod
    def _is_infinite_size(min_x, min_y, max_x, max_y):
        return any(math.isinf(x) for x in (min_x, min_y, max_x, max_y))

    kicad_expr_tag_name: Literal["kicad_pcb"] = "kicad_pcb"


class MissingBoardOutlineError(ValueError):
    pass
