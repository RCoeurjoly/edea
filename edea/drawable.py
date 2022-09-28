from __future__ import annotations

from dataclasses import dataclass
from math import tau, cos, sin
from typing import Tuple, Union

import numpy as np
import svg

from bbox import BoundingBox
from .parser import Movable


@dataclass(init=False)
class BaseDrawable(Movable):
    """
    Drawable is an object which can be converted to an SVG
    pin: line with text
    polyline: symbols drawn with line(s), e.g. the ground symbol
    rectangle: usually ic symbols
    """

    dpi = 2540

    @property
    def mmpd(self):
        return self.dpi / 25.4

    def to_dots(self, val, places=2):
        if not isinstance(val, float):
            val = float(val)
        return round(val * self.mmpd, places)

    def iter_to_dots(self, vals, places=2):
        for val in vals:
            yield self.to_dots(val, places=places)

    def point_to_dots(self, pt, places=2, offset=(0.0, 0.0)) -> Tuple[float, float]:
        return self.to_dots(offset[0] + pt[0], places=places), self.to_dots(offset[0] + pt[1], places=places)

    def points_to_dots(self, pts, places=2, offset=(0.0, 0.0)):
        for pt in pts:
            yield self.point_to_dots(pt, places, offset)

    def draw(self) -> None | svg.Polyline | svg.Rect | svg.Text | svg.Circle:
        raise NotImplementedError("should be implemented by the child class")

    def parse_visual(self, node: Union[svg.G | svg.Rect | svg.Circle | svg.Polyline | svg.Ellipse]) -> None:
        if hasattr(self, "tstamp"):
            node.id = self.tstamp[0]

        """parse fill/stroke, if present"""
        if hasattr(self, "stroke"):
            color, opacity = self.parse_color(self.stroke.color)

            # in kicad 0 usually means default
            if opacity == 0:
                opacity = 1

            stroke_width = self.stroke.width[0]
            if stroke_width == 0:
                stroke_width = 0.1524  # kicad default stroke width

            node.stroke = f"rgb({color})"
            node.stroke_opacity = opacity
            node.stroke_width = self.to_dots(stroke_width)

            match self.stroke.type[0]:
                case ("default" | "solid"):
                    pass
                case "dot":
                    node.stroke_dasharray = [1]
                case "dash":
                    node.stroke_dasharray = [3, 1]
                case "dash_dot":
                    node.stroke_dasharray = [3, 1, 1, 1]
                case "dash_dot_dot":
                    node.stroke_dasharray = [3, 1, 1, 1, 1, 1]

        if hasattr(self, "fill"):
            match self.fill.type[0]:
                case "none":
                    node.fill = "none"
                case "background":
                    # TODO: figure out how to access theme background
                    node.fill = "none"
                case "outline":
                    color, opacity = self.parse_color(self.stroke.color)
                    node.fill = f"rgb({color})"
                    node.fill_opacity = f"{opacity}"

        # add the layer name(s) as css class(es) for interactivity features
        if hasattr(self, "layer"):
            node.class_ = [self.layer[0][1:-1].replace('.', '_')]
        elif hasattr(self, "layers"):
            node.class_ = [name[1:-1].replace('.', '_') for name in self.layers.data]

        if hasattr(self, "at") and len(self.at) > 2 and self.at[2] != 0:
            # pad angle should be ignored as it refers to the footprint and not the pad directly
            if self.name in ["pad", "label", "property"]:
                return

            angle = self.at[2]

            # TODO: if type is label and angle 180, don't rotate but anchor at end of text instead of start
            # TODO: move this into a helper method because point_to_dots needs this too

            # TODO: mirror elements on the back layers along the x axis

            node.transform = [svg.Translate(self.to_dots(self.at[0]), self.to_dots(self.at[1])), svg.Rotate(angle)]

    def parse_color(self, color: list):
        """converts `r g b a` to a tuple of `(r,g,b)` and `alpha`"""
        return (f"{color[0]},{color[1]},{color[2]}", color[3])


@dataclass(init=False)
class Pts(Movable):
    """Movable is an object with a position"""

    def move_xy(self, x: float, y: float) -> None:
        """move_xy adds the position offset x and y to the object"""
        for point in self.data:
            if point.name == "xy":
                point.data[0] += x
                point.data[1] += y


@dataclass(init=False)
class Pad(BaseDrawable):
    """Pad"""

    def corners(self):
        """Returns a numpy array containing every corner [x,y]"""
        if len(self.at) > 2:
            angle = self.at.data[2] / tau
        else:
            angle = 0
        origin = self.at.data[
                 0:2
                 ]  # in this case we explicitly need to access the data list because of the range op
        # otherwise it would return a list of Expr

        if self[2] in ["rect", "roundrect", "oval", "custom"]:
            # TODO optimize this, this is called quite often

            points = np.array([[1, 1], [1, -1], [-1, 1], [-1, -1]], dtype=np.float64)
            if self[2] == "oval":
                points = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]], dtype=np.float64)
            w = self.size.data[0] / 2
            h = self.size.data[1] / 2
            angle_cos = cos(angle)
            angle_sin = sin(angle)
            for i, _ in enumerate(points):
                points[i] = origin + points[i] * [
                    (w * angle_cos + h * angle_sin),
                    (h * angle_cos + w * angle_sin),
                ]

        elif self[2] == "circle":
            points = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]], dtype=np.float64)
            radius = self.size.data[0] / 2
            for i, _ in enumerate(points):
                points[i] = origin + points[i] * [radius, radius]
        else:
            raise NotImplementedError(f"pad shape {self[2]} is not implemented")

        return points

    def draw(self) -> None | svg.Polyline | svg.Rect | svg.Circle:
        pad_type = self.data[2]

        if pad_type == "rect":
            node = svg.Rect(width=self.to_dots(self.size[0]), height=self.to_dots(self.size[1]))
        elif pad_type == "roundrect":
            node = svg.Rect(width=self.to_dots(self.size[0]), height=self.to_dots(self.size[1]),
                            rx=self.roundrect_rratio[0])
        elif pad_type == "custom":
            node = svg.Polyline(points=[])
        elif pad_type == "circle":
            node = svg.Circle(r=self.to_dots(self.size[0] / 2), fill="red", fill_opacity=0.5)
        elif pad_type == "oval":
            node = svg.Ellipse()
        else:
            raise NotImplementedError(pad_type)

        if pad_type in ["rect", "roundrect"]:
            at = [self.at[0] - self.size[0] / 2, self.at[1] - self.size[1] / 2]
            node.x, node.y = self.point_to_dots(at)
        elif pad_type == "circle":
            node.cx, node.cy = self.point_to_dots(self.at)
        elif pad_type == "custom":
            for pt in self.primitives.gr_poly.pts:
                node.points.extend(self.point_to_dots(pt))

        self.parse_visual(node)

        return node


@dataclass(init=False)
class FPLine(BaseDrawable):
    """FPLine"""

    def corners(self):
        """corners returns start and end of the FPLine"""
        points = np.array(
            [[self.start[0], self.start[1]], [self.end[0], self.end[1]]],
            dtype=np.float64,
        )
        return points

    def bounding_box(self) -> BoundingBox:
        """bounding_box of the fp_line"""
        return BoundingBox(self.corners())

    def draw(self) -> svg.Polyline:
        node = svg.Polyline(points=[])

        self.parse_visual(node)

        node.stroke_width = self.to_dots(self.width[0])
        node.points = [*self.point_to_dots(self.start),
                       *self.point_to_dots(self.end)]
        node.stroke = "black"
        node.stroke_linecap = "round"

        return node


@dataclass(init=False)
class Polygon(BaseDrawable):
    """Polygon
    TODO: Zone polygons are with absolute positions, are there other types?
    """

    def bounding_box(self) -> BoundingBox:
        """bounding_box of the polygon"""
        return BoundingBox(self.corners())

    def corners(self) -> np.array:
        """corners returns the min and max points of a polygon"""
        x_points = []
        y_points = []

        for point in self.pts:
            if point.name != "xy":
                raise NotImplementedError(
                    f"the following polygon format isn't implemented yet: {point}"
                )
            x_points.append(point[0])
            y_points.append(point[1])

        npx = np.array(x_points)
        npy = np.array(y_points)

        max_x = np.amax(npx)
        min_x = np.amin(npx)
        max_y = np.amax(npy)
        min_y = np.amin(npy)

        return np.array(
            [
                [min_x, min_y],
                [min_x, max_y],
                [max_x, max_y],
                [max_x, min_y],
            ],
            dtype=np.float64,
        )

    def draw(self) -> svg.Polyline:
        node = svg.Polyline(points=[])

        self.parse_visual(node)

        node.stroke_width = self.to_dots(0.2)  # TODO: maybe get this from the zone?
        node.points = list(self.points_to_dots(self.pts))

        if self.name == "filled_polygon":
            node.fill = "orange"
            node.fill_opacity = 0.1
        else:
            node.fill = "green"
            node.fill_opacity = 0.1

        return node


@dataclass(init=False)
class Footprint(BaseDrawable):
    """Footprint"""

    def bounding_box(self) -> BoundingBox:
        """return the BoundingBox"""
        box = BoundingBox([])
        if hasattr(self, "pad"):
            # check if it's a single pad only
            if isinstance(self.pad, list):
                _ = [box.envelop(pad.corners()) for pad in self.pad]
            else:
                box.envelop(self.pad.corners())

            if len(self.at.data) > 2:
                box.rotate(self.at.data[2])
            box.translate(self.at.data[0:2])

        if hasattr(self, "fp_line"):
            # check if it's a single line only
            if isinstance(self.fp_line, list):
                _ = [box.envelop(pad.corners()) for pad in self.pad]
            else:
                box.envelop(self.fp_line.corners())

            if len(self.at.data) > 2:
                box.rotate(self.at.data[2])
            box.translate(self.at.data[0:2])

        # TODO(ln): implement other types too, though pads and lines should work well enough

        return box

    def prepend_path(self, path: str):
        """prepend_path prepends the uuid path to the current one"""
        # path is always in the format of /<uuid>[/<uuid>]
        sub = self.path.data[0].strip('"')
        self.path.data[0] = f'"/{path}{sub}"'

    def draw(self) -> svg.G:
        fp_group = svg.G(elements=[], id=self.tstamp[0])

        if len(self.at) == 3:
            fp_group.transform = [svg.Translate(self.to_dots(self.at[0]), self.to_dots(self.at[1])),
                                  svg.Rotate(self.at[2])]
        else:
            fp_group.transform = [svg.Translate(self.to_dots(self.at[0]), self.to_dots(self.at[1]))]
        for element in self.data:
            if isinstance(element, BaseDrawable):
                node = element.draw()
                fp_group.elements.append(node)

        return fp_group


@dataclass(init=False)
class SchematicSymbol(BaseDrawable):
    """Symbol"""

    def draw(self) -> svg.G:
        sym_group = svg.G(elements=[])

        if hasattr(self, "uuid"):
            sym_group.id = self.uuid[0]

        # group at is only set if a symbol library symbol is being drawn
        if hasattr(self, "at"):
            t = [svg.Translate(self.to_dots(self.at[0]), self.to_dots(self.at[1]))]

            if len(self.at) == 3:
                t.append(svg.Rotate(self.at[2]))

            sym_group.transform = t

        for element in (e for e in self.data if isinstance(e, BaseDrawable)):
            # skip hidden expressions
            if hasattr(element, "effects") and "hide" in element.effects or element.name == "property":
                continue
            sym_group.elements.append(element.draw())

        return sym_group


@dataclass(init=False)
class Drawable(BaseDrawable):
    """
    Drawable is an object which can be converted to an SVG
    pin: line with text
    polyline: symbols drawn with line(s), e.g. the ground symbol
    rectangle: usually ic symbols
    """

    def draw(self) -> None | svg.Polyline | svg.Rect | svg.Text | svg.Circle:
        """draw the shape with the given offset"""
        # node = Elem(self.name)
        node_name = self.name
        if node_name == "pin":
            return None
        elif node_name in ["polyline", "wire", "gr_poly", "fp_poly", "segment"]:
            node = svg.Polyline(points=[])
        elif node_name == "rectangle":
            node = svg.Rect()
        elif node_name in ["property", "hierarchical_label", "text", "label", "fp_text"]:
            node = svg.Text()
        elif node_name in ["junction", "via"]:
            node = svg.Circle()
        else:
            raise NotImplementedError(node_name)

        self.parse_visual(node)

        if node_name == "pin":
            # raise NotImplementedError(node_name)
            return None
        elif node_name == "polyline":
            # list of tuples to list
            node.points = [point for points in self.points_to_dots(self.data[0]) for point in points]
        elif node_name == "rectangle":
            xc, yc = [self.start[0], self.end[0]], [self.start[1], self.end[1]]
            width = max(xc) - min(xc)
            height = max(yc) - min(yc)
            svgx = min(self.start[0], self.end[0])
            svgy = min(self.start[1], self.end[1])

            node.x = self.to_dots(svgx)
            node.y = self.to_dots(svgy)
            node.width = self.to_dots(width)
            node.height = self.to_dots(height)
        elif node_name == "wire":
            node.class_ = ["wire"]
            for point in self.data[0]:
                node.points.extend([self.to_dots(point.data[0]), self.to_dots(point.data[1])])
        elif node_name in ["property", "hierarchical_label", "text", "label", "fp_text"]:
            has_effects = hasattr(self, "effects")

            # check if it's hidden
            if has_effects and "hide" in self.effects:
                return None

            text = self.data[0].strip('"')
            if node_name in ["property", "fp_text"]:
                text = self.data[1].strip(
                    '"'
                )  # property is key, value and we only display the value

            anchor = "middle"

            x_mid = self.at[0]

            font_size = 1.27  # default font size
            if has_effects and hasattr(self.effects, "font"):
                if hasattr(self.effects.font, "size"):
                    font_size = self.effects.font.size[0]
                if hasattr(self.effects, "justify"):
                    if self.effects.justify[0] == "left":
                        anchor = "start"
                        # x_mid -= len(text)/2 * font_size
                    elif self.effects.justify[0] == "middle":
                        anchor = "center"
                    elif self.effects.justify[0] == "right":
                        anchor = "end"
                        x_mid += len(text) / 2 * font_size

            node.text_anchor = anchor

            y = self.at[1]
            if node_name in ["property", "hierarchical_label"]:
                y += font_size / 2

            # if len(position) > 0 and position[0] != 0 and position[1] != 0:
            #    x_mid = position[0] + x_mid
            #    y = position[1] - y

            node.font_family = "monospace"
            node.x = self.to_dots(x_mid)
            node.y = self.to_dots(y)
            node.font_size = self.to_dots(font_size)
            node.text = text
        elif node_name == "junction":
            node.cx = self.to_dots(self.at[0])
            node.cy = self.to_dots(self.at[1])
            node.r = self.to_dots(0.5)
            node.fill = "green"
            node.stroke = "green"
            node.stroke_width = 0
        elif node_name == "segment":
            node.stroke_width = self.to_dots(self.width[0])
            node.points = [self.to_dots(self.start[0]), self.to_dots(self.start[1]), self.to_dots(self.end[0]),
                           self.to_dots(self.end[1])]
            node.stroke = "black"
            node.stroke_linecap = "round"
        elif node_name == "via":
            node.cx = self.to_dots(self.at[0])
            node.cy = self.to_dots(self.at[1])
            node.stroke_width = self.to_dots(self.drill[0])
            node.r = self.to_dots(self.size[0] / 2)
            node.fill = "none"
            node.stroke = "black"
        elif node_name == "zone":
            pass
        else:
            raise NotImplementedError(node_name)

        return node
