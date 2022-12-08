"""
Methods to draw `edea.types.schematic.symbol` types as SVG.

SPDX-License-Identifier: EUPL-1.2
"""
from enum import Enum
from typing import Literal, Optional, Union

import svg

from edea.draw.schematic.shapes import (
    draw_arc,
    draw_circle,
    draw_polyline,
    draw_rectangle,
)
from edea.types.schematic.symbol import (
    Effects,
    Font,
    JustifyHoriz,
    JustifyVert,
    LibSymbol,
    Pin,
    PinName,
    PinNumber,
    SubSymbol,
    SymbolProperty,
)


def draw_lib_symbol(
        expr: LibSymbol,
        at=(0, 0),
        rotation: Literal[0, 90, 180, 270] = 0,
        mirror: Literal["x", "y", None] = None,
        draw_props=True,
        draw_pin_nums=True,
        draw_pin_names=True,
) -> svg.G:
    draw_pin_nums = draw_pin_nums and not expr.pin_numbers.hide
    draw_pin_names = draw_pin_names and not expr.pin_names.hide
    pin_name_offset = (
        expr.pin_names.offset if expr.pin_names.offset is not None else 0.504
    )

    elements: list[svg.Element] = []
    for sym in [expr] + expr.symbol:
        elements += draw_symbol(
            sym,
            at,
            mirror=mirror,
            rotation=rotation,
            draw_pin_nums=draw_pin_nums,
            draw_pin_names=draw_pin_names,
            pin_name_offset=pin_name_offset,
        )
    if draw_props:
        elements += [
            draw_property(x, at, rotation=rotation, mirror=mirror, flip_y_axis=True)
            for x in expr.property
        ]

    # we don't want the background fill to be drawn over anything else
    elements.sort(
        key=lambda x: (x.class_ is None) or ("fill-background" not in x.class_)  # type: ignore
    )

    transform = []
    transform_origin = None
    if mirror == "x":
        transform.append(svg.Scale(1, -1))
    elif mirror == "y":
        transform.append(svg.Scale(-1, 1))
    if rotation != 0:
        transform.append(svg.Rotate(-rotation))
    if not transform:
        transform = None
    else:
        transform_origin = f"{at[0]} {at[1]}"

    return svg.G(
        class_=["symbol"],
        elements=elements,
        transform=transform,
        transform_origin=transform_origin,
    )


def draw_symbol(
        expr: Union[SubSymbol, LibSymbol],
        at: tuple[float, float] = (0, 0),
        rotation: Literal[0, 90, 180, 270] = 0,
        mirror=None,
        draw_pin_nums=True,
        draw_pin_names=True,
        pin_name_offset=0.504,
) -> list[svg.Element]:
    elements: list[svg.Element] = []
    elements += [draw_rectangle(x, at, flip_y_axis=True) for x in expr.rectangle]
    elements += [draw_polyline(x, at, flip_y_axis=True) for x in expr.polyline]
    elements += [draw_circle(x, at, flip_y_axis=True) for x in expr.circle]
    elements += [draw_arc(x, at, flip_y_axis=True) for x in expr.arc]
    elements += [
        draw_pin(
            x,
            at,
            symbol_rotation=rotation,
            symbol_mirror=mirror,
            draw_pin_nums=draw_pin_nums,
            draw_pin_names=draw_pin_names,
            pin_name_offset=pin_name_offset,
        )
        for x in expr.pin
    ]
    return elements


def kicad_justify_h_to_anchor(
        justify_h: JustifyHoriz,
        rotation: Literal[0, 90, 180, 270],
        mirror: Literal["x", "y", None],
) -> str:
    # normalize orientation
    orient = Orientation((rotation, mirror))
    match justify_h:
        case JustifyHoriz.LEFT:
            if orient in [(0, "y"), (90, "x"), (90, None), (180, None)]:
                text_anchor = "end"
            else:
                text_anchor = "start"
        case JustifyHoriz.CENTER:
            text_anchor = "middle"
        case JustifyHoriz.RIGHT:
            if orient in [(0, "y"), (90, "x"), (90, None), (180, None)]:
                text_anchor = "start"
            else:
                text_anchor = "end"

    return f"text-anchor:{text_anchor};"


def kicad_font_to_css(expr: Font) -> str:
    # not sure what's going on here, kicad's 1.27mm seems to be close to
    # font-size:0.5mm. there's also a second dimension for the font but that's
    # rarely (never?) exposed in kicad GUI
    return f"font-size:{expr.size[0] / 2.54}mm;"


def kicad_effects_to_css(expr: Effects) -> str:
    style = kicad_font_to_css(expr.font)

    match expr.justify.vertical:
        case JustifyVert.TOP:
            dominant_baseline = "top"
        case JustifyVert.CENTER:
            dominant_baseline = "middle"
        case JustifyVert.BOTTOM:
            dominant_baseline = "hanging"

    style += f"dominant-baseline:{dominant_baseline};"

    if expr.hide:
        style += "visibility:hidden;"

    return style


def draw_property(
        expr: SymbolProperty,
        at: tuple[float, float] = (0, 0),
        rotation: Literal[0, 90, 180, 270] = 0,
        flip_y_axis=True,
        mirror: Literal["x", "y", None] = None,
) -> svg.Text:
    x = at[0] + expr.at[0]
    if flip_y_axis:
        y = at[1] - expr.at[1]
    else:
        y = at[1] + expr.at[1]

    style = kicad_justify_h_to_anchor(
        expr.effects.justify.horizontal,
        rotation=rotation,
        mirror=mirror,
    )

    style += kicad_effects_to_css(expr.effects)

    # text is rotated either 90 or 0 in total to keep it readable
    text_rotation = (rotation + expr.at[2]) % 180

    transform: Optional[list[svg.Transform]] = None
    if text_rotation != 0:
        transform = [svg.Rotate(-text_rotation, x, y)]

    return svg.Text(
        class_=["property", "prop-" + expr.key.lower()],
        style=style,
        text=expr.value,
        x=x,
        y=y,
        transform=transform,
    )


def draw_pin(
        expr: Pin,
        at: tuple[float, float] = (0, 0),
        symbol_rotation: Literal[0, 90, 180, 270] = 0,
        symbol_mirror: Literal["x", "y", None] = None,
        draw_pin_nums=True,
        draw_pin_names=True,
        pin_name_offset=0.504,
) -> svg.G:
    elements: list[svg.Element] = []
    pin_rotation = expr.at[2]
    x1 = at[0] + expr.at[0]
    y1 = at[1] - expr.at[1]
    x2 = x1 + expr.length
    pin_line = svg.Line(
        class_=["pin-line"],
        transform=[svg.Rotate(-pin_rotation, x1, y1)],
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y1,
    )
    elements.append(pin_line)
    if not expr.hide and draw_pin_nums:
        # center the pin number to the pin
        match pin_rotation:
            case 0:
                nx = x1 + expr.length / 2
                ny = y1
            case 90:
                nx = x1
                ny = y1 - expr.length / 2
            case 180:
                nx = x1 - expr.length / 2
                ny = y1
            case 270:
                nx = x1
                ny = y1 + expr.length / 2

        number = draw_pin_number(
            expr.number,
            at=(nx, ny),
            rotation=pin_rotation,
            symbol_rotation=symbol_rotation,
            symbol_mirror=symbol_mirror,
        )
        elements.append(number)
    if not expr.hide and draw_pin_names:
        match pin_rotation:
            case 0:
                nx = x1 + expr.length
                ny = y1
            case 90:
                nx = x1
                ny = y1 - expr.length
            case 180:
                nx = x1 - expr.length
                ny = y1
            case 270:
                nx = x1
                ny = y1 + expr.length

        pin_name = draw_pin_name(
            expr.name,
            at=(nx, ny),
            rotation=pin_rotation,
            symbol_rotation=symbol_rotation,
            symbol_mirror=symbol_mirror,
            pin_name_offset=pin_name_offset,
        )
        elements.append(pin_name)

    return svg.G(class_=["pin"], elements=elements)


def draw_pin_number(
        expr: PinNumber,
        at=(0, 0),
        rotation: Literal[0, 90, 180, 270] = 0,
        symbol_rotation: Literal[0, 90, 180, 270] = 0,
        symbol_mirror: Literal["x", "y", None] = None,
) -> svg.Text:
    style = kicad_font_to_css(expr.effects.font)
    style += "text-anchor:middle;"

    transform: Optional[list[svg.Transform]] = []
    transform_origin = None

    applied_mirror = None
    orient = Orientation((symbol_rotation, symbol_mirror))
    if orient == (0, "x"):
        transform.append(svg.Scale(1, -1))
        applied_mirror = "x"
    elif orient in [(0, "y"), (90, "x"), (270, "x")]:
        transform.append(svg.Scale(-1, 1))
        applied_mirror = "y"

    match symbol_rotation:
        case 0:
            text_rotation = rotation % 180
        case 90:
            text_rotation = -(rotation % 180)
        case 180:
            text_rotation = (rotation % 180) + 180
        case 270:
            text_rotation = -(rotation % 180) + 180
    text_rotation = (text_rotation + 360) % 360
    if text_rotation != 0:
        transform.append(svg.Rotate(-text_rotation))

    x = at[0]
    y = at[1]
    # apply a little spacing away from the pin
    match Orientation((text_rotation, applied_mirror)):
        case (0, None) | (0, "y"):
            y -= 0.25
        case (90, None) | (90, "x"):
            x -= 0.25
        case (180, None) | (0, "x"):
            y += 0.25
        case (270, None) | (270, "x"):
            x += 0.25

    if not transform:
        transform = None
    else:
        transform_origin = f"{x} {y}"

    return svg.Text(
        class_=["pin-number"],
        transform=transform,
        transform_origin=transform_origin,
        text=expr.text,
        style=style,
        x=x,
        y=y,
    )


def draw_pin_name(
        expr: PinName,
        at=(0, 0),
        rotation: Literal[0, 90, 180, 270] = 0,
        symbol_rotation: Literal[0, 90, 180, 270] = 0,
        symbol_mirror: Literal["x", "y", None] = None,
        pin_name_offset=0.504,
) -> svg.Text:
    style = kicad_font_to_css(expr.effects.font)
    style += "dominant-baseline:middle;"

    transform: Optional[list[svg.Transform]] = []
    transform_origin = None

    applied_mirror = None
    orient = Orientation((symbol_rotation, symbol_mirror))
    if orient == (0, "x"):
        transform.append(svg.Scale(1, -1))
        applied_mirror = "x"
    elif orient in [(0, "y"), (90, "x"), (270, "x")]:
        transform.append(svg.Scale(-1, 1))
        applied_mirror = "y"

    match symbol_rotation:
        case 0:
            text_rotation = rotation % 180
            if (rotation, applied_mirror) in [
                (180, None),
                (270, None),
                (90, "x"),
                (0, "y"),
                (270, "y"),
                (90, "x"),
                (180, "x"),
            ]:
                style += "text-anchor:end;"
        case 90:
            text_rotation = -(rotation % 180)
            if (rotation, applied_mirror) in [
                (90, None),
                (180, None),
                (0, "y"),
                (90, "y"),
            ]:
                style += "text-anchor:end;"
        case 180:
            text_rotation = (rotation % 180) + 180
            if (rotation, applied_mirror) in [
                (0, None),
                (90, None),
            ]:
                style += "text-anchor:end;"
        case 270:
            text_rotation = -(rotation % 180) + 180
            if (rotation, applied_mirror) in [
                (270, None),
                (0, None),
                (180, "y"),
                (270, "y"),
            ]:
                style += "text-anchor:end;"
    text_rotation = (text_rotation + 360) % 360
    if text_rotation != 0:
        transform.append(svg.Rotate(-text_rotation))

    x = at[0]
    y = at[1]

    # apply spacing away from the pin
    match rotation:
        case 0:
            x += pin_name_offset + 0.2
        case 90:
            y -= pin_name_offset + 0.2
        case 180:
            x -= pin_name_offset + 0.2
        case 270:
            y += pin_name_offset + 0.2

    if not transform:
        transform = None
    else:
        transform_origin = f"{x} {y}"

    return svg.Text(
        class_=["pin-name"],
        transform=transform,
        transform_origin=transform_origin,
        style=style,
        text=expr.text,
        x=x,
        y=y,
    )


Rotate = Literal[0, 90, 180, 270]
Mirror = Literal["x", "y", None]


class Orientation(tuple[Rotate, Mirror], Enum):
    """
    Enum that unifies rotation and mirroring into one orientation. Allows
    us to normalize rotation and mirroring the way KiCad normalizes it.
    """

    UNCHANGED = (0, None)
    ROTATE_90 = (90, None)
    ROTATE_180 = (180, None)
    ROTATE_270 = (270, None)
    MIRROR_X = (0, "x")
    MIRROR_Y = (0, "y")
    ROTATE_90_MIRROR_X = (90, "x")
    ROTATE_270_MIRROR_X = (270, "x")

    @classmethod
    def _missing_(cls, value: tuple[int, Mirror]):
        """Normalize rotation and mirroring the way KiCad normalizes it."""
        if value[0] >= 360:
            return cls((value[0] % 360, value[1]))
        if value[0] < 0:
            return cls((value[0] + 360, value[1]))
        match value:
            case (90, "y"):
                return cls((270, None))
            case (180, "y"):
                return cls((0, "x"))
            case (270, "y"):
                return cls((90, "x"))
            case (180, "x"):
                return cls((0, "y"))
