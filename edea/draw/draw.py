"""
Draw EDeA types as SVG.

SPDX-License-Identifier: EUPL-1.2
"""
from typing import Optional, Union

import svg

from edea.draw.schematic import (
    draw_bus,
    draw_bus_entry,
    draw_global_label,
    draw_hierarchical_label,
    draw_junction,
    draw_lib_symbol,
    draw_local_label,
    draw_no_connect,
    draw_schematic,
    draw_wire,
)
from edea.draw.schematic.shapes import (
    draw_arc,
    draw_circle,
    draw_polyline,
    draw_rectangle,
)
from edea.draw.themes import ThemeName, get_theme
from edea.draw.themes.style import sch_theme_to_style
from edea.types.schematic import (
    Bus,
    BusEntry,
    GlobalLabel,
    HierarchicalLabel,
    Junction,
    LibSymbol,
    LocalLabel,
    NoConnect,
    Schematic,
    Wire,
)
from edea.types.schematic.shapes import Arc, Circle, Polyline, Rectangle

DrawableSchExpr = Union[
    Arc,
    Bus,
    BusEntry,
    Circle,
    GlobalLabel,
    HierarchicalLabel,
    Junction,
    LibSymbol,
    LocalLabel,
    NoConnect,
    Polyline,
    Rectangle,
    Schematic,
    Wire,
]

# will be a Union of SchExpr and PcbExpr?
Drawable = DrawableSchExpr


def draw_svg(
        expr: Drawable, theme: Optional[ThemeName] = ThemeName.KICAD_2022
) -> svg.SVG:
    """
    Draw a `Drawable` `KicadExpr` as a svg.py `svg.SVG` document. You can
    optionally set the theme to one of `ThemeName` which gets included in the
    SVG as a style tag. The default style is `KICAD_2022` which is the default
    style KiCad used in the year 2022. If the theme is set to `None` then no
    style tag is included in the output (useful if you want to apply CSS styling
    externally).
    """
    # TODO: use actual dimensions of thing we are drawing if not a schematic
    width = 210
    height = 297
    elements: list[svg.Element] = []

    if isinstance(expr, DrawableSchExpr):
        if isinstance(expr, Schematic):
            width, height = expr.paper.as_dimensions_mm()

        if theme is not None:
            theme_obj = get_theme(theme)
            style = sch_theme_to_style(theme_obj.schematic)
            elements.append(style)

    elements.append(draw_element(expr))

    return svg.SVG(
        viewBox=svg.ViewBoxSpec(0, 0, width, height),
        width=svg.Length(width, "mm"),
        height=svg.Length(height, "mm"),
        elements=elements,
    )


def draw_element(expr: Drawable, at: tuple[float, float] = (0, 0)) -> svg.Element:
    """
    Draw a `Drawable` `KicadExpr` as a svg.py `svg.Element`.
    """
    match expr:
        case Arc():
            return draw_arc(expr, at)
        case Bus():
            return draw_bus(expr, at)
        case BusEntry():
            return draw_bus_entry(expr, at)
        case Circle():
            return draw_circle(expr, at)
        case GlobalLabel():
            return draw_global_label(expr, at)
        case HierarchicalLabel():
            return draw_hierarchical_label(expr, at)
        case Junction():
            return draw_junction(expr, at)
        case LibSymbol():
            return draw_lib_symbol(expr, at)
        case LocalLabel():
            return draw_local_label(expr, at)
        case NoConnect():
            return draw_no_connect(expr, at)
        case Polyline():
            return draw_polyline(expr, at)
        case Rectangle():
            return draw_rectangle(expr, at)
        case Schematic():
            return draw_schematic(expr, at)
        case Wire():
            return draw_wire(expr, at)
        case _:
            raise TypeError(f"Cannot draw item of type '{type(expr)}'.")
