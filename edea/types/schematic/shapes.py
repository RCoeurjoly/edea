"""
Dataclasses describing the graphic items found in .kicad_sch files.

SPDX-License-Identifier: EUPL-1.2
"""
from dataclasses import field
from enum import Enum
from typing import Optional

from pydantic.dataclasses import dataclass
from pydantic.color import Color

from edea.types.config import PydanticConfig
from edea.types.schematic.base import KicadSchExpr


class FillType(str, Enum):
    NONE = "none"
    OUTLINE = "outline"
    BACKGROUND = "background"


class StrokeType(str, Enum):
    DEFAULT = "default"
    DASH = "dash"
    DASH_DOT = "dash_dot"
    DASH_DOT_DOT = "dash_dot_dot"
    DOT = "dot"
    SOLID = "solid"


@dataclass(config=PydanticConfig)
class Stroke(KicadSchExpr):
    width: float = 0
    type: StrokeType = StrokeType.DEFAULT
    color: Color = Color((0, 0, 0, 0.0))


@dataclass(config=PydanticConfig)
class Fill(KicadSchExpr):
    type: FillType = FillType.NONE


@dataclass(config=PydanticConfig)
class XY(KicadSchExpr):
    x: float
    y: float


@dataclass(config=PydanticConfig)
class Pts(KicadSchExpr):
    xy: list[XY] = field(default_factory=list)


@dataclass(config=PydanticConfig)
class Polyline(KicadSchExpr):
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=Fill)


@dataclass(config=PydanticConfig)
class Rectangle(KicadSchExpr):
    start: tuple[float, float]
    end: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=Fill)


@dataclass(config=PydanticConfig)
class Circle(KicadSchExpr):
    center: tuple[float, float]
    radius: float
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=Fill)


@dataclass(config=PydanticConfig)
class Radius(KicadSchExpr):
    at: tuple[float, float]
    length: float
    angles: tuple[float, float]


@dataclass(config=PydanticConfig)
class Arc(KicadSchExpr):
    start: tuple[float, float]
    mid: tuple[float, float]
    end: tuple[float, float]
    radius: Optional[Radius] = None
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=Fill)
