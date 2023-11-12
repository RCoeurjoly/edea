import pytest

from edea.kicad.parser import from_str
from edea.kicad.pcb import MissingBoardOutlineError, Pcb


def test_exact_board_size():
    file_name = "tests/kicad_projects/ferret/ferret.kicad_pcb"
    with open(file_name, encoding="utf-8") as f:
        pcb = from_str(f.read())

    assert isinstance(pcb, Pcb)
    assert pcb.size().width_mm == 50.0 and pcb.size().height_mm == 50.0


def test_raises_error_for_pcb_without_outline():
    file_name = "tests/kicad_projects/MP2451/MP2451.kicad_pcb"
    with open(file_name, encoding="utf-8") as f:
        pcb = from_str(f.read())

    assert isinstance(pcb, Pcb)
    with pytest.raises(MissingBoardOutlineError):
        pcb.size()


def test_circle_in_edge_cuts_layer():
    file_name = "tests/kicad_projects/pcb_size/circle/circle.kicad_pcb"
    with open(file_name, encoding="utf-8") as f:
        pcb = from_str(f.read())
    assert isinstance(pcb, Pcb)
    assert pcb.size().width_mm == 71.84 and pcb.size().height_mm == 71.84


def test_line_in_edge_cuts_layer():
    file_name = "tests/kicad_projects/pcb_size/line/line.kicad_pcb"
    with open(file_name, encoding="utf-8") as f:
        pcb = from_str(f.read())
    assert isinstance(pcb, Pcb)
    assert pcb.size().width_mm == 25.4 and pcb.size().height_mm == 25.4


def test_rect_in_edge_cuts_layer():
    file_name = "tests/kicad_projects/pcb_size/rect/rect.kicad_pcb"
    with open(file_name, encoding="utf-8") as f:
        pcb = from_str(f.read())
    assert isinstance(pcb, Pcb)
    assert pcb.size().width_mm == 27.94 and pcb.size().height_mm == 27.94


def test_polygon_in_edge_cuts_layer():
    file_name = "tests/kicad_projects/pcb_size/polygon/polygon.kicad_pcb"
    with open(file_name, encoding="utf-8") as f:
        pcb = from_str(f.read())
    assert isinstance(pcb, Pcb)
    assert pcb.size().width_mm == 35.56 and pcb.size().height_mm == 55.88


def test_arc_in_edge_cuts_layer():
    file_name = "tests/kicad_projects/pcb_size/arc/arc.kicad_pcb"
    with open(file_name, encoding="utf-8") as f:
        pcb = from_str(f.read())
    assert isinstance(pcb, Pcb)
    assert pcb.size().width_mm == 43.36 and pcb.size().height_mm == 50.8


def test_arc_2_in_edge_cuts_layer():
    file_name = "tests/kicad_projects/pcb_size/arc/arc_2.kicad_pcb"
    with open(file_name, encoding="utf-8") as f:
        pcb = from_str(f.read())
    assert isinstance(pcb, Pcb)
    assert pcb.size().height_mm == 43.36 and pcb.size().width_mm == 50.8


def test_arc_3_in_edge_cuts_layer():
    file_name = "tests/kicad_projects/pcb_size/arc/arc_3.kicad_pcb"
    with open(file_name, encoding="utf-8") as f:
        pcb = from_str(f.read())
    assert isinstance(pcb, Pcb)
    assert pcb.size().width_mm == 43.36 and pcb.size().height_mm == 50.8


def test_arc_4_in_edge_cuts_layer():
    file_name = "tests/kicad_projects/pcb_size/arc/arc_4.kicad_pcb"
    with open(file_name, encoding="utf-8") as f:
        pcb = from_str(f.read())
    assert isinstance(pcb, Pcb)
    assert pcb.size().height_mm == 43.36 and pcb.size().width_mm == 50.8
