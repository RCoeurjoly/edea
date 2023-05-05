"""
Dataclasses describing the graphic items found in .kicad_sch files.

SPDX-License-Identifier: EUPL-1.2
"""
from dataclasses import field
from typing import Optional

from pydantic.dataclasses import dataclass

from edea.types.common import Pts, Stroke
from edea.types.config import PydanticConfig
from edea.types.schematic.base import KicadSchExpr
from edea.types.str_enum import StrEnum


class FillType(StrEnum):
    NONE = "none"
    OUTLINE = "outline"
    BACKGROUND = "background"


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
