"""
Dataclasses describing the contents of .kicad_pcb files.
"""

import itertools
import math
from copy import deepcopy
from dataclasses import field
from typing import Annotated, Any, ClassVar, Literal, Optional, Protocol, Sequence
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
    """
    General board config.

    :param thickness: The overall board thickness.
    """

    thickness: float = 0


@dataclass(config=PydanticConfig, eq=False)
class StackupLayerThickness(KicadPcbExpr):
    """
    A layer thickness within a stackup in KiCad PCB expressions.

    :param value: The thickness value of the layer.
    :param locked: Whether the layer thickness is locked or not.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("thickness").
    """

    value: Annotated[float, m("kicad_no_kw")]
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["thickness"]] = "thickness"


@dataclass(config=PydanticConfig, eq=False)
class StackupLayer(KicadPcbExpr):
    """
    A layer within a stackup in KiCad PCB expressions.

    `KiCad layer <https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/index.html#_stack_up_layer_settings>`_

    :param name: The name of the layer.
    :param type: The type of the layer.
    :param color: The layer color.
    :param thickness: The thickness of the layer.
    :param material: The material of the layer.
    :param epsilon_r: The dielectric constant of the layer material.
    :param loss_tangent: The loss tangent of the layer material.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("layer").

    .. note::
        The `type` field is an arbitrary string, not a `CanonicalLayer`.

    """

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
    """
    A PCB stackup in KiCad PCB expressions.

    `KiCad stackup <https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/index.html#_stack_up_settings>`_

    :param layers: The individual layers in the stackup.
    :param copper_finish: The copper finish type for the PCB (e.g., ENIG, OSP).
    :param dielectric_constraints: Whether dielectric constraints are applied during design rule check (DRC) or not.
    :param edge_connector: The type of edge connector for the PCB.
    :param castellated_pads: Whether castellated pads are used on the PCB or not.
    :param edge_plating: Whether edge plating is applied to the PCB or not.

    """

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
    """
    Defines the possible output formats for PCB plots generated in KiCad.
    """

    GERBER = "0"
    """
    Industry-standard format for PCB manufacturing.
    """
    POSTSCRIPT = "1"
    """
    Page description language for printing or generating vector graphics.
    """
    SVG = "2"
    """
    Scalable Vector Graphics format for web or vector editing.
    """
    DXF = "3"
    """
    Drawing Exchange Format for interoperability with CAD software.
    """
    HPGL = "4"
    """
    Hewlett-Packard Graphics Language for plotter output.
    """
    PDF = "5"
    """
    Portable Document Format for universal document sharing.
    """


@dataclass(config=PydanticConfig, eq=False)
class PlotSettings(KicadPcbExpr):
    """
    The settings used for generating PCB plots (fabrication outputs) in KiCad.

    :param layerselection: A string representing the bitmask for selecting layers to be plotted.
    :param plot_on_all_layers_selection: A string representing another layer selection bitmask.
    :param disableapertmacros: Whether to disable aperture macros during plotting or not.
    :param usegerberextensions: Whether to use Gerber extensions for advanced features or not.
    :param usegerberattributes: Whether to use Gerber attributes for enhanced data embedding or not.
    :param usegerberadvancedattributes: Whether to use advanced Gerber attributes or not.
    :param creategerberjobfile: Whether to create a Gerber job file or not.
    :param gerberprecision: The precision (number of decimal places) used for Gerber data.
    :param dashed_line_dash_ratio: The dash-to-gap ratio for dashed lines.
    :param dashed_line_gap_ratio: The gap-to-dash ratio for dashed lines.
    :param svgprecision: The precision (number of decimal places) used for SVG output.
    :param excludeedgelayer: Whether to exclude the edge layer from plotting.
    :param plotframeref: Whether to plot frame references.
    :param viasonmask: Whether to plot vias on the mask layer.
    :param mode: The plot mode (1 or 2, interpretation depends on context).
    :param useauxorigin: Whether to use the auxiliary origin for plotting or not.
    :param hpglpennumber: The pen number used for HPGL plots.
    :param hpglpenspeed: The pen speed used for HPGL plots.
    :param hpglpendiameter: The pen diameter used for HPGL plots.
    :param dxfpolygonmode: Whether to use polygon mode for DXF output or not.
    :param dxfimperialunits: Whether to use imperial units for DXF output or not.
    :param dxfusepcbnewfont: Whether to use the KiCad PCB font for DXF output or not.
    :param psnegative: Whether to generate negative output for PostScript plots or not.
    :param psa4output: Whether to generate PS4 output for PostScript plots or not.
    :param plotreference: Whether to plot references (designators) or not.
    :param plotvalue: Whether to plot values (component values) or not.
    :param plotinvisibletext: Whether to plot invisible text or not.
    :param sketchpadsonfab: Whether to include the sketch pad on fabrication output or not.
    :param subtractmaskfromsilk: Whether to subtract the mask from the silkscreen during plotting or not.
    :param outputformat: The desired output format for the plot files.
    :param mirror: Whether to mirror the output or not.
    :param drillshape: The drill shape for drill plots.
    :param scaleselection: The scale selection for plots.
    :param outputdirectory: The output directory for the generated plot files.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("pcbplotparams").

    .. warning::
        The `dashed_line_dash_ratio`, `dashed_line_gap_ratio`, and `psa4output` are undocumented in the KiCad file format documentation.

    """

    layerselection: str = "0x00010fc_ffffffff"
    plot_on_all_layers_selection: str = "0x0000000_00000000"
    disableapertmacros: bool = False
    usegerberextensions: bool = False
    usegerberattributes: bool = True
    usegerberadvancedattributes: bool = True
    creategerberjobfile: bool = True
    gerberprecision: Optional[int] = None
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
    """
    The various settings and properties that govern the overall PCB design

    :param stackup: A `Stackup` instance defining the layer stackup for the PCB.
    :param pad_to_mask_clearance: The clearance between pads and the solder mask (in mm).
    :param solder_mask_min_width: The minimum width of the solder mask (in mm).
    :param pad_to_paste_clearance: The clearance between pads and the solder paste (in mm).
    :param pad_to_paste_clearance_ratio: The ratio used to calculate solder paste clearance from pad size.
    :param allow_soldermask_bridges_in_footprints: Whether to allow soldermask bridges within footprints or not.
    :param aux_axis_origin: The coordinates of the auxiliary axis origin (in mm).
    :param grid_origin: The coordinates of the grid origin (in mm).
    :param pcbplotparams: A `PlotSettings` instance defining the PCB plot parameters for generating fabrication outputs.

    """

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
    """
    A PCB trace segment (connection) in KiCad PCB expressions.

    :param locked: Whether the line is locked, cannot be edited.
    :param start: The starting x-Y coordinates the line (in mm).
    :param end: The ending x-Y coordinates of the line (in mm).
    :param width: the width of the trace line (in mm).
    :param layer: The canonical layer the track segment resides on.
    :param net: The net ordinal number which net in the net section that the segment is part of.
    :param tstamp: The unique identifier (UUID) for the line object.

    """

    locked: Annotated[bool, m("kicad_kw_bool")] = False
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: float = 0.0
    layer: CanonicalLayerName = "F.Cu"
    net: int = 0
    tstamp: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class Via(KicadPcbExpr):
    """
    A via (plated hole) in KiCad PCB expressions.

    :param type: The type of via (through-hole, blind, or microvia).
    :param locked: Whether the via is locked, cannot be edited.
    :param at: The coordinates of the center of the via (in mm).
    :param size: The diameter of the via annular ring (in mm).
    :param drill: The drill diameter of the via (in mm).
    :param layers: The canonical layer set the via connects.
    :param remove_unused_layers: Whether to remove unused layers from the via or not.
    :param keep_end_layers: Whether to keep only the end layers connected to the via or not
    :param free: Whether the via is free to be moved outside it's assigned net.
    :param zone_layer_connections: A list of zone layers the via connects to.
    :param net: The net ordinal number which net in the net section that the segment is part of.
    :param tstamp: The unique identifier (UUID) for the line object.

    """

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
    """
    An arc (curved trace segment) in KiCad PCB expressions.

    :param locked: Whether the line is locked, cannot be edited.
    :param start: The starting X-Y coordinates of the arc (in mm).
    :param mid: The midpoint X-Y coordinates of the radius of the arc (in mm).
    :param end: The ending X-Y coordinates of the arc (in mm).
    :param width: The line width (in mm).
    :param layer: The canonical layer the track arc resides on.
    :param net: The net ordinal number which net in the net section that the segment is part of.
    :param tstamp: The unique identifier (UUID) of the line object.

    """

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
    """
    A target (component placement reference) in KiCad PCB expressions.

    :param type: The type of target.
    :param at: The X-Y coordinates of the target placement (in mm).
    :param size: The size of the target (in mm).
    :param width: The width of the target.
    :param layer: The layer on which the target is placed.
    :param tstamp: A unique identifier (UUID) for the target.

    """

    type: Annotated[str, m("kicad_no_kw")]
    at: Position
    size: float
    width: float
    layer: CanonicalLayerName
    tstamp: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig)
class BoardSize:
    """
    The overall PCB size in KiCad PCB expressions.

    :param width_mm: The width of the PCB board (in mm).
    :param height_mm: The height of the PCB board (in mm).
    """

    width_mm: float
    height_mm: float


@dataclass(config=PydanticConfig, eq=False)
class Pcb(KicadPcbExpr):
    """
    A KiCad PCB file.

    :param version: The version of the PCB file format.
    :param generator: The software generator of the PCB file.
    :param general: The general settings of the PCB layout.
    :param paper: The paper settings for printing the PCB layout.
    :param title_block: The title block information for the PCB layout.
    :param layers: A list of layers used in the PCB layout.
    :param setup: The setup settings for the PCB layout.
    :param properties: A list of properties associated with the PCB layout.
    :param nets: A list of nets (connections) in the PCB layout.
    :param footprints: A list of footprints used in the PCB layout.
    :param zones: A list of copper zones in the PCB layout.
    :param images: A list of images included in the PCB layout.
    :param gr_lines: A list of graphical lines in the PCB layout.
    :param gr_text_items: A list of graphical text items in the PCB layout.
    :param gr_text_boxes: A list of graphical text boxes in the PCB layout.
    :param gr_rects: A list of graphical rectangles in the PCB layout.
    :param gr_circles: A list of graphical circles in the PCB layout.
    :param gr_arcs: A list of graphical arcs in the PCB layout.
    :param gr_curves: A list of graphical curves in the PCB layout.
    :param gr_polys: A list of graphical polygons in the PCB layout.
    :param beziers: A list of Bezier curves in the PCB layout.
    :param gr_bboxes: A list of graphical bounding boxes in the PCB layout.
    :param dimensions: A list of graphical dimensions in the PCB layout.
    :param segments: A list of track segments in the PCB layout.
    :param vias: A list of vias (connections between layers) in the PCB layout.
    :param arcs: A list of arcs in the PCB layout.
    :param groups: A list of groups in the PCB layout.
    :param targets: A list of targets in the PCB layout.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("kicad_pcb").

    """

    version: Literal["20221018"] = "20221018"

    @validator("version")
    @classmethod
    def check_version(cls, v: Any) -> Literal["20221018"]:
        """
        Validator for the 'version' field, ensures that only the stable KiCad 7 PCB file format.

        :param v: The version value to validate.
        :returns: The validated version value.
        :raises VersionError: If an unsupported version is provided.
        """
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
        """
        Inserts another PCB layout into this one.

        :param name: The name of the layout being inserted.
        :param layout: The layout object to be inserted.
        :param uuid_prefix: UUID prefix.
        """
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
        """
        Calculates the size (width, height) of the board.

        :returns: The calculated board size.

        :raises MissingBoardOutlineError: If the board outline is missing.
        :raises ValueError: If the board size cannot be calculated.
        """
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
    """
    This exception is raised when the PCB layout is missing the board outline information.

    This error indicates a critical issue with the PCB data as the board outline defines the physical dimensions of the PCB.
    """
