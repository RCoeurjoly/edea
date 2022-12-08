"""
Methods to draw `edea.types.schematic` types as SVG.

SPDX-License-Identifier: EUPL-1.2
"""
from math import isclose
from typing import Optional, Union

import svg
from pydantic.color import Color

from edea.draw.schematic.shapes import kicad_stroke_to_style
from edea.draw.schematic.symbol import draw_lib_symbol, draw_property, kicad_font_to_css
from edea.types.schematic import (Bus, BusEntry, GlobalLabel, HierarchicalLabel, Junction, LibSymbol, LocalLabel,
                                  NoConnect, Schematic, SymbolUse, Wire, )


def draw_schematic(expr: Schematic, at=(0, 0)) -> svg.G:
    lib_symbols = {}
    for sym in expr.lib_symbols.symbol:
        lib_symbols[sym.name] = sym

    symbols = []
    for use in expr.symbol:
        sym = lib_symbols[use.lib_id]
        symbols.append(draw_symbol_use(use, sym, at))

    wires = []
    for wire in expr.wire:
        wires.append(draw_wire(wire, at))

    buses = []
    bus_points = []
    for bus in expr.bus:
        for xy in bus.pts.xy:
            bus_points.append((xy.x, xy.y))
        buses.append(draw_bus(bus, at))

    junctions = []
    for j in expr.junction:
        # kicad draws bus and wire junctions differently but doesn't mark the
        # bus junctions in schematic files, we have to see if our junction is on a bus
        is_bus_junction = False
        for bp in bus_points:
            if isclose(bp[0], j.at[0]) and isclose(bp[1], j.at[1]):
                is_bus_junction = True
                break
        junctions.append(draw_junction(j, at, is_bus_junction=is_bus_junction))

    local_labels = []
    for l in expr.label:
        local_labels.append(draw_local_label(l, at))

    global_labels = []
    for l in expr.global_label:
        global_labels.append(draw_global_label(l, at))

    hierarchical_labels = []
    for l in expr.hierarchical_label:
        hierarchical_labels.append(draw_hierarchical_label(l, at))

    bus_entries = [draw_bus_entry(x, at) for x in expr.bus_entry]

    no_connects = [draw_no_connect(x, at) for x in expr.no_connect]

    elements = (
            symbols + buses + bus_entries + wires + junctions + local_labels + global_labels + hierarchical_labels + no_connects)

    return svg.G(class_=["schematic"], elements=elements)


def draw_symbol_use(use: SymbolUse, sym: LibSymbol, at: tuple[float, float] = (0, 0)) -> svg.G:
    absolute_at = (at[0] + use.at[0], at[1] + use.at[1])
    rotation = use.at[2]
    drawn_sym = draw_lib_symbol(sym, at=absolute_at, rotation=rotation, mirror=use.mirror, draw_props=False)

    props: list[svg.Element] = [draw_property(x, at=at, rotation=rotation, flip_y_axis=False, mirror=use.mirror) for x
                                in use.property]
    elements: list[svg.Element] = [drawn_sym] + props
    return svg.G(class_=["symbol-use"], elements=elements)


def draw_wire(expr: Wire, at=(0, 0)) -> svg.Polyline:
    style = kicad_stroke_to_style(expr.stroke)
    points = [(at[0] + xy.x, at[1] + xy.y) for xy in expr.pts.xy]
    return svg.Polyline(class_=["wire"], style=style, points=[num for pt in points for num in pt], )


def draw_bus(expr: Bus, at=(0, 0)) -> svg.Polyline:
    style = kicad_stroke_to_style(expr.stroke)
    points = [(at[0] + xy.x, at[1] + xy.y) for xy in expr.pts.xy]
    return svg.Polyline(class_=["bus"], style=style, points=[num for pt in points for num in pt], )


def draw_bus_entry(expr: BusEntry, at=(0, 0)) -> svg.Polyline:
    style = kicad_stroke_to_style(expr.stroke)
    x1 = at[0] + expr.at[0]
    y1 = at[1] + expr.at[1]
    x2 = x1 + expr.size[0]
    y2 = y1 + expr.size[1]
    points = [x1, y1, x2, y2]
    return svg.Polyline(class_=["wire", "bus-entry"], style=style, points=points, )


def draw_junction(expr: Junction, at=(0, 0), is_bus_junction=False) -> svg.Circle:
    r = 0.5
    if expr.diameter != 0:
        r = expr.diameter / 2

    style = None
    if expr.color != Color((0, 0, 0, 0)):
        style = f"fill:{expr.color.as_rgb()};"

    class_ = ["junction"]
    if is_bus_junction:
        class_.append("junction-bus")

    return svg.Circle(class_=class_, style=style, cx=at[0] + expr.at[0], cy=at[1] + expr.at[1], r=r, )


def draw_label_text(expr: Union[LocalLabel, GlobalLabel, HierarchicalLabel], at=(0, 0), class_=None) -> svg.Text:
    offset = 0.4
    style = kicad_font_to_css(expr.effects.font)
    x = at[0] + expr.at[0]
    y = at[1] + expr.at[1] - offset
    rotation = expr.at[2]
    transform: Optional[list[svg.Transform]] = None
    if rotation in [90, 270]:
        transform = [svg.Rotate(-90, x, y)]
    if rotation in [180, 270]:
        style += "text-anchor:end;"
    if rotation in [0, 90]:
        x += offset
    elif rotation in [180, 270]:
        x -= offset

    return svg.Text(class_=class_, transform=transform, style=style, text=expr.text, x=x, y=y, )


def draw_local_label(expr: LocalLabel, at=(0, 0)) -> svg.Text:
    return draw_label_text(expr, at, class_=["label-local"])


def draw_global_label(expr: GlobalLabel, at=(0, 0)) -> svg.Text:
    return draw_label_text(expr, at, class_=["label-global"])


def draw_hierarchical_label(expr: HierarchicalLabel, at=(0, 0)) -> svg.Text:
    return draw_label_text(expr, at, class_=["label-hierarchical"])


def draw_no_connect(expr: NoConnect, at=(0, 0)) -> svg.Path:
    # half the length of the lines that form the no-connect cross
    half_l = 0.635
    mid = (at[0] + expr.at[0], at[1] + expr.at[1])
    line_a = [(mid[0] - half_l, mid[1] - half_l), (mid[0] + half_l, mid[1] + half_l), ]
    line_b = [(mid[0] + half_l, mid[1] - half_l), (mid[0] - half_l, mid[1] + half_l), ]
    return svg.Path(class_=["no-connect"],
                    d=[svg.MoveTo(line_a[0][0], line_a[0][1]), svg.LineTo(line_a[1][0], line_a[1][1]),
                       svg.MoveTo(line_b[0][0], line_b[0][1]), svg.LineTo(line_b[1][0], line_b[1][1]), ], )
