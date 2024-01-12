import math
from dataclasses import field
from typing import Annotated, ClassVar, Literal, Optional
from uuid import UUID, uuid4

import numpy as np
from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.common import Effects, Pts, Stroke

from .base import KicadPcbExpr
from .common import BaseTextBox, CanonicalLayerName, Position, RenderCache


@dataclass(config=PydanticConfig, eq=False)
class LayerKnockout(KicadPcbExpr):
    name: Annotated[
        CanonicalLayerName, m("kicad_always_quotes", "kicad_no_kw")
    ] = "F.Cu"
    knockout: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["layer"]] = "layer"


@dataclass(config=PydanticConfig, eq=False)
class GraphicalText(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    at: Position = field(default_factory=Position)
    layer: Optional[LayerKnockout] = None
    tstamp: UUID = field(default_factory=uuid4)
    effects: Effects = field(default_factory=Effects)
    render_cache: Optional[RenderCache] = None
    kicad_expr_tag_name: ClassVar[Literal["gr_text"]] = "gr_text"


@dataclass(config=PydanticConfig, eq=False)
class GraphicalTextBox(BaseTextBox):
    kicad_expr_tag_name: ClassVar[Literal["gr_text_box"]] = "gr_text_box"


@dataclass(config=PydanticConfig, eq=False)
class GraphicalLine(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: Optional[float] = None
    stroke: Optional[Stroke] = None
    layer: Optional[CanonicalLayerName] = None
    angle: Optional[float] = None
    kicad_expr_tag_name: ClassVar[Literal["gr_line"]] = "gr_line"

    def envelope(
        self, min_x: float, max_x: float, min_y: float, max_y: float
    ) -> tuple[float, float, float, float]:
        """Envelope the line in a bounding box."""
        for pt in self.start, self.end:
            min_x = min(min_x, pt[0])
            max_x = max(max_x, pt[0])
            min_y = min(min_y, pt[1])
            max_y = max(max_y, pt[1])
        return min_x, max_x, min_y, max_y


@dataclass(config=PydanticConfig, eq=False)
class GraphicalLineTopLevel(GraphicalLine):
    tstamp: UUID = field(default_factory=uuid4)


@dataclass(config=PydanticConfig, eq=False)
class GraphicalRectangle(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: Optional[float] = None
    stroke: Optional[Stroke] = None
    fill: Optional[Literal["solid", "yes", "none"]] = None
    layer: Optional[CanonicalLayerName] = None
    kicad_expr_tag_name: ClassVar[Literal["gr_rect"]] = "gr_rect"

    def envelope(
        self, min_x: float, max_x: float, min_y: float, max_y: float
    ) -> tuple[float, float, float, float]:
        """Envelope the rectangle in a bounding box."""
        for pt in self.start, self.end:
            min_x = min(min_x, pt[0])
            max_x = max(max_x, pt[0])
            min_y = min(min_y, pt[1])
            max_y = max(max_y, pt[1])
        return min_x, max_x, min_y, max_y


@dataclass(config=PydanticConfig, eq=False)
class GraphicalRectangleTopLevel(GraphicalRectangle):
    tstamp: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["gr_rect"]] = "gr_rect"


@dataclass(config=PydanticConfig, eq=False)
class GraphicalCircle(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    center: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    stroke: Optional[Stroke] = None
    width: Optional[float] = None
    fill: Optional[Literal["solid", "yes", "none"]] = None
    layer: Optional[CanonicalLayerName] = None
    kicad_expr_tag_name: ClassVar[Literal["gr_circle"]] = "gr_circle"

    def envelope(
        self, min_x: float, max_x: float, min_y: float, max_y: float
    ) -> tuple[float, float, float, float]:
        """Envelope the circle in a bounding box."""
        radius = math.dist(self.end, self.center)
        min_x = min(min_x, self.center[0] - radius)
        max_x = max(max_x, self.center[0] + radius)
        min_y = min(min_y, self.center[1] - radius)
        max_y = max(max_y, self.center[1] + radius)
        return min_x, max_x, min_y, max_y


@dataclass(config=PydanticConfig, eq=False)
class GraphicalCircleTopLevel(GraphicalCircle):
    tstamp: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["gr_circle"]] = "gr_circle"


@dataclass(config=PydanticConfig, eq=False)
class GraphicalArc(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    start: tuple[float, float] = (0, 0)
    mid: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    width: Optional[float] = None
    stroke: Optional[Stroke] = None
    layer: Optional[CanonicalLayerName] = None
    kicad_expr_tag_name: ClassVar[Literal["gr_arc"]] = "gr_arc"

    def center(self) -> tuple[float, float]:
        """Algebraic solution to find the center of an arc
        given three points on its circumference."""
        x1, y1 = self.start
        x2, y2 = self.mid
        x3, y3 = self.end

        A_1_2 = np.linalg.det(
            np.array(
                [
                    [x1**2 + y1**2, y1, 1],
                    [x2**2 + y2**2, y2, 1],
                    [x3**2 + y3**2, y3, 1],
                ]
            )
        )
        A_1_1 = np.linalg.det(np.array([[x1, y1, 1], [x2, y2, 1], [x3, y3, 1]]))
        A_1_3 = np.linalg.det(
            np.array(
                [
                    [x1**2 + y1**2, x1, 1],
                    [x2**2 + y2**2, x2, 1],
                    [x3**2 + y3**2, x3, 1],
                ]
            )
        )
        return (A_1_2 / (2 * A_1_1), -A_1_3 / (2 * A_1_1))

    def angles_rad(self):
        """Returns a set of angles (in radians) that the arc spans."""
        center = self.center()
        start_angle = round(
            math.degrees(
                math.atan2(self.start[1] - center[1], self.start[0] - center[0])
            )
        )
        mid_angle = round(
            math.degrees(math.atan2(self.mid[1] - center[1], self.mid[0] - center[0]))
        )
        end_angle = round(
            math.degrees(math.atan2(self.end[1] - center[1], self.end[0] - center[0]))
        )

        is_counterclockwise = start_angle <= mid_angle <= end_angle
        # Calculate the angle range based on direction
        if is_counterclockwise:
            angle_range = range(start_angle, end_angle + 1)
        else:
            end_angle %= 360
            if end_angle < start_angle:
                angle_range = range(end_angle, start_angle - 360 - 1, -1)
            else:
                angle_range = range(start_angle, end_angle + 1)

        return set(math.radians(angle % 360) for angle in angle_range)

    def envelope(
        self, min_x: float, max_x: float, min_y: float, max_y: float
    ) -> tuple[float, float, float, float]:
        """Envelope the arc in a bounding box."""
        center = self.center()
        radius = math.dist(center, self.start)
        for angle in self.angles_rad():
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
        return min_x, max_x, min_y, max_y


@dataclass(config=PydanticConfig, eq=False)
class GraphicalArcTopLevel(GraphicalArc):
    tstamp: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["gr_arc"]] = "gr_arc"


@dataclass(config=PydanticConfig, eq=False)
class GraphicalPolygon(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    pts: Pts = field(default_factory=Pts)
    stroke: Optional[Stroke] = None
    width: Optional[float] = None
    fill: Optional[Literal["solid", "yes", "none"]] = None
    layer: Optional[CanonicalLayerName] = None
    kicad_expr_tag_name: ClassVar[Literal["gr_poly"]] = "gr_poly"

    def envelope(
        self, min_x: float, max_x: float, min_y: float, max_y: float
    ) -> tuple[float, float, float, float]:
        """Envelope the polygon in a bounding box."""
        for pt in self.pts.xys:
            min_x = min(min_x, pt.x)
            max_x = max(max_x, pt.x)
            min_y = min(min_y, pt.y)
            max_y = max(max_y, pt.y)
        return min_x, max_x, min_y, max_y


@dataclass(config=PydanticConfig, eq=False)
class GraphicalPolygonTopLevel(GraphicalPolygon):
    tstamp: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["gr_poly"]] = "gr_poly"


@dataclass(config=PydanticConfig, eq=False)
class GraphicalBezier(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    layer: Optional[CanonicalLayerName] = None
    tstamp: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["bezier"]] = "bezier"

    def envelope(
        self, min_x: float, max_x: float, min_y: float, max_y: float
    ) -> tuple[float, float, float, float]:
        """Envelope the curve in a bounding box."""
        for pt in self.pts.xys:
            min_x = min(min_x, pt.x)
            max_x = max(max_x, pt.x)
            min_y = min(min_y, pt.y)
            max_y = max(max_y, pt.y)
        return min_x, max_x, min_y, max_y


@dataclass(config=PydanticConfig, eq=False)
class GraphicalCurve(GraphicalBezier):
    """
    This isn't documented in the Kicad docs, but it is in some files.
    This is what bezier was called before KiCad 7.
    """

    kicad_expr_tag_name: ClassVar[Literal["gr_curve"]] = "gr_curve"


@dataclass(config=PydanticConfig, eq=False)
class GraphicalBoundingBox(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)
    kicad_expr_tag_name: ClassVar[Literal["gr_bbox"]] = "gr_bbox"


class DimensionFormatUnits(StrEnum):
    Inches = "0"
    Mils = "1"
    Millimeters = "2"
    Automatic = "3"


class DimensionFormatUnitsFormat(StrEnum):
    NoSuffix = "0"
    BareSuffix = "1"
    WrapSuffix = "2"


@dataclass(config=PydanticConfig, eq=False)
class DimensionFormat(KicadPcbExpr):
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    units: DimensionFormatUnits = DimensionFormatUnits.Millimeters
    units_format: DimensionFormatUnitsFormat = DimensionFormatUnitsFormat.WrapSuffix
    precision: int = 4
    override_value: Optional[str] = None
    suppress_zeroes: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["format"]] = "format"


class DimensionStyleTextPositionMode(StrEnum):
    Outside = "0"
    InLine = "1"
    Manual = "2"


class DimensionStyleTextFrame(StrEnum):
    NoFrame = "0"
    Rectangle = "1"
    Circle = "2"
    RoundedRectangle = "3"


@dataclass(config=PydanticConfig, eq=False)
class DimensionStyle(KicadPcbExpr):
    thickness: float = 0.0
    arrow_length: float = 0.0
    text_position_mode: DimensionStyleTextPositionMode = (
        DimensionStyleTextPositionMode.Outside
    )
    extension_height: Optional[float] = None
    extension_offset: Optional[float] = None
    text_frame: Optional[DimensionStyleTextFrame] = None
    keep_text_aligned: Annotated[bool, m("kicad_kw_bool")] = False
    kicad_expr_tag_name: ClassVar[Literal["style"]] = "style"


@dataclass(config=PydanticConfig, eq=False)
class GraphicalDimension(KicadPcbExpr):
    locked: Annotated[bool, m("kicad_kw_bool")] = False
    type: Literal["aligned", "leader", "center", "orthogonal", "radial"] = "aligned"
    layer: CanonicalLayerName = "F.Cu"
    tstamp: UUID = field(default_factory=uuid4)
    pts: Pts = field(default_factory=Pts)
    height: Optional[float] = None
    orientation: Optional[float] = None
    leader_length: Optional[float] = None
    gr_text: Optional[GraphicalText] = None
    format: Optional[DimensionFormat] = None
    style: DimensionStyle = field(default_factory=DimensionStyle)
    kicad_expr_tag_name: ClassVar[Literal["dimension"]] = "dimension"
