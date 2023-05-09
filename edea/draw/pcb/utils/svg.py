"""
Utilities for working with SVG files.
Adapted from https://github.com/kitspace/kitspace-v2/blob/HEAD/processor/src/tasks/processKicadPCB/shrink_svg.py
SPDX-License-Identifier: EUPL-1.2
"""

from typing import Tuple, Union
from xml.etree.ElementTree import ElementTree  # nosec

import defusedxml.ElementTree as DET
import svgpathtools

Numeric = Union[int, float]
Box = Tuple[Numeric, Numeric, Numeric, Numeric]


def merge_bbox(left: Box, right: Box) -> Box:
    """
    Merge bounding boxes in format (xmin, xmax, ymin, ymax)
    """
    return tuple(
        f(_left, _right) for _left, _right, f in zip(left, right, [min, max, min, max])
    )


def shrink_svg(svg: ElementTree, margin_mm: float) -> None:
    """
    Shrink the SVG canvas to the size of the drawing. Add margin in
    KiCAD units.
    """
    root = svg.getroot()
    # not sure why we need to do `tostring` and then `fromstring` here but
    # otherwise we just get an empty list for `paths`.
    # `copy.deepcopy(root)` didn't work.
    paths = svgpathtools.document.flattened_paths(DET.fromstring(DET.tostring(root)))

    if len(paths) == 0:
        return
    bbox = paths[0].bbox()
    for x in paths:
        bbox = merge_bbox(bbox, x.bbox())
    bbox = list(bbox)
    bbox[0] -= margin_mm
    bbox[1] += margin_mm
    bbox[2] -= margin_mm
    bbox[3] += margin_mm

    root.set("viewBox", f"{bbox[0]} {bbox[2]} {bbox[1] - bbox[0]} {bbox[3] - bbox[2]}")
    root.set("width", str(bbox[1] - bbox[0]) + "mm")
    root.set("height", str(bbox[3] - bbox[2]) + "mm")


def remove_color(svg_element):
    """
    Removes `stroke` and `fill` properties from inline styles on an SVG element
    parsed by ElementTree. Also removes `stroke-opacity` and `fill-opacity`
    when they are not set to 0.
    """
    style = svg_element.get("style")
    if style is not None:
        style = style.split(";")
        style = [rule.split(":") for rule in style if rule != ""]
        style = [(key.strip(), value.strip()) for (key, value) in style]

        new_style = []
        for key, value in style:
            if key not in ("fill", "stroke", "fill-opacity", "stroke-opacity"):
                new_style.append((key, value))

        new_style_string = ""
        for key, value in new_style:
            new_style_string += f"{key}:{value}; "

        svg_element.set("style", new_style_string.strip())


def empty_svg(**attrs: str) -> ElementTree:
    """Construct an empty SVG document with the given attributes."""
    document = ElementTree(
        DET.fromstring(
            """<?xml version = "1.0" standalone = "no"?>
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
            "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" >
        <svg xmlns = "http://www.w3.org/2000/svg" version = "1.1"
            width="29.7002cm" height="21.0007cm" viewBox="0.000 0.000 297.002 210.00">
        </svg >"""
        )
    )
    root = document.getroot()
    for key, value in attrs.items():
        root.attrib[key] = value
    return document
