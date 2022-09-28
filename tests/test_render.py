"""
SVG Rendering tests

SPDX-License-Identifier: EUPL-1.2
"""
from math import isclose
import os

import svg as svg_py

from edea.draw import draw_element, draw_svg
from edea.edea import PCB
from edea.types.parser import from_str
from tests.util import get_path_to_test_file, get_test_output_dir


class TestRendering:
    def test_draw_rect(self):
        expr = from_str("(rectangle (start -5.08 5.08) (end 5.08 -1.905))")

        assert draw_element(expr) == svg_py.Rect(
            x=-5.08,
            y=-5.08,
            width=10.16,
            height=6.985,
            class_=["fill-none"],
        )

    def test_draw_rect_stroke(self):
        expr = from_str(
            "(rectangle (start -5.08 5.08) (end 5.08 -1.905) (stroke (width 0.254) (type default) (color 120 85 0 0.5)) (fill (type background))))"
        )

        drawn = draw_element(expr, at=(20, 10))

        assert isinstance(drawn, svg_py.Rect)
        assert isclose(drawn.x, 14.92)
        assert isclose(drawn.y, 4.92)
        assert isclose(drawn.width, 10.16)
        assert isclose(drawn.height, 6.985)

        assert drawn.style is not None
        style = drawn.style.split(";")
        assert "stroke-width:0.254" in style
        assert "stroke:rgba(120, 85, 0, 0.5)" in style

        assert "fill-background" in drawn.class_

    def test_draw_polyline(self):
        expr = from_str(
            "(polyline (pts (xy -1.524 0.508) (xy 1.524 0.508)) (stroke (width 0) (type default) (color 0 0 0 0)) (fill (type none)))"
        )

        assert draw_element(expr) == svg_py.Polyline(
            points=[-1.524, -0.508, 1.524, -0.508],
            class_=["fill-none"],
        )

    def test_draw_polyline_stroke(self):
        expr = from_str(
            "(polyline (pts (xy -1.524 0.508) (xy 1.524 0.508)) (stroke (width 0.3048) (type default) (color 0 50 0 0.2)) (fill (type outline)))"
        )

        drawn = draw_element(expr, at=(12, 0))

        assert isinstance(drawn, svg_py.Polyline)
        assert drawn.points is not None
        assert isclose(drawn.points[0], 10.476)
        assert isclose(drawn.points[1], -0.508)
        assert isclose(drawn.points[2], 13.524)
        assert isclose(drawn.points[3], -0.508)

        assert drawn.style is not None
        style = drawn.style.split(";")
        assert "stroke-width:0.3048" in style
        assert "stroke:rgba(0, 50, 0, 0.2)" in style

        assert drawn.class_ is not None
        assert "fill-outline" in drawn.class_

    def test_draw_rect_direction(self):
        """kicad draws rects in any direction. SVG needs width and height to be positive."""
        expr = from_str(
            """
              (rectangle (start 74.93 20.32) (end 45.72 -7.62)
                (stroke (width 0) (type default) (color 0 0 0 0))
                (fill (type none))
              )
            """
        )
        drawn = draw_element(expr)
        assert isinstance(drawn, svg_py.Rect)
        assert type(drawn.x) is float and isclose(drawn.x, 45.72)
        assert type(drawn.y) is float and isclose(drawn.y, -20.32)
        assert type(drawn.width) is float and isclose(drawn.width, 74.93 - 45.72)
        assert type(drawn.height) is float and isclose(drawn.height, 20.32 + 7.62)

    def test_draw_file_ferret(self):
        sch_path = get_path_to_test_file("ferret/control.kicad_sch")
        with open(sch_path, encoding="utf-8") as f:
            sch = from_str(f.read())

        svg = draw_svg(sch)
        assert isinstance(svg, svg_py.SVG)

        output = get_test_output_dir()
        svg_path = os.path.join(output, "schematic_ferret_control.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg.as_str())

    def test_draw_file_rotation(self):
        sch_path = get_path_to_test_file("rotation/rotation.kicad_sch")
        with open(sch_path, encoding="utf-8") as f:
            sch = from_str(f.read())

        svg = draw_svg(sch)
        assert isinstance(svg, svg_py.SVG)

        output = get_test_output_dir()
        svg_path = os.path.join(output, "schematic_rotation.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg.as_str())

    def test_draw_file_labels(self):
        sch_path = get_path_to_test_file("labels/labels.kicad_sch")
        with open(sch_path, encoding="utf-8") as f:
            sch = from_str(f.read())

        svg = draw_svg(sch)
        assert isinstance(svg, svg_py.SVG)

        output = get_test_output_dir()
        svg_path = os.path.join(output, "schematic_labels.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg.as_str())

    def test_draw_pcb(self):
        with open(
            "../tests/kicad_projects/ferret/ferret.kicad_pcb", encoding="utf-8"
        ) as f:
            pcb = PCB(from_str(f.read()), "ferret", "")

        canvas = pcb.draw()
        with open("../test_pcb.svg", "w", encoding="utf-8") as f:
            f.write(str(canvas))
