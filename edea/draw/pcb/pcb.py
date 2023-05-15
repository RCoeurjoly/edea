"""
Methods for drawing PCBs from KiCad files.
SPDX-License-Identifier: EUPL-1.2
"""
import glob
import os
import re
from tempfile import NamedTemporaryFile, TemporaryDirectory
import time
from xml.etree.ElementTree import SubElement, register_namespace  # nosec

import defusedxml.ElementTree as DET
import pcbnew

from edea.draw.themes import ThemeName, get_theme
from edea.draw.themes.style import board_theme_to_style

from .utils.kicad_version import KicadVersionError, is_kicad_v7
from .utils.svg import empty_svg, remove_color, shrink_svg

# map to names used in the kicad theme json
_to_css_map = {
    "f_cu": "copper f",
    "b_cu": "copper b",
    "f_adhesive": "f_adhes",
    "b_adhesive": "b_adhes",
    "f_silkscreen": "f_silks",
    "b_silkscreen": "b_silks",
    "user_drawings": "dwgs_user",
    "user_eco1": "eco1_user",
    "user_eco2": "eco2_user",
    "f_couryard": "f_crtyd",
    "b_couryard": "b_crtyd",
}


def _set_plot_options(plot_control, tmpdir):
    plot_options = plot_control.GetPlotOptions()
    plot_options.SetOutputDirectory(tmpdir)
    plot_options.SetPlotFrameRef(False)
    plot_options.SetSketchPadLineWidth(pcbnew.FromMM(0.35))
    plot_options.SetAutoScale(False)
    plot_options.SetMirror(False)
    plot_options.SetUseGerberAttributes(False)
    plot_options.SetScale(1)
    plot_options.SetUseAuxOrigin(True)
    plot_options.SetNegative(False)
    plot_options.SetPlotReference(True)
    plot_options.SetPlotValue(True)
    plot_options.SetPlotInvisibleText(False)
    plot_options.SetDrillMarksType(pcbnew.DRILL_MARKS_NO_DRILL_SHAPE)

    # remove solder mask from silk to be sure there is no silk on pads
    plot_options.SetSubtractMaskFromSilk(True)


def draw_pcb(content: str, theme: ThemeName) -> str:
    """
    Draws a KiCad board file from the content of `.kicad_pcb` file.
    """
    with TemporaryDirectory() as tmpdir:
        with NamedTemporaryFile(
            mode="w", delete=False, suffix=".kicad_pcb", dir=tmpdir, encoding="utf-8"
        ) as input_file:
            input_file.write(content)

        board = pcbnew.LoadBoard(input_file.name)

        plot_control = pcbnew.PLOT_CONTROLLER(board)
        _set_plot_options(plot_control, tmpdir)

        plot_plan = []

        start = pcbnew.PCBNEW_LAYER_ID_START
        end = pcbnew.PCBNEW_LAYER_ID_START + pcbnew.PCB_LAYER_ID_COUNT
        for i in range(start, end):
            name = pcbnew.LayerName(i).replace(".", "_")
            plot_plan.append((name, i))

        for layer_name, layer_id in plot_plan:
            plot_control.SetLayer(layer_id)
            plot_control.OpenPlotfile(layer_name, pcbnew.PLOT_FORMAT_SVG)
            plot_control.PlotLayer()
            time.sleep(0.01)
            plot_control.ClosePlot()

        register_namespace("", "http://www.w3.org/2000/svg")

        layers = []
        for layer_name, _ in plot_plan:
            fileglob = os.path.join(tmpdir, f"*-{layer_name}.svg")
            (filepath,) = glob.glob(fileglob)
            tree = DET.parse(filepath)
            layers.append((layer_name, tree))

        new_tree = empty_svg()
        new_root = new_tree.getroot()

    theme_obj = get_theme(theme)
    style = board_theme_to_style(theme_obj.board)

    SubElement(
        new_root,
        "style",
        {
            "type": "text/css",
            "xmlns": "http://www.w3.org/2000/svg",
        },
    ).text = style.text

    for layer_name, tree in layers:
        css_class = layer_name.lower()
        if css_class in _to_css_map:
            css_class = _to_css_map[css_class]
        elif match := re.match(r"in(\d+)_cu", css_class):
            css_class = f"copper in{match[1]}"

        layer = tree.getroot()
        group = SubElement(
            new_root,
            "g",
            {
                "class": f"kicad_svg_layer {css_class}",
            },
        )
        for child in layer:
            for e in child.iter():
                remove_color(e)
            group.append(child)

    shrink_svg(new_tree, margin_mm=1.5)

    return DET.tostring(new_root, encoding="unicode")


kicad_version = pcbnew.GetBuildVersion()
if not is_kicad_v7(kicad_version):
    raise KicadVersionError(
        f"KiCAD v7 required for drawing PCBs, found {kicad_version}"
    )
