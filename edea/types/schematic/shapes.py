"""
Dataclasses describing the graphic items found in .kicad_sch files.

SPDX-License-Identifier: EUPL-1.2
"""
from dataclasses import field
from enum import Enum
from typing import Optional

from edea.types.color import Color
from pydantic.dataclasses import dataclass

from edea.types.common import Pts
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


@dataclass(config=PydanticConfig, eq=False)
class Stroke(KicadSchExpr):
    width: float = 0
    type: StrokeType = StrokeType.DEFAULT
    color: Color = (0, 0, 0, 0.0)


@dataclass(config=PydanticConfig, eq=False)
class Fill(KicadSchExpr):
    type: FillType = FillType.NONE


@dataclass(config=PydanticConfig, eq=False)
class Polyline(KicadSchExpr):
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=Fill)


@dataclass(config=PydanticConfig, eq=False)
class Bezier(KicadSchExpr):
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=Fill)


@dataclass(config=PydanticConfig, eq=False)
class Rectangle(KicadSchExpr):
    start: tuple[float, float]
    end: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=Fill)


@dataclass(config=PydanticConfig, eq=False)
class Circle(KicadSchExpr):
    center: tuple[float, float]
    radius: float
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=Fill)


@dataclass(config=PydanticConfig, eq=False)
class Radius(KicadSchExpr):
    at: tuple[float, float]
    length: float
    angles: tuple[float, float]


@dataclass(config=PydanticConfig, eq=False)
class Arc(KicadSchExpr):
    start: tuple[float, float]
    mid: tuple[float, float]
    end: tuple[float, float]
    radius: Optional[Radius] = None
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=Fill)
