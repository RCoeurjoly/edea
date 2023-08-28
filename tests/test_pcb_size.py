import pytest

from edea.types.parser import from_str
from edea.types.pcb import MissingBoardOutlineError, Pcb


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
