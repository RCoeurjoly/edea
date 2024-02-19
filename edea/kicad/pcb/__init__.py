"""
Dataclasses describing the contents of .kicad_pcb files.

SPDX-License-Identifier: EUPL-1.2
"""
import itertools
import math
from copy import deepcopy
from dataclasses import field
from typing import Annotated, ClassVar, Literal, Optional, Protocol, Sequence
from uuid import UUID, uuid4

from pydantic import validator
from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.base import custom_parser, custom_serializer
from edea.kicad.common import Paper, PaperStandard, TitleBlock, VersionError
from edea.kicad.s_expr import SExprList

from .base import KicadPcbExpr
from .common import Group, Image, Net, Position, Property, Zone
from .footprint import Footprint
from .graphics import (
    GraphicalArcTopLevel,
    GraphicalBezier,
    GraphicalBoundingBox,
    GraphicalCircleTopLevel,
    GraphicalCurve,
    GraphicalDimension,
    GraphicalLineTopLevel,
    GraphicalPolygonTopLevel,
    GraphicalRectangleTopLevel,
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
    kicad_expr_tag_name: ClassVar[Literal["thickness"]] = "thickness"


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
    kicad_expr_tag_name: ClassVar[Literal["layer"]] = "layer"


@dataclass(config=PydanticConfig, eq=False)
class Stackup(KicadPcbExpr):
    layers: list[StackupLayer] = field(default_factory=list)
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

    kicad_expr_tag_name: ClassVar[Literal["pcbplotparams"]] = "pcbplotparams"


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
    at: Position
    size: float
    width: float
    layer: CanonicalLayerName
    tstamp: UUID = field(default_factory=uuid4)


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
    properties: list[Property] = field(default_factory=list)
    nets: list[Net] = field(default_factory=list)
    footprints: list[Footprint] = field(default_factory=list)
    zones: list[Zone] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)

    # Graphics
    gr_lines: list[GraphicalLineTopLevel] = field(default_factory=list)
    gr_text_items: list[GraphicalText] = field(default_factory=list)
    gr_text_boxes: list[GraphicalTextBox] = field(default_factory=list)
    gr_rects: list[GraphicalRectangleTopLevel] = field(default_factory=list)
    gr_circles: list[GraphicalCircleTopLevel] = field(default_factory=list)
    gr_arcs: list[GraphicalArcTopLevel] = field(default_factory=list)
    gr_curves: list[GraphicalCurve] = field(default_factory=list)
    gr_polys: list[GraphicalPolygonTopLevel] = field(default_factory=list)
    beziers: list[GraphicalBezier] = field(default_factory=list)
    gr_bboxes: list[GraphicalBoundingBox] = field(default_factory=list)
    dimensions: list[GraphicalDimension] = field(default_factory=list)
    # end Graphics

    # Tracks
    segments: list[Segment] = field(default_factory=list)
    vias: list[Via] = field(default_factory=list)
    arcs: list[Arc] = field(default_factory=list)
    # end Tracks
    groups: list[Group] = field(default_factory=list)

    # UNDOCUMENTED: `target`
    targets: list[Target] = field(default_factory=list)

    def insert_layout(
        self, name: str, layout: "Pcb", uuid_prefix: Optional[UUID] = None
    ) -> None:
        """Insert another PCB layout into this one"""
        group: Group = Group(name=name)

        self.arcs += _copy_and_group(group, layout.arcs)
        self.beziers += _copy_and_group(group, layout.beziers)
        self.dimensions += _copy_and_group(group, layout.dimensions)
        self.gr_arcs += _copy_and_group(group, layout.gr_arcs)
        self.gr_circles += _copy_and_group(group, layout.gr_circles)
        self.gr_curves += _copy_and_group(group, layout.gr_curves)
        self.gr_lines += _copy_and_group(group, layout.gr_lines)
        self.gr_polys += _copy_and_group(group, layout.gr_polys)
        self.gr_rects += _copy_and_group(group, layout.gr_rects)
        self.gr_text_boxes += _copy_and_group(group, layout.gr_text_boxes)
        self.gr_text_items += _copy_and_group(group, layout.gr_text_items)
        self.targets += _copy_and_group(group, layout.targets)

        self.gr_bboxes += deepcopy(layout.gr_bboxes)
        self.images += deepcopy(layout.images)

        new_nets: list[Net] = []
        net_lookup: dict[int, Net] = {}
        net_start_n = 0
        for net in self.nets:
            net_start_n = max(net_start_n, net.number)

        for net in layout.nets:
            new_name = net.name
            if net.name.startswith("/"):
                new_name = f"/{name}{net.name}"
            new_net = Net(number=net_start_n + net.number + 1, name=new_name)
            net_lookup[net.number] = new_net
            new_nets.append(new_net)
        self.nets += new_nets
        new_footprints: list[Footprint] = _copy_and_group(group, layout.footprints)
        for fp in new_footprints:
            for pad in fp.pads:
                if pad.net is not None:
                    pad.net = deepcopy(net_lookup[pad.net.number])
            if uuid_prefix is not None and fp.path is not None:
                fp.path = f"/{uuid_prefix}/{fp.path}"
        self.footprints += new_footprints

        new_segments = _copy_and_group(group, layout.segments)
        _reassign_nets(net_lookup, new_segments)
        self.segments += new_segments

        new_vias = _copy_and_group(group, layout.vias)
        _reassign_nets(net_lookup, new_vias)
        self.vias += new_vias

        new_zones = _copy_and_group(group, layout.zones)
        _reassign_nets(net_lookup, new_zones)
        self.zones += new_zones

        self.groups += deepcopy(layout.groups) + [group]

    def size(self):
        """Calculate the size (width, height) of the board"""
        # pylint: disable=too-many-branches
        min_x = min_y = float("inf")
        max_x = max_y = float("-inf")

        is_missing_board_outline = True

        for gr in itertools.chain(
            self.gr_lines,
            self.gr_rects,
            self.gr_arcs,
            self.gr_polys,
            self.gr_curves,
            self.gr_circles,
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

    kicad_expr_tag_name: ClassVar[Literal["kicad_pcb"]] = "kicad_pcb"


class _HasTstamp(Protocol):
    tstamp: UUID


class _HasNetInt(Protocol):
    net: int


def _reassign_nets(net_lookup: dict[int, Net], xs: Sequence[_HasNetInt]) -> None:
    for x in xs:
        x.net = net_lookup[x.net].number


def _copy_and_group(group: Group, xs: Sequence[_HasTstamp]) -> list:
    for x in xs:
        group.members.append(x.tstamp)
    return list(deepcopy(xs))


class MissingBoardOutlineError(ValueError):
    pass
