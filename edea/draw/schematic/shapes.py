"""
Methods to draw `edea.types.schematic.shapes` as SVG.

SPDX-License-Identifier: EUPL-1.2
"""
import math
from typing import Optional

import svg
from pydantic.color import Color

from edea.types.schematic.shapes import (
    Arc,
    Circle,
    FillType,
    Polyline,
    Rectangle,
    Stroke,
)


def kicad_fill_to_class(t: FillType) -> str:
    return "fill-" + t.value


def kicad_stroke_to_style(expr: Stroke) -> Optional[str]:
    # for kicad color is the default if its all 0s
    color = expr.color
    stroke = None if color == Color((0, 0, 0, 0.0)) else color.as_rgb()
    stroke_width = None if expr.width == 0 else expr.width

    # we use css style instead of attributes so they don't get overriden by the
    # document css
    style = ""
    if stroke is not None:
        style += f"stroke:{stroke};"

    if stroke_width is not None:
        style += f"stroke-width:{stroke_width};"

    style = None if style == "" else style

    return style


def draw_rectangle(expr: Rectangle, at=(0, 0), flip_y_axis=True) -> svg.Rect:
    style = kicad_stroke_to_style(expr.stroke)
    class_ = [kicad_fill_to_class(expr.fill.type)]
    # inside a symbol kicad's y-axis is positive as it goes up, SVG's y-axis is
    # positive as it goes down.
    if flip_y_axis:
        start = (expr.start[0], -expr.start[1])
        end = (expr.end[0], -expr.end[1])
    # outside of symbols kicad's y-axis is positve as it goes down, just like SVG
    else:
        start = (expr.start[0], expr.start[1])
        end = (expr.end[0], expr.end[1])
    #  rects in SVG can only have positive width and height
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    width = abs(end[0] - start[0])
    height = abs(end[1] - start[1])

    return svg.Rect(
        style=style,
        class_=class_,
        x=at[0] + x,
        y=at[1] + y,
        width=width,
        height=height,
    )


def draw_polyline(expr: Polyline, at=(0, 0), flip_y_axis=True) -> svg.Polyline:
    style = kicad_stroke_to_style(expr.stroke)
    class_ = [kicad_fill_to_class(expr.fill.type)]
    # inside a symbol kicad's y-axis is positive as it goes up, SVG's y-axis is
    # positive as it goes down
    if flip_y_axis:
        points = [(at[0] + xy.x, at[1] - xy.y) for xy in expr.pts.xy]
    # outside of symbols kicad's y-axis is positve as it goes down, just like SVG
    else:
        points = [(at[0] + xy.x, at[1] + xy.y) for xy in expr.pts.xy]

    return svg.Polyline(
        style=style,
        class_=class_,
        points=[num for pt in points for num in pt],
    )


def draw_circle(expr: Circle, at=(0, 0), flip_y_axis=True) -> svg.Circle:
    style = kicad_stroke_to_style(expr.stroke)
    class_ = [kicad_fill_to_class(expr.fill.type)]
    cx = expr.center[0]
    # inside a symbol kicad's y-axis is positive as it goes up, SVG's y-axis is
    # positive as it goes down.
    if flip_y_axis:
        cy = -expr.center[1]
    else:
        cy = expr.center[1]

    return svg.Circle(
        class_=class_,
        style=style,
        cx=at[0] + cx,
        cy=at[1] + cy,
        r=expr.radius,
    )


def draw_arc(expr: Arc, at=(0, 0), flip_y_axis=True) -> svg.Path:
    style = kicad_stroke_to_style(expr.stroke)
    class_ = ["arc", kicad_fill_to_class(expr.fill.type)]
    # inside a symbol kicad's y-axis is positive as it goes up, SVG's y-axis is
    # positive as it goes down.
    if flip_y_axis:
        start = (at[0] + expr.start[0], at[1] - expr.start[1])
        end = (at[0] + expr.end[0], at[1] - expr.end[1])
    # outside of symbols kicad's y-axis is positve as it goes down, just like SVG
    else:
        start = (at[0] + expr.start[0], at[1] + expr.start[1])
        end = (at[0] + expr.end[0], at[1] + expr.end[1])

    # we want a point that has a magnitude of radius and is equal in both x and
    # y. this is so that we get a circular arc and not an elliptical  "squashed
    # circle" one.
    # that point is (radius / 2, radius / 2)
    half_r = math.dist(expr.start, expr.mid) / 2

    return svg.Path(
        style=style,
        class_=class_,
        d=[
            svg.MoveTo(start[0], start[1]),
            svg.Arc(
                rx=half_r,
                ry=half_r,
                angle=0,
                large_arc=False,
                sweep=False,
                x=end[0],
                y=end[1],
            ),
        ],
    )
