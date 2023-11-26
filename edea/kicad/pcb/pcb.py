"""
Dataclasses describing the contents of .kicad_pcb files.

SPDX-License-Identifier: EUPL-1.2
"""
from dataclasses import field
import itertools
import math
from typing import Annotated, Literal, Optional
from uuid import UUID, uuid4

from pydantic import validator
from pydantic.dataclasses import dataclass

from edea.kicad._fields import make_meta as m
from edea.kicad.base import custom_parser, custom_serializer
from edea.kicad.common import Paper, PaperStandard, TitleBlock, VersionError
from edea.kicad.config import PydanticConfig
from edea.kicad.s_expr import SExprList
from edea.kicad.str_enum import StrEnum

from .base import KicadPcbExpr
from .common import Group, Image, Net, PositionIdentifier, Property, Zone
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
    value: Annotated[float, m("kicad_no_kw")]
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: Literal["thickness"] = "thickness"


@dataclass(config=PydanticConfig, eq=False)
class StackupLayer(KicadPcbExpr):
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    # This is an arbitrary string, not a `CanonicalLayer`.
    type: str
    color: Annotated[Optional[str], m("kicad_always_quotes")] = None
    thickness: Optional[StackupLayerThickness] = None
    material: Annotated[Optional[str], m("kicad_always_quotes")] = None
    epsilon_r: Optional[float] = None
    loss_tangent: Optional[float] = None
    kicad_expr_tag_name: Literal["layer"] = "layer"


@dataclass(config=PydanticConfig, eq=False)
class Stackup(KicadPcbExpr):
    layer: list[StackupLayer] = field(default_factory=list)
    copper_finish: Optional[str] = None
    dielectric_constraints: Annotated[
        bool, m("kicad_bool_yes_no", "kicad_omits_default")
    ] = False
    edge_connector: Annotated[
        Literal["yes", "bevelled", None], m("kicad_omits_default")
    ] = None
    castellated_pads: Annotated[
        bool, m("kicad_bool_yes_no", "kicad_omits_default")
    ] = False
    edge_plating: Annotated[bool, m("kicad_bool_yes_no", "kicad_omits_default")] = False


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
    plot_on_all_layers_selection: str = "0x0000000_00000000"
    disableapertmacros: bool = False
    usegerberextensions: bool = False
    usegerberattributes: bool = True
    usegerberadvancedattributes: bool = True
    creategerberjobfile: bool = True
    gerberprecision: Optional[int] = None
    # UNDOCUMENTED: `dashed_line_dash_ratio`, `dashed_line_gap_ratio`
    dashed_line_dash_ratio: Optional[float] = None
    dashed_line_gap_ratio: Optional[float] = None
    svgprecision: int = 4
    excludeedgelayer: Annotated[bool, m("kicad_omits_default")] = False
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
    mirror: bool = False
    drillshape: int = 0
    scaleselection: int = 0
    outputdirectory: Annotated[str, m("kicad_always_quotes")] = ""

    kicad_expr_tag_name: Literal["pcbplotparams"] = "pcbplotparams"


@dataclass(config=PydanticConfig, eq=False)
class Setup(KicadPcbExpr):
    stackup: Optional[Stackup] = None
    pad_to_mask_clearance: float = 0.0
    solder_mask_min_width: Annotated[float, m("kicad_omits_default")] = 0.0
    pad_to_paste_clearance: Annotated[float, m("kicad_omits_default")] = 0.0
    pad_to_paste_clearance_ratio: Annotated[float, m("kicad_omits_default")] = 100.0
    allow_soldermask_bridges_in_footprints: Annotated[
        bool, m("kicad_bool_yes_no", "kicad_omits_default")
    ] = False
    aux_axis_origin: Annotated[tuple[float, float], m("kicad_omits_default")] = (
        0.0,
        0.0,
    )
    grid_origin: Annotated[tuple[float, float], m("kicad_omits_default")] = (0.0, 0.0)
    pcbplotparams: PlotSettings = field(default_factory=PlotSettings)


@dataclass(config=PydanticConfig, eq=False)
class Segment(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: float = 0.0
    layer: CanonicalLayerName = "F.Cu"
    net: int = 0
    tstamp: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class Via(KicadPcbExpr):
    type: Annotated[
        Literal["blind", "micro", "through"], m("kicad_no_kw", "kicad_omits_default")
    ] = "through"
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    at: tuple[float, float] = (0, 0)
    size: float = 0
    drill: float = 0
    layers: list[str] = field(default_factory=list)
    remove_unused_layers: Annotated[bool, m("kicad_kw_bool_empty")] = False
    keep_end_layers: Annotated[bool, m("kicad_kw_bool_empty")] = False
    free: Annotated[bool, m("kicad_kw_bool_empty")] = False
    zone_layer_connections: Annotated[
        list[CanonicalLayerName], m("kicad_omits_default")
    ] = field(
        default_factory=list,
    )
    net: int = 0
    tstamp: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class Arc(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    start: tuple[float, float] = (0, 0)
    mid: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: float = 0.0
    layer: CanonicalLayerName = "F.Cu"
    net: int = 0
    tstamp: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class Target(KicadPcbExpr):
    type: Annotated[str, m("kicad_no_kw")]
    at: PositionIdentifier
    size: float
    width: float
    layer: CanonicalLayerName
    tstamp: Optional[UUID] = None


@dataclass(config=PydanticConfig)
class BoardSize:
    width_mm: float
    height_mm: float


@dataclass(config=PydanticConfig, eq=False)
class Pcb(KicadPcbExpr):
    version: Literal["20221018"] = "20221018"

    @validator("version")
    @classmethod
    def check_version(cls, v) -> Literal["20221018"]:
        if v == "20221018":
            return v
        raise VersionError(
            "Only the stable KiCad 7 PCB file format, i.e. '20221018' is supported. "
            f"  Got '{v}'. Please open and re-save the file with KiCad 7 if you can."
        )

    generator: str = "edea"
    general: General = field(default_factory=General)
    paper: Paper = field(default_factory=PaperStandard)
    title_block: Optional[TitleBlock] = None

    layers: Annotated[list[Layer], m("kicad_always_quotes")] = field(
        default_factory=list,
    )

    @custom_serializer("layers")
    def _layers_to_list(self, layers: list[Layer]) -> list[SExprList]:
        lst: SExprList = ["layers"]
        return [lst + [layer_to_list(layer) for layer in layers]]

    @classmethod
    @custom_parser("layers")
    def _list_to_layers(cls, exprs: SExprList) -> tuple[list[Layer], SExprList]:
        exp = None
        for e in exprs:
            if isinstance(e, list) and len(e) > 0 and e[0] == "layers":
                exp = e
                break

        if exp is None:
            raise ValueError("Not found")

        exprs.remove(exp)

        rest = exp[1:]
        lst: list[Layer] = []
        for e in rest:
            if not isinstance(e, list):
                raise ValueError(f"Expecting layer got: '{e}'")
            if len(e) < 3 or len(e) > 4:
                raise ValueError(
                    f"Expecting layer expression of length 3 or 4 got: '{e}'"
                )
            lst.append(tuple(e))  # type: ignore
        return lst, exprs

    setup: Setup = field(default_factory=Setup)
    property: list[Property] = field(default_factory=list)
    net: list[Net] = field(default_factory=list)
    footprint: list[Footprint] = field(default_factory=list)
    zone: list[Zone] = field(default_factory=list)
    image: list[Image] = field(default_factory=list)

    # Graphics
    gr_line: list[GraphicalLine] = field(default_factory=list)
    gr_text: list[GraphicalText] = field(default_factory=list)
    gr_text_box: list[GraphicalTextBox] = field(default_factory=list)
    gr_rect: list[GraphicalRectangle] = field(default_factory=list)
    gr_circle: list[GraphicalCircle] = field(default_factory=list)
    gr_arc: list[GraphicalArc] = field(default_factory=list)
    gr_curve: list[GraphicalCurve] = field(default_factory=list)
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
