from dataclasses import field
from typing import Annotated, ClassVar, Literal, Optional
from uuid import UUID

from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.common import Effects, Pts, Stroke

from .base import KicadPcbExpr
from .layer import CanonicalLayerName, WildCardLayerName


@dataclass(config=PydanticConfig, eq=False)
class Position(KicadPcbExpr):
    """
    A position element within a KiCad PCB file.

    :param x: The X coordinates of the position.
    :param y: The X coordinates of the position.
    :param angle: The orientation angle of the position.
    :param unlocked: Whether the position orientation can be anything other than the upright orientation or not.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("at").
    """

    x: Annotated[float, m("kicad_no_kw")] = 0
    y: Annotated[float, m("kicad_no_kw")] = 0
    angle: Annotated[float, m("kicad_no_kw", "kicad_omits_default")] = 0
    unlocked: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["at"]] = "at"


@dataclass(config=PydanticConfig, eq=False)
class ConnectionPads(KicadPcbExpr):
    """
    A connection pads.

    :param type: The type of pad connection.
    :param clearance: The minimum clearance distance for connected pads.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("connect_pads").
    """

    type: Annotated[
        Literal["yes", "no", "full", "thru_hole_only", None], m("kicad_no_kw")
    ] = None
    clearance: float = 0
    kicad_expr_tag_name: ClassVar[Literal["connect_pads"]] = "connect_pads"


@dataclass(config=PydanticConfig, eq=False)
class ZoneKeepOutSettings(KicadPcbExpr):
    """
    The zone keepout settings within a KiCad PCB file, defining allowed elements within keepout zones.

    `KiCad zone keepout <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_zone_keep_out_settings>`_

    :param tracks: Whether tracks should be excluded from the keep out area. Valid attributes are allowed and not_allowed.
    :param vias: Whether vias should be excluded from the keep out area. Valid attributes are allowed and not_allowed.
    :param pads: Whether pads should be excluded from the keep out area. Valid attributes are allowed and not_allowed.
    :param copperpour: Whethercopper pours should be excluded from the keep out area. Valid attributes are allowed and not_allowed.
    :param footprints: Whether footprints should be excluded from the keep out area. Valid attributes are allowed and not_allowed.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("keepout") or not.
    """

    tracks: Literal["allowed", "not_allowed"]
    vias: Literal["allowed", "not_allowed"]
    pads: Literal["allowed", "not_allowed"]
    copperpour: Literal["allowed", "not_allowed"]
    footprints: Literal["allowed", "not_allowed"]
    kicad_expr_tag_name: ClassVar[Literal["keepout"]] = "keepout"


class ZoneFillIslandRemovalMode(StrEnum):
    """
    Different Island removal modes for zone fills within a KiCad PCB file.
    """

    Always = "0"
    """
    Remove all islands (copper areas disconnected from the main zone).
    """
    Never = "1"
    """
    Keep all islands.
    """
    MinimumArea = "2"
    """
    Remove islands with area smaller than a specified threshold.
    """


class ZoneFillHatchSmoothingLevel(StrEnum):
    """
    Different smoothing levels for hatched zone fills within a KiCad PCB file.
    """

    No = "0"
    """
    No smoothing applied to the hatch edges.
    """
    Fillet = "1"
    """
    Apply a fillet (rounded corner) smoothing to the hatch edges.
    """
    ArcMinimum = "2"
    """
    Use minimum arc radius for smoothing hatch edges.
    """
    ArcMaximum = "3"
    """
    Use maximum arc radius for smoothing hatch edges.
    """


class ZoneFillHatchBorderAlgorithm(StrEnum):
    """
    Different algorithms for defining the border of hatched zone fills within a KiCad PCB file.
    """

    ZoneMinimumThickness = "zone_min_thickness"
    """
    Use minimum zone thickness to define the border.
    """
    HatchThickness = "hatch_thickness"
    """
    Use hatch thickness to define the border.
    """


@dataclass(config=PydanticConfig, eq=False)
class ZoneFillSettings(KicadPcbExpr):
    """
    The zone fill settings within a KiCad PCB file, defining properties for filling copper zones.

    `KiCad fill settings <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_zone_fill_settings>`_

    :param yes: If the zone should be filled.
    :param mode: How the zone is filled. The only valid fill mode is hatched.
    :param thermal_gap: The distance from the zone to all pad thermal relief connections to the zone.
    :param thermal_bridge_width: The spoke width for all pad thermal relief connection to the zone.
    :param smoothing: The style of corner smoothing and the radius of the smoothing.
    :param radius: The radius.
    :param island_removal_mode: The mode for removing islands within the zone fill.
    :param island_area_min: The minimum allowable zone island.
    :param hatch_thickness: The thickness for hatched fills.
    :param hatch_gap: The distance between lines for hatched fills.
    :param hatch_orientation: The line angle for hatched fills.
    :param hatch_smoothing_level: How hatch outlines are smoothed.
    :param hatch_smoothing_value: The ratio between the hole and the chamfer/fillet size.
    :param hatch_border_algorithm: Whether the zone line thickness is used when performing a hatch fill or not.
    :param hatch_min_hole_area: The minimum area a hatch file hole can be.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("fill").

    .. warning::
        The `radius` field is not documented in the KiCad file format documentation but we have seen it in the wild.
    """

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
    """
    A filled polygon element within a KiCad PCB file, defining a zone fill area on a specific layer.

    `KiCad filled polygon <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_zone_fill_polygons>`_

    :param layer: The canonical layer the zone fill resides on.
    :param island: Whether the polygon defines an island within a zone fill or not.
    :param pts: A list of polygon X-Y coordinates used to fill the zone.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("filled_polygon").
    """

    layer: CanonicalLayerName
    island: Annotated[bool, m("kicad_kw_bool_empty")] = False
    pts: Pts = field(default_factory=Pts)
    kicad_expr_tag_name: ClassVar[Literal["filled_polygon"]] = "filled_polygon"


@dataclass(config=PydanticConfig, eq=False)
class Polygon(KicadPcbExpr):
    """
    A simple polygon element within a KiCad PCB file, defining a closed shape without filling.

    :param pts: List of lists of points defining the polygon's outer and potential inner contours.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("polygon").
    """

    pts: list[Pts] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["polygon"]] = "polygon"


class Hatch(StrEnum):
    """
    Different hatch options for ZoneFillPolygon and Polygon elements within a KiCad PCB file.
    """

    Edge = "edge"
    """
    Hatch along the polygon edges.
    """
    Full = "full"
    """
    Fill the entire polygon area with hatch.
    """
    None_ = "none"
    """
    No hatching applied to the polygon.
    """


@dataclass(config=PydanticConfig, eq=False)
class ZoneAttrTearDrop(KicadPcbExpr):
    """
    A teardrop attribute for zone fills within a KiCad PCB file.

    :param type: This specifies the type of teardrop element
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element, which is always "teardrop".

    """

    type: Literal["padvia", "track_end"] = "padvia"
    kicad_expr_tag_name: ClassVar[Literal["teardrop"]] = "teardrop"


@dataclass(config=PydanticConfig, eq=False)
class ZoneAttr(KicadPcbExpr):
    """
    The zone attributes within a KiCad PCB file, potentially defining teardrop clearance shapes.

    :param teardrop: Teardrop clearance shape definition for the zone.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("attr").
    """

    teardrop: ZoneAttrTearDrop
    kicad_expr_tag_name: ClassVar[Literal["attr"]] = "attr"


@dataclass(config=PydanticConfig, eq=False)
class Zone(KicadPcbExpr):
    """
    A zone object within a KiCad PCB file, defining a designated area on specific copper layers.

    `KiCad zone <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_zone>`_

    .. note::
        Some zones have `layers` instead of `layer`.
        But it's always guaranteed to have all the layers in the `layers` list
        after initialization.

    :param locked: Whether the zone is locked for editing or not.
    :param net: The net ordinal number which net in the nets section that the zone is part of.
    :param net_name: The name of the net if the zone is not a keep out area.
    :param layer: The canonical layer the zone resides on.
    :param layers: It specifies the copper layers for the zone.
    :param tstamp: The unique identifier (UUID) for the zone object.
    :param name: The name for the zone if one has been assigned.
    :param hatch: The zone outline display hatch style and pitch
    :param priority: The zone priority if it is not zero.
    :param attr: The reference to a `ZoneAttr` object defining additional zone attributes.
    :param connect_pads: The pad connection type and clearance.
    :param min_thickness: The minimum fill width allowed in the zone.
    :param filled_areas_thickness: The zone like width is not used when determining the zone fill area.
    :param keepout: The keep out items if the zone defines as a keep out area.
    :param fill: The configuration for zone filling, including mode, island removal, hatch options, etc.
    :param polygons: X-Y coordinates of corner points of the polygon outline.
    :param filled_polygons: List of polygons used to fill the zone.

    .. note::
        The `tstamp` field got renamed to `uuid` in 20240108 (KiCad 8).

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
    tstamp: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
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
    kicad_expr_tag_name: ClassVar[Literal["zone"]] = "zone"


@dataclass(config=PydanticConfig, eq=False)
class Group(KicadPcbExpr):
    """
    A group element within a KiCad PCB file, allowing you to group other elements for organizational purposes.

    `KiCad group <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_group>`_

    :param name: The name of the group.
    :param locked: Whether the group is locked for editing or not.
    :param id: The unique identifier (UUID) for the group element.
    :param members: A list of unique identifiers of the objects belonging to the group.

    .. note::
        The `id` field got renamed to `uuid` in 20240108 (KiCad 8).

    """

    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    id: Optional[UUID] = None
    uuid: Optional[UUID] = None
    members: list[UUID] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["group"]] = "group"


@dataclass(config=PydanticConfig, eq=False)
class RenderCache(KicadPcbExpr):
    """
    A render cache element within a KiCad PCB file, potentially used for optimizing rendering of complex elements.

    :param name: The name of the render cache.
    :param number: A number of the render cache.
    :param polygons: The cached geometry.
    """

    name: Annotated[str, m("kicad_no_kw")]
    number: Annotated[float, m("kicad_no_kw")]
    polygons: list[Polygon] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["render_cache"]] = "render_cache"


@dataclass(config=PydanticConfig, eq=False)
class BaseTextBox(KicadPcbExpr):
    """
    A base textbox element within a KiCad PCB file, providing a foundation for various text objects.

    :param locked: Whether the text box is locked for editing or not.
    :param text: The text content of the box.
    :param start: The starting X-Y coordinates of the text box.
    :param end: The ending X-Y coordinates of the text box.
    :param pts: The reference to a `Pts` object defining the text box outline.
    :param layer: The canonical layer the text box resides on.
    :param effects: Reference to an `Effects` object defining text effects.
    :param render_cache: Reference to a `RenderCache` element for potentially cached rendering.
    :param angle: The rotation angle for the text box.
    :param stroke: Reference to a `stroke` object defining the text outline style.
    :param hide: Whether the text box is hidden or not.
    :param border: Whether the text box has a border or not.
    :param tstamp: The unique identifier (UUID) for the text box element.
    :param uuid: The unique identifier (UUID) for the text box element.

    .. note::
        The `tstamp` field got renamed to `uuid` in 20240108 (KiCad 8).


    """

    locked: Annotated[bool, m("kicad_kw_bool")] = False
    text: Annotated[str, m("kicad_no_kw")] = ""
    start: Optional[tuple[float, float]] = None
    end: Optional[tuple[float, float]] = None
    pts: Optional[Pts] = None
    layer: CanonicalLayerName = "F.Cu"
    effects: Effects = field(default_factory=Effects)
    render_cache: Optional[RenderCache] = None
    angle: Optional[float] = None
    stroke: Optional[Stroke] = None
    hide: Annotated[bool, m("kicad_kw_bool")] = False
    border: Annotated[Optional[bool], m("kicad_bool_yes_no", "kicad_omits_default")] = (
        None
    )
    tstamp: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    uuid: Annotated[Optional[UUID], m("kicad_omits_default")] = None
    kicad_expr_tag_name: ClassVar[
        Literal["base_textbox", "fp_text_box", "gr_text_box"]
    ] = "base_textbox"


@dataclass(config=PydanticConfig, eq=False)
class Net(KicadPcbExpr):
    """
    A net connection for the pad within a KiCad PCB file.

    :param number: The number of the net connection.
    :param name: The name of the net connection.
    """

    number: Annotated[int, m("kicad_no_kw")]
    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    kicad_expr_tag_name: ClassVar[Literal["net"]] = "net"


@dataclass(config=PydanticConfig, eq=False)
class Image(KicadPcbExpr):
    """
    An embedded image within a KiCad PCB file.

    `KiCad image <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_images>`_

    :param at: The X-Y coordinates of the image.
    :param uuid: The unique identifier (UUID) for the image element.
    :param layer: The associated board layer of the image using one canonical layer name.
    :param scale: The scale factor of the image..
    :param data: The image data in the portable network graphics format (PNG) encoded with MIME type base64.
    :param locked: Whether the image is locked for editing or not.

    .. note::
        The fields `uuid` and `locked` were added in 20240108 (KiCad 8).

    """

    at: tuple[float, float]
    uuid: Optional[UUID] = None
    layer: CanonicalLayerName = "F.Cu"
    scale: Optional[float] = None
    data: list[str] = field(default_factory=list)
    locked: Annotated[Optional[bool], m("kicad_bool_yes_no", "kicad_omits_default")] = (
        None
    )
    kicad_expr_tag_name: ClassVar[Literal["image"]] = "image"


@dataclass(config=PydanticConfig, eq=False)
class TearDrops(KicadPcbExpr):
    """
    The teardrops settings within a KiCad PCB file.

    :param best_length_ratio: The best length ratio for the teardrops.
    :param max_length: The maximum length for the teardrops.
    :param best_width_ratio: The best width ratio for the teardrops.
    :param max_width: The maximum width for the teardrops.
    :param curve_points: The number of curve points for the teardrops.
    :param filter_ratio: The filter ratio for the teardrops.
    :param enabled: Whether the teardrops are enabled or not.
    :param allow_two_segments: Whether two segments are allowed for the teardrops or not.
    :param prefer_zone_connections: Whether zone connections are preferred for the teardrops or not.

    """

    best_length_ratio: float
    max_length: float
    best_width_ratio: float
    max_width: float
    curve_points: int
    filter_ratio: float
    enabled: Annotated[bool, m("kicad_bool_yes_no")]
    allow_two_segments: Annotated[bool, m("kicad_bool_yes_no")]
    prefer_zone_connections: Annotated[bool, m("kicad_bool_yes_no")]
    kicad_expr_tag_name: ClassVar[Literal["teardrops"]] = "teardrops"


@dataclass(config=PydanticConfig, eq=False)
class LayerKnockout(KicadPcbExpr):
    """
    Indicates that the text in a layer should be knocked out.

    `kicad graphical text <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_graphical_text>`_

     :param name: The name of the copper layer to be knocked out
     :param knockout: Whether the layer is knocked out or not.
     :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("layer").
    """

    name: Annotated[CanonicalLayerName, m("kicad_always_quotes", "kicad_no_kw")] = (
        "F.Cu"
    )
    knockout: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["layer"]] = "layer"


@dataclass(config=PydanticConfig, eq=False)
class Property(KicadPcbExpr):
    """
    A property element within a KiCad PCB file.

    :param key: The name of the property and must be unique.
    :param value: The value of the property.
    """

    key: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    value: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    at: Optional[Position] = None
    layer: Optional[LayerKnockout] = None
    effects: Optional[Effects] = None
    render_cache: Optional[RenderCache] = None
    uuid: Optional[UUID] = None
    hide: Annotated[Optional[bool], m("kicad_bool_yes_no", "kicad_omits_default")] = (
        None
    )
    unlocked: Annotated[
        Optional[bool], m("kicad_bool_yes_no", "kicad_omits_default")
    ] = None
    kicad_expr_tag_name: ClassVar[Literal["property"]] = "property"
