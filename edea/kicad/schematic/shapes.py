"""
Dataclasses describing the graphic items found in .kicad_sch files.

SPDX-License-Identifier: EUPL-1.2
"""
from dataclasses import field
from typing import ClassVar, Literal, Optional

from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._str_enum import StrEnum
from edea.kicad.common import Pts, Stroke
from edea.kicad.schematic.base import KicadSchExpr


class FillType(StrEnum):
    NONE = "none"
    OUTLINE = "outline"
    BACKGROUND = "background"


@dataclass(config=PydanticConfig, eq=False)
class FillSimple(KicadSchExpr):
    type: FillType = FillType.BACKGROUND
    kicad_expr_tag_name: ClassVar[Literal["fill"]] = "fill"


@dataclass(config=PydanticConfig, eq=False)
class FillColor(KicadSchExpr):
    color: tuple[int, int, int, float] = (0, 0, 0, 0)
    kicad_expr_tag_name: ClassVar[Literal["fill"]] = "fill"


@dataclass(config=PydanticConfig, eq=False)
class FillTypeColor(KicadSchExpr):
    type: Literal["color"] = "color"
    color: tuple[int, int, int, float] = (0, 0, 0, 0)
    kicad_expr_tag_name: ClassVar[Literal["fill"]] = "fill"


Fill = FillSimple | FillColor | FillTypeColor


@dataclass(config=PydanticConfig, eq=False)
class Polyline(KicadSchExpr):
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)


@dataclass(config=PydanticConfig, eq=False)
class Bezier(KicadSchExpr):
    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)


@dataclass(config=PydanticConfig, eq=False)
class Rectangle(KicadSchExpr):
    start: tuple[float, float]
    end: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)


@dataclass(config=PydanticConfig, eq=False)
class Circle(KicadSchExpr):
    center: tuple[float, float]
    radius: float
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)


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
    fill: Fill = field(default_factory=FillSimple)
